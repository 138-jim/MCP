from resolve_lib.folder import Folder
from resolve_lib.media_pool_item import MediaPoolItem
from resolve_lib.timeline import Timeline

def test_get_root_folder(media_pool):
    root = media_pool.get_root_folder()
    assert isinstance(root, Folder)
    assert root.get_name() == "Master"

def test_get_current_folder(media_pool):
    folder = media_pool.get_current_folder()
    assert isinstance(folder, Folder)

def test_create_subfolder(media_pool):
    root = media_pool.get_root_folder()
    new = media_pool.add_subfolder("Test Bin", root)
    assert isinstance(new, Folder)

def test_folder_clips(media_pool):
    folder = media_pool.get_current_folder()
    clips = folder.get_clips()
    assert len(clips) == 2
    assert all(isinstance(c, MediaPoolItem) for c in clips)

def test_folder_subfolders(media_pool):
    root = media_pool.get_root_folder()
    subs = root.get_subfolders()
    assert len(subs) == 1
    assert subs[0].get_name() == "B-Roll"

def test_import_media(media_pool):
    items = media_pool.import_media(["/path/to/clip.mov"])
    assert len(items) == 1
    assert isinstance(items[0], MediaPoolItem)

def test_create_empty_timeline(media_pool):
    tl = media_pool.create_empty_timeline("New TL")
    assert isinstance(tl, Timeline)

def test_clip_metadata(media_pool):
    folder = media_pool.get_current_folder()
    clip = folder.get_clips()[0]
    meta = clip.get_metadata()
    assert isinstance(meta, dict)
    assert clip.set_metadata("Description", "test") is True

def test_clip_markers(media_pool):
    folder = media_pool.get_current_folder()
    clip = folder.get_clips()[0]
    assert clip.add_marker(10, "Blue", "Test", "Note", 1) is True
    assert isinstance(clip.get_markers(), dict)

def test_refresh_folders(media_pool):
    assert media_pool.refresh_folders() is True

def test_clip_clear_marks(media_pool):
    folder = media_pool.get_current_folder()
    clip = folder.get_clips()[0]
    assert clip.clear_mark_in() is True
    assert clip.clear_mark_out() is True
