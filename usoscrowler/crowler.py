import time
import pymongo

from tornado import gen, ioloop, queues

MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'usos-test2'

SLEEP = 10

from usosapi.usosupdater import USOSUpdater


@gen.coroutine
def main():
    queue = queues.Queue()
    db = pymongo.Connection(MONGODB_URI)[MONGODB_NAME]

    @gen.coroutine
    def crowl():
        for user in db.users.find():
            usos = db.usosinstances.find_one({'usos_id': user['usos_id']})

            updater = USOSUpdater(usos['url'], usos['consumer_key'], usos['consumer_secret'], user['access_token_key'], user['access_token_secret'])
            print user['mobile_id'], updater.request_user_info()

            time.sleep(SLEEP)

    @gen.coroutine
    def worker():
        while True:
            yield crowl()

    worker()

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)