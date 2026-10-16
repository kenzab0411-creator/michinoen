# 道の縁

平泉を訪れる旅行者と地域のドライバーをつなぐ、学習用のヒッチハイク支援アプリです。

## 起動方法

```bash
.venv/bin/python app.py
```

ブラウザで `http://127.0.0.1:5000/` を開きます。

## PythonAnywhere Beginner への公開

このアプリは、PythonAnywhere の WSGI から読み込まれても SQLite を
`instance/michinoen.db` に作成します。SQLite ファイルは Git に含めません。

1. PythonAnywhere で Beginner アカウントを作り、**Consoles > Bash** を開きます。
2. Python のバージョンを確認します。

   ```bash
   ls /usr/bin/python3.*
   ```

3. リポジトリを取得し、仮想環境を作成します。`python3.13` は実際に使える同じ
   バージョンに読み替えてください。

   ```bash
   cd ~
   git clone https://github.com/kenzab0411-creator/michinoen.git camp-app
   cd ~/camp-app
   mkdir -p ~/.virtualenvs
   python3.13 -m venv ~/.virtualenvs/camp-app
   source ~/.virtualenvs/camp-app/bin/activate
   pip install -r requirements.txt
   ```

4. **Web > Add a new web app** で、`Manual configuration` を選びます。手順2と同じ
   Python バージョンを選択し、Virtualenv に次を設定します。

   ```text
   /home/あなたのユーザー名/.virtualenvs/camp-app
   ```

5. WSGI configuration file を開き、中身を次に置き換えます。`あなたのユーザー名`
   は PythonAnywhere のユーザー名に変更し、`十分に長いランダムな文字列` は自分で
   作成した秘密鍵に置き換えてください。

   ```python
   import os
   import sys

   os.environ["SECRET_KEY"] = "十分に長いランダムな文字列"

   path = "/home/あなたのユーザー名/camp-app"
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```

6. **Web > Static files** に次を追加します。

   | URL | Directory |
   | --- | --- |
   | `/static/` | `/home/あなたのユーザー名/camp-app/static` |

7. **Web** タブの **Reload** を押し、`https://あなたのユーザー名.pythonanywhere.com`
   を開きます。

Web アプリの期限や外部通信の制限は、PythonAnywhere Beginner のプラン仕様に従います。

## 現在できること

- 利用時の注意に同意してからアプリを使う
- 日本語と英語を画面上で切り替える
- 旅行者が移動リクエストを送信する
- 出発地・行き先を自由入力し、任意でGoogle Mapsリンクを添付する
- ドライバーが、ニックネームと車の特徴を入力してリクエストを承諾または見送る
- 旅行者がドライバーの返答、車の特徴、迎え時間、合言葉を確認する

## デモの流れ

1. `/` で利用時の注意を確認し、同意します。
2. 旅行者のリクエストを送信します。
3. `/driver/requests` で届いたリクエストを開き、ニックネーム、車の特徴、「乗せる」と迎え時間を登録します。
4. 旅行者の結果画面を更新し、ドライバー情報と合言葉を確認します。

画面上部の `日本語 / English` から表示言語を切り替えられます。

旅行者は、リクエスト送信後に表示される結果確認用URLを保存しておくと、画面を閉じた後も返答状況を確認できます。
