# coding=UTF-8


from commons.constants import collections, fields
from commons.mixins.ApiMixin import ApiMixin

EXCLUDE_FIELDS = {fields.MONGO_ID: False, fields.CREATED_TIME: False, fields.UPDATE_TIME: False,
                  fields.USOS_ID: False, fields.USER_ID: False}


class CrsTestsMixin(ApiMixin):
    async def api_crstests(self):
        pipeline = {fields.USER_ID: self.get_current_user()[fields.MONGO_ID]}
        if self.do_refresh():
            await self.db_remove(collections.CRSTESTS, pipeline)

        crstests_doc = await self.db[collections.CRSTESTS].find_one(pipeline, EXCLUDE_FIELDS)

        if not crstests_doc:
            crstests_doc = await self.usosCall(path='services/crstests/participant')
            crstests_doc[fields.USER_ID] = self.get_current_user()[fields.MONGO_ID]

            crstests_doc.pop('terms')  # no need at this point

            # rewrite response to list of crstests
            crstests = list()
            for term_id in crstests_doc['tests']:
                for crstest in crstests_doc['tests'][term_id]:
                    crstest_doc = crstests_doc['tests'][term_id][crstest]
                    crstest_doc[fields.TERM_ID] = term_id
                    crstests.append(crstest_doc)

            crstests_doc['tests'] = crstests

            await self.db_insert(collections.CRSTESTS, crstests_doc)

            crstests_doc = await self.db[collections.CRSTESTS].find_one(pipeline, EXCLUDE_FIELDS)

        return crstests_doc
