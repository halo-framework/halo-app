from halo_app.app.uow import AbsUnitOfWork
from halo_app.classes import AbsBaseClass
from halo_app.views.filters import Filter


class AbsViewFetcher(AbsBaseClass):
    sql_query = ''
    dict_params = {}

    def set_sql_query(self):
        return self.sql_query

    def query(self,params:dict,uow:AbsUnitOfWork,filters:[Filter]=None)->[dict]:
        sql_query = self.set_sql_query()
        with uow:
            results = list(uow.session.execute(sql_query,self.dict_params))
        return results

