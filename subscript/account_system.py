#Выделенный файл для работы с аккаунтами

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import session
from subscript.filework import does_user_exist

Debug_mode = True #эта переменная при состоянии True вместо отправки кода на почту выводит его в print()
                   #вызвано тем, что слишком много писем с mail.ru почты приводит к блокировке почты из-за спама
                   #(может уже нет, так как я написал в поддержку, но это не факт)

def getlogin(reset_auth = True):
    if session.get('user', '') == '':
        session['user'] = 'placeholder'
    if (reset_auth):
        session['auth'] = False
    if (not does_user_exist(session.get('user', ''))):
        session['user'] = 'placeholder'
    return session['user']

def setlogin(email):
    session['user'] = email

def sendmail(mail, code):
    if (Debug_mode):
        print(f"Ваш код: {code}")
        return
    fromaddr = "school_dining@mail.ru"
    toaddr = mail
    mypass = "2Fbpad1vaFtJbVgl8bs4"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Ваш код авторизации"
    scode = ""
    for i in code:
        scode += str(i)
    body = f"Ваш код: {code}"
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(fromaddr, mypass)
    text = msg.as_string()
    try:
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except:
        server.quit()