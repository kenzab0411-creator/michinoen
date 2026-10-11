from peewee import CharField, Model

from database import db


class BaseModel(Model):
    class Meta:
        database = db


class Driver(BaseModel):
    name = CharField(max_length=50)
    car_description = CharField(max_length=100)
