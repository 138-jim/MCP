"""Entry point: python -m resolve_mcp"""

from resolve_mcp.server import create_server


def main():
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
