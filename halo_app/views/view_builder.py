from halo_app.app.uow import AbsUnitOfWork
from halo_app.classes import AbsBaseClass
from halo_app.views.query_filters import Filter
from halo_app.views.view_fetcher import AbsViewFetcher


class Dto(AbsBaseClass):
    pass

class AbsViewBuilder(AbsBaseClass):

    def __init__(self,fetcher:AbsViewFetcher):
        super(AbsViewBuilder,self).__init__()
        self.view_fetcher = fetcher

    def process_data(self,data:[dict])->[Dto]:
        return []

    def find(self,params:dict,uow:AbsUnitOfWork,filters:[Filter]=None)->[Dto]:
        data:[dict] = self.view_fetcher.query(params,uow,filters)
        results:[Dto] = self.process_data(data)
        return results
