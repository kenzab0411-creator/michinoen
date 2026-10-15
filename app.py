import secrets
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, session, url_for

from database import DATABASE_PATH, db
from models import Driver, RideRequest


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-before-production"


TRANSLATIONS = {
    "ja": {
        "app_name": "道の縁",
        "tagline": "旅人と地域の善意をつなぐ、平泉のヒッチハイク掲示板",
        "home_intro": "移動に困っている旅行者と、手助けできる地域のドライバーをつなぎます。",
        "traveler_button": "ヒッチハイクをお願いする",
        "driver_button": "施し主（ドライバー）として参加する",
        "how_to_use": "使い方",
        "how_to_use_text": "旅行者は希望を送信し、ドライバーは届いたリクエストから返答します。",
        "safety_notes": "利用時の注意",
        "safety_note_1": "乗車・送迎は、双方が内容を確認し、納得した場合だけ行ってください。",
        "safety_note_2": "待ち合わせは人目のある安全な場所を選びましょう。",
        "safety_note_3": "緊急時はこのアプリを使わず、警察・救急などへ連絡してください。",
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
        "drivers": "ドライバー一覧",
        "driver_requests": "届いたリクエスト",
        "new_requests_banner": "新しい対応待ちリクエストが {count} 件あります。",
        "no_pending_requests": "現在、対応待ちのリクエストはありません。",
        "no_requests": "まだリクエストは届いていません。",
        "request_from": "リクエスト",
        "respond_to_request": "リクエストに返答する",
        "pickup_time": "迎えに行ける時間",
        "in_15_minutes": "15分後",
        "in_30_minutes": "30分後",
        "in_60_minutes": "60分後",
        "accept_request": "乗せる",
        "decline_request": "今回は見送る",
        "response_error": "承諾する場合は迎えの時間を選んでください。",
        "response_saved": "返答を登録しました。",
        "status_pending": "対応待ち",
        "status_accepted": "承諾済み",
        "status_declined": "見送り",
        "accepted_by": "{driver_name}さんが承諾しました",
        "declined_by": "{driver_name}さんが見送りました",
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
        "pickup_location_example": "例: 平泉駅、または自由に入力",
        "pickup_map_url": "出発地のGoogle Mapsリンク（任意）",
        "hiraizumi_station": "平泉駅",
        "chusonji": "中尊寺",
        "motsuji": "毛越寺",
        "destination": "行き先",
        "destination_example": "例: 中尊寺、または自由に入力",
        "destination_map_url": "行き先のGoogle Mapsリンク（任意）",
        "open_map": "地図を開く",
        "find_driver": "乗せてくれる人を探す",
        "request_sent": "リクエストを送信しました",
        "request_sent_intro": "ドライバーからの返事をお待ちください。",
        "request_details": "リクエスト内容",
        "request_error": "すべての項目を入力・選択してください。",
        "map_url_error": "地図リンクには http:// または https:// から始まるURLを入力してください。",
        "make_another_request": "別のリクエストを送る",
        "driver_response": "ドライバーからの返事",
        "waiting_for_response": "ドライバーからの返事を待っています。",
        "refresh": "画面を更新する",
        "accepted_response": "{driver_name}さんが {minutes}分後 に迎えに行きます！",
        "declined_response": "今回は乗せられるドライバーが見つかりませんでした。",
        "car_description": "車の特徴",
        "meeting_code": "合言葉",
        "save_result_url": "結果確認用URL",
        "save_result_url_intro": "このURLを保存すると、後でドライバーからの返事を確認できます。",
    },
    "en": {
        "app_name": "Michi no En",
        "tagline": "A Hiraizumi ride board connecting travelers and local goodwill",
        "home_intro": "We connect travelers who need a ride with local drivers who can help.",
        "traveler_button": "Request a hitchhike",
        "driver_button": "Join as a driver",
        "how_to_use": "How it works",
        "how_to_use_text": "Travelers send a request. Drivers reply from their incoming requests.",
        "safety_notes": "Safety notes",
        "safety_note_1": "Only travel together after both people have checked the details and agreed.",
        "safety_note_2": "Choose a public, safe place to meet.",
        "safety_note_3": "For emergencies, contact the police or emergency services instead of using this app.",
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
        "drivers": "Drivers",
        "driver_requests": "Incoming requests",
        "new_requests_banner": "You have {count} new pending ride request(s).",
        "no_pending_requests": "There are no pending requests right now.",
        "no_requests": "No ride requests have arrived yet.",
        "request_from": "Ride request",
        "respond_to_request": "Respond to request",
        "pickup_time": "Pickup time",
        "in_15_minutes": "In 15 minutes",
        "in_30_minutes": "In 30 minutes",
        "in_60_minutes": "In 60 minutes",
        "accept_request": "Accept",
        "decline_request": "Decline",
        "response_error": "When accepting, select a pickup time.",
        "response_saved": "Your response has been saved.",
        "status_pending": "Pending",
        "status_accepted": "Accepted",
        "status_declined": "Declined",
        "accepted_by": "Accepted by {driver_name}",
        "declined_by": "Declined by {driver_name}",
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
        "pickup_location_example": "e.g. Hiraizumi Station, or enter your own pickup location",
        "pickup_map_url": "Google Maps link for pickup (optional)",
        "hiraizumi_station": "Hiraizumi Station",
        "chusonji": "Chuson-ji Temple",
        "motsuji": "Motsu-ji Temple",
        "destination": "Destination",
        "destination_example": "e.g. Chuson-ji Temple, or enter your own destination",
        "destination_map_url": "Google Maps link for destination (optional)",
        "open_map": "Open map",
        "find_driver": "Find a driver",
        "request_sent": "Your request has been sent",
        "request_sent_intro": "Please wait for a driver's reply.",
        "request_details": "Request details",
        "request_error": "Please complete all fields.",
        "map_url_error": "Map links must start with http:// or https://.",
        "make_another_request": "Send another request",
        "driver_response": "Driver response",
        "waiting_for_response": "Waiting for a driver's response.",
        "refresh": "Refresh",
        "accepted_response": "{driver_name} will pick you up in {minutes} minutes!",
        "declined_response": "No driver is available for this ride right now.",
        "car_description": "Car description",
        "meeting_code": "Meeting code",
        "save_result_url": "Result link",
        "save_result_url_intro": "Save this link to check the driver's response later.",
    },
}


