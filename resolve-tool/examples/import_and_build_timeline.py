"""Example: import media and build a timeline from clips."""

from resolve_lib import connect, Session


def main():
    raw_resolve = connect()
    session = Session(raw_resolve)
    pm = session.get_project_manager()
    project = pm.get_current_project()
    pool = project.get_media_pool()

    # Import media files
    clips = pool.import_media([
        "/Volumes/Media/Footage/shot_001.mov",
        "/Volumes/Media/Footage/shot_002.mov",
        "/Volumes/Media/Footage/shot_003.mov",
    ])
    print(f"Imported {len(clips)} clips")

    # Create a timeline from the imported clips
    timeline = pool.create_timeline_from_clips("Assembly Edit", clips)
    print(f"Created timeline: {timeline.get_name()}")

    # Check what we built
    video_count = timeline.get_track_count("video")
    audio_count = timeline.get_track_count("audio")
    print(f"Tracks: {video_count} video, {audio_count} audio")

    # List items in video track 1
    items = timeline.get_item_list_in_track("video", 1)
    for item in items:
        print(f"  - {item.get_name()} ({item.get_duration()} frames)")

    # Add a marker
    timeline.add_marker(0, "Blue", "Start", "Beginning of edit")
    print("Added start marker")

    pm.save_project()
    print("Saved")


if __name__ == "__main__":
    main()
