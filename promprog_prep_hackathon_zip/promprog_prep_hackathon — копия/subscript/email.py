import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendmail(mail, code):
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
    server.sendmail(fromaddr, toaddr, text)
    server.quit()