"""Plik inicjalizujacy klase MyServer ktora zarzadza akcjami zwiazanymi z serwerem."""
# -*- coding: utf-8 -*-
import configparser
import logging
import smtplib

import email_handler

class MyServer:
    """
    Klasa zarzadzajaca serwerem.
    Atrybuty klasy ktore sa wczytywane z pliku konfiguracyjnego:
    :param smtp_server (str): Host serwera.
    :param smtp_port (int): Port serwera.
    :param server (SMTP_SSL): Serwer.
    :param username (str): Nazwa uzytkownika do logowania sie na poczte nadawcy.
    :param password (str): Haslo do logowania sie na poczte nadawcy.
    """
    def __init__(self, config_path: str, server: smtplib.SMTP_SSL=None):
        """
        Funkcja inicjlaizujaca klase MyServer.
        :param config_path (str): Sciezka do pliku konfiguracyjnego.
        :param server (SMTP_SSL): Serwer.
        """             
        config = configparser.ConfigParser()
        config.read(config_path)   
        
        self.smtp_server = config.get('Serwer', 'host')
        self.smtp_port = int(config.get('Serwer', 'port'))  
        self._validate_smtp_port()
        self.username = config.get('Serwer', 'username')
        self.password = config.get('Serwer', 'password') 
        self.server = server 
        self.email_info = email_handler.Email(config_path)  

    def _validate_smtp_port(self):
        """
        Funkcja ktora sprawdza czy port jest poprawny.
        """
        if self.smtp_port < 1 or self.smtp_port > 65535:
           raise ValueError("The variable 'smtp_port' loaded from the configuration file is less than 0.")            
    
    def _connect_to_server(self):
        """
        Funkcja sluzaca do nawiazywania polaczenia z serwerem.
        """
        logging.info("Attempt to connect to the server.")        
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        logging.info("A connection to the server has been established.")
            
    def _log_in(self):
        """
        Funkcja sluzaca do logowania sie na poczte.
        """

        self.server.login(self.username, self.password)
        logging.info("Successfully logged in to the server.")

            
    def _disconnect_from_server(self):   
        """
        Funkcja sluzaca do rozlaczenia polaczenia z serwerem.
        """
        self.server.quit()
        logging.info("Successfully logged out from the server.")
       
    def _send_emails(self):
        """
        Funkcja obslugujaca wszystkie niezbedne akcje zwiazane z wysylaniem emaili.
        """
        self._connect_to_server()
        self._log_in()
        self.email_info._send_emails(self.server)
        self._disconnect_from_server()


         


         
        