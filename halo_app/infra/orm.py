import logging
from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey,
    event,
)
from sqlalchemy.orm import mapper, relationship, clear_mappers

from halo_app.domain import model

logger = logging.getLogger(__name__)

metadata = MetaData()


items = Table(
    'items', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('data', String(255)),
    Column('item_dtl_id', ForeignKey('item_dtls.id')),
)

item_dtls = Table(
    'item_dtls', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('desc', String(255)),
    Column('qty', Integer, nullable=False),
)


items_view = Table(
    'items_view', metadata,
    Column('item_dtl_id', Integer),
    Column('data', String(255)),
    Column('desc', String(255)),
    Column('qty', Integer, nullable=False),
)


def start_mappers():
    logger.info("Starting mappers")
    item_mapper = mapper(model.Item, items)
    dtls_mapper = mapper(model.Detail, item_dtls, properties={
        '_dtls': relationship(
            item_mapper,
            secondary=items,
            collection_class=set,
        )
    })


@event.listens_for(model.Item, 'load')
def receive_load(item, _):
    item.events = []
