# coding=utf-8

from datetime import datetime

from commons import constants
from commons.enumerators import JobStatus, JobType

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

def user_job(user_id, job_type):
    return {
        constants.USER_ID: user_id,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_MESSAGE: None,
        constants.JOB_STATUS: JobStatus.PENDING.value,
        constants.JOB_TYPE: job_type
    }


def initial_user_job(user_id):
    return user_job(user_id, JobType.INITIAL_USER_CRAWL.value)


def refresh_user_job(user_id):
    return user_job(user_id, JobType.REFRESH_USER_CRAWL.value)


def update_user_job(user_id):
    return user_job(user_id, JobType.UPDATE_USER_CRAWL.value)


def subscribe_user_job(user_id):
    return user_job(user_id, JobType.SUBSCRIBE_USOS.value)
