import logging
from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey,
    event,
)
from sqlalchemy.orm import mapper, relationship

from halo_app.domain import model

logger = logging.getLogger(__name__)

metadata = MetaData()

items = Table(
    'items', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('other', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),
)


items_view = Table(
    'items_view', metadata,
    Column('id', String(255)),
    Column('other', String(255)),
    Column('more', String(255)),
)


def start_mappers():
    logger.info("Starting mappers")
    #item_mapper = mapper(model.Item, items)


@event.listens_for(model.Item, 'load')
def receive_load(item, _):
    item.events = []
