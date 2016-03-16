import sys
import traceback


from usosutils.usoscrawler import UsosCrawler


def clean_database():
    uc = UsosCrawler()

    try:
        uc.drop_collections()
        uc.recreate_usos()
        uc.recreate_dictionaries()
    except Exception, ex:
        print "Problem during dtabase cleanup: {0}".format(ex.message)
        traceback.print_exc()
        sys.exit(-1)


def main():
    clean_database()


if __name__ == "__main__":
    main()
