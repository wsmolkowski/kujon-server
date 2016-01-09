# services/tt/student?start=2016-01-09&days=1

# services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles

user = {  u'first_name': u'Woj',
          u'last_name': u'Skki',
          u'student_status': 1,
          u'sex': u'M',
          u'titles': {u'after': None, u'before': None},
          u'has_email': True,
          u'student_programmes': [
            {u'id': u'1264',u'programme': {
                                            u'description': {
                                                u'en': u'Vocational Studies in Computer Science',
                                                u'pl': u'Zawodowe Studia Informatyki, niestacjonarne (wieczorowe), pierwszego stopnia'},
                                            u'id': u'WZ-ZSI'}
            },
            {u'id': u'50932',u'programme': {
                                            u'description': {
                                                u'en': u'Computer Science, part-time evening studies, second cycle programme',
                                                u'pl': u'Magisterskie Studia Uzupe\u0142niaj\u0105ce z Informatyki, niestacjonarne (wieczorowe), drugiego stopnia'
                                            },
                                            u'id': u'WU-MSUI'}
             }],
          u'id': u'1613',
          u'student_number': u'2085',
          u'email': u'ws@com.pl'}


# /services/courses/course_edition?course_id=1000-612ARR&fields=course_id|course_name|term_id|grades
grades = {
  "course_id": "1000-612ARR",
  "term_id": "2004/TZ",
  "grades": {
    "course_units_grades": {},
    "course_grades": {
      "1": {
        "value_symbol": "3,5",
        "exam_session_number": 1,
        "exam_id": 19050,
        "value_description": {
          "en": "3,5 - satisfactory",
          "pl": "dostateczny plus"
        }
      }
    }
  },
  "course_name": {
    "en": "Distributed and Parallel Algorithms",
    "pl": "Algorytmy rozproszone i równoległe"
  }
}

# services/courses/user?active_terms_only=false&fields=course_editions

