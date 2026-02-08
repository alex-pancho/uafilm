import threading
import webbrowser
from miniapp.app import app

HOST = "127.0.0.1"
PORT = 5000

def run_flask():
    app.run(port=PORT)

t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

webbrowser.open(f"http://{HOST}:{PORT}")
t.join()