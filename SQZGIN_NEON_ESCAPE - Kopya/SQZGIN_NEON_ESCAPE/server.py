# server.py
import hmac
import os
import threading
from functools import wraps
from flask import Flask, Response, abort, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("VIEW_SESSION_SECRET", "varsayilan-cok-gizli-oturum-anahtari-123456")
UPLOAD_TOKEN = os.environ.get("PHONE_UPLOAD_TOKEN", "varsayilan-cok-gizli-telefon-token-123456")
VIEW_PASSWORD = os.environ.get("VIEW_PASSWORD", "123456")

condition = threading.Condition()
latest_jpeg = None
frame_version = 0


def viewer_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("viewer_ok"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


@app.get("/")
@viewer_required
def index():
    return """
    <!doctype html>
    <html lang="tr">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Telefon Canlı Yayın</title>
    <style>
      body { background:#10131b; color:#eef2ff; font:16px sans-serif; text-align:center; margin:24px; }
      img { width:100%; max-width:900px; height:auto; background:#05070a; border-radius:12px; border: 2px solid #00f3ff; }
      #status { color: #70f7be; margin-top: 10px; font-family: monospace; }
    </style>
    </head>
    <body>
    <h2>Telefon Canlı Ekran</h2>
    <p id="status">Bağlantı bekleniyor...</p>
    <img id="stream" src="/stream.mjpg" alt="Canlı ekran">
    <script>
      const img = document.getElementById("stream");
      const status = document.getElementById("status");
      img.onload = () => { status.textContent = "Akış aktif ve bağlı!"; };
      img.onerror = () => { status.textContent = "Akış kesildi!"; };
    </script>
    </body>
    </html>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if hmac.compare_digest(supplied, VIEW_PASSWORD):
            session["viewer_ok"] = True
            return redirect(url_for("index"))
        return """<p style="color:red;font-family:sans-serif;text-align:center;margin-top:50px;">Yanlış Parola! <a href="/login">Tekrar Dene</a></p>""", 403
    return """
    <body style="background:#10131b;color:#eef2ff;font-family:sans-serif;text-align:center;margin-top:100px;">
      <h2>İzleme Girişi</h2>
      <form method="post">
        <input type="password" name="password" placeholder="Parola" style="padding:10px;font-size:16px;border-radius:6px;border:none;">
        <button type="submit" style="padding:10px 20px;font-size:16px;background:#00f3ff;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">Giriş</button>
      </form>
    </body>
    """


@app.post("/api/frame")
def upload_frame():
    global latest_jpeg, frame_version
    auth = request.headers.get("Authorization", "")
    expected = f"Bearer {UPLOAD_TOKEN}"
    if not hmac.compare_digest(auth, expected):
        abort(401)

    data = request.data
    if not data:
        abort(400)

    with condition:
        latest_jpeg = data
        frame_version += 1
        condition.notify_all()
    return "OK", 200


@app.get("/stream.mjpg")
@viewer_required
def stream():
    def generate():
        last_v = -1
        while True:
            with condition:
                if frame_version == last_v:
                    condition.wait(timeout=1.0)
                if frame_version == last_v:
                    continue
                last_v = frame_version
                frame = latest_jpeg
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n"
                       b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n" +
                       frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)