@app.context_processor
def inject_language():
    locale = session.get("locale", "ja")
    pending_request_count = RideRequest.select().where(RideRequest.status == "pending").count()
    return {
        "locale": locale,
        "t": TRANSLATIONS[locale],
        "pending_request_count": pending_request_count,
    }


def initialize_database():
    """SQLiteファイルと必要なテーブルを用意する。"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    db.connect(reuse_if_open=True)
    db.create_tables([Driver, RideRequest])
    add_ride_request_columns()


def add_ride_request_columns():
    """古いSQLiteデータベースにも地図リンク用の列を追加する。"""
    columns = {column.name for column in db.get_columns("riderequest")}
    new_columns = {
        "pickup_map_url": "VARCHAR(500)",
        "destination_map_url": "VARCHAR(500)",
        "driver_id": "INTEGER",
        "pickup_minutes": "VARCHAR(10)",
        "meeting_code": "VARCHAR(2)",
        "access_token": "VARCHAR(64)",
    }
    for name, definition in new_columns.items():
        if name not in columns:
            db.execute_sql(f"ALTER TABLE riderequest ADD COLUMN {name} {definition}")
    db.execute_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS riderequest_access_token "
        "ON riderequest (access_token) WHERE access_token IS NOT NULL"
    )


def is_valid_map_url(value):
    if not value:
        return True
    return urlparse(value).scheme in {"http", "https"}


def create_access_token():
    """旅行者だけが結果を確認するための推測されにくいURL用トークン。"""
    return secrets.token_urlsafe(24)


def localized_request_values(ride_request, text):
    """DBの内部値を、現在選ばれている言語の表示用テキストに変換する。"""
    people_count_keys = {"1": "one_person", "2": "two_people", "3+": "three_or_more"}
    legacy_pickup_keys = {
        "hiraizumi_station": "hiraizumi_station",
        "chusonji": "chusonji",
        "motsuji": "motsuji",
    }
    return {
        "people_count": text[people_count_keys[ride_request.people_count]],
        "gender": text[ride_request.gender],
        "age_group": text[ride_request.age_group],
        "pickup_location": text.get(
            legacy_pickup_keys.get(ride_request.pickup_location, ""),
            ride_request.pickup_location,
        ),
        "destination": ride_request.destination,
    }


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/driver")
def driver_portal():
    if Driver.select().exists():
        return redirect(url_for("driver_requests"))
    return redirect(url_for("new_driver"))


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
            "pickup_map_url": request.form.get("pickup_map_url", "").strip() or None,
            "destination": request.form.get("destination", "").strip(),
            "destination_map_url": request.form.get("destination_map_url", "").strip()
            or None,
        }

        required_fields = (
            "people_count",
            "gender",
            "age_group",
            "pickup_location",
            "destination",
        )
        text = TRANSLATIONS[session.get("locale", "ja")]
        if not all(fields[name] for name in required_fields):
            error = text["request_error"]
        elif not all(
            is_valid_map_url(fields[name])
            for name in ("pickup_map_url", "destination_map_url")
        ):
            error = text["map_url_error"]
        else:
            ride_request = RideRequest.create(**fields, access_token=create_access_token())
            return redirect(url_for("request_result", request_id=ride_request.id))

    return render_template("requests/new.html", error=error)


@app.route("/requests/<int:request_id>/sent")
def request_sent(request_id):
    ride_request = RideRequest.get_or_none(RideRequest.id == request_id)
    if ride_request is None:
        return redirect(url_for("new_request"))

    text = TRANSLATIONS[session.get("locale", "ja")]
    request_values = localized_request_values(ride_request, text)
    return render_template(
        "requests/sent.html", ride_request=ride_request, request_values=request_values
    )


@app.route("/requests/<int:request_id>/result")
def request_result(request_id):
    ride_request = RideRequest.get_or_none(RideRequest.id == request_id)
    if ride_request is None:
        return redirect(url_for("new_request"))
    return render_result_page(ride_request)


@app.route("/requests/check/<access_token>")
def check_request_result(access_token):
    ride_request = RideRequest.get_or_none(RideRequest.access_token == access_token)
    if ride_request is None:
        return redirect(url_for("new_request"))
    return render_result_page(ride_request)


def render_result_page(ride_request):
    result_url = None
    if ride_request.access_token:
        result_url = url_for(
            "check_request_result", access_token=ride_request.access_token, _external=True
        )
    return render_template(
        "requests/result.html", ride_request=ride_request, result_url=result_url
    )


@app.route("/driver/requests")
def driver_requests():
    all_requests = RideRequest.select().order_by(RideRequest.id.desc())
    return render_template(
        "driver_requests/index.html",
        ride_requests=all_requests,
        drivers=Driver.select(),
    )


@app.route("/driver/requests/<int:request_id>/respond", methods=["GET", "POST"])
def respond_to_request(request_id):
    ride_request = RideRequest.get_or_none(
        (RideRequest.id == request_id) & (RideRequest.status == "pending")
    )
    if ride_request is None:
        return redirect(url_for("driver_requests"))

    current_driver = Driver.select().order_by(Driver.id.desc()).first()
    if current_driver is None:
        return redirect(url_for("new_driver"))

    error = None
    if request.method == "POST":
        decision = request.form.get("decision")
        pickup_minutes = request.form.get("pickup_minutes")
        valid_pickup_minutes = {"15", "30", "60"}

        if decision not in {"accepted", "declined"}:
            error = TRANSLATIONS[session.get("locale", "ja")]["response_error"]
        elif decision == "accepted" and pickup_minutes not in valid_pickup_minutes:
            error = TRANSLATIONS[session.get("locale", "ja")]["response_error"]
        else:
            ride_request.driver = current_driver
            ride_request.status = decision
            ride_request.pickup_minutes = pickup_minutes if decision == "accepted" else None
            ride_request.meeting_code = (
                f"{secrets.randbelow(100):02d}" if decision == "accepted" else None
            )
            ride_request.save()
            return redirect(url_for("driver_requests", saved="1"))

    text = TRANSLATIONS[session.get("locale", "ja")]
    return render_template(
        "driver_requests/respond.html",
        ride_request=ride_request,
        request_values=localized_request_values(ride_request, text),
        error=error,
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
