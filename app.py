from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from database import DATABASE_PATH, db
from models import Driver


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-before-production"


TRANSLATIONS = {
    "ja": {
        "app_name": "道の縁",
        "driver_registration": "ドライバー登録",
        "driver_registration_intro": "旅行者を乗せられる地域の方の情報を登録します。",
        "name": "お名前",
        "name_example": "例: ダリア",
        "car_description": "車の特徴・色",
        "car_example": "例: 白い軽自動車",
        "register": "登録する",
        "required_error": "お名前と車の特徴・色を入力してください。",
        "registered_drivers": "登録済みドライバー",
        "no_drivers": "まだドライバーは登録されていません。",
        "register_driver": "ドライバーを登録する",
        "language": "言語",
    },
    "en": {
        "app_name": "Michi no En",
        "driver_registration": "Driver registration",
        "driver_registration_intro": "Register your information as a local driver who can help travelers.",
        "name": "Your name",
        "name_example": "e.g. Daria",
        "car_description": "Car description / color",
        "car_example": "e.g. White compact car",
        "register": "Register",
        "required_error": "Please enter your name and a description of your car.",
        "registered_drivers": "Registered drivers",
        "no_drivers": "No drivers have registered yet.",
        "register_driver": "Register a driver",
        "language": "Language",
    },
}


@app.context_processor
def inject_language():
    locale = session.get("locale", "ja")
    return {"locale": locale, "t": TRANSLATIONS[locale]}


def initialize_database():
    """SQLiteファイルと必要なテーブルを用意する。"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    db.connect(reuse_if_open=True)
    db.create_tables([Driver])


@app.route("/")
def index():
    return redirect(url_for("new_driver"))


@app.route("/language/<locale>")
def set_language(locale):
    if locale in TRANSLATIONS:
        session["locale"] = locale
    return redirect(request.referrer or url_for("index"))


@app.route("/drivers/new", methods=["GET", "POST"])
def new_driver():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        car_description = request.form.get("car_description", "").strip()

        if not name or not car_description:
            error = TRANSLATIONS[session.get("locale", "ja")]["required_error"]
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
