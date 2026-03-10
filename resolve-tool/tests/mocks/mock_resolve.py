"""Full mock of the DaVinci Resolve API hierarchy for testing."""

from __future__ import annotations

from unittest.mock import MagicMock


def create_mock_resolve() -> MagicMock:
    """Create a complete mock of the Resolve API object hierarchy.

    Returns a MagicMock configured to simulate:
    Resolve -> ProjectManager -> Project -> MediaPool/Timeline -> etc.
    """
    resolve = MagicMock(name="Resolve")

    # Root Resolve methods
    resolve.GetVersionString.return_value = "19.0.0"
    resolve.GetProductName.return_value = "DaVinci Resolve"
    resolve.GetCurrentPage.return_value = "edit"
    resolve.OpenPage.return_value = True
    resolve.GetKeyframeMode.return_value = 0
    resolve.SetKeyframeMode.return_value = True
    resolve.LoadLayoutPreset.return_value = True
    resolve.UpdateLayoutPreset.return_value = True
    resolve.ExportLayoutPreset.return_value = True
    resolve.DeleteLayoutPreset.return_value = True
    resolve.ImportLayoutPreset.return_value = True

    # Export LUT constants
    resolve.EXPORT_LUT_17PTCUBE = 0
    resolve.EXPORT_LUT_33PTCUBE = 1
    resolve.EXPORT_LUT_65PTCUBE = 2
    resolve.EXPORT_LUT_PANASONICVLUT = 3

    # ProjectManager
    pm = MagicMock(name="ProjectManager")
    resolve.GetProjectManager.return_value = pm

    pm.GetDatabaseList.return_value = [
        {"DbType": "Disk", "DbName": "Local Database"},
    ]
    pm.GetCurrentDatabase.return_value = {"DbType": "Disk", "DbName": "Local Database"}
    pm.SetCurrentDatabase.return_value = True
    pm.OpenFolder.return_value = True
    pm.GetCurrentFolder.return_value = "Root"
    pm.GetFolderListInCurrentFolder.return_value = ["Drama", "Commercial"]
    pm.CreateFolder.return_value = True
    pm.GetProjectListInCurrentFolder.return_value = ["MyProject", "TestProject"]
    pm.SaveProject.return_value = True
    pm.CloseProject.return_value = True
    pm.DeleteProject.return_value = True
    pm.ImportProject.return_value = True
    pm.ExportProject.return_value = True
    pm.RestoreProject.return_value = True
    pm.GotoRootFolder.return_value = True
    pm.GotoParentFolder.return_value = True
    pm.DeleteFolder.return_value = True

    # Project
    project = MagicMock(name="Project")
    pm.CreateProject.return_value = project
    pm.LoadProject.return_value = project
    pm.GetCurrentProject.return_value = project

    project.GetName.return_value = "MyProject"
    project.SetName.return_value = True
    project.GetUniqueId.return_value = "proj-uuid-001"
    _project_settings = {
        "timelineFrameRate": "24",
        "timelineResolutionWidth": "1920",
        "timelineResolutionHeight": "1080",
    }
    project.GetSetting.side_effect = lambda key="": _project_settings.get(key, "") if key else dict(_project_settings)
    project.SetSetting.return_value = True
    project.GetTimelineCount.return_value = 2
    project.GetPresetList.return_value = ["YouTube 1080p", "ProRes Master"]
    project.GetRenderPresetList.return_value = ["YouTube 1080p", "ProRes Master"]
    project.LoadRenderPreset.return_value = True
    project.SaveAsNewRenderPreset.return_value = True
    project.GetCurrentRenderFormatAndCodec.return_value = {"format": "mp4", "codec": "H.264"}
    project.GetRenderFormats.return_value = {"mp4": "MP4", "mov": "QuickTime"}
    project.GetRenderCodecs.return_value = {"H264": "H.264", "H265": "H.265"}
    project.SetRenderSettings.return_value = True
    project.GetRenderJobList.return_value = []
    project.GetRenderJobStatus.return_value = {"JobStatus": "Ready"}
    project.AddRenderJob.return_value = "job-001"
    project.DeleteRenderJob.return_value = True
    project.DeleteAllRenderJobs.return_value = True
    project.StartRendering.return_value = True
    project.IsRenderingInProgress.return_value = False
    cg1 = _make_color_group("Group A")
    project.GetColorGroupsList.return_value = [cg1]
    project.AddColorGroup.return_value = cg1
    project.DeleteColorGroup.return_value = True
    project.RefreshLUTList.return_value = True
    project.InsertAudioToCurrentTrackAtPlayhead.return_value = True
    project.LoadBurnInPreset.return_value = True
    project.ExportCurrentFrameAsStill.return_value = True
    project.SetCurrentRenderFormatAndCodec.return_value = True
    project.DeleteRenderPreset.return_value = True
    project.ImportRenderPreset.return_value = True
    project.ExportRenderPreset.return_value = True
    project.ImportBurnInPreset.return_value = True
    project.ExportBurnInPreset.return_value = True

    # MediaPool
    media_pool = MagicMock(name="MediaPool")
    project.GetMediaPool.return_value = media_pool

    root_folder = _make_folder("Master", clips=["Clip_A.mov", "Clip_B.mp4"])
    sub_folder = _make_folder("B-Roll", clips=["BRoll_01.mov"])
    root_folder.GetSubFolderList.return_value = [sub_folder]

    media_pool.GetRootFolder.return_value = root_folder
    media_pool.GetCurrentFolder.return_value = root_folder
    media_pool.SetCurrentFolder.return_value = True
    media_pool.AddSubFolder.return_value = _make_folder("NewBin")
    media_pool.DeleteFolders.return_value = True
    media_pool.MoveFolders.return_value = True
    media_pool.MoveClips.return_value = True
    media_pool.DeleteClips.return_value = True
    media_pool.RelinkClips.return_value = True
    media_pool.UnlinkClips.return_value = True
    media_pool.GetUniqueId.return_value = "pool-uuid-001"
    media_pool.ExportMetadata.return_value = True

    empty_timeline = _make_timeline("Empty Timeline")
    media_pool.CreateEmptyTimeline.return_value = empty_timeline
    media_pool.ImportTimelineFromFile.return_value = empty_timeline

    imported_clip = _make_media_pool_item("Imported.mov")
    media_pool.ImportMedia.return_value = [imported_clip]
    media_pool.AppendToTimeline.return_value = [imported_clip]
    media_pool.CreateTimelineFromClips.return_value = empty_timeline
    media_pool.AutoSyncAudio.return_value = [imported_clip]
    media_pool.RefreshFolders.return_value = True
    media_pool.CreateStereoClip.return_value = imported_clip

    # MediaStorage
    media_storage = MagicMock(name="MediaStorage")
    resolve.GetMediaStorage.return_value = media_storage
    media_storage.GetMountedVolumeList.return_value = ["/Volumes/Media", "/Volumes/SSD"]
    media_storage.GetSubFolderList.return_value = ["ProjectA", "ProjectB"]
    media_storage.GetFileList.return_value = ["clip001.mov", "clip002.mp4"]
    media_storage.AddItemListToMediaPool.return_value = [imported_clip]
    media_storage.AddClipMattesToMediaPool.return_value = True
    media_storage.AddTimelineMattesToMediaPool.return_value = []
    media_storage.RevealInStorage.return_value = True

    # Gallery
    gallery = MagicMock(name="Gallery")
    project.GetGallery.return_value = gallery
    album = _make_gallery_still_album("Album 1")
    gallery.GetCurrentStillAlbum.return_value = album
    gallery.SetCurrentStillAlbum.return_value = True
    gallery.GetGalleryStillAlbums.return_value = [album]
    gallery.GetAlbumName.return_value = "Album 1"
    gallery.SetAlbumName.return_value = True
    gallery.CreateGalleryStillAlbum.return_value = album
    pg_album = _make_gallery_still_album("PowerGrade 1")
    gallery.GetGalleryPowerGradeAlbums.return_value = [pg_album]
    gallery.CreateGalleryPowerGradeAlbum.return_value = pg_album

    # Timelines
    tl1 = _make_timeline("Timeline 1")
    tl2 = _make_timeline("Timeline 2")

    def get_timeline_by_index(idx):
        return [tl1, tl2][idx - 1] if 1 <= idx <= 2 else None

    project.GetTimelineByIndex.side_effect = get_timeline_by_index
    project.GetCurrentTimeline.return_value = tl1
    project.SetCurrentTimeline.return_value = True

    return resolve


