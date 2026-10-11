from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from database import DATABASE_PATH, db
from models import Driver


app = Flask(__name__)


def initialize_database():
    """SQLiteファイルと必要なテーブルを用意する。"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    db.connect(reuse_if_open=True)
    db.create_tables([Driver])


@app.route("/")
def index():
    return redirect(url_for("new_driver"))


@app.route("/drivers/new", methods=["GET", "POST"])
def new_driver():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        car_description = request.form.get("car_description", "").strip()

        if not name or not car_description:
            error = "お名前と車の特徴・色を入力してください。"
        else:
            Driver.create(name=name, car_description=car_description)
            return redirect(url_for("drivers"))

    return render_template("drivers/new.html", error=error)


@app.route("/drivers")
def drivers():
    return render_template("drivers/index.html", drivers=Driver.select())


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
