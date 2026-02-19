"""Example: create a project, set settings, and add a timeline."""

from resolve_lib import connect, Session


def main():
    raw_resolve = connect()
    session = Session(raw_resolve)
    pm = session.get_project_manager()

    # Create a new project
    project = pm.create_project("My New Project")
    print(f"Created project: {project.get_name()}")

    # Set some project settings
    project.set_setting("timelineResolutionWidth", "1920")
    project.set_setting("timelineResolutionHeight", "1080")
    project.set_setting("timelineFrameRate", "24")
    print("Set to 1920x1080 @ 24fps")

    # Create an empty timeline
    pool = project.get_media_pool()
    timeline = pool.create_empty_timeline("Main Edit")
    print(f"Created timeline: {timeline.get_name()}")

    # Save
    pm.save_project()
    print("Project saved")


if __name__ == "__main__":
    main()