def _make_folder(name: str, clips: list[str] | None = None) -> MagicMock:
    folder = MagicMock(name=f"Folder({name})")
    folder.GetName.return_value = name
    folder.GetUniqueId.return_value = f"folder-{name.lower()}"
    folder.GetSubFolderList.return_value = []
    folder.Export.return_value = True
    folder.TranscribeAudio.return_value = True
    folder.ClearTranscription.return_value = True

    clip_items = [_make_media_pool_item(c) for c in (clips or [])]
    folder.GetClipList.return_value = clip_items
    return folder


def _make_media_pool_item(name: str) -> MagicMock:
    item = MagicMock(name=f"MediaPoolItem({name})")
    item.GetName.return_value = name
    item.GetUniqueId.return_value = f"clip-{name.lower()}"
    item.GetMediaId.return_value = f"media-{name.lower()}"
    item.GetMetadata.return_value = {"Clip Name": name, "Duration": "00:00:10:00"}
    item.SetMetadata.return_value = True
    item.GetThirdPartyMetadata.return_value = {}
    item.SetThirdPartyMetadata.return_value = True
    item.DeleteThirdPartyMetadata.return_value = True
    item.GetMarkers.return_value = {}
    item.AddMarker.return_value = True
    item.DeleteMarkerAtFrame.return_value = True
    item.DeleteMarkerByCustomData.return_value = True
    item.DeleteMarkersByColor.return_value = True
    item.UpdateMarkerCustomData.return_value = True
    item.GetMarkerCustomData.return_value = ""
    _clip_props = {"Format": "mov", "FPS": "24", "Resolution": "1920x1080"}
    item.GetClipProperty.side_effect = lambda key=None: _clip_props.get(key, "") if key else dict(_clip_props)
    item.SetClipProperty.return_value = True
    item.GetClipColor.return_value = ""
    item.SetClipColor.return_value = True
    item.GetFlagList.return_value = []
    item.AddFlag.return_value = True
    item.ClearFlags.return_value = True
    item.ReplaceClip.return_value = True
    item.LinkProxyMedia.return_value = True
    item.UnlinkProxyMedia.return_value = True
    item.TranscribeAudio.return_value = True
    item.ClearTranscription.return_value = True
    item.GetAudioMapping.return_value = None
    item.ClearMarkIn.return_value = True
    item.ClearMarkOut.return_value = True
    item.GetMarkIn.return_value = 0
    item.GetMarkOut.return_value = 100
    return item


