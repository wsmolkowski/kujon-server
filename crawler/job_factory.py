# coding=utf-8

from datetime import datetime

from commons import constants
from commons.enumerators import JobStatus, JobType


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


def update_user_job(user_id):
    return user_job(user_id, JobType.UPDATE_USER_CRAWL.value)


def subscribe_user_job(user_id):
    return user_job(user_id, JobType.SUBSCRIBE_USOS.value)
