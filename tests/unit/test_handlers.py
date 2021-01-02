# pylint: disable=no-self-use
from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Dict, List
import pytest
from halo_app import bootstrap
from halo_app.domain import command
from halo_app.app import handler, uow as unit_of_work
from halo_app.domain import repository


class FakeRepository(repository.AbsRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


class FakeUnitOfWork(unit_of_work.AbsUnitOfWork):

    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        publish=lambda *args: None,
    )


class TestAddBatch:

    def test_for_new_product(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None))
        assert boundry.uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert boundry.uow.committed


    def test_for_existing_product(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("b1", "GARISH-RUG", 100, None))
        boundry.execute(command.CreateBatch("b2", "GARISH-RUG", 99, None))
        assert "b2" in [b.reference for b in boundry.uow.products.get("GARISH-RUG").batches]



class TestAllocate:

    def test_allocates(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None))
        boundry.execute(command.Allocate("o1", "COMPLICATED-LAMP", 10))
        [batch] = boundry.uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_quantity == 90


    def test_errors_for_invalid_sku(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("b1", "AREALSKU", 100, None))

        with pytest.raises(handler.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
            boundry.execute(command.Allocate("o1", "NONEXISTENTSKU", 10))

    def test_commits(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("b1", "OMINOUS-MIRROR", 100, None))
        boundry.execute(command.Allocate("o1", "OMINOUS-MIRROR", 10))
        assert boundry.uow.committed


class TestChangeBatchQuantity:

    def test_changes_available_quantity(self):
        boundry = bootstrap_test_app()
        boundry.execute(command.CreateBatch("batch1", "ADORABLE-SETTEE", 100, None))
        [batch] = boundry.uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        boundry.execute(command.ChangeBatchQuantity("batch1", 50))
        assert batch.available_quantity == 50


    def test_reallocates_if_necessary(self):
        boundry = bootstrap_test_app()
        history = [
            command.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
            command.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            command.Allocate("order1", "INDIFFERENT-TABLE", 20),
            command.Allocate("order2", "INDIFFERENT-TABLE", 20),
        ]
        for msg in history:
            boundry.execute(msg)
        [batch1, batch2] = boundry.uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        boundry.execute(command.ChangeBatchQuantity("batch1", 25))

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
