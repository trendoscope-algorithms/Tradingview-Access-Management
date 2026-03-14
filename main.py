from dotenv import load_dotenv
load_dotenv()

import server

if __name__ == '__main__':
    server.start_server()