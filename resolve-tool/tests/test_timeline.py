from resolve_lib.timeline import Timeline
from resolve_lib.timeline_item import TimelineItem
from resolve_lib.exceptions import ResolveValidationError
import pytest

def test_timeline_name(timeline):
    assert timeline.get_name() == "Timeline 1"

def test_timeline_frames(timeline):
    assert timeline.get_start_frame() == 0
    assert timeline.get_end_frame() == 1000

def test_timeline_timecode(timeline):
    assert timeline.get_start_timecode() == "01:00:00:00"
    assert timeline.get_current_timecode() == "01:00:05:00"

def test_track_count(timeline):
    count = timeline.get_track_count("video")
    assert count == 2

def test_track_name(timeline):
    name = timeline.get_track_name("video", 1)
    assert isinstance(name, str)

def test_get_items_in_track(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    assert len(items) == 2
    assert all(isinstance(i, TimelineItem) for i in items)

def test_markers(timeline):
    markers = timeline.get_markers()
    assert 100 in markers
    assert timeline.add_marker(200, "Red", "New", "note", 1) is True

def test_export(timeline):
    assert timeline.export("/tmp/out.aaf", "AAF") is True

def test_duplicate(timeline):
    dup = timeline.duplicate_timeline("Copy")
    assert isinstance(dup, Timeline)

def test_generators(timeline):
    gens = timeline.get_available_generators()
    assert len(gens) >= 1

def test_titles(timeline):
    titles = timeline.get_available_titles()
    assert len(titles) >= 1

def test_scene_detect(timeline):
    cuts = timeline.detect_scene_cuts()
    assert len(cuts) == 3

def test_invalid_track_type(timeline):
    with pytest.raises(ResolveValidationError):
        timeline.get_track_count("invalid")

def test_timeline_item_properties(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    assert item.get_name() == "Shot_001"
    assert item.get_duration() == 120
    props = item.get_property()
    assert isinstance(props, dict)

def test_timeline_item_markers(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    assert item.add_marker(5, "Green", "Action") is True

def test_timeline_item_fusion_comps(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    names = item.get_fusion_comp_name_list()
    assert "Composition 1" in names

def test_timeline_item_color_versions(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    versions = item.get_version_name_list("local")
    assert "Version 1" in versions

def test_insert_fusion_generator(timeline):
    item = timeline.insert_fusion_generator_in_timeline("Background")
    assert isinstance(item, TimelineItem)

def test_insert_fusion_title(timeline):
    item = timeline.insert_fusion_title_in_timeline("Text+")
    assert isinstance(item, TimelineItem)

def test_get_current_video_item(timeline):
    item = timeline.get_current_video_item()
    assert isinstance(item, TimelineItem)

def test_convert_timeline_to_stereo(timeline):
    assert timeline.convert_timeline_to_stereo() is True

def test_timeline_item_delete_take(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    assert item.delete_take_by_index(1) is True

def test_timeline_item_rename_version(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    assert item.rename_version_by_name("Version 1", "Version A", "local") is True

def test_timeline_item_get_clip_cache(timeline):
    items = timeline.get_item_list_in_track("video", 1)
    item = items[0]
    assert item.get_clip_cache() is True
