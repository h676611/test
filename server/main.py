import pyvisa
import threading
from server import Server
from psu_queue import PSUQueue

if __name__ == "__main__":
    server = Server()

    # Optionally start server in its own thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    print("Server running. Waiting for clients...")

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server shutting down...")
