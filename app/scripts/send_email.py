import requests

#import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.mime.text import MIMEText

class SendEmail(object):
  def send_raw(self, sender='', recipients='', subject='', html=''):
    return requests.post(
      "",
      auth=("api", ""),
      data={
        "from": sender,
        "to": [recipients],
        "subject": subject,
        "html": html
      },
      verify=False
    )

  def send_attach(self, sender='', recipients='', subject='', html='', filename=''):
    return requests.post(
      "",
      auth=("api", ""),
      files=[("attachment", open(filename))],
      data={
        "from": sender,
        "to": [recipients],
        "subject": subject,
        "html": html
      },
      verify=False
    )

email = SendEmail()
