# coding=UTF-8


from commons.UsosCaller import UsosCaller
from commons.constants import collections, fields
from commons.mixins.DaoMixin import DaoMixin

EXCLUDE_FIELDS = {fields.MONGO_ID: False, fields.CREATED_TIME: False, fields.UPDATE_TIME: False,
                  fields.USOS_ID: False, fields.USER_ID: False}


class CrsTestsMixin(DaoMixin):
    async def api_crstests(self):
        pipeline = {fields.USER_ID: self.get_current_user()[fields.MONGO_ID]}
        if self.do_refresh():
            await self.db_remove(collections.CRSTESTS, pipeline)

        crstests_doc = await self.db[collections.CRSTESTS].find_one(pipeline, EXCLUDE_FIELDS)

        if not crstests_doc:
            crstests_doc = await UsosCaller(self._context).call(path='services/crstests/participant')
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

    async def api_crstests_grades(self, node_id):
        pipeline = {fields.NODE_ID: node_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(collections.CRSTESTS_GRADES, pipeline)

        crstests_doc = await self.db[collections.CRSTESTS_GRADES].find_one(pipeline)

        if not crstests_doc:
            try:
                crstests_doc = await UsosCaller(self._context).call(path='services/crstests/user_grade',
                                                                    arguments={'node_id': node_id})
            except Exception as ex:
                await self.exc(ex, finish=False)
                return

            crstests_doc[fields.NODE_ID] = node_id
            crstests_doc[fields.USER_ID] = self.get_current_user()[fields.MONGO_ID]

            await self.db_insert(collections.CRSTESTS_GRADES, crstests_doc)

        return crstests_doc

    async def api_crstests_points(self, node_id):
        pipeline = {fields.NODE_ID: node_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(collections.CRSTESTS_POINTS, pipeline)

        crstests_doc = await self.db[collections.CRSTESTS_POINTS].find_one(pipeline)

        if not crstests_doc:
            crstests_doc = await UsosCaller(self._context).call(path='services/crstests/user_point',
                                                                arguments={'node_id': node_id})
            crstests_doc[fields.NODE_ID] = node_id
            crstests_doc[fields.USER_ID] = self.get_current_user()[fields.MONGO_ID]

            await self.db_insert(collections.CRSTESTS_POINTS, crstests_doc)

        return crstests_doc
