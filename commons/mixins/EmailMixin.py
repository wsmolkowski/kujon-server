# coding=UTF-8

import tornado.gen
from emailqueue.queues import MongoDbEmailQueue

from commons import settings, constants


class EmailMixin(object):
    _email_queue = None

    @property
    def email_queue(self):
        if not self._email_queue:
            self._email_queue = MongoDbEmailQueue(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_password=settings.SMTP_PASSWORD,
                mongodb_uri=settings.MONGODB_URI,
                mongodb_collection=constants.COLLECTION_EMAIL_QUEUE,
                mongodb_database=settings.MONGODB_NAME,
                queue_maxsize=0
            )
        return self._email_queue

    @tornado.gen.coroutine
    def email_registration(self):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]})

        usos_doc = self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])
        recipient = user_doc[constants.USER_EMAIL]

        self.email_queue.sendmail(
            subject='Witamy w serwisie {0}.'.format(settings.PROJECT_TITLE),
            from_addr=settings.SMTP_USER,
            to_addrs=recipient if type(recipient) is list else [recipient],
            text='\nCześć,'
                 '\nRejestracja w USOS {0} zakończona pomyślnie.'
                 '\nW razie pytań, bądź wątpliwości pozostajemy do Twojej dyspozycji.'
                 '\nNapisz do nas {1}'
                 '\nPozdrawiamy,'
                 '\nZespół {2}\n'.format(usos_doc['name'], settings.SMTP_USER, settings.PROJECT_TITLE),
            mime_type='plain',
            charset='utf-8',
            scheduled_hours_from_now=0
        )
