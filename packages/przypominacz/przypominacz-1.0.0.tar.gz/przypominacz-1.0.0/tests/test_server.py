"""Testy dla pliku 'server.py' """
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import configparser
import io
import smtplib
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reminder")))
from reminder.server import MyServer

class TestMyServer(unittest.TestCase):
    
    @patch('builtins.open', return_value = io.StringIO('[Other_section]\nsome_key: some_value')) 
    def test_load_config_missing_section(self, mock_open):
        """
        Test wczytania danych z pliku, w ktorym brakuje odpowiedniej sekcji.
        :param mock_open: Mock dla funkcji 'open'.        
        """
        with self.assertRaises(configparser.NoSectionError) as my_except:
             MyServer('fake_file.ini')
        self.assertEqual(str(my_except.exception), "No section: 'Serwer'")
    
    @patch('email_handler.Email', autospec=True)    
    @patch('builtins.open')
    def test_invalid_arguments(self, mock_open, mock_email_handler):
        """
        Test wczytywania niepoprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_open.return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = j11\nusername = test@example.com\npassword = examplePassword')
        with self.assertRaises(ValueError)as my_except:
            MyServer('fake_path.ini')
        self.assertEqual(str(my_except.exception), "invalid literal for int() with base 10: 'j11'")
        
        mock_open.return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = -111\nusername = test@example.com\npassword = examplePassword')
        with self.assertRaises(ValueError)as my_except:
            MyServer('fake_path.ini')
        self.assertEqual(str(my_except.exception), "The variable 'smtp_port' loaded from the configuration file is less than 0.")
        

    @patch('email_handler.Email', autospec=True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    def test_successed_loaded_data(self, mock_open, mock_email_handler):
        """
        Test wczytywania poprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        server_instance =MyServer('fake_file.ini')       
        self.assertEqual(server_instance.smtp_server, 'test.example.com')
        self.assertEqual(server_instance.smtp_port, 111)
        self.assertEqual(server_instance.username , 'test@example.com')
        self.assertEqual(server_instance.password , 'examplePassword')
           
    @patch('email_handler.Email', autospec=True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL')
    def test__connect_to_server_success(self, mock_smtp, mock_open, mock_email_handler):
        """
        Test poprawnego laczenia sie z serverem SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        server_instance = MyServer('fake_path.ini')
        server_instance._connect_to_server()        
        mock_smtp.assert_called_once_with(server_instance.smtp_server, server_instance.smtp_port)
        self.assertIsNotNone(server_instance.server)
        
    @patch('email_handler.Email', autospec=True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL', autospec=True)
    def test__connect_to_server_failure(self, mock_smtp, mock_open, mock_email_handler):
        """
        Test niepoprawnego laczenia sie z serverem SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_smtp.side_effect = smtplib.SMTPException("Connection error")
        server_instance = MyServer('fake_path.ini')
        with self.assertRaises(smtplib.SMTPException)as my_except:
            server_instance._connect_to_server()
        self.assertEqual(str(my_except.exception), "Connection error")
           
    @patch('email_handler.Email', autospec=True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL')
    def test_login_success(self, mock_smtp, mock_open, mock_email_handler):     
        """
        Test poprawnego logowania sie na serwerze SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_smtp.login.return_value = None           
        server_instance = MyServer('fake_path.ini',server = mock_smtp)        
        server_instance._log_in()       
        mock_smtp.login.assert_called_once_with(server_instance.username, server_instance.password)    
        
    @patch('email_handler.Email', autospec=True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL')
    def test_login_failure(self, mock_smtp, mock_open, mock_email_handler):
        """
        Test niepoprawnego logowania sie na serwerze SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_smtp.login.side_effect = Exception("Login error")
        server_instance = MyServer('fake_path.ini',server = mock_smtp)        
        with self.assertRaises(Exception):
            server_instance._log_in()               
        mock_smtp.login.assert_called_once_with(server_instance.username, server_instance.password)
            
    @patch('email_handler.Email', autospec=True)
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL')
    def test_disconnect_success(self, mock_smtp, mock_open, mock_exist, mock_email_handler):
        """
        Test poprawnego wylogowania sie z serwera SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funckji 'exist'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_smtp.quit.return_value = None
        server_instance = MyServer('fake_path.ini',server = mock_smtp)
        server_instance._disconnect_from_server()        
        mock_smtp.quit.assert_called_once()
  
    @patch('email_handler.Email', autospec=True)
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open', return_value = io.StringIO('[Serwer]\nhost = test.example.com\nport = 111\nusername = test@example.com\npassword = examplePassword'))
    @patch('smtplib.SMTP_SSL')
    def test_disconnect_success(self, mock_smtp, mock_open, mock_exist, mock_email_handler):
        """
        Test niepoprawnego wylogowania sie z serwera SMTP.
        :param mock_smtp: Mock dla obiektu 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funckji 'exist'.
        :param mock_email_handler: Mock dla klasy Email.
        """
        mock_smtp.quit.side_effect = Exception('Disconnect failed.')
        server_instance = MyServer('fake_path.ini',server = mock_smtp)        
        with self.assertRaises(Exception):
            server_instance._disconnect_from_server()        
        mock_smtp.quit.assert_called_once()
    
if __name__ == '__main__':
    unittest.main()