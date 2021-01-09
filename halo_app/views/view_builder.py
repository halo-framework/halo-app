from halo_app.app.context import HaloContext
from halo_app.app.uow import AbsUnitOfWork
from halo_app.classes import AbsBaseClass
from halo_app.views.query_filters import Filter
from halo_app.views.view_fetcher import AbsViewFetcher
from halo_app.views.dto import AbsDto as Dto
from halo_app.views.view_response import HaloViewResponse


class AbsViewBuilder(AbsBaseClass):
    view_fetcher = None

    def __init__(self,fetcher:AbsViewFetcher):
        super(AbsViewBuilder,self).__init__()
        self.view_fetcher = fetcher

    def process_data(self,data:[dict])->[Dto]:
        return []

    def find(self,halo_context:HaloContext,params:dict,uow:AbsUnitOfWork,filters:[Filter]=None)->HaloViewResponse:
        try:
            data:[dict] = self.view_fetcher.query(params,uow,filters)
            results:[Dto] = self.process_data(data)
            return HaloViewResponse(results)
        except Exception as e:
            return HaloViewResponse(None,code=500)
