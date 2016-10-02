# coding=utf-8

HEADER = 'Cześć,'
FOOTER = '''
\nW razie pytań lub pomysłów na zmianę - napisz do nas. Dzięki Tobie {0} będzie lepszy.\
\nPozdrawiamy,
\nzespół {1}
\nemail: {2}
\n<img src={2}/static/img/logo-landing.png></img>
'''


def build_email(message, project_title, smtp_email, deploy_web):
    return '{0}\n{1}\n{2}'.format(HEADER, message, FOOTER.format(project_title, project_title, smtp_email, deploy_web))


def email_register(confirmation_url, project_title, smtp_email, deploy_web):
    message = '''\nDziękujemy za utworzenie konta.
        \nAby zakończyć rejestrację kliknij tutaj <a href="{0}">tutaj :)</a>
            '''.format(confirmation_url)

    return build_email(message, project_title, smtp_email, deploy_web)


def email_archive(project_title, smtp_email, deploy_web):
    message = '\nTwoje konto zostało skasowane, zastanów się czy nie wrócić do nas.'
    return build_email(message, project_title, smtp_email, deploy_web)


def email_register(project_title, smtp_email, deploy_web):
    message = '\nRejestracja Twojego konta zakończona pomyślnie.'
    return build_email(message, project_title, smtp_email, deploy_web)