def _make_timeline(name: str) -> MagicMock:
    tl = MagicMock(name=f"Timeline({name})")
    tl.GetName.return_value = name
    tl.SetName.return_value = True
    tl.GetUniqueId.return_value = f"tl-{name.lower().replace(' ', '-')}"
    tl.GetStartFrame.return_value = 0
    tl.GetEndFrame.return_value = 1000
    tl.GetStartTimecode.return_value = "01:00:00:00"
    tl.SetStartTimecode.return_value = True
    tl.GetCurrentTimecode.return_value = "01:00:05:00"
    tl.SetCurrentTimecode.return_value = True

    tl.GetTrackCount.return_value = 2
    tl.AddTrack.return_value = True
    tl.DeleteTrack.return_value = True
    tl.GetTrackName.return_value = "Video 1"
    tl.SetTrackName.return_value = True
    tl.SetTrackEnable.return_value = True
    tl.GetIsTrackEnabled.return_value = True
    tl.SetTrackLock.return_value = True
    tl.GetIsTrackLocked.return_value = False

    # Timeline items
    item1 = _make_timeline_item("Shot_001")
    item2 = _make_timeline_item("Shot_002")
    tl.GetItemListInTrack.return_value = [item1, item2]
    tl.DeleteClips.return_value = True
    tl.GrabStill.return_value = MagicMock(name="Still")
    tl.GrabAllStills.return_value = []

    tl.GetMarkers.return_value = {100: {"color": "Blue", "name": "Mark1", "note": "", "duration": 1}}
    tl.AddMarker.return_value = True
    tl.DeleteMarkerAtFrame.return_value = True
    tl.DeleteMarkerByCustomData.return_value = True
    tl.DeleteMarkersByColor.return_value = True
    tl.UpdateMarkerCustomData.return_value = True
    tl.GetMarkerCustomData.return_value = ""

    tl.Export.return_value = True
    tl.ImportIntoTimeline.return_value = True
    tl.DuplicateTimeline.return_value = tl
    tl.CreateCompoundClip.return_value = item1
    tl.CreateFusionClip.return_value = item1

    tl.GetAvailableGenerators.return_value = [{"Name": "Solid Color"}, {"Name": "10 Point Star"}]
    tl.InsertGeneratorIntoTimeline.return_value = item1
    tl.GetAvailableTitles.return_value = [{"Name": "Text+"}, {"Name": "Scroll"}]
    tl.InsertTitleIntoTimeline.return_value = item1
    tl.GetAvailableTransitions.return_value = [{"Name": "Cross Dissolve"}]

    tl.DetectSceneCuts.return_value = [100, 250, 480]
    tl.CreateSubtitlesFromAudio.return_value = True
    tl.ExportSubtitle.return_value = True

    tl.GetMarkIn.return_value = -1
    tl.GetMarkOut.return_value = -1
    tl.SetMarkIn.return_value = True
    tl.SetMarkOut.return_value = True

    tl.GetSetting.return_value = {}
    tl.SetSetting.return_value = True
    tl.GetThumbnail.return_value = {}

    tl.SetVoiceIsolationState.return_value = True
    tl.GetVoiceIsolationState.return_value = True
    tl.GetNodeGraph.return_value = _make_node_graph()

    tl.InsertOFXGeneratorIntoTimeline.return_value = item1
    tl.InsertFusionGeneratorIntoTimeline.return_value = item1
    tl.InsertFusionTitleIntoTimeline.return_value = item1
    tl.GetCurrentVideoItem.return_value = item1
    tl.ConvertTimelineToStereo.return_value = True

    return tl


