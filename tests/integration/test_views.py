# pylint: disable=redefined-outer-name
from datetime import date
from sqlalchemy.orm import clear_mappers
from unittest import mock
import pytest
from halo_app import bootstrap, views
from halo_app.domain import command
from halo_app.app import uow as unit_of_work
from halo_app.infra import sql_uow
today = date.today()


@pytest.fixture
def sqlite_boundry(sqlite_session_factory):
    boundry = bootstrap.bootstrap(
        start_orm=True,
        uow=sql_uow.SqlAlchemyUnitOfWork(sqlite_session_factory),
        publish=lambda *args: None,
    )
    yield boundry
    clear_mappers()

def test_allocations_view(sqlite_boundry):
    sqlite_boundry.execute(commands.CreateBatch('sku1batch', 'sku1', 50, None))
    sqlite_boundry.handle(commands.CreateBatch('sku2batch', 'sku2', 50, today))
    sqlite_boundry.handle(commands.Allocate('order1', 'sku1', 20))
    sqlite_boundry.handle(commands.Allocate('order1', 'sku2', 20))
    # add a spurious batch and order to make sure we're getting the right ones
    sqlite_boundry.handle(commands.CreateBatch('sku1batch-later', 'sku1', 50, today))
    sqlite_boundry.handle(commands.Allocate('otherorder', 'sku1', 30))
    sqlite_boundry.handle(commands.Allocate('otherorder', 'sku2', 10))

    assert views.allocations('order1', sqlite_boundry.uow) == [
        {'sku': 'sku1', 'batchref': 'sku1batch'},
        {'sku': 'sku2', 'batchref': 'sku2batch'},
    ]


def test_deallocation(sqlite_boundry):
    sqlite_boundry.handle(commands.CreateBatch('b1', 'sku1', 50, None))
    sqlite_boundry.handle(commands.CreateBatch('b2', 'sku1', 50, today))
    sqlite_boundry.handle(commands.Allocate('o1', 'sku1', 40))
    sqlite_boundry.handle(commands.ChangeBatchQuantity('b1', 10))

    assert views.allocations('o1', sqlite_boundry.uow) == [
        {'sku': 'sku1', 'batchref': 'b2'},
    ]
