# coding=utf-8

from datetime import datetime

from commons import constants


def email_job(subject, from_addr, to_addrs, text, mime_type='plain', charset='utf-8'):

    return {
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_STATUS: constants.JOB_PENDING,
        constants.SMTP_SUBJECT: subject,
        constants.SMTP_FROM: from_addr,
        constants.SMTP_TO: to_addrs,
        constants.SMTP_TEXT: text,
        constants.SMTP_MIME_TYPE: mime_type,
        constants.SMTP_CHARSET: charset,
    }