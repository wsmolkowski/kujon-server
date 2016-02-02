import tornado.gen
import tornado.options
from tornado.queues import LifoQueue

from usoscrowler import UsosCrowler


class UsosQueue():
    crower = UsosCrowler()
    user_queue = LifoQueue()

    def put_user(self, user_id):
        self.user_queue.put(user_id)

    @tornado.gen.coroutine
    def queue_watcher(self):
        while True:
            users_id = yield self.user_queue.get()
            self.crower.initial_user_crowl(users_id)