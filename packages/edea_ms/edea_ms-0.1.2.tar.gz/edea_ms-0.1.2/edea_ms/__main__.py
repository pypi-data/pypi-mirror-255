import argparse

import uvicorn

from .core.auth import single_user
from .main import app

parser = argparse.ArgumentParser(
    prog="edea-ms",
    description="EDeA Measurement Server - Manage and Visualize data for Test and Measurement as Code",
)

parser.add_argument(
    "--local",
    action="store_true",
    help="Run as a single user local instance without authentication",
)
parser.add_argument(
    "-l", "--host", help="Host address to listen on", default="127.0.0.1"
)
parser.add_argument("-p", "--port", help="Host port to listen on", default=8000)


def main() -> None:
    args = parser.parse_args()

    if args.local:
        single_user.enable()
        print(
            "WARN: edea-ms is running as a single user instance without authentication"
        )

    # to play with API run the script and visit http://127.0.0.1:8000/docs
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
