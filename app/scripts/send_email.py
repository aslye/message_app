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
      "https://api.mailgun.net/v3/mg.reticentroot.com/messages",
      auth=("api", "key-6d3072d1fb205c9703f5ff977b3c466b"),
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
