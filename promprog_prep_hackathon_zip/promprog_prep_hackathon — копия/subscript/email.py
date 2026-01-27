import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#DOES NOT WORK, WORK IN PROGRESS

SMTP_SERVERS = {
    'gmail': {
        'server': 'smtp.gmail.com',
        'port': 587,  # для STARTTLS
        'port_ssl': 465  # для SSL
    },
    'yandex': {
        'server': 'smtp.yandex.ru',
        'port': 587,
        'port_ssl': 465
    },
    'mailru': {
        'server': 'smtp.mail.ru',
        'port': 587,
        'port_ssl': 465
    },
    'outlook': {
        'server': 'smtp-mail.outlook.com',
        'port': 587
    },
    'yahoo': {
        'server': 'smtp.mail.yahoo.com',
        'port': 587,
        'port_ssl': 465
    }
}

def send_email_with_service(service='yahoo'):
    sender_email = "school_dining@yahoo.com" # Поставь свою почту
    sender_password = "hleb_s_cementom"       # Поставь свой пароль
    
    smtp_info = SMTP_SERVERS[service]
    
    try:
        # Вариант с STARTTLS (рекомендуется)
        with smtplib.SMTP(smtp_info['server'], smtp_info['port']) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Создание и отправка письма
            msg = MIMEText("Текст письма")
            msg['Subject'] = 'Тема'
            msg['From'] = sender_email
            msg['To'] = 'plushasstudio@gmail.com'
            
            server.send_message(msg)
            print(f"Письмо отправлено через {service}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
send_email_with_service()