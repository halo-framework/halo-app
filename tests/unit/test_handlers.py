# pylint: disable=no-self-use
from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Dict, List
import pytest
from halo_app import bootstrap
from halo_app.app import command
from halo_app.app import handler, uow as unit_of_work
from halo_app.domain import repository
from halo_app.entrypoints import client_util
from halo_app.sys_util import SysUtil
from fake import FakeUnitOfWork

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
        boundray = bootstrap_test_app()
        halo_context = client_util.get_halo_context({})
        halo_request = SysUtil.create_command_request(halo_context, "z0", {'id':1})
        ret = boundray.execute(halo_request)
        assert ret.success is True
        #assert boundray.uow.products.get("CRUNCHY-ARMCHAIR") is not None
        #assert boundray.uow.committed

    def test_for_new_product(self):
        boundray = bootstrap_test_app()
        halo_context = client_util.get_halo_context({})
        halo_request = SysUtil.create_command_request(halo_context, "z0", {'id':1})
        boundray.execute(halo_request)
        assert boundray.uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert boundray.uow.committed


    def test_for_existing_product(self):
        boundray = bootstrap_test_app()
        boundray.execute(command.CreateBatch("b1", "GARISH-RUG", 100, None))
        boundray.execute(command.CreateBatch("b2", "GARISH-RUG", 99, None))
        assert "b2" in [b.reference for b in boundray.uow.products.get("GARISH-RUG").batches]



class TestAllocate:

    def test_allocates(self):
        boundray = bootstrap_test_app()
        boundray.execute(command.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None))
        boundray.execute(command.Allocate("o1", "COMPLICATED-LAMP", 10))
        [batch] = boundray.uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_quantity == 90


    def test_errors_for_invalid_sku(self):
        boundray = bootstrap_test_app()
        boundray.execute(command.CreateBatch("b1", "AREALSKU", 100, None))

        with pytest.raises(handler.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            boundray.execute(command.Allocate("o1", "NONEXISTENTSKU", 10))

    def test_commits(self):
        boundary = bootstrap_test_app()
        boundary.execute(command.CreateBatch("b1", "OMINOUS-MIRROR", 100, None))
        boundary.execute(command.Allocate("o1", "OMINOUS-MIRROR", 10))
        assert boundary.uow.committed


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
