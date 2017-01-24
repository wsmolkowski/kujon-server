# coding=utf-8

import json
import logging
import sys
from datetime import datetime, timedelta

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

USOS_SUBSCRIBE_TIMEOUT = 60


def buildMessage(error):
    if hasattr(error, 'response') and hasattr(error.response, 'body') and error.response.body:
        return str(error.response.body)
    return str(error)


async def subscribe_usos(config, db, usos_doc, http_client):
    async def callUnitilSuccess(context, event_type, callback_url, verify_token):

        try_until = datetime.now() + timedelta(seconds=USOS_SUBSCRIBE_TIMEOUT + 2)

        while True:
            try:
                subscribe_doc = await context.usosCaller.call(
                    path='services/events/subscribe_event',
                    arguments={
                        'event_type': event_type,
                        'callback_url': callback_url,
                        'verify_token': str(verify_token)
                    })

                return subscribe_doc

            except Exception as ex:
                if datetime.now() < try_until:
                    logging.warning('waiting for executing: {0} {1} {2}'.format(event_type, callback_url, verify_token))
                    await gen.sleep(USOS_SUBSCRIBE_TIMEOUT)
                    continue
                raise ex

    try:
        logging.info('re subscribe start for usos: {0}'.format(usos_doc))

        context = Context(config, usos_doc=usos_doc, io_loop=IOLoop.current(),
                          http_client=http_client)
        context.setUp()

        try:
            current_subscriptions = await context.usosCaller.call(path='services/events/subscriptions')
            if current_subscriptions and isinstance(current_subscriptions, list):
                current_subscriptions = json.dumps(current_subscriptions)
                current_subscriptions = escape.json_decode(current_subscriptions)

            logging.info(
                'current subscriptions usos: {0} {1}'.format(usos_doc[fields.USOS_ID], current_subscriptions))
        except Exception as ex:
            logging.exception(ex)
            current_subscriptions = list()

        if current_subscriptions:
            try:
                unsubscribe_doc = await context.usosCaller.call(path='services/events/unsubscribe')
                logging.info(
                    'unsubscribe usos: {0} result ok: {1}'.format(usos_doc[fields.USOS_ID], unsubscribe_doc))
            except HTTPError as ex:
                logging.error(
                    'unsubscribe usos: {0} result error: {1}'.format(usos_doc[fields.USOS_ID], buildMessage(ex)))
            except Exception as ex:
                logging.exception(ex)
        else:
            logging.warning(
                'skiping unsubscribe usos: {0} {1}'.format(usos_doc[fields.USOS_ID], current_subscriptions))

        await db[collections.SUBSCRIPTIONS].remove({fields.USOS_ID: usos_doc[fields.MONGO_ID]})

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                callback_url = '{0}/{1}/{2}'.format(config.DEPLOY_EVENT,
                                                    usos_doc[fields.USOS_ID],
                                                    event_type.split('/')[-1])

                verify_token = await db[collections.EVENTS_VERIFY_TOKENS].insert({
                    fields.USOS_ID: usos_doc[fields.USOS_ID],
                    fields.EVENT_TYPE: event_type,
                    fields.CREATED_TIME: datetime.now()
                })

                subscribe_doc = await callUnitilSuccess(context, event_type, callback_url, verify_token)
                subscribe_doc[fields.USOS_ID] = usos_doc[fields.MONGO_ID]
                subscribe_doc[fields.CREATED_TIME] = datetime.now()
                await db[collections.SUBSCRIPTIONS].insert(subscribe_doc)

                logging.info('subscribe usos: {0} result: {1}'.format(usos_doc[fields.USOS_ID], subscribe_doc))

            except HTTPError as ex:
                logging.error('subscribe usos: {0} event_type {1} result error: {2}'.format(
                    usos_doc[fields.USOS_ID], event_type, buildMessage(ex)))
            except Exception as ex:
                logging.exception(ex)

            logging.info('re subscribe end for usos: {0}'.format(usos_doc[fields.USOS_ID]))

    except Exception as ex:
        logging.exception(ex)


async def main():
    config = Config(sys.argv[1])
    utils.initialize_logging('resubscribe_usoses', log_dir=config.LOG_DIR)
    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]

    http_client = utils.http_client(config.PROXY_HOST, config.PROXY_PORT, io_loop=IOLoop.current())
    logging.info(http_client)

    cursor = db[collections.USOSINSTANCES].find({'enabled': True})
    usoses_docs = await cursor.to_list(None)
    total = len(usoses_docs)
    processed = 0

    for usos_doc in usoses_docs:
        processed += 1
        logging.info('{0} processing {1} out of {2}'.format('#' * 50, processed, total))
        await subscribe_usos(config, db, usos_doc, http_client)


if __name__ == '__main__':
    '''
        usage:
            python3 resubscribe_usoses.py demo
    '''

    if len(sys.argv) != 2:
        sys.exc_info('Provide 1 parameters: environment')

    parse_command_line()

    logging.getLogger().setLevel(logging.INFO)

    IOLoop.current().run_sync(main)