def _make_timeline_item(name: str) -> MagicMock:
    item = MagicMock(name=f"TimelineItem({name})")
    item.GetName.return_value = name
    item.GetDuration.return_value = 120
    item.GetStart.return_value = 0
    item.GetEnd.return_value = 120
    item.GetLeftOffset.return_value = 0
    item.GetRightOffset.return_value = 0
    item.GetSourceStartFrame.return_value = 0
    item.GetSourceEndFrame.return_value = 120
    item.GetUniqueId.return_value = f"item-{name.lower()}"

    item.GetClipEnabled.return_value = True
    item.SetClipEnabled.return_value = True

    item.GetProperty.return_value = {"Pan": 0.0, "Tilt": 0.0, "ZoomX": 1.0, "ZoomY": 1.0, "Opacity": 100.0}
    item.SetProperty.return_value = True

    item.GetMarkers.return_value = {}
    item.AddMarker.return_value = True
    item.DeleteMarkerAtFrame.return_value = True
    item.DeleteMarkerByCustomData.return_value = True
    item.DeleteMarkersByColor.return_value = True
    item.UpdateMarkerCustomData.return_value = True
    item.GetMarkerCustomData.return_value = ""

    item.GetFlagList.return_value = []
    item.AddFlag.return_value = True
    item.ClearFlags.return_value = True
    item.GetClipColor.return_value = ""
    item.SetClipColor.return_value = True

    item.GetFusionCompCount.return_value = 1
    item.GetFusionCompByIndex.return_value = MagicMock(name="FusionComp")
    item.GetFusionCompNameList.return_value = ["Composition 1"]
    item.AddFusionComp.return_value = MagicMock(name="FusionComp")
    item.ImportFusionComp.return_value = MagicMock(name="FusionComp")
    item.ExportFusionComp.return_value = True
    item.DeleteFusionCompByName.return_value = True
    item.LoadFusionCompByName.return_value = MagicMock(name="FusionComp")
    item.RenameFusionCompByName.return_value = True

    item.GetVersionNameList.return_value = ["Version 1"]
    item.LoadVersionByName.return_value = True
    item.AddVersion.return_value = True
    item.DeleteVersionByName.return_value = True

    item.GetCDL.return_value = {"slope": "1 1 1", "offset": "0 0 0", "power": "1 1 1", "saturation": "1"}
    item.SetCDL.return_value = True
    item.CopyGrades.return_value = True
    item.ExportLUT.return_value = True

    item.GetNodeGraph.return_value = _make_node_graph()
    item.GetColorGroup.return_value = None
    item.AssignToColorGroup.return_value = True
    item.RemoveFromColorGroup.return_value = True

    item.GetCurrentVersion.return_value = {"versionName": "Version 1", "versionType": 0}
    item.ResetAllNodeColors.return_value = True
    item.GetIsColorOutputCacheEnabled.return_value = True
    item.SetColorOutputCache.return_value = True

    item.CreateMagicMask.return_value = True
    item.Stabilize.return_value = True
    item.SmartReframe.return_value = True
    item.SetClipCache.return_value = True
    item.SetVoiceIsolationState.return_value = True
    item.GetVoiceIsolationState.return_value = {"isEnabled": False, "amount": 0}

    mpi = _make_media_pool_item(name)
    item.GetMediaPoolItem.return_value = mpi

    item.DeleteTakeByIndex.return_value = True
    item.RenameVersionByName.return_value = True
    item.GetClipCache.return_value = True
    item.GetTakesCount.return_value = 2
    item.GetSelectedTakeIndex.return_value = 1
    item.SelectTakeByIndex.return_value = True
    item.FinalizeTake.return_value = True
    item.AddTake.return_value = True

    return item


