from sqlalchemy.schema import MetaData, Table, Column, ForeignKey
from sqlalchemy.types import Integer, String, Boolean, Text, DateTime


meta = MetaData()

Table('device', meta,
    Column('id', String(32), primary_key=True),
    Column('name', String(255)),
    Column('type', String(255)),
    Column('version', String(255)),
    Column('ip', String(255)),
    Column('port', Integer),
    Column('user', String(255)),
    Column('password', String(255)),
    Column('extra', Text()),
)

Table('loadbalancer', meta,
    Column('id', String(32), primary_key=True),
    Column('device_id', String(32), ForeignKey('device.id')),
    Column('name', String(255)),
    Column('algorithm', String(255)),
    Column('protocol', String(255)),
    Column('status', String(255)),
    Column('tenant_id', String(255)),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=False),
    Column('extra', Text()),
)

Table('serverfarm', meta,
    Column('id', String(32), primary_key=True),
    Column('lb_id', String(32), ForeignKey('loadbalancer.id')),
    Column('name', String(255)),
    Column('type', String(255)),
    Column('status', String(255)),
    Column('extra', Text()),
)

Table('virtualserver', meta,
    Column('id', String(32), primary_key=True),
    Column('sf_id', String(32), ForeignKey('serverfarm.id')),
    Column('lb_id', String(32), ForeignKey('loadbalancer.id')),
    Column('name', String(255)),
    Column('address', String(255)),
    Column('mask', String(255)),
    Column('port', String(255)),
    Column('status', String(255)),
    Column('extra', Text()),
)

Table('server', meta,
    Column('id', String(32), primary_key=True),
    Column('sf_id', String(32), ForeignKey('serverfarm.id')),
    Column('name', String(255)),
    Column('type', String(255)),
    Column('address', String(255)),
    Column('port', String(255)),
    Column('weight', Integer),
    Column('status', String(255)),
    Column('parent_id', Integer),
    Column('deployed', Boolean, default=False),
    Column('vm_id', Integer),
    Column('extra', Text()),
)

Table('probe', meta,
    Column('id', String(32), primary_key=True),
    Column('sf_id', String(32), ForeignKey('serverfarm.id')),
    Column('name', String(255)),
    Column('type', String(255)),
    Column('extra', Text()),
)

Table('sticky', meta,
    Column('id', String(32), primary_key=True),
    Column('sf_id', String(32), ForeignKey('serverfarm.id')),
    Column('name', String(255)),
    Column('type', String(255)),
    Column('extra', Text()),
)

Table('predictor', meta,
    Column('id', String(32), primary_key=True),
    Column('sf_id', String(32), ForeignKey('serverfarm.id')),
    Column('type', String(255)),
    Column('extra', Text()),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    meta.create_all()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    meta.drop_all()
