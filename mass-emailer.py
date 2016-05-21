#!/usr/bin/python
import configparser
import csv
import hashlib
import logging
import os
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    host = config.get("SMTP", "HOST")
    port = config.getint("SMTP", "PORT")
    username = config.get("SMTP", "USERNAME")
    password = config.get("SMTP", "PASSWORD")

    subject = config.get("GENERAL", "EMAIL_SUBJECT")

    limit = config.getint("GENERAL", "LIMIT")
    check_duplicates = config.getboolean("GENERAL", "DETECT_DUPLICATES")

    return host, port, username, password, subject, limit, check_duplicates


def login(host: str, port: int, username: str, password: str):
    try:
        server = smtplib.SMTP(host + port)
        server.starttls()
        server.login(username, password)
        return server
    except smtplib.SMTPAuthenticationError:
        logger.error("Incorrect username or password")
        server.close()
        sys.exit(1)


def save_progress(file_hash: str, row: int, email: str, name: str):
    # Write to the file and create a new one if it doesn't exist
    with open("last_position.dat", "w+") as file:
        lines = list()
        lines.append("HASH=" + file_hash)
        lines.append("ROW=" + row)
        lines.append("EMAIL=" + email)
        lines.append("NAME=" + name)
        file.writelines(lines)


def send_mail(server: smtplib.SMTP, me: str, recipient: str, name: str, subject: str, template: str):
    try:
        text = template.replace("%name%", name).replace("%email%", recipient)

        msg = MIMEMultipart('alternative')
        # TODO: add name tag
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = recipient

        content = MIMEText(text, "html")
        msg.attach(content)
        # TODO: ADD PLAIN MESSAGE
        # msg.attach(MIMEText(plain, "plain"))

        server.send_message(me, recipient, msg.as_string())
        return True
    except smtplib.SMTPRecipientsRefused:
        logger.warn("Recipient refused")
        return False


# Main content

# logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Mass-Emailer")
logger.setLevel(logging.DEBUG)

logger.debug("Started")

# Configuration init
host, port, username, password, subject, limit, check_duplicates = load_config()
template = ""
with open("email-text.html") as templateFile:
    template = templateFile.read()

email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

server = login(host, port, username, password)

# Start sending the messages
recipientsFile = open("recipients.csv")
file_hash = hashlib.md5(open("recipients.csv").read()).hexdigest()

# Makes it possible to read it by the column name
reader = csv.DictReader(recipientsFile)

raw_rows = list(reader)

# Read last location
if os.path.isfile("last_position.dat"):
    logger.debug("LAST_POSITION FILE FOUND")
    with open("last_position.dat") as last_file:
        lines = last_file.readlines()
        # TODO: read last position

recipientsFile.close()

failed_emails = 0
success_emails = 0

# Check for duplicates
rows = set(raw_rows)
# TODO: FIX DUPLICATE CHECK
# if check_duplicates and len(rows) != len(raw_rows):
#     logger.warn("There are duplicates in the recipients list")
#     duplicates = list(raw_rows - rows)
#     for duplicate in enumerate(duplicates):
#         logger.warn("DUPLICATE: " + duplicate)

total_rows = len(rows)
for rowIndex, row in enumerate(rows):
    email = row['email']
    name = row['name']
    if rowIndex % limit == 0:
        logger.info("Limit reached. Waiting now" + time.strftime("%H:%M:%S"))
        # One hour
        time.sleep(60 * 60)

    if not email_regex.match(email):
        logger.error("Email: " + email + " is not valid")
        continue

    logger.info("Progress %d/%d content: %s" % (rowIndex + 1, total_rows, row))
    # TODO: reconnect server
    if send_mail(server, username, email, name, subject, template):
        success_emails += 1
    else:
        failed_emails += 1

    save_progress(file_hash, rowIndex, email, name)

# Close the connect gracefully
server.quit()

logger.info("END")
logger.info("SUCCESSFUL SENT: " + success_emails)
logger.info("FAILED SENT: " + failed_emails)
