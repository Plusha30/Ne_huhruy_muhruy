import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
#WIP

fromaddr = "school_dining@mail.ru"
toaddr = "plushasstudio@gmail.com"
mypass = "2Fbpad1vaFtJbVgl8bs4"
 
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Привет от питона"
body = f"Ваш код: {randint(1000, 9999)}"
msg.attach(MIMEText(body, 'plain'))
server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
server.login(fromaddr, mypass)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()