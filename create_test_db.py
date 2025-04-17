from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, TIMESTAMP, insert
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
# Создание движка для подключения к базе данных
engine = create_engine("postgresql://nastya@localhost:5432/postgres")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS travel_db"))

metadata = MetaData(schema='test')

city = Table('city', metadata,
    Column('city_id', Integer, primary_key=True),
    Column('name', String(100), unique=True, nullable=False),
    schema='test'
)

directory_route = Table('directory_route', metadata,
    Column('id', Integer, primary_key=True),
    Column('type_transport', String(100), nullable=False),
    Column('departure_city', Integer, ForeignKey('test.city.city_id'), nullable=False),
    Column('arrival_city', Integer, ForeignKey('test.city.city_id'), nullable=False),
    Column('distance', Integer, nullable=False),
    Column('price', Integer, nullable=False),
    schema='test'
)

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('full_name', String(255), nullable=False),
    Column('passport', String(20), unique=True, nullable=False),
    Column('phone', String(20), unique=True, nullable=False),
    Column('email', String(100), unique=True, nullable=False),
    Column('username', String(50), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    schema='test'
)

accommodations = Table('entertainment', metadata,
        Column('id', Integer, primary_key=True), 
        Column('duration', String(50), nullable=False),
        Column('address', String(255), nullable=False),
        Column('event_name', String(255), nullable=False),
        Column('event_time', TIMESTAMP, nullable=False),
        schema='test')


entertainment = Table('accommodations', metadata,
        Column('id', Integer, primary_key=True), 
        Column('price', Integer, nullable=False),
        Column('address', String(255), nullable=False),
        Column('name', String(255), nullable=False),
        Column('type', String(50), nullable=False),
        Column('rating', Integer, nullable=False),
        Column('check_in', TIMESTAMP, nullable=False),
        Column('check_out', TIMESTAMP, nullable=False),
        schema='test')

travel = Table('travel', metadata,
    Column('id', Integer, primary_key=True),
    Column('status', String(50), nullable=False),
    Column('user_id', Integer, ForeignKey('test.users.id'), nullable=False),
    schema='test'
)

route = Table('route', metadata,
    Column('id', Integer, primary_key=True),
    Column('d_route_id', Integer, ForeignKey('test.directory_route.id'), nullable=False),
    Column('travel_id', Integer, ForeignKey('test.travel.id'), nullable=False),
    Column('start_time', TIMESTAMP, nullable=False),
    Column('end_time', TIMESTAMP, nullable=False),
    schema='test'
)

travel_entertainment = Table('travel_entertainment', metadata,
    Column('id', Integer, primary_key=True),
    Column('travel_id', Integer, ForeignKey('test.travel.id'), nullable=False),
    Column('entertainment_id', Integer, ForeignKey('test.entertainment.id'), nullable=False),
    schema='test'
)

travel_accommodations = Table('travel_accommodations', metadata,
    Column('id', Integer, primary_key=True),
    Column('travel_id', Integer, ForeignKey('test.travel.id'), nullable=False),
    Column('accommodation_id', Integer, ForeignKey('test.accommodations.id'), nullable=False),
    schema='test'
)
