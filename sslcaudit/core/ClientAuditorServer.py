# ----------------------------------------------------------------------
# SSLCAUDIT - a tool for automating security audit of SSL clients
# Released under terms of GPLv3, see COPYING.TXT
# Copyright (C) 2012 Alexandre Bezroutchko abb@gremwell.com
# ----------------------------------------------------------------------

import  logging
from threading import Thread
from Queue import Queue
import itertools
import threading
from sslcaudit.core.ClientConnection import ClientConnection
from sslcaudit.core.ClientHandler import ClientHandler
from sslcaudit.core.ThreadingTCPServer import ThreadingTCPServer

logger = logging.getLogger('ClientAuditorTCPServer')


class ClientAuditorServer(Thread):
    '''
    This class with specification of listen port, a list of profiles, and result queue.
    It works in a separate Thread and uses ClientAuditorTCPServer server to receive connections from clients under test.
    It distinguishes between different clients by their IP addresses. It creates an instance of ClientHandler class
    for each individual client and calls ClientHandler.handle() for each incoming connection.
    By itself this class does not interpret the content of 'profiles' in any way, just passes it to the constructor of
    ClientHandler. If res_queue is None, this class will create its own Queue and make accessible to users of this class
    via ClientAuditorServer res_queue.
    '''

    def __init__(self, listen_on, profile_factories, res_queue=None):
        Thread.__init__(self, target=self.run)
        self.daemon = True

        self.listen_on = listen_on
        self.clients = {}
        self.lock = threading.Lock()  # this lock has to be acquired before using clients dictionary
        self.profile_factories = profile_factories

        # create a local result queue unless one is already provided
        if res_queue == None:
            self.res_queue = Queue()
        else:
            self.res_queue = res_queue

        # create TCP server and make it use our method to handle the requests
        self.tcp_server = ThreadingTCPServer(self.listen_on)
        self.tcp_server.finish_request = self.finish_request

    def finish_request(self, sock, client_address):
        # this method overrides TCPServer implementation and actually handles new connections
        # it may be invoked from different threads, in parallel

        # create new conn object and obtain client id
        conn = ClientConnection(sock, client_address)
        client_id = conn.get_client_id()

        # find or create a session handler
        with self.lock:
            if not self.clients.has_key(client_id):
                logger.debug('new client %s [id %s]', conn, client_id)
                profiles = self.mk_client_profiles_list()
                handler = ClientHandler(client_id, profiles, self.res_queue)
                self.clients[client_id] = handler
            else:
                handler = self.clients[client_id]

        # handle the request
        handler.handle(conn)

    def run(self):
        logger.info('listen_on: %s' % str(self.listen_on))
        self.tcp_server.serve_forever()

    def stop(self):
        ''' this method can only be invoked if the server is already running '''
        self.tcp_server.shutdown()
        self.server_close()

    def server_close(self):
        self.tcp_server.server_close()

    def mk_client_profiles_list(self):
        return list(itertools.chain.from_iterable(self.profile_factories))
