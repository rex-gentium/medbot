from sqlalchemy import Table, Column, BigInteger, String, MetaData, ForeignKey

metadata = MetaData()

users_table = Table('user', metadata,
                    Column('id', BigInteger, primary_key=True),
                    Column('state_id', BigInteger, ForeignKey('state.id')))

states_table = Table('state', metadata,
                     Column('id', BigInteger, primary_key=True),
                     Column('name', String))


