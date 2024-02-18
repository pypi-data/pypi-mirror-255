"""Glowny plik zarzadzajacy calym funkcjonowaniem programu."""
# -*- coding: utf-8 -*-
from datetime import time as time_datetime
from datetime import timedelta, datetime
import configparser
import logging
import random
import sched
import time
import os
import smtplib

import server

logging.basicConfig(filename = 'logs/reminder_logging.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
__all__ = ['start_task', 'stop_task', 'make_new_remind'] 

class Reminder:
    """
    Glowna klasa, ktora zarzadza funkcjonowaniem calego programu.
    Atrybuty klasy ktore sa wczytywane z pliku konfiguracyjnego:
    :param from_time_frame (datetime): Poczatek przedzialu czasowego w ktorym beda wysylane maile.
    :param to_time_frame (datetime): Koniec przedzialu czasowego w ktorym beda wysylane maile.
    :param days (list[int]): Lista dni w ktore bede wysylane maile.
    :param average_frequency (int): Srednia czestotliwosc z jaka beda wysylane maile.
    :param server_info (MyServer): Obiekt klasy MyServer.
    :param background_thread (Thread): Parametr okreslajacy dzialanie programu w tle.
    :param is_running (bool): Parametr ktory uruchamia glowna petle programu.
    """
    def __init__(self,config_path: str):
        """
        Funkcja inicjalizujaca klase Reminder.
        :param config_path (str): Sciezka do pliku konfiguracyjnego.        
        """
        if not (os.path.exists(config_path)):
            raise FileNotFoundError
            
        config = configparser.ConfigParser()
        config.read(config_path)   
            
        self.from_time_frame = datetime.strptime(config.get('Reminder', 'from_time_frame'), "%H:%M").time()
        self.to_time_frame = datetime.strptime(config.get('Reminder', 'to_time_frame'), "%H:%M").time()
        self.days = [int(day) for day in config.get('Reminder', 'days').split(',')]
        self.average_frequency = int(config.get('Reminder', 'average_frequency'))
        self._validate_data()
        self.server_info = server.MyServer(config_path)
        self.is_running = False    
        
            
    def _validate_data(self):
        """
        Funkcja ktora waliduje wczytane dane do klasy Reminder.
        """
        self._validate_time_frame()
        self._validate_days()
        self._validate_average_frequency()
        
    def _validate_time_frame(self):  
        """
        Funkcja ktora sprawdza czy wczytany przedzial czasowy jest poprawny.
        """
        if self.from_time_frame > self.to_time_frame:
           raise ValueError(f"Incorrect time frames: {self.from_time_frame} is a later time than {self.to_time_frame}.")  
                                                          
    def _validate_days(self):
        """
        Funkcja ktora sprawdza czy dni w ktorych maja byc wysylane emaile sa poprawne.
        """
        for day in self.days:
                if day>6 or day<0:
                   raise ValueError("The variable 'days' loaded from the configuration file is not within the range from 0 to 6.")

    def _validate_average_frequency(self):
        """
        Funkcja ktora sprawdza czy srednia czestotliwosc jesr poprawna.
        """
        if self.average_frequency < 1:
          raise ValueError("The variable 'average_frequency' loaded from the configuration file is less than 1.")  
                    
    def _reminder_task(self):
        """
        Funkcja ktora zawiera glowna petle programu.
        """                 
        while self.is_running:
            self.server_info._send_emails()
            s = sched.scheduler(time.time, time.sleep)
            
            for _ in range(self.average_frequency):
            
                start_seconds = self.from_time_frame.hour * 3600 + self.from_time_frame.minute * 60
                end_seconds = self.to_time_frame.hour * 3600 + self.to_time_frame.minute * 60

                random_seconds = random.randint(start_seconds, end_seconds)
                random_time = time_datetime(hour=random_seconds // 3600, minute=(random_seconds % 3600) // 60)
                random_day = random.choice(self.days)
                
                scheduled_day = datetime.now() + timedelta(days=(random_day - datetime.now().weekday()))
                scheduled_day = scheduled_day.replace(hour=random_time.hour, minute=random_time.minute) 
                print(scheduled_day)
                if scheduled_day >= datetime.now():
                    s.enterabs(scheduled_day.timestamp(), 1, self.server_info._send_emails, ())
                        
            while s.queue:
                if not self.is_running:
                    break
                
                s.run(blocking=False)
                time.sleep(1)

            if not self.is_running:
                print('Script ended')
                break
            
            # Ustalam date na koniec biezacego tygodnia
            end_of_current_week = datetime.now() + timedelta(days=(6 - datetime.now().weekday()))
            end_of_current_week = end_of_current_week.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Program czeka do konca biezacego tygodnia
            logging.info("All emails scheduled for this week have been sent.")
            logging.info("The program waits until the end of the current week.")
            while self.is_running and (datetime.now() < end_of_current_week):
                time.sleep(1)
        
    def start_task(self):
        """Funkcja ta ustawia parametr 'is.running' na true, po czym uruchamia glowna funkcje programu."""
        
        try:
            if not self.is_running:
                logging.info("The program has been started.")
                self.is_running = True
                self._reminder_task()
        
        except smtplib.SMTPException as e:
            logging.error(f"An error occurred during login: {e}")       
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
        finally:
            self.stop_task()
        
    def stop_task(self):
        """Funkcja ta ustawia parametr 'is.running' na false, po czym konczy dzialanie programu."""
        self.is_running = False       
        logging.info("The program has been terminated.")
        logging.shutdown()
         
def make_new_remind(config_path: str)-> Reminder|None:   
    """
    Funkcja tworzaca nowy obiekt klasy Remind.
    :param config_path (str): Sciezka do pliku z konfiguracja.
    :return new_remind (Reminder|None)
    """
    try:
        new_remind = Reminder(config_path)
    except FileNotFoundError:
        logging.error(f"The configuration file was not found: {config_path}")
        new_remind = None
    except configparser.Error as e:
        logging.error(f"Error in the configuration file: {config_path}")
        logging.error(f"Error message: {str(e)}")     
        new_remind = None
    except ValueError as e:
        logging.error(f"Error occurred during data validation: {str(e)}")
        new_remind = None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        new_remind = None
    finally:   
        return new_remind