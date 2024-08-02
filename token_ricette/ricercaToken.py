import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
from dateutil import parser, tz
import httpx
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def login_gmail():
    logging.info("Tentativo di login all'email.")
    try:
        email_address = EMAIL_ADDRESS
        password = EMAIL_PASSWORD
        sender_email = 'noreply@apss.tn.it'

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, password)
        logging.info("Login riuscito.")
        mail.select("inbox")
        status, messages = mail.search(None, f'(FROM "{sender_email}")')
        if status != "OK":
            raise Exception("Errore durante la ricerca delle email.")
        message_ids = messages[0].split()
        logging.info(f"Trovate {len(message_ids)} email.")
        return mail, message_ids
    except Exception as e:
        logging.error(f"Errore durante il login o la ricerca delle email: {e}")
        return None, []

def parse_email_date(date_str):
    try:
        return parser.parse(date_str, dayfirst=True).astimezone(tz.tzlocal())
    except Exception as e:
        logging.error(f"Errore durante il parsing della data dell'email: {e}")
        return None

def is_token_valid(email_date, validity_minutes=60):
    try:
        current_time = datetime.now(tz.tzlocal())
        time_difference = (current_time - email_date).total_seconds() / 60
        is_valid = 0 <= time_difference <= validity_minutes
        logging.info(f"Token valido: {is_valid}")
        return is_valid
    except Exception as e:
        logging.error(f"Errore durante la validazione del token: {e}")
        return False

def extract_token_from_email(msg, subject_keyword, span_class=None, table_index=None):
    try:
        if subject_keyword in msg["Subject"]:
            logging.info(f"Email trovata con soggetto: {subject_keyword}")
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type in ["text/plain", "text/html"]:
                        body = part.get_payload(decode=True)
                        if body:
                            soup = BeautifulSoup(body.decode('utf-8', 'ignore'), "html.parser")
                            if span_class:
                                token = soup.find("span", class_=span_class).get_text()
                                logging.info(f"Token trovato: {token}")
                                return token
                            if table_index is not None:
                                table_data = soup.find("table").find_all("td")
                                if len(table_data) > table_index:
                                    token = table_data[table_index].get_text()
                                    logging.info(f"Token trovato: {token}")
                                    return token
            else:
                body = msg.get_payload(decode=True)
                if body:
                    soup = BeautifulSoup(body.decode('utf-8', 'ignore'), "html.parser")
                    if span_class:
                        token = soup.find("span", class_=span_class).get_text()
                        logging.info(f"Token trovato: {token}")
                        return token
                    if table_index is not None:
                        table_data = soup.find("table").find_all("td")
                        if len(table_data) > table_index:
                            token = table_data[table_index].get_text()
                            logging.info(f"Token trovato: {token}")
                            return token
        return None
    except Exception as e:
        logging.error(f"Errore durante l'estrazione del token dall'email: {e}")
        return None

def token_emergenze():
    logging.info("Inizio estrazione token emergenze.")
    mail, message_ids = login_gmail()
    token = None
    valid = False

    num_emails_to_read = 10  # Cambia questo valore se necessario

    for msg_id in message_ids[::-1][:num_emails_to_read]:
        try:
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            email_date = parse_email_date(msg["Date"])

            if email_date:
                token = extract_token_from_email(msg, "Token per SAR emergenza", span_class="p14LB")
                if token:
                    valid = is_token_valid(email_date)
                    break
        except Exception as e:
            logging.error(f"Errore durante l'elaborazione dell'email con ID {msg_id}: {e}")

    mail.logout()
    logging.info(f"Token emergenze: {token}, valido: {valid}")
    return token, valid

def token_ricetta_bianca_elettronica():
    logging.info("Inizio estrazione token ricetta bianca elettronica.")
    mail, message_ids = login_gmail()
    token = None
    valid = False

    num_emails_to_read = 10  # Cambia questo valore se necessario

    for msg_id in message_ids[::-1][:num_emails_to_read]:
        try:
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            token = extract_token_from_email(msg, "A.P.S.S. - Token per Ricetta Bianca Elettronica", table_index=1)
            if token:
                validita_token = extract_token_from_email(msg, "A.P.S.S. - Token per Ricetta Bianca Elettronica", table_index=5)
                if validita_token:
                    if (parse_email_date(validita_token) - datetime.now(tz.tzlocal())).total_seconds() / 60 > 0:
                        valid = True
                        break
        except Exception as e:
            logging.error(f"Errore durante l'elaborazione dell'email con ID {msg_id}: {e}")

    mail.logout()
    logging.info(f"Token ricetta bianca elettronica: {token}, valido: {valid}")
    return token, valid

def richiesta_token_emergenza():
    logging.info("Inizio richiesta token emergenza tramite HTTP.")
    try:
        with httpx.Client(timeout=None, follow_redirects=True) as client:
            data = {
                'user': USERNAME,
                'password': PASSWORD,
                'login': 'login',
            }
            response = client.post("https://servizi.apss.tn.it/farmacie/login.php", data=data)
            logging.info(f"Richiesta HTTP completata con status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Errore durante la richiesta HTTP: {e}")

if __name__ == "__main__":
    # logging.info(f"Token emergenze: {token_emergenze()}")
    logging.info(f"Token ricetta bianca elettronica: {token_ricetta_bianca_elettronica()}")