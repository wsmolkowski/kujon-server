# coding=UTF-8


def dict_value_student_status(student_status):
    if student_status == 0:
        return 'brak'
    elif student_status == 1:
        return 'nieaktywny student'
    elif student_status == 2:
        return 'aktywny student'


def dict_value_is_currently_conducted(is_currently_conducted):
    if is_currently_conducted:
        return 'TAK'
    else:
        return 'NIE'


def dict_value_staff_status(staff_status):
    if staff_status == 1:
        return 'Pracownik'
    if staff_status == 2:
        return 'Nauczyciel akademicki'
    if staff_status == 0:
        return 'Nieaktywny pracownik'
