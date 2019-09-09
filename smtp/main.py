import socket
import json
import getpass
import ssl
from base64 import b64encode
from configparser import ConfigParser

CONFIG_FILENAME = 'config.ini'
MIME_TYPES = {}
BOUNDARY = 'insta --> @bullyfeed; vk --> @romutchio'


def handle_attachments(attachments):
    message_attachments = ''
    files = attachments.split(', ')
    print(files)
    for file in files:
        (_, extension) = file.split('.')
        mime_type = MIME_TYPES[extension]
        with open(file, 'rb') as f:
            file_encoded = b64encode(f.read())
            message_attachments += \
                (f'Content-Disposition: attachment; '
                 f'filename="{file}"\n'
                 f'Content-Transfer-Encoding: base64\n'
                 f'Content-Type: {mime_type}; name="{file}"\n\n') \
                + file_encoded.decode() + \
                f'\n--{BOUNDARY}\n'
    with open('logs.txt', 'w') as f:
        f.write(message_attachments)

    return message_attachments


def create_message(login, recipients, theme, text, attachments):
    return (
        f'From: {login}\n'
        f'To: {recipients}\n'
        f'Subject: {theme}\n'
        'MIME-Version: 1.0\n'
        f'Content-Type: multipart/mixed; boundary="{BOUNDARY}"\n\n'
        f'--{BOUNDARY}\n'
        'Content-Type: text/plain; charset=utf-8\n'
        'Content-Transfer-Encoding: 8bit\n\n'
        f'{text}\n'
        f'--{BOUNDARY}\n'
        f'{attachments}--\n.'
    )


def send_command(sock, command, buffer=1024):
    sock.send(command + b'\n')
    return sock.recv(buffer).decode()


def send_message(address, port, login, password, recipients, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock = ssl.wrap_socket(sock)
        sock.settimeout(1)
        sock.connect((address, port))
        print(send_command(sock, b'EHLO test'))
        print(send_command(sock, b'AUTH LOGIN'))
        print(send_command(sock, b64encode(login.encode())))
        print(send_command(sock, b64encode(password.encode())))
        print(send_command(sock, b'MAIL FROM: ' + 'magaz.asanov@urfu.ru'.encode()))
        for recipient in recipients:
            print(send_command(sock, b'RCPT TO: ' + recipient.encode()))
        print(send_command(sock, b'DATA'))
        print(send_command(sock, message.encode()))
        print('Message sent')


def parse_config(config_parser):
    message = config_parser['Message']

    sender = config_parser['SenderInfo']
    recipients = [','.join(config_parser['RecipientInfo'])]
    login = sender['Login']

    theme = message['Theme']
    text_filename = message['Text']
    attachment_files = message['Attachments']
    return message, sender, recipients, login, theme, text_filename, attachment_files


def prepare_message_content(text_filename, attachment_files):
    with open(text_filename, 'r') as f:
        text = f.read()

    if text[0] == '.':
        text = '.' + text

    text = text.replace('\n.', '\n..')

    attachments = handle_attachments(attachment_files)

    return text, attachments


if __name__ == '__main__':
    password = getpass.getpass('Password:')
    with open('mimetypes.json') as json_file:
        MIME_TYPES = json.load(json_file)

    config_parser = ConfigParser(allow_no_value=True)
    with open(CONFIG_FILENAME, 'r') as f:
        config_parser.read_file(f)
    (message, sender, recipients, login, theme, text_filename, attachment_files) = parse_config(config_parser)
    (text, attachments) = prepare_message_content(text_filename, attachment_files)
    generated_message = create_message(login, recipients, theme, text, attachments)
    server_info = config_parser['Server']
    (address, port) =(server_info['Host']), int(server_info['Port'])
    send_message(address, port, login, password, recipients, generated_message)
