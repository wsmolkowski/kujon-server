# coding=utf-8

import json
import logging
import sys
from datetime import datetime

import motor.motor_tornado
from tornado import gen, escape
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define

from commons import utils
from commons.config import Config
from commons.constants import fields, collections
from commons.context import Context

define('environment', default='development')


def buildMessage(error):
    if hasattr(error, 'response') and hasattr(error.response, 'body') and error.response.body:
        return str(error.response.body)
    return str(error)


async def subscribe_user(config, db, user_doc, http_client):
    try:
        logging.info('re subscribe start for user: {0}'.format(user_doc[fields.MONGO_ID]))
        usos_doc = await db[collections.USOSINSTANCES].find_one({fields.USOS_ID: user_doc[fields.USOS_ID]})

        context = Context(config, user_doc=user_doc, usos_doc=usos_doc, io_loop=IOLoop.current(),
                          http_client=http_client)
        context.setUp()

        try:
            current_subscriptions = await context.usosCaller.call(path='services/events/subscriptions')
            if current_subscriptions and isinstance(current_subscriptions, list):
                current_subscriptions = json.dumps(current_subscriptions)
                current_subscriptions = escape.json_decode(current_subscriptions)

            logging.info(
                'current subscriptions user: {0} {1}'.format(user_doc[fields.MONGO_ID], current_subscriptions))
        except Exception as ex:
            logging.exception(ex)
            current_subscriptions = list()

        if current_subscriptions:
            try:
                unsubscribe_doc = await context.usosCaller.call(path='services/events/unsubscribe')
                logging.info(
                    'unsubscribe user: {0} result ok: {1}'.format(user_doc[fields.MONGO_ID], unsubscribe_doc))
            except HTTPError as ex:
                logging.error(
                    'unsubscribe user: {0} result error: {1}'.format(user_doc[fields.MONGO_ID], buildMessage(ex)))
            except Exception as ex:
                logging.exception(ex)
        else:
            logging.warning(
                'skiping unsubscribe user: {0} {1}'.format(user_doc[fields.MONGO_ID], current_subscriptions))

        if fields.USOS_USER_ID not in user_doc:
            logging.error('nieznany {0} dla {1}'.format(fields.USOS_USER_ID, user_doc))
            return

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                callback_url = '{0}/{1}/{2}'.format(config.DEPLOY_EVENT,
                                                    user_doc[fields.USOS_ID],
                                                    user_doc[fields.USOS_USER_ID])

                verify_token = await db[collections.EVENTS_VERIFY_TOKENS].insert({
                    fields.USER_ID: user_doc[fields.MONGO_ID],
                    fields.EVENT_TYPE: event_type,
                    fields.CREATED_TIME: datetime.now()
                })

                subscribe_doc = await context.usosCaller.call(path='services/events/subscribe_event',
                                                              arguments={
                                                                  'event_type': event_type,
                                                                  'callback_url': callback_url,
                                                                  'verify_token': str(verify_token)
                                                              })
                logging.info('subscribe user: {0} result: {1}'.format(user_doc[fields.MONGO_ID], subscribe_doc))

            except HTTPError as ex:
                logging.error('subscribe user: {0} event_type {1} result error: {2}'.format(
                    user_doc[fields.MONGO_ID], event_type, buildMessage(ex)))
            except Exception as ex:
                logging.exception(ex)

            logging.info('re subscribe end for user: {0}'.format(user_doc[fields.MONGO_ID]))
    except Exception as ex:
        logging.exception(ex)


async def main():
    config = Config(sys.argv[1])
    utils.initialize_logging('resubscribe users', log_dir=config.LOG_DIR)
    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]

    http_client = utils.http_client(config.PROXY_HOST, config.PROXY_PORT, io_loop=IOLoop.current())
    logging.info(http_client)

    total = await db[collections.USERS].find({fields.USOS_PAIRED: True}).count()
    processed = 0

    cursor = db[collections.USERS].find({fields.USOS_PAIRED: True})
    user_jobs = list()
    async for user_doc in cursor:
        processed += 1
        logging.info('{0} processing {1} out of {2}'.format('#' * 50, processed, total))

        user_jobs.append(subscribe_user(config, db, user_doc, http_client))
        if len(user_jobs) > 10:
            result = await gen.multi(user_jobs)
            user_jobs = list()

    if len(user_jobs) > 0:
        result = await gen.multi(user_jobs)


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
