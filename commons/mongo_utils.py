from datetime import datetime

import constants


def user_job(user_id):
    return {
        constants.USER_ID: user_id,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_STATUS: constants.JOB_PENDING,
    }


def initial_user_job(user_id):
    job = user_job(user_id)
    job[constants.JOB_TYPE] = 'initial_user_crawl'
    return job


def update_user_job(user_id):
    job = user_job(user_id)
    job[constants.JOB_TYPE] = 'update_user_crawl'
    return job
