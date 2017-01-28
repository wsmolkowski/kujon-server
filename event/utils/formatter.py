# coding=UTF-8

from commons.constants import fields


def format_user_point(user_point, event_operation):
    notification = "[OPERATION] punty: [POINTS] ze sprawdzianu ([COURSE_NAME])"
    message_title = "Powiadomienie - [OPERATION] punkty: [POINTS] ze sprawdzianu ([COURSE_NAME])"
    message_body = 'Kujon przesyła powiadomienie - [OPERATION] punkty ze sprawdzianu:\n' \
                   'Punkty: [POINTS]\n' \
                   'Przedmiot: [COURSE_NAME]\n' \
                   'Komentarz: [PUBLIC_COMMENT]\n' \
                   'Wpisane przez: [LECTURER]\n'

    # check empty values
    if fields.COURSE_NAME not in user_point:
        user_point[fields.COURSE_NAME] = 'brak'
    if 'points' not in user_point:
        user_point['points'] = 'brak'
    if 'grader' not in user_point:
        user_point['grader'] = 'brak'
    if 'comment' not in user_point:
        user_point['comment'] = '-'

    # check operation
    if event_operation == 'create':
        operation = 'Wpisano'
    elif event_operation == 'update':
        operation = 'Zaktualizowano'
    elif event_operation == 'update':
        operation = 'Usunięto'
    else:
        operation = 'brak'

    tags = {'[OPERATION]': operation,
            '[COURSE_NAME]': str(user_point[fields.COURSE_NAME]) if user_point[fields.COURSE_NAME] else 'brak',
            '[POINTS]': str(user_point['points']) if 'points' in user_point else 'brak',
            '[PUBLIC_COMMENT]': str(user_point['comment']) if user_point['comment'] else '-',
            '[LECTURER]': str(user_point['grader']) if user_point['grader'] else '-'
            }
    for key, value in tags.items():
        notification = notification.replace(key, value)
        message_title = message_title.replace(key, value)
        message_body = message_body.replace(key, value)

    return notification, message_title, message_body


def format_user_grade(user_grade, event_operation):
    notification = "[OPERATION] ocenę: [GRADE] ze sprawdzianu ([COURSE_NAME]) - [PASSED]"
    message_title = "Powiadomienie - [OPERATION] ocenę: [GRADE] ze sprawdzianu ([COURSE_NAME]) - [PASSED]"
    message_body = 'Kujon przesyła powiadomienie - [OPERATION] ocenę ze sprawdzianu:\n' \
                   'Ocena: [GRADE]\n' \
                   'Zaliczone: tak\n' \
                   'Przedmiot: [COURSE_NAME]\n' \
                   'Komentarz: [PUBLIC_COMMENT]\n' \
                   'Wpisane przez: [LECTURER]\n'

    # check empty values
    if fields.COURSE_NAME not in user_grade:
        user_grade[fields.COURSE_NAME] = 'brak'
    if 'grade' not in user_grade or 'decimal_value' not in user_grade['grade'] or 'passes' not in user_grade[
        'grade']:
        user_grade['grade'] = dict()
        user_grade['grade']['decimal_value'] = 'brak'
        user_grade['grade']['passes'] = 'brak'
    if 'grader' not in user_grade:
        user_grade['grader'] = 'brak'
    if 'public_comment' not in user_grade:
        user_grade['public_comment'] = '-'

    # check operation
    if event_operation == 'create':
        operation = 'Wpisano'
    elif event_operation == 'update':
        operation = 'Zaktualizowano'
    elif event_operation == 'update':
        operation = 'Usunięto'
    else:
        operation = 'brak'

    tags = {'[OPERATION]': operation,
            '[COURSE_NAME]': str(user_grade[fields.COURSE_NAME]) if user_grade[fields.COURSE_NAME] else 'brak',
            '[GRADE]': str(user_grade['grade']['decimal_value']) if user_grade['grade'][
                'decimal_value'] else 'brak',
            '[PUBLIC_COMMENT]': str(user_grade['public_comment']) if user_grade['public_comment'] else '-',
            '[LECTURER]': str(user_grade['grader']) if user_grade['grader'] else '[brak]',
            '[PASSED]': 'zalicza' if user_grade['grade']['passes'] else 'nie zalicza',
            }
    for key, value in tags.items():
        notification = notification.replace(key, value)
        message_title = message_title.replace(key, value)
        message_body = message_body.replace(key, value)

    return notification, message_title, message_body
