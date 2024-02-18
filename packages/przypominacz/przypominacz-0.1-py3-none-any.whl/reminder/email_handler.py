"""Plik ten zawiera implementacje klasy Email ktora zarzadza wysylaniem emaili."""
# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import configparser
import logging
import re

class Email:
    """
    Klasa zarzadzajaca wysylaniem emaili.
    Atrybuty klasy ktore sa wczytywane z pliku konfiguracyjnego:
    :param from_address (str): Adres mailowy nadawcy.
    :param to_addresses (list[str]): Lista adresow mailowych odbiorcow.
    :param subject (str): Temat emaila.
    :param body (str): Tresc emaila.
    """
    def __init__(self, config_path: str):
        """
        Funkcja inicjalizujaca klase Email.
        :param config_path (str): Sciezka do pliku konfiguracyjnego.        
        """             
        config = configparser.ConfigParser()
        config.read(config_path)   
        
        self.from_address = config.get('Email_info', 'from_address')
        self._validate_emails(self.from_address)
        self.to_addresses = list(config.get('Email_info', 'to_addresses').split(', '))
        self._validate_emails(self.to_addresses)
        self.subject = config.get('Email_info', 'subject')
        self.body = config.get('Email_info', 'body')
        
    def _validate_emails(self, emails:list[str]|str):
        """
        Funkcja ktora sprawdza poprawnosc emaili.
        :param emails (list[str]|str): Lista emaili, badz pojedynczy email. 
        """
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if isinstance(emails, str):
            emails = [emails]
        for email in emails:
            if not email_regex.match(email):
                logging.info(f"Email address: {email} has an incorrect format.")

    def _send_emails(self, server: SMTP_SSL):
        """
        Funkcja sluzaca do wysylania emaili do odbiorcow z listy 'to_addresses'.
        :param server (SMTP_SSL): Serwer.
        """
        for address in self.to_addresses:            
            self.message = MIMEMultipart()
            self.message['To'] = address
            self.message['From'] = self.from_address
            self.message['Subject'] = self.subject
            self.message.attach(MIMEText(self.body, 'plain'))
            server.sendmail(self.from_address, address, self.message.as_string())
        
        logging.info('Emails have been sent successfully.')