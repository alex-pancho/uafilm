import threading
import os
import signal
import webbrowser
from PIL import Image
import pystray
from pystray import MenuItem as item
from miniapp.app import app

HOST = "127.0.0.1"
PORT = 80

def run_flask():
    app.run(port=PORT, use_reloader=False)


def quit_app(icon, item):
    icon.stop()
    os.kill(os.getpid(), signal.SIGTERM)

def quit_app(icon, item):
    icon.stop()
    os.kill(os.getpid(), signal.SIGTERM)

def create_tray():
    try:
        image = Image.open("icons8-dale-96.ico")
    except:
        image = Image.new("RGB", (64, 64), "black")

    menu = (
        item("Відкрити", lambda icon, item: webbrowser.open(f"http://{HOST}:{PORT}")),
        item("Вийти", quit_app),
    )

    icon = pystray.Icon("UA kino DB rescue", image, "UA kino DB rescue аpp", menu)
    icon.run()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    threading.Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    create_tray()
