from datetime import datetime

import constants


def user_job_insert(user_id):
    return {
        constants.USER_ID: user_id,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_STATUS: constants.JOB_START,
    }
