# coding=utf-8

from datetime import datetime

from commons import constants
from commons.enumerators import JobStatus

SMTP_SUBJECT = 'subject'
SMTP_FROM = 'from'
SMTP_TO = 'to'
SMTP_TEXT = 'text'
SMTP_MIME_TYPE = 'mime_type'
SMTP_CHARSET = 'charset'


def email_job(subject, from_addr, to_addrs, text, mime_type='plain', charset='utf-8', user_id=None):

    return {
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_STATUS: JobStatus.PENDING.value,
        constants.USER_ID: user_id,
        SMTP_SUBJECT: subject,
        SMTP_FROM: from_addr,
        SMTP_TO: to_addrs,
        SMTP_TEXT: text,
        SMTP_MIME_TYPE: mime_type,
        SMTP_CHARSET: charset,
    }