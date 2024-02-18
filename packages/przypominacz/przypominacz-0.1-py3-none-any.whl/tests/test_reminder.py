"""Testy dla pliku 'reminderm.py"""
# -*- coding: utf-8 -*-
import datetime
import unittest
from unittest.mock import patch
from datetime import datetime
import threading
import io
import configparser
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reminder")))
from reminder.reminderm import Reminder
from reminder.server import MyServer

class TestReminder(unittest.TestCase):

    @patch('server.MyServer', autospec=True)
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open', return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:05\nto_time_frame = 13:09\ndays = 2, 4\naverage_frequency = 5'))
    def test_successed_loaded_data(self, mock_open, mock_exist, mock_MyServer):
        """
        Test wczytywania poprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funkcji 'os.path.exists'.
        :param mock_server: Mock dla klasy MyServer.
        """
        reminder_instance = Reminder('fake_file.ini')       
        self.assertEqual(reminder_instance.from_time_frame, datetime.strptime('13:05', "%H:%M").time())
        self.assertEqual(reminder_instance.to_time_frame, datetime.strptime('13:09', "%H:%M").time())
        self.assertEqual(reminder_instance.days , [2,4])
        self.assertEqual(reminder_instance.average_frequency , 5)
              
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open')
    def test_arguments_exceptions(self, mock_open, mock_exist):
        """
        Test wczytywania niepoprawnych danych z pliku konfiguracyjnego.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funkcji 'os.path.exists'.
        """
        #test niepoprawny format time_frame  
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:10\nto_time_frame = 13:j0\ndays = 2\naverage_frequency = 5')
        with self.assertRaises(Exception) as my_except:
            Reminder('fake_path.ini')
        self.assertEqual(str(my_except.exception), "time data '13:j0' does not match format '%H:%M'")
        #test niepoprawny format time_frame        
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:11\nto_time_frame = 13:g9\ndays = 2\naverage_frequency = 5')
        with self.assertRaises(Exception) as my_except:
            Reminder('fake_file.ini')       
        self.assertEqual(str(my_except.exception), "time data '13:g9' does not match format '%H:%M'")
        #test niepoprawny format days
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:05\nto_time_frame = 13:09\ndays = t0\naverage_frequency = 10')
        with self.assertRaises(Exception) as my_except:
            Reminder('fake_file.ini') 
        self.assertEqual(str(my_except.exception), "invalid literal for int() with base 10: 't0'")
        #test niepoprawny format average_frequency
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:05\nto_time_frame = 13:09\ndays = 2\naverage_frequency = j')
        with self.assertRaises(Exception) as my_except:
            Reminder('fake_file.ini') 
        self.assertEqual(str(my_except.exception), "invalid literal for int() with base 10: 'j'")
                          
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open')
    def test_init_invalid_arguments(self, mock_open, mock_exist):
        """
        Test walidacji niepopawnych danych.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funkcji 'os.path.exists'.
        :param mock_server: Mock dla klasy 'MyServer'.
        """
        #test niepoprawne przedzialy timr_frame
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:15\nto_time_frame = 13:10\ndays = 2\naverage_frequency = 5')
        with self.assertRaises(ValueError)as my_except:
            Reminder('fake_path.ini')
        self.assertEqual(str(my_except.exception), "Incorrect time frames: 13:15:00 is a later time than 13:10:00.")
        #test niepoprawny format days
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:05\nto_time_frame = 13:09\ndays = 10\naverage_frequency = 10')
        with self.assertRaises(ValueError)as my_except:
            Reminder('fake_path.ini')
        self.assertEqual(str(my_except.exception), "The variable 'days' loaded from the configuration file is not within the range from 0 to 6.")
        #test niepoprawny format average_frequency
        mock_open.return_value = io.StringIO('[Reminder]\nfrom_time_frame = 13:05\nto_time_frame = 13:09\ndays = 2\naverage_frequency = 0')
        with self.assertRaises(ValueError) as my_except:
            Reminder('fake_path.ini')
        self.assertEqual(str(my_except.exception), "The variable 'average_frequency' loaded from the configuration file is less than 1.")

    def test_init_invalid_file(self):
        """
        Test wczytania pliku konfiguracyjnego o nieprawidlowej sciezce.
        """   
        with self.assertRaises(FileNotFoundError):
            Reminder('fake_path.ini')
        
    @patch('os.path.exists', return_value = True)
    @patch('builtins.open', return_value = io.StringIO('[Other_section]\nsome_key: some_value'))
    def test_init_missing_section(self, mock_open, mock_exist):
        """
        Test wczytania danych z pliku, w ktorym brakuje odpowiedniej sekcji.
        :param mock_open: Mock dla funkcji 'open'.
        :param mock_exist: Mock dla funkcji 'os.path.exists'.
        """
        with self.assertRaises(configparser.NoSectionError):
             Reminder('fake_file.ini')
             
    @patch('reminder.reminderm.logging.error')   
    @patch('sys.exit')
    def test_reminder_task(self, mock_exit, mock_log_error):        
        """
        Test sprawdzajacy poprawne dzialanie glownej funkcji 'reminder_task'.
        :param mock_exit: Mock dla funkcji 'exit'. 
        :param mock_log_error: Mock dla funkcji 'logging.error'.
        """
        new_remind = Reminder('config\configuration.ini')

        watek_glowny = threading.Thread(target=new_remind.start_task)
        watek_glowny.start()

        time.sleep(5)

        zatrzymaj_watek = threading.Thread(target=new_remind.stop_task)
        zatrzymaj_watek.start()

        watek_glowny.join()

        mock_log_error.assert_not_called()
        
if __name__ == '__main__':
    unittest.main()