courses = {u'course_editions': {
            u'2004/TZ': [
                {u'course_id': u'1000-612ARR', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Distributed and Parallel Algorithms',u'pl': u'Algorytmy rozproszone i r\xf3wnoleg\u0142e'}},
                {u'course_id': u'1000-612FSP', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Formal Specifications',u'pl': u'Formalne specyfikacje'}},
                {u'course_id': u'1000-612MDB', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Advanced Database Access Methods',u'pl': u'Zaawansowane metody dost\u0119pu do baz danych'}},
                {u'course_id': u'1000-612SIZ', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Enterprise Resource Planning',u'pl': u'Systemy informatyczne zarz\u0105dzania'}},
                {u'course_id': u'1000-612SK2', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Computer Networks II',u'pl': u'Sieci komputerowe II'}},
                {u'course_id': u'1000-621PSC', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Network Programming',u'pl': u'Programowanie sieciowe'}},
                {u'course_id': u'1000-622SK2', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Computer Networks II - laboratory',u'pl': u'Sieci komputerowe II - laboratorium'}},
                {u'course_id': u'1000-6M04NH', u'term_id': u'2004/TZ',
                    u'course_name': {u'en': u'Moderm Heuristic Methods',u'pl': u'Nowoczesne metody heurystyczne'}}],
            u'2003/TJ': [
                {u'course_id': u'1000-611ASK', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Architecture of Modern Computer Systems',u'pl': u'Architektura wsp\xf3\u0142czesnych system\xf3w komputerowych'}},
                {u'course_id': u'1000-611MAD', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Discrete Mathematics', u'pl': u'Matematyka dyskretna'}},
                {u'course_id': u'1000-611PIM', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Imperative Programming', u'pl': u'Programowanie imperatywne'}},
                {u'course_id': u'1000-611TMA', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Set Theory and Algebra', u'pl': u'Teoria mnogo\u015bci i algebra'}},
                {u'course_id': u'1000-611WSO', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Modern Operating Systems', u'pl': u'Wsp\xf3\u0142czesne systemy operacyjne'}},
                {u'course_id': u'1000-621LPC', u'term_id': u'2003/TJ',
                    u'course_name': {u'en': u'Programming Laboratory: C++', u'pl': u'Laboratorium programowania:  C++'}}],
            u'2001/TZ': [
                {u'course_id': u'1000-4M00DM', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Data Mining', u'pl': u'Data mining'}},
                {u'course_id': u'1000-413SRO', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Distributed Systems', u'pl': u'Systemy rozproszone'}},
                {u'course_id': u'1000-4M01AS', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'AS/400 Environment',u'pl': u'\u015arodowisko AS/400'}},
                {u'course_id': u'1000-413WOP', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Software Development',u'pl': u'Wytw\xf3rstwo oprogramowania'}},
                {u'course_id': u'1000-413SIN', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Artificial Intelligence and Expert Systems',u'pl': u'Sztuczna inteligencja i systemy doradcze'}},
                {u'course_id': u'1000-423LSR', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Distributed Systems Laboratory',u'pl': u'Laboratorium system\xf3w rozproszonych'}},
                {u'course_id': u'1000-4M00PF', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Functional Programming',u'pl': u'Programowanie funkcyjne'}},
                {u'course_id': u'1000-412MRJ', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Compiler construction',u'pl': u'Metody realizacji j\u0119zyk\xf3w programowania'}},
                {u'course_id': u'1000-412POB', u'term_id': u'2001/TZ',
                    u'course_name': {u'en': u'Object-Oriented Programming',u'pl': u'Programowanie obiektowe'}}],
            u'2000/TZ': [
                {u'course_id': u'1000-412BAZ', u'term_id': u'2000/TZ',
                    u'course_name': {u'en': u'Databases', u'pl': u'Bazy danych'}},
                {u'course_id': u'1000-412MOP', u'term_id': u'2000/TZ',
                    u'course_name': {u'en': u'Optimization Methods', u'pl': u'Metody optymalizacji'}},
                {u'course_id': u'1000-422CPP', u'term_id': u'2000/TZ',
                    u'course_name': {u'en': u'Object-Oriented Programming Laboratory',u'pl': u'Laboratorium programowania obiektowego'}},
                {u'course_id': u'1000-411WDL', u'term_id': u'2000/TZ',
                    u'course_name': {u'en': u'Introduction to Logic', u'pl': u'Wst\u0119p do logiki'}}],
            u'2004/TL': [
                {u'course_id': u'1000-612BDB', u'term_id': u'2004/TL',
                    u'course_name': {u'en': u'Databases in Banking and Management',u'pl': u'Bazy danych w bankowo\u015bci i zarz\u0105dzaniu'}},
                {u'course_id': u'1000-612BSK', u'term_id': u'2004/TL',
                    u'course_name': {u'en': u'Security of Computer Networks', u'pl': u'Bezpiecze\u0144stwo sieci komputerowych'}},
                {u'course_id': u'1000-612RSO', u'term_id': u'2004/TL',
                    u'course_name': {u'en': u'Distributed Operating Systems', u'pl': u'Rozproszone systemy operacyjne'}},
                {u'course_id': u'1000-621LPW', u'term_id': u'2004/TL',
                    u'course_name': {u'en': u'Programming Laboratory: Visual Programming',u'pl': u'Laboratorium programowania: programowanie wizualne'}}],
            u'2003/TL': [
                {u'course_id': u'1000-611AS1', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Sequential Algorithms I', u'pl': u'Algorytmy sekwencyjne I'}},
                {u'course_id': u'1000-611BAD', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Databases', u'pl': u'Bazy danych'}},
                {u'course_id': u'1000-611LOG', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Logic', u'pl': u'Logika'}},
                {u'course_id': u'1000-611PFL', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Declarative Programming: Functional and in Logic',u'pl': u'Programowanie deklaratywne: funkcyjne i w logice'}},
                {u'course_id': u'1000-621MRB', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Database Development Methods', u'pl': u'Metody realizacji baz danych'}},
                {u'course_id': u'1000-621LPW', u'term_id': u'2003/TL',
                    u'course_name': {u'en': u'Programming Laboratory: Visual Programming',u'pl': u'Laboratorium programowania: programowanie wizualne'}}],
            u'2002/TJ': [
                {u'course_id': u'1000-423SKO', u'term_id': u'2002/TJ',
                    u'course_name': {u'en': u'Computer Networks Laboratory', u'pl': u'Laboratorium sieci komputerowych'}}
                ],
            u'2004/TJ': [
                {u'course_id': u'1000-612AS2', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Sequential Algorithms II',u'pl': u'Algorytmy sekwencyjne II'}},
                {u'course_id': u'1000-612OPO', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Software Development - Organization and Management',u'pl': u'Organizacja i zarz\u0105dzanie produkcj\u0105 oprogramowania'}},
                {u'course_id': u'1000-612PSI', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Information Systems Design',u'pl': u'Projektowanie system\xf3w informacyjnych'}},
                {u'course_id': u'1000-612SJP', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Semantics of Programming Languages',u'pl': u'Semantyka j\u0119zyk\xf3w programowania'}},
                {u'course_id': u'1000-612SK1', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Computer Networks I',u'pl': u'Sieci komputerowe I'}},
                {u'course_id': u'1000-622SK1', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Computer Networks I - laboratory',u'pl': u'Sieci komputerowe I - laboratorium'}},
                {u'course_id': u'1000-6M04PM', u'term_id': u'2004/TJ', u'course_name': {
                    u'en': u'Mass Storage Devices - Networking, Backup and Management',u'pl': u'Pami\u0119ci masowe - urz\u0105dzenia, sieci, archiwizacja i zarz\u0105dzanie'}},
                {u'course_id': u'1000-611TEO', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Theory of Computation',u'pl': u'Teoria oblicze\u0144'}},
                {u'course_id': u'1000-612WOP', u'term_id': u'2004/TJ',
                    u'course_name': {u'en': u'Software Development',u'pl': u'Wytw\xf3rstwo oprogramowania'}}],
            u'2003/TZ': [
                {u'course_id': u'1000-621LPH', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Programming Laboratory: HTML and Java',u'pl': u'Laboratorium programowania:  HTML i Java'}},
                {u'course_id': u'1000-621PSC', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Network Programming', u'pl': u'Programowanie sieciowe'}},
                {u'course_id': u'1000-611WSK', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Introduction to Computer Networks', u'pl': u'Wst\u0119p do sieci komputerowych'}},
                {u'course_id': u'1000-611STD', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Data structures', u'pl': u'Struktury danych'}},
                {u'course_id': u'1000-611TEO', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Theory of Computation', u'pl': u'Teoria oblicze\u0144'}},
                {u'course_id': u'1000-611POW', u'term_id': u'2003/TZ',
                    u'course_name': {u'en': u'Object-Oriented and Concurrent Programming',u'pl': u'Programowanie obiektowe i wsp\xf3\u0142bie\u017cne'}}],
            u'2000/TL': [
                {u'course_id': u'1000-411ASD', u'term_id': u'2000/TL',
                    u'course_name': {u'en': u'Algorithms and Data Structures', u'pl': u'Algorytmy i struktury danych'}},
                {u'course_id': u'1000-412AAL', u'term_id': u'2000/TL',
                    u'course_name': {u'en': u'Algorithm Analysis', u'pl': u'Analiza algorytm\xf3w'}},
                {u'course_id': u'1000-412PWS', u'term_id': u'2000/TL',
                    u'course_name': {u'en': u'Concurrent Programming', u'pl': u'Programowanie wsp\xf3\u0142bie\u017cne'}},
                {u'course_id': u'1000-422BAZ', u'term_id': u'2000/TL',
                    u'course_name': {u'en': u'Database Laboratory', u'pl': u'Laboratorium baz danych'}}],
            u'2001/TJ': [
                {u'course_id': u'1000-423SKO', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'Computer Networks Laboratory', u'pl': u'Laboratorium sieci komputerowych'}},
                {u'course_id': u'1000-413TPR', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'Information System Development Methods',u'pl': u'Technologia produkcji system\xf3w informatycznych'}},
                {u'course_id': u'1000-4M00PL', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'Programming in Logics', u'pl': u'Programowanie w logice'}},
                {u'course_id': u'1000-423CAS', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'CASE Laboratory', u'pl': u'Laboratorium CASE'}},
                {u'course_id': u'1000-413MSP', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'Program Specification Methods', u'pl': u'Metody specyfikacji program\xf3w'}},
                {u'course_id': u'1000-413SKO', u'term_id': u'2001/TJ',
                    u'course_name': {u'en': u'Computer Networks', u'pl': u'Sieci komputerowe'}}],
            u'2000/TJ': [
                {u'course_id': u'1000-412AKO', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Computer Architecture', u'pl': u'Architektura komputer\xf3w'}},
                {u'course_id': u'1000-412SOP', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Operating Systems', u'pl': u'Systemy operacyjne'}},
                {u'course_id': u'1000-422UNI', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Unix Laboratory', u'pl': u'Laboratorium systemu Unix'}},
                {u'course_id': u'1000-412RPR', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Probability Calculus and Statistics',u'pl': u'Rachunek prawdopodobie\u0144stwa i statystyka'}},
                {u'course_id': u'1000-412PNI', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Low-level Programming', u'pl': u'Programowanie niskopoziomowe'}},
                {u'course_id': u'1000-412JAO', u'term_id': u'2000/TJ',
                    u'course_name': {u'en': u'Languages and Automata', u'pl': u'J\u0119zyki i automaty'}}],
            u'2001/TL': [
                {u'course_id': u'1000-413OIZ', u'term_id': u'2001/TL',
                    u'course_name': {u'en': u'Organization and Management', u'pl': u'Organizacja i zarz\u0105dzanie'}},
                {u'course_id': u'1000-413RFI', u'term_id': u'2001/TL',
                    u'course_name': {u'en': u'Finance', u'pl': u'Rachunkowo\u015b\u0107 i finanse'}},
                {u'course_id': u'1000-413PIS', u'term_id': u'2001/TL',
                    u'course_name': {u'en': u'Legal and Social Issues in Information Technology',u'pl': u'Prawne i spo\u0142eczne aspekty informatyki'}}],
            u'2004': [
                {u'course_id': u'1000-622PBD', u'term_id': u'2004',
                    u'course_name': {u'en': u'Designing large databases', u'pl': u'Projekt du\u017cej bazy danych'}},
                {u'course_id': u'1000-6D0001', u'term_id': u'2004',
                    u'course_name': {u'en': u'Master Seminar', u'pl': u'Seminarium magisterskie'}}],
            u'2001': [
                {u'course_id': u'1000-4S00IO', u'term_id': u'2001',
                 u'course_name': {u'en': u'Software Engineering - seminar',u'pl': u'In\u017cynieria oprogramowania - seminarium'}}]
            }
}