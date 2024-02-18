import csv
import email
import imaplib
import re
from concurrent.futures import ThreadPoolExecutor

import requests

def search_email(mail_server, username, password, subject=None, sender=None, recipient=None):
    with imaplib.IMAP4_SSL(host=mail_server) as imap_server:
        try:
            imap_server.login(username, password)
        except imaplib.IMAP4.error as e:
            print("IMAP login failed:", e)
            return []

        imap_server.select("INBOX")

        search_criteria = []
        if subject:
            search_criteria.append(f'SUBJECT "{subject}"')
        if sender:
            search_criteria.append(f'FROM "{sender}"')
        if recipient:
            search_criteria.append(f'TO "{recipient}"')

        if not search_criteria:
            return []

        search_string = " ".join(search_criteria)
        _, selected_mails = imap_server.search(None, search_string)
        email_list = []

        for num in selected_mails[0].split():
            _, data = imap_server.fetch(num, "(RFC822)")
            _, bytes_data = data[0]
            email_message = email.message_from_bytes(bytes_data)

            email_details = {
                "from": email_message["from"],
                "to": email_message["to"],
                "date": email_message["date"],
                "subject": email_message["subject"],
            }

            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type in ["text/plain", "text/html", "html"]:
                    try:
                        message = part.get_payload(decode=True)
                        email_details["body"] = message.decode()
                    except UnicodeDecodeError as e:
                        print("Failed to decode email body:", e)
                    break

            email_list.append(email_details)

    return email_list


def find_smtreports_zip_from_gmail(emails, report_num):
    url_pattern = re.compile(r"http.*{}.*\.zip".format(report_num))
    urls = [
        url_pattern.findall(item.get("body", ""))
        for item in emails
        if isinstance(item, dict)
    ]

    unique_urls = list(set([url for sublist in urls for url in sublist]))
    print(unique_urls)

    return unique_urls[0] if unique_urls else None

def extract_http_url(emails):
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    for data in emails:
        body = data.get("body", "")
        urls = re.findall(url_pattern, body)
        if urls:
            return urls[0]

    return None

def process_email(subject, sender, recipient):
    email_data = search_email(
        subject=subject, sender=sender, recipient=recipient
    )

    url_to_click = extract_http_url(email_data)

    if url_to_click:
        print("HTTP URL found:", url_to_click)
        try:
            response = requests.get(url_to_click)
            print(f"Clicking URL: {url_to_click} {response}")
        except requests.exceptions.RequestException as e:
            print("Failed to make HTTP request:", e)
    else:
        print("No HTTP URL found.")

def process_emails(subject, sender, recipients, max_workers=None):
    total_recipients = len(recipients)
    processed_count = 0

    def process_email_wrapper(recipient):
        nonlocal processed_count
        process_email(subject, sender, recipient)
        processed_count += 1
        print(f"Processed {processed_count}/{total_recipients} recipients")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_email_wrapper, recipients)




# recipients = ['adam28@qat.co.in']
#process_emails(subject=subject, sender=sender, recipients=recipients)


"""     email_list = ['http://smt.com//414896-cHJhcHA0X2F1dG9tYXRpb24xXzE2Nzg2NDIzNTU=.zip',
                  'http://smt.com//414897-cHJhcHA0X2F1dG9tYXRpb24xXzE2Nzg2NDI1NjU=.zip',
                  'http://smt.com/jobs//414895-cHJhcHA0X2F1dG9tYXRpb24xXzE2Nzg2NDE3MDU=.zip']
    gmail_helper.find_smtreports_zip_from_gmail(email_list, '414897') """
