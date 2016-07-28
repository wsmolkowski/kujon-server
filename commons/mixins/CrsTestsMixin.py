# coding=UTF-8


from commons import constants
from commons.UsosCaller import UsosCaller
from commons.mixins.DaoMixin import DaoMixin

EXCLUDE_FIELDS = {constants.MONGO_ID: False, constants.CREATED_TIME: False, constants.UPDATE_TIME: False,
                  constants.USOS_ID: False, constants.USER_ID: False}


class CrsTestsMixin(DaoMixin):
    async def api_crstests(self):
        pipeline = {constants.USER_ID: self.get_current_user()[constants.MONGO_ID]}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_CRSTESTS, pipeline)

        crstests_doc = await self.db[constants.COLLECTION_CRSTESTS].find_one(pipeline, EXCLUDE_FIELDS)

        if not crstests_doc:
            crstests_doc = await UsosCaller(self._context).call(path='services/crstests/participant')
            crstests_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            crstests_doc.pop('terms')  # no need at this point

            # rewrite response to list of crstests
            crstests = list()
            for term_id in crstests_doc['tests']:
                for crstest in crstests_doc['tests'][term_id]:
                    crstest_doc = crstests_doc['tests'][term_id][crstest]
                    crstest_doc[constants.TERM_ID] = term_id
                    crstests.append(crstest_doc)

            crstests_doc['tests'] = crstests

            await self.db_insert(constants.COLLECTION_CRSTESTS, crstests_doc)

            crstests_doc = await self.db[constants.COLLECTION_CRSTESTS].find_one(pipeline, EXCLUDE_FIELDS)

        return crstests_doc

    async def api_crstests_grades(self, node_id):
        pipeline = {constants.NODE_ID: node_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_CRSTESTS_GRADES, pipeline)

        crstests_doc = await self.db[constants.COLLECTION_CRSTESTS_GRADES].find_one(pipeline)

        if not crstests_doc:
            try:
                crstests_doc = await UsosCaller(self._context).call(path='services/crstests/user_grade',
                                                                    arguments={'node_id': node_id})
            except Exception as ex:
                await self.exc(ex, finish=False)
                return None

            crstests_doc[constants.NODE_ID] = node_id
            crstests_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            await self.db_insert(constants.COLLECTION_CRSTESTS_GRADES, crstests_doc)

        return crstests_doc

    async def api_crstests_points(self, node_id):
        pipeline = {constants.NODE_ID: node_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_CRSTESTS_POINTS, pipeline)

        crstests_doc = await self.db[constants.COLLECTION_CRSTESTS_POINTS].find_one(pipeline)

        if not crstests_doc:
            crstests_doc = await UsosCaller(self._context).call(path='services/crstests/user_point',
                                                                arguments={'node_id': node_id})
            crstests_doc[constants.NODE_ID] = node_id
            crstests_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            await self.db_insert(constants.COLLECTION_CRSTESTS_POINTS, crstests_doc)

        return crstests_doc
