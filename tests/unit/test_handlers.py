# pylint: disable=no-self-use
from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Dict, List
import pytest
from halo_app import bootstrap, exceptions
from halo_app.app import command
from halo_app.app.exceptions import CommandNotMappedException
from halo_app.app import handlers, uow as unit_of_work
from halo_app.domain import repository
from halo_app.entrypoints import client_util
from halo_app.infra.sql_uow import SqlAlchemyUnitOfWork
from halo_app.sys_util import SysUtil
from fake import FakeUnitOfWork, FakePublisher

from base import *

bootstrap.COMMAND_HANDLERS["z0"] = A0.run_command_class  # simple handle + fail
bootstrap.COMMAND_HANDLERS["z1"] = A1.run_command_class  # event 1 api
bootstrap.COMMAND_HANDLERS["z1a"] = A1.run_command_class  # event empty api
bootstrap.COMMAND_HANDLERS["z1b"] = A1.run_command_class  # event seq api
bootstrap.COMMAND_HANDLERS["z1c"] = A1.run_command_class  # event saga api
bootstrap.COMMAND_HANDLERS["z2"] = A8.run_command_class
bootstrap.COMMAND_HANDLERS["z8"] = A8.run_command_class
bootstrap.COMMAND_HANDLERS["z3"] = A3.run_command_class
# bootstrap.COMMAND_HANDLERS["z7"] = A7.run_command_class
bootstrap.COMMAND_HANDLERS["z4"] = A2.run_command_class
bootstrap.COMMAND_HANDLERS["z5"] = A2.run_command_class
bootstrap.COMMAND_HANDLERS["z6"] = A2.run_command_class
bootstrap.COMMAND_HANDLERS["z15"] = A15a.run_command_class
bootstrap.COMMAND_HANDLERS["z16"] = A15b.run_command_class
bootstrap.COMMAND_HANDLERS["z17"] = A17.run_command_class
bootstrap.EVENT_HANDLERS[TestHaloEvent] = [A9.run_event_class]
bootstrap.QUERY_HANDLERS["q1"] = A10.run_query_class
bootstrap.QUERY_HANDLERS["q2"] = A11.run_query_class


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        publish=lambda *args: None,
    )



class TestCommand:

    def test_for_new_item(self):
        bus = bootstrap_test_app()
        os.environ['DEBUG_LOG'] = 'true'
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {'id':'1'})
        halo_response = bus.execute(halo_request)
        response = SysUtil.process_response_for_client(halo_response)
        if response.error:
            print(json.dumps(response.error, indent=4, sort_keys=True))
        assert response.success is True
        assert bus.uow.items.get("1") is not None
        assert bus.uow.committed


    def test_for_existing_item(self):
        bus = bootstrap_test_app()
        os.environ['DEBUG_LOG'] = 'true'
        halo_context = client_util.get_halo_context({}, client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {'id': '0'})
        halo_response = bus.execute(halo_request)
        response = SysUtil.process_response_for_client(halo_response)
        if response.error:
            print(json.dumps(response.error, indent=4, sort_keys=True))
        item = bus.uow.items.get("1")
        bs = [item]
        assert '1' in [b.id for b in bs]


    def test_errors_for_invalid_command(self):
        bus = bootstrap_test_app()
        os.environ['DEBUG_LOG'] = 'true'
        halo_context = client_util.get_halo_context({}, client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "zk0", {'id': '0'})
        halo_response = bus.execute(halo_request)
        assert halo_response.error.message == "exception thrown!"
        assert halo_response.error.cause.message == "command method_id zk0"
        #with pytest.raises(CommandNotMappedException, match="Invalid"):
        #    halo_response = bus.execute(halo_request)

    def test_errors_for_invalid_item_id(self):
        bus = bootstrap_test_app()
        os.environ['DEBUG_LOG'] = 'true'
        halo_context = client_util.get_halo_context({}, client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "zk0", {'id': '0'})
        halo_response = bus.execute(halo_request)
        assert halo_response.error.message == "exception thrown!"
        assert halo_response.error.cause.message == "command method_id zk0"
        #with pytest.raises(CommandNotMappedException, match="Invalid"):
        #    halo_response = bus.execute(halo_request)

    def test_commits(self):
        bus = bootstrap_test_app()
        os.environ['DEBUG_LOG'] = 'true'
        halo_context = client_util.get_halo_context({}, client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {'id': '0'})
        halo_response = bus.execute(halo_request)
        halo_request1 = SysUtil.create_command_request(halo_context, "z1", {'id': '1'})
        halo_response1 = bus.execute(halo_request1)
        assert bus.uow.committed


class TestChangeBatchQuantity:

    def test_changes_available_quantity(self):
        boundary = bootstrap_test_app()
        boundary.execute(command.CreateBatch("batch1", "ADORABLE-SETTEE", 100, None))
        [batch] = boundary.uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        boundary.execute(command.ChangeBatchQuantity("batch1", 50))
        assert batch.available_quantity == 50


    def test_reallocates_if_necessary(self):
        boundary = bootstrap_test_app()
        history = [
            command.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
            command.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            command.Allocate("order1", "INDIFFERENT-TABLE", 20),
            command.Allocate("order2", "INDIFFERENT-TABLE", 20),
        ]
        for msg in history:
            boundary.execute(msg)
        [batch1, batch2] = boundary.uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        boundary.execute(command.ChangeBatchQuantity("batch1", 25))

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
