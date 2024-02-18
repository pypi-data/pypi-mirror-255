"""Testy dla pliku 'email_handler.py' """
# -*- coding: utf-8 -*-
from unittest.mock import patch, ANY, call
import configparser
import unittest
import os
import sys
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reminder")))
from reminder.email_handler import Email

class TestEmailHandler(unittest.TestCase):
    
    @patch('builtins.open', return_value = io.StringIO('[Email_info]\nfrom_address = test@example.com\nto_addresses = recipient1@example.com, recipient2@example.com\nsubject = Test Subject\nbody = Test Body'))
    def test_successed_loaded_data(self, mock_open):
        """
        Test wczytywania poprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        """
        email_instance = Email('fake_file.ini')       
        self.assertEqual(email_instance.from_address, 'test@example.com')
        self.assertEqual(email_instance.to_addresses, ['recipient1@example.com', 'recipient2@example.com'])
        self.assertEqual(email_instance.subject , 'Test Subject')
        self.assertEqual(email_instance.body , 'Test Body')
       
    @patch('builtins.open', return_value = io.StringIO('[Other_section]\nsome_key: some_value')) 
    def test_load_config_missing_section(self, mock_open):
        """
        Test wczytywania danych z pliku konfiguracyjnego w ktorym brakuje sekcji.
        :param mock_open: Mock dla funkcji 'open'.
        """
        with self.assertRaises(configparser.NoSectionError) as my_except:
             Email('fake_file.ini')
        self.assertEqual(str(my_except.exception), "No section: 'Email_info'")
        
    @patch('reminder.email_handler.logging.info') 
    @patch('builtins.open')
    def test_invalid_arguments(self, mock_open, mock_log_info):
        """
        Test wczytywania niepoprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_log_error: Mock dla funkcji 'logging.error'.
        """
        mock_open.return_value = io.StringIO('[Email_info]\nfrom_address = testexample.com\nto_addresses = recipient1@example.com, recipient2@example.com\nsubject = Test Subject\nbody = Test Body')
        Email('fake_path.ini')       
        mock_log_info.assert_called_with("Email address: testexample.com has an incorrect format.")
        
    @patch('builtins.open', return_value = io.StringIO('[Email_info]\nfrom_address = test@example.com\nto_addresses = recipient1@example.com, recipient2@example.com\nsubject = Test Subject\nbody = Test Body'))      
    @patch('smtplib.SMTP_SSL')   
    def test__send_emails_successful(self, mock_smtp, mock_open):
        """
        Test poprawnego wysylania emaili.
        :param mock_smtp: Mock dla instancji klasy 'SMTP_SSL'.
        :param mock_open: Mock dla funkcji 'open'.
        """
        mock_server_instance = mock_smtp.return_value        
        email_instance = Email('fake_path.ini')       
        with patch.object(mock_server_instance, 'sendmail') as mock_sendmail:
            email_instance._send_emails(mock_server_instance)

        expected_calls = [call(email_instance.from_address, address, ANY) for address in email_instance.to_addresses]
        mock_sendmail.assert_has_calls(expected_calls, any_order=True)  
            
if __name__ == '__main__':
    unittest.main()