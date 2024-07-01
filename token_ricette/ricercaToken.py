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

def login_gmail():
    try:
        email_address = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        sender_email = 'noreply@apss.tn.it'

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, password)
        mail.select("inbox")
        status, messages = mail.search(None, f'(FROM "{sender_email}")')
        if status != "OK":
            raise Exception("Failed to search emails.")
        message_ids = messages[0].split()
        return mail, message_ids
    except Exception as e:
        print(f"Failed to login and search emails: {e}")
        return None, []

def parse_email_date(date_str):
    return parser.parse(date_str).astimezone(tz.tzlocal())

def is_token_valid(email_date, validity_minutes=60):
    current_time = datetime.now(tz.tzlocal())
    time_difference = (current_time - email_date).total_seconds() / 60
    return 0 <= time_difference <= validity_minutes

def extract_token_from_email(msg, subject_keyword, span_class=None, table_index=None):
    if subject_keyword in msg["Subject"]:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True)
                    if body:
                        soup = BeautifulSoup(body.decode('utf-8', 'ignore'), "html.parser")
                        if span_class:
                            return soup.find("span", class_=span_class).get_text()
                        if table_index is not None:
                            table_data = soup.find("table").find_all("td")
                            if len(table_data) > table_index:
                                return table_data[table_index].get_text()
        else:
            body = msg.get_payload(decode=True)
            if body:
                soup = BeautifulSoup(body.decode('utf-8', 'ignore'), "html.parser")
                if span_class:
                    return soup.find("span", class_=span_class).get_text()
                if table_index is not None:
                    table_data = soup.find("table").find_all("td")
                    if len(table_data) > table_index:
                        return table_data[table_index].get_text()
    return None

def token_emergenze():
    mail, message_ids = login_gmail()
    token = None
    valid = False

    for msg_id in message_ids[::-1][:100]:
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        email_date = parse_email_date(msg["Date"])

        token = extract_token_from_email(msg, "Token per SAR emergenza", span_class="p14LB")
        if token:
            valid = is_token_valid(email_date)
            break

    mail.logout()
    return token, valid

def token_ricetta_bianca_elettronica():
    mail, message_ids = login_gmail()
    token = None
    valid = False

    # Specify the number of emails to read
    num_emails_to_read = 20 # Change this to the desired number

    for msg_id in message_ids[::-1][:num_emails_to_read]:
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        email_date = parse_email_date(msg["Date"])

        token = extract_token_from_email(msg, "A.P.S.S. - Token per Ricetta Bianca Elettronica", table_index=1)
        if token:
            validita_token = extract_token_from_email(msg, "A.P.S.S. - Token per Ricetta Bianca Elettronica", table_index=5)
            if validita_token:
                valid = is_token_valid(parse_email_date(validita_token), validity_minutes=(parse_email_date(validita_token) - datetime.now(tz.tzlocal())).total_seconds() / 60)
                break

    mail.logout()
    return token, valid

def richiesta_token_emergenza():
    with httpx.Client(timeout=None, follow_redirects=True) as client:
        data = {
            'user': os.getenv("USERNAME"),
            'password': os.getenv("PASSWORD"),
            'login': 'login',
        }
        response = client.post("https://servizi.apss.tn.it/farmacie/login.php", data=data)

if __name__ == "__main__":
    logging.info(f"Token emergenze: {token_emergenze()}")
    logging.info(f"Token ricetta bianca elettronica: {token_ricetta_bianca_elettronica()}")
