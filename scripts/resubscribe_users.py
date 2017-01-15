# coding=utf-8

import logging
import sys

import motor.motor_tornado
from tornado import gen
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define

from commons import utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import fields, collections
from commons.context import Context

define('environment', default='development')


async def main():
    config = Config(sys.argv[1])
    utils.initialize_logging('resubscribe users', log_dir=config.LOG_DIR)
    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]

    aes = AESCipher(config.AES_SECRET)
    logging.info(aes)

    cursor = db[collections.USERS].find({fields.USOS_PAIRED: True})
    async for user_doc in cursor:
        try:
            logging.info('re subscribe start for user: {0}'.format(user_doc[fields.MONGO_ID]))
            usos_doc = await db[collections.USOSINSTANCES].find_one({fields.USOS_ID: user_doc[fields.USOS_ID]})

            context = Context(config, user_doc=user_doc, usos_doc=usos_doc, io_loop=IOLoop.current())
            context.setUp()

            encrypted_user_id = aes.encrypt(str(user_doc[fields.MONGO_ID])).decode()

            try:
                unsubscribe_doc = await context.usosCaller.call(path='services/events/unsubscribe')
                logging.info('unsubscribe user: {0} result ok: {1}'.format(user_doc[fields.MONGO_ID], unsubscribe_doc))
            except HTTPError as ex:
                logging.error(
                    'unsubscribe user: {0} result error: {1}'.format(user_doc[fields.MONGO_ID], str(ex.response.body)))
            except Exception as ex:
                logging.exception(ex)

            callback_url = '{0}/{1}/{2}'.format(config.DEPLOY_EVENT, user_doc[fields.USOS_ID],
                                                user_doc[fields.USOS_USER_ID])

            for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
                try:
                    subscribe_doc = await context.usosCaller.call(path='services/events/subscribe_event',
                                                                  arguments={
                                                                      'event_type': event_type,
                                                                      'callback_url': callback_url,
                                                                      'verify_token': encrypted_user_id
                                                                  })
                    logging.info('subscribe user: {0} result: {1}'.format(user_doc[fields.MONGO_ID], subscribe_doc))

                    await gen.sleep(2)

                except HTTPError as ex:
                    logging.error('subscribe user: {0} event_type {1} result error: {2}'.format(
                        user_doc[fields.MONGO_ID], event_type, str(ex.response.body)))
                except Exception as ex:
                    logging.exception(ex)

                logging.info('re subscribe end for user: {0}'.format(user_doc[fields.MONGO_ID]))
        except Exception as ex:
            logging.exception(ex)


if __name__ == '__main__':
    '''
        usage:
            python3 resubscribe_users.py demo
    '''

    if len(sys.argv) != 2:
        sys.exc_info('Provide 1 parameters: environment')

    parse_command_line()

    logging.getLogger().setLevel(logging.INFO)

    IOLoop.current().run_sync(main)
