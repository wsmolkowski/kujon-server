
# return converted
def dict_value_student_status(student_status):
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

def dict_value_is_currently_conducted(is_currently_conducted):
    if is_currently_conducted:
        return 'TAK'
    else:
        return 'NIE'