"""Basic connection example — connect to Resolve and print version info."""

from resolve_lib import connect, Session


def main():
    # Connect to a running DaVinci Resolve instance
    raw_resolve = connect()
    session = Session(raw_resolve)

    print(f"Product: {session.get_product_name()}")
    print(f"Version: {session.get_version()}")
    print(f"Current page: {session.get_current_page()}")

    # Get project info
    pm = session.get_project_manager()
    project = pm.get_current_project()
    print(f"Current project: {project.get_name()}")
    print(f"Timeline count: {project.get_timeline_count()}")


if __name__ == "__main__":
    main()
