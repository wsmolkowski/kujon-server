from datetime import datetime

from commons import constants


def user_job(user_id, job_type):
    return {
        constants.USER_ID: user_id,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_MESSAGE: None,
        constants.JOB_STATUS: constants.JOB_PENDING,
        constants.JOB_TYPE: job_type
}


def initial_user_job(user_id):
    return user_job(user_id, 'initial_user_crawl')


def update_user_job(user_id):
    return user_job(user_id, 'update_user_crawl')


def remove_user_job(user_id):
    return user_job(user_id, 'remove_user')
