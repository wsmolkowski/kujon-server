# coding=utf-8

from datetime import datetime

from commons.constants import fields
from commons.enumerators import JobStatus, JobType


def user_job(user_id, job_type):
    return {
        fields.USER_ID: user_id,
        fields.CREATED_TIME: datetime.now(),
        fields.UPDATE_TIME: None,
        fields.JOB_MESSAGE: None,
        fields.JOB_STATUS: JobStatus.PENDING.value,
        fields.JOB_TYPE: job_type
    }


def initial_user_job(user_id):
    return user_job(user_id, JobType.INITIAL_USER_CRAWL.value)


def refresh_user_job(user_id):
    return user_job(user_id, JobType.REFRESH_USER_CRAWL.value)


def subscribe_user_job(user_id):
    return user_job(user_id, JobType.SUBSCRIBE_USOS.value)

