''' ----------------------------------------------------------------------
SSLCAUDIT - a tool for automating security audit of SSL clients
Released under terms of GPLv3, see COPYING.TXT
Copyright (C) 2012 Alexandre Bezroutchko abb@gremwell.com
---------------------------------------------------------------------- '''

import sys, logging

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import SSLCAuditGUIGenerated

logger = logging.getLogger('SSLCAuditGUI')

class SSLCAuditGUI(object):
    def __init__(self, options):
        '''
        Initialize UI. Dictionary 'options' comes from SSLCAuditUI.parse_options().
        '''
        self.options = options

        self.app = QApplication(sys.argv)
        self.window = SSLCauditGUIWindow(self.options)

    def run(self):
        self.window.show()
        
        return self.app.exec_()


class SSLCauditGUIWindow(QMainWindow):
    def __init__(self, options, parent=None):
        '''
        Initialize UI. Dictionary 'options' comes from SSLCAuditUI.parse_options().
        '''
        QMainWindow.__init__(self, parent)
        
        self.options = options
        
        # Initialize the UI and store it within the self.ui variable
        self.ui = SSLCAuditGUIGenerated.Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Gives the "Start" button an icon.
        self.ui.startButton.setIcon(QIcon.fromTheme('media-playback-start'))

        # Gives each of the "Browse" buttons an icon.
        for control in [
          self.ui.certificateBrowse1,
          self.ui.certificateBrowse2,
          self.ui.keyBrowse1,
          self.ui.keyBrowse2
        ]:
          control.setIcon(QIcon.fromTheme('document-open'))
        
        # Validates the IP address box via regex
        ip_validator = QRegExpValidator(self)
        ip_validator.setRegExp(QRegExp(
            r'^([01]?\d\d?|2[0-4]\d|25[0-5])\.' +
             r'([01]?\d\d?|2[0-4]\d|25[0-5])\.' +
             r'([01]?\d\d?|2[0-4]\d|25[0-5])\.' +
             r'([01]?\d\d?|2[0-4]\d|25[0-5])$'
        ))
        self.ui.ipAddressLineEdit.setValidator(ip_validator)
        
        # Validates the port box via an integer validator
        port_validator = QIntValidator(self)
        port_validator.setRange(0, 65535)
        self.ui.portLineEdit.setValidator(port_validator)
        