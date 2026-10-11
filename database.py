from pathlib import Path

from peewee import SqliteDatabase


DATABASE_PATH = Path("instance") / "michinoen.db"
db = SqliteDatabase(DATABASE_PATH)
