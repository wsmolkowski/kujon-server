import sys
import traceback
import tornado.gen
import tornado.ioloop
from usosutils.usoscrawler import UsosCrawler


@tornado.gen.coroutine
def clean_database():
    uc = UsosCrawler()

    try:
        uc.drop_collections()
        uc.recreate_usos()
        yield uc.recreate_dictionaries()
    except Exception, ex:
        print "Problem during dtabase cleanup: {0}".format(ex.message)
        traceback.print_exc()
        sys.exit(-1)


def main():
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(clean_database)


if __name__ == "__main__":
    main()
