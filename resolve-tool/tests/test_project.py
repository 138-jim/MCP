from resolve_lib.graph import Graph


def test_delete_render_preset(project):
    assert project.delete_render_preset("Old Preset") is True
    project._obj.DeleteRenderPreset.assert_called_with("Old Preset")


def test_import_render_preset(project):
    assert project.import_render_preset("/tmp/preset.xml") is True


def test_export_render_preset(project):
    assert project.export_render_preset("YouTube 1080p", "/tmp/yt.xml") is True


def test_set_current_render_format_and_codec(project):
    assert project.set_current_render_format_and_codec("mp4", "H264") is True


def test_import_burn_in_preset(project):
    assert project.import_burn_in_preset("/tmp/burnin.xml") is True


def test_export_burn_in_preset(project):
    assert project.export_burn_in_preset("Default", "/tmp/burnin.xml") is True


def test_graph_refresh_lut_list(timeline):
    graph = timeline.get_node_graph()
    assert isinstance(graph, Graph)
    assert graph.refresh_lut_list() is True
