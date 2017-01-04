# coding=UTF-8

from commons.usoshelper import dict_value_student_status, dict_value_staff_status

NUMBER_SEARCH_RESULTS = 20  # USOS api max


class ApiMixinSearch(object):
    async def api_search_users(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/users/search2',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[user[id|student_status|staff_status|employment_positions|titles]|match]|next_page',
                                         })

        if 'items' in search_doc:
            for elem in search_doc['items']:
                user = elem['user']

                # change student status to name
                if 'student_status' in user:
                    user['student_status'] = dict_value_student_status(user['student_status'])

                # change staff_status to dictionary
                user['staff_status'] = dict_value_staff_status(user['staff_status'])

        return search_doc

    async def api_search_courses(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/courses/search',
                                         arguments={
                                             'name': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[course_id|match]|next_page',
                                         })

        return search_doc

    async def api_search_faculties(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/fac/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'id|match|postal_address',
                                             'visibility': 'all'
                                         })

        return search_doc

    async def api_search_programmes(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/progs/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[match|programme[id|name|mode_of_studies|level_of_studies|duration|faculty[id]]]|next_page',
                                         })

        return search_doc

    async def api_search_theses(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/theses/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[match|thesis[type|id|title|authors|supervisors|faculty[id|name]]]|next_page',
                                         })

        return search_doc
