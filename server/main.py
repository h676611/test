import threading
from .server import Server

if __name__ == "__main__":
    server = Server()

    # Optionally start server in its own thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()


    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server shutting down...")
