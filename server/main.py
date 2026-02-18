import threading
from .server import Server
import json

if __name__ == "__main__":

    with open(r'server\psu_config.json', 'r') as file:
        config_file = json.load(file)

    server = Server(config=config_file)

    # Optionally start server in its own thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()


    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server shutting down...")
