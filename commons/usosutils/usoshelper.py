
# return converted
def convert_student_status_to_name(student_status):
    '''
    function returns converted user_stata
    :param student_status: int
    :return: name of status
    '''
    if student_status == 0:
        return u'brak'
    elif student_status == 1:
        return u'nieaktywny student'
    elif student_status == 2:
        return u'aktywny student'