def _make_color_group(name: str) -> MagicMock:
    group = MagicMock(name=f"ColorGroup({name})")
    group.GetName.return_value = name
    group.SetName.return_value = True
    group.GetClipsInTimeline.return_value = []
    group.GetPreClipNodeGraph.return_value = _make_node_graph()
    group.GetPostClipNodeGraph.return_value = _make_node_graph()
    return group


def _make_gallery_still_album(name: str) -> MagicMock:
    album = MagicMock(name=f"GalleryStillAlbum({name})")
    still1 = MagicMock(name="Still1")
    still2 = MagicMock(name="Still2")
    album.GetStills.return_value = [still1, still2]
    album.GetLabel.return_value = "Still Label"
    album.SetLabel.return_value = True
    album.ImportStills.return_value = True
    album.ExportStills.return_value = True
    album.DeleteStills.return_value = True
    return album


def _make_node_graph() -> MagicMock:
    graph = MagicMock(name="NodeGraph")
    graph.GetNumNodes.return_value = 3
    graph.GetLUT.return_value = ""
    graph.SetLUT.return_value = True
    graph.GetNodeCacheMode.return_value = 0
    graph.SetNodeCacheMode.return_value = True
    graph.GetNodeLabel.return_value = "Corrector 1"
    graph.SetNodeLabel.return_value = True
    graph.GetToolsInNode.return_value = ["ColorCorrector"]
    graph.SetNodeEnabled.return_value = True
    graph.GetNodeEnabled.return_value = True
    graph.ApplyGradeFromDRX.return_value = True
    graph.ApplyArriCdlLut.return_value = True
    graph.ResetAllGrades.return_value = True
    graph.RefreshLUTList.return_value = True
    return graph
