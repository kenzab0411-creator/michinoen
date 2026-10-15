from peewee import CharField, Model

from database import db


class BaseModel(Model):
    class Meta:
        database = db


class Driver(BaseModel):
    name = CharField(max_length=50)
    car_description = CharField(max_length=100)


class RideRequest(BaseModel):
    people_count = CharField(max_length=10)
    gender = CharField(max_length=10)
    age_group = CharField(max_length=10)
    pickup_location = CharField(max_length=50)
    pickup_map_url = CharField(max_length=500, null=True)
    destination = CharField(max_length=100)
    destination_map_url = CharField(max_length=500, null=True)
    # 既存SQLiteとの互換性のために残す。新規リクエストでは使用しない。
    requested_time = CharField(max_length=20, default="")
    status = CharField(default="pending")
