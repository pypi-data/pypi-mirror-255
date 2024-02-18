import os
import requests
import datetime
import inspect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
from datetime import date
from dotenv import load_dotenv

def trial_function():
    print("Hey it's woooorking!")

def rfplogger(log_message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    calling_module = inspect.getframeinfo(inspect.currentframe().f_back).function
    log_entry = f"{timestamp} - {calling_module}: {log_message}\n"
    with open("logfile.txt", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry)

def extract_file_extension(file_url):
    # Parse the URL to handle both formats
    parsed_url = urlparse(file_url)

    # Split the path component to get the filename
    filename = os.path.basename(parsed_url.path)

    # Split the filename to get the file extension
    _, file_extension = os.path.splitext(filename)

    # Clean up any query parameters that might be part of the extension
    file_extension = file_extension.split('?')[0]

    return file_extension

def download_file_local(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

def delete_local_file(file_name):
    try:
        # Check if file exists
        if os.path.exists(file_name):
            # Delete the file
            os.remove(file_name)
            return f"File '{file_name}' has been deleted."
        else:
            return f"File '{file_name}' does not exist."

    except Exception as e:
        return f"An error occurred while deleting the file: {e}"

def download_image(image_url, local_file_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

    return

def send_email(email_type="info", email_message="Message", originator="Rikpy"):
    
    load_dotenv()


    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        email_recipient = os.getenv("ERROR_EMAIL_RECIPIENT")

        # Email content
        message = MIMEMultipart()
        message["From"] = smtp_user
        message["To"] = email_recipient
        if email_type == "error":
            email_subject = f"Error Notification from {originator} {date.today()}"
        else:
            email_subject = f"Info Notification from {originator} {date.today()}"
        message["Subject"] = email_subject
        
        body = f"Message from the application:\n\n{email_message}"
        message.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_pass)
            response=server.sendmail(smtp_user, email_recipient, message.as_string())
            # xlogger(response)
    except Exception as e:
        rfplogger(e)
        print(f"Error sending email: {e}")