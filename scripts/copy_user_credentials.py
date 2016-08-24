# coding=UTF-8

import sys

from scripts.dbutils import DbUtils


def main(arguments):
    email_from = arguments[0]
    email_to = arguments[1]
    environment_from = arguments[2]
    environment_to = arguments[3]

    print('copying from email: {0} (environment: {0}) to email: {0} (ennvironment {0})'.format(
        email_from, environment_from, email_to, environment_to
    ))

    dbu = DbUtils(environment_to)
    dbu.copy_user_credentials(email_from=email_from, email_to=email_to, environment_to=environment_to,
                              environment_from=environment_from)

    print('copying ok')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exc_info('Provide 4 parameters: email_from email_to environment_from environment_to')

    main(sys.argv[1:])
