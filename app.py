from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from database import DATABASE_PATH, db
from models import Driver, RideRequest


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
        "request_ride": "ヒッチハイクをお願いする",
        "request_ride_intro": "移動したい内容を入力すると、地域のドライバーに届きます。",
        "people_count": "人数",
        "one_person": "1人",
        "two_people": "2人",
        "three_or_more": "3人以上",
        "gender": "性別",
        "male": "男性",
        "female": "女性",
        "mixed": "混合",
        "age_group": "年代",
        "teens": "10代",
        "twenties": "20代",
        "thirties_or_more": "30代以上",
        "pickup_location": "出発地",
        "hiraizumi_station": "平泉駅",
        "chusonji": "中尊寺",
        "motsuji": "毛越寺",
        "destination": "行き先",
        "destination_example": "例: 中尊寺、または自由に入力",
        "requested_time": "希望の時間",
        "now": "今すぐ",
        "within_15_minutes": "15分以内",
        "within_30_minutes": "30分以内",
        "find_driver": "乗せてくれる人を探す",
        "request_sent": "リクエストを送信しました",
        "request_sent_intro": "ドライバーからの返事をお待ちください。",
        "request_details": "リクエスト内容",
        "request_error": "すべての項目を入力・選択してください。",
        "make_another_request": "別のリクエストを送る",
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
        "request_ride": "Request a ride",
        "request_ride_intro": "Enter your travel details to send a request to local drivers.",
        "people_count": "Number of people",
        "one_person": "1 person",
        "two_people": "2 people",
        "three_or_more": "3 or more people",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "mixed": "Mixed group",
        "age_group": "Age group",
        "teens": "Teens",
        "twenties": "20s",
        "thirties_or_more": "30 or older",
        "pickup_location": "Pickup location",
        "hiraizumi_station": "Hiraizumi Station",
        "chusonji": "Chuson-ji Temple",
        "motsuji": "Motsu-ji Temple",
        "destination": "Destination",
        "destination_example": "e.g. Chuson-ji Temple, or enter your own destination",
        "requested_time": "Preferred time",
        "now": "Right now",
        "within_15_minutes": "Within 15 minutes",
        "within_30_minutes": "Within 30 minutes",
        "find_driver": "Find a driver",
        "request_sent": "Your request has been sent",
        "request_sent_intro": "Please wait for a driver's reply.",
        "request_details": "Request details",
        "request_error": "Please complete all fields.",
        "make_another_request": "Send another request",
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
    db.create_tables([Driver, RideRequest])


@app.route("/")
def index():
    return redirect(url_for("new_request"))


@app.route("/language/<locale>")
def set_language(locale):
    if locale in TRANSLATIONS:
        session["locale"] = locale
    return redirect(request.referrer or url_for("index"))


@app.route("/requests/new", methods=["GET", "POST"])
def new_request():
    error = None

    if request.method == "POST":
        fields = {
            "people_count": request.form.get("people_count", ""),
            "gender": request.form.get("gender", ""),
            "age_group": request.form.get("age_group", ""),
            "pickup_location": request.form.get("pickup_location", ""),
            "destination": request.form.get("destination", "").strip(),
            "requested_time": request.form.get("requested_time", ""),
        }

        if not all(fields.values()):
            error = TRANSLATIONS[session.get("locale", "ja")]["request_error"]
        else:
            ride_request = RideRequest.create(**fields)
            return redirect(url_for("request_sent", request_id=ride_request.id))

    return render_template("requests/new.html", error=error)


@app.route("/requests/<int:request_id>/sent")
def request_sent(request_id):
    ride_request = RideRequest.get_or_none(RideRequest.id == request_id)
    if ride_request is None:
        return redirect(url_for("new_request"))

    text = TRANSLATIONS[session.get("locale", "ja")]
    people_count_keys = {"1": "one_person", "2": "two_people", "3+": "three_or_more"}
    request_values = {
        "people_count": text[people_count_keys[ride_request.people_count]],
        "gender": text[ride_request.gender],
        "age_group": text[ride_request.age_group],
        "pickup_location": text[ride_request.pickup_location],
        "destination": ride_request.destination,
        "requested_time": text[ride_request.requested_time],
    }
    return render_template(
        "requests/sent.html", ride_request=ride_request, request_values=request_values
    )


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
