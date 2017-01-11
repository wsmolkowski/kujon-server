# coding=utf-8

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from commons.constants import fields, collections

HEADER = 'Cześć,'
FOOTER = '''
W razie pytań lub pomysłów na zmianę - napisz do nas. Dzięki Tobie {0} będzie lepszy.
\nPozdrawiamy,
\nzespół {1}
\n: {2}
'''

SMTP_SUBJECT = 'subject'
SMTP_FROM = 'from'
SMTP_TO = 'to'
SMTP_TEXT = 'text'
SMTP_HTML = 'html'
SMTP_MIME_TYPE = 'mime_type'
SMTP_CHARSET = 'charset'


class EmailMixin(object):
    def __build_text_email(self, message):
        return '{0}\n{1}\n{2}'.format(HEADER, message,
                                      FOOTER.format(self.config.PROJECT_TITLE, self.config.PROJECT_TITLE,
                                                    self.config.SMTP_EMAIL, self.config.DEPLOY_WEB))

    def __build_html_email(self, message):
        return '''\
        <html>
          <head>
            <meta charset="UTF-8">
            <link href='https://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
            <link href="{0}/static/css/style_email.css" rel="stylesheet">
          </head>
          <body>
            <p>
                <br>
                {1}<br><br>
                {2}<br>
            </p>
            <p>
            W razie pytań lub pomysłów na zmianę - napisz do nas. Dzięki Tobie {3} będzie lepszy.<br><br>
            Pozdrawiamy,<br>
            zespół <a href={4}>{5}</a><br>
            {6}<br>
            </p><br>
            <img src={7}/static/img/logo-landing.png></img>
            <br>
          </body>
        </html>
        '''.format(self.config.DEPLOY_WEB, HEADER, message, self.config.PROJECT_TITLE, self.config.DEPLOY_WEB,
                   self.config.PROJECT_TITLE, self.config.SMTP_EMAIL, self.config.DEPLOY_WEB).strip()

    def __email_register(self, confirmation_url, html=False):
        message = '\nDziękujemy za utworzenie konta.' \
                  '\nAby zakończyć rejestrację kliknij tutaj <a href="{0}">tutaj :)</a>'.format(confirmation_url)
        if html:
            return self.__build_html_email(message)
        return self.__build_text_email(message)

    def __email_archive(self, html=False):
        if html:
            return self.__build_html_email('\nTwoje konto zostało skasowane. Zastanów się czy nie wrócić do nas :-)')
        return self.__build_text_email('\nTwoje konto zostało skasowane, zastanów się czy nie wrócić do nas.')

    def __email_register_info(self, html=False):
        message = '\nRejestracja Twojego konta zakończona pomyślnie.'
        if html:
            return self.__build_html_email(message)
        return self.__build_text_email(message)

    def __email_contact(self, contact_msg, email, user_id, html=False):
        if html:
            return self.__build_html_email(
                '<p>Nowa wiadomość od użytkownik: email: {0}<br>mongo_id: {1}<br>wiadomość:<br>{2}<br></p>'.format(
                    email, user_id, contact_msg))
        return self.__build_text_email(
            'Nowa wiadomość od użytkownik: email: {0} mongo_id: {1} \nwiadomość:\n{2}\n'.format(email, user_id,
                                                                                                contact_msg))

    async def __send_email(self, subject, from_addr, to_addrs, text, html):
        try:
            logging.debug('__send_email from_addr:{0} to_addrs:{1}'.format(from_addr, to_addrs))

            smtp = smtplib.SMTP()
            smtp.connect(self.config.SMTP_HOST, self.config.SMTP_PORT)
            smtp.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)

            msg = MIMEMultipart('alternative')

            msg['Subject'] = '[{0}] {1}'.format(self.config.PROJECT_TITLE, subject)
            msg['From'] = to_addrs
            msg['To'] = ','.join(to_addrs)

            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            if not isinstance(to_addrs, list):
                to_addrs = [to_addrs, ]

            smtp.sendmail(from_addr, to_addrs, msg.as_string())

            msg_doc = await self.db[collections.MESSAGES].insert({
                fields.USER_ID: self.getUserId(return_object_id=True),
                fields.CREATED_TIME: datetime.now(),
                fields.FIELD_MESSAGE_FROM: self.config.PROJECT_TITLE,
                fields.FIELD_MESSAGE_TYPE: 'email',
                fields.JOB_MESSAGE: text
            })

            logging.debug('__send_email from_addr:{0} to_addrs:{1} resulted in: {2}'.format(
                from_addr, to_addrs, msg_doc))

            smtp.quit()

            return msg_doc
        except Exception as ex:
            logging.exception(ex)

    async def email_contact(self, subject, message, email):
        user_id = self.getUserId(return_object_id=True)
        return await self.__send_email(
            subject=subject,
            from_addr=self.config.SMTP_EMAIL,
            to_addrs=self.config.SMTP_EMAIL,
            text=self.__email_contact(message, email, user_id),
            html=self.__email_contact(message, email, user_id, html=True)
        )

    async def email_archive_user(self, recipient):
        return await self.__send_email(
            subject='Usunęliśmy Twoje konto',
            from_addr=self.config.SMTP_EMAIL,
            to_addrs=recipient,
            text=self.__email_archive(),
            html=self.__email_archive(html=True),
        )

    async def email_registration(self, user_doc=None):
        if not user_doc:
            user_doc = self.get_current_user()

        recipient = user_doc[fields.USER_EMAIL]

        return await self.__send_email(
            subject='Rejestracja w Kujon.mobi',
            from_addr=self.config.SMTP_EMAIL,
            to_addrs=recipient,
            text=self.__email_register_info(),
            html=self.__email_register_info(html=True),
        )

    async def email_confirmation(self, email, user_id):
        confirmation_url = '{0}/authentication/email_confim/{1}'.format(self.config.DEPLOY_API,
                                                                        self.aes.encrypt(str(user_id)).decode())
        logging.debug('confirmation_url: {0}'.format(confirmation_url))

        return await self.__send_email(
            subject='Dokończ rejestrację konta',
            from_addr=self.config.SMTP_EMAIL,
            to_addrs=email,
            text=self.__email_register(confirmation_url),
            html=self.__email_register(confirmation_url, html=True),
        )
