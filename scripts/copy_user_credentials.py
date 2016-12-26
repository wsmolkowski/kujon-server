# coding=UTF-8

import logging
import sys

from scripts.dbutils import DbUtils


def main(arguments):
    email_from = arguments[0]
    email_to = arguments[1]
    environment_from = arguments[2]
    environment_to = arguments[3]

    print('copying from email: {0} (environment: {1}) to email: {2} (environment {3})'.format(
        email_from, environment_from, email_to, environment_to
    ))

    try:
        DbUtils(None).copy_user_credentials(email_from=email_from, email_to=email_to, environment_to=environment_to,
                                            environment_from=environment_from)

        print('copying ok')
    except Exception as ex:
        logging.exception(ex)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exc_info('Provide 4 parameters: email_from email_to environment_from environment_to')

    main(sys.argv[1:])
