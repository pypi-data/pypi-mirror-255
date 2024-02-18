def main():
    import argparse

    parser = argparse.ArgumentParser(prog="redlite", description="CLI ops for redlite")
    subparsers = parser.add_subparsers(required=True, dest="cmd")

    parser_server = subparsers.add_parser("server", help="starts UI server")
    parser_server.add_argument("--port", "-p", type=int, default=8000, help="Server port")

    parser_server = subparsers.add_parser("upload", help="Uploads all tasks to ZenoML (for review and analysis)")
    parser_server.add_argument("--api-key", "-k", help="Zeno API key (if not set, must be in ZENO_API_KEY env)")

    args = parser.parse_args()
    if args.cmd == "server":
        from .server._app import main as server_main

        print("*** HTTP UI server")
        server_main(args.port)

    elif args.cmd == "upload":
        from .zeno.upload import upload

        upload(api_key=args.api_key)


if __name__ == "__main__":
    main()
