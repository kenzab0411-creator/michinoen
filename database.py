from pathlib import Path

from peewee import SqliteDatabase


# 実行した場所に関係なく、常にこのアプリのフォルダー内に保存する。
# PythonAnywhere の WSGI から読み込まれた場合も同じ場所を使える。
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "instance" / "michinoen.db"
db = SqliteDatabase(DATABASE_PATH)
