from halo_app.app.uow import AbsUnitOfWork
from halo_app.classes import AbsBaseClass
from halo_app.views.filters import Filter


class AbsViewFetcher(AbsBaseClass):
    sql_query = ''
    dict_params = {}

    def query(self,params:dict,uow:AbsUnitOfWork,filters:[Filter]=None)->[dict]:

        with uow:
            results = list(uow.session.execute(self.sql_query,self.dict_params))
        return results

