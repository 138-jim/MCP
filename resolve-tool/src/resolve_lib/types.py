"""Enums, TypedDicts, and constants for the Resolve wrapper."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Page(str, Enum):
    MEDIA = "media"
    CUT = "cut"
    EDIT = "edit"
    FUSION = "fusion"
    COLOR = "color"
    FAIRLIGHT = "fairlight"
    DELIVER = "deliver"


class TrackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"


class KeyframeMode(int, Enum):
    ALL = 0
    COLOR = 1
    SIZING = 2


class ExportType(str, Enum):
    AAF = "AAF"
    DRT = "DRT"
    EDL = "EDL"
    FCP_7_XML = "FCP_7_XML"
    FCPXML_1_8 = "FCPXML_1_8"
    FCPXML_1_9 = "FCPXML_1_9"
    FCPXML_1_10 = "FCPXML_1_10"
    FCPXML_1_11 = "FCPXML_1_11"
    HDR_10_PROFILE_A = "HDR_10_PROFILE_A"
    HDR_10_PROFILE_B = "HDR_10_PROFILE_B"
    TEXT_CSV = "TEXT_CSV"
    TEXT_TAB = "TEXT_TAB"
    DOLBY_VISION_VER_2_9 = "DOLBY_VISION_VER_2_9"
    DOLBY_VISION_VER_4_0 = "DOLBY_VISION_VER_4_0"
    DOLBY_VISION_VER_5_1 = "DOLBY_VISION_VER_5_1"
    OTIO = "OTIO"


class CompositeMode(str, Enum):
    NORMAL = "normal"
    ADD = "add"
    SUBTRACT = "subtract"
    DIFFERENCE = "difference"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    HARDLIGHT = "hardlight"
    SOFTLIGHT = "softlight"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color dodge"
    COLOR_BURN = "color burn"
    LINEAR_DODGE = "linear dodge"
    LINEAR_BURN = "linear burn"
    LINEAR_LIGHT = "linear light"
    VIVID_LIGHT = "vivid light"
    PIN_LIGHT = "pin light"
    HARD_MIX = "hard mix"
    EXCLUSION = "exclusion"
    HUE = "hue"
    SATURATION = "saturation"
    COLORMODE = "color"
    LUMINOSITY = "luminosity"
    FOREGROUND = "foreground"


class ScalingMode(str, Enum):
    CROP = "crop"
    FIT = "fit"
    FILL = "fill"
    STRETCH = "stretch"


class ResizeFilter(str, Enum):
    SHARPER = "sharper"
    SMOOTHER = "smoother"
    BICUBIC = "bicubic"
    BILINEAR = "bilinear"
    LANCZOS = "lanczos"


class AlignType(int, Enum):
    SOUND = 0
    TIMECODE = 1


class StereoEye(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class StillExportFormat(str, Enum):
    DPX = "dpx"
    CIN = "cin"
    TIF = "tif"
    JPG = "jpg"
    PNG = "png"
    PPM = "ppm"
    BMP = "bmp"
    XPM = "xpm"


# ---------------------------------------------------------------------------
# TypedDicts
# ---------------------------------------------------------------------------

class DatabaseInfo(TypedDict, total=False):
    DbType: str  # "Disk" or "PostgreSQL"
    DbName: str
    IpAddress: str


class RenderSettings(TypedDict, total=False):
    SelectAllFrames: bool
    MarkIn: int
    MarkOut: int
    TargetDir: str
    CustomName: str
    UniqueFilenameStyle: int  # 0=prefix, 1=suffix
    ExportVideo: bool
    ExportAudio: bool
    FormatWidth: int
    FormatHeight: int
    FrameRate: float


class ClipInfo(TypedDict, total=False):
    mediaPoolItem: object
    startFrame: int
    endFrame: int
    mediaType: int  # 1=video, 2=audio
    trackIndex: int
    recordFrame: int


class MarkerInfo(TypedDict, total=False):
    color: str
    duration: int
    note: str
    name: str
    customData: str


class TimelineImportOptions(TypedDict, total=False):
    timelineName: str
    importSourceClips: bool
    sourceClipsPath: str
    sourceClipsFolders: list[str]
    interlaceProcessing: bool


class TimelineExportSubtitleSettings(TypedDict, total=False):
    SrtFilePath: str
    SrtFileEncoding: str


# ---------------------------------------------------------------------------
# Constants — Resolve property keys used by Get/SetProperty
# ---------------------------------------------------------------------------

TIMELINE_ITEM_PROPERTIES = [
    "Pan", "Tilt", "ZoomX", "ZoomY", "ZoomGang",
    "RotationAngle", "AnchorPointX", "AnchorPointY",
    "Pitch", "Yaw", "FlipX", "FlipY",
    "CropLeft", "CropRight", "CropTop", "CropBottom",
    "CropSoftness", "CropRetain",
    "DynamicZoomEase",
    "CompositeMode", "Opacity",
    "Distortion", "LensCorrectionType",
    "RetimeProcess", "MotionEstimation", "Scaling",
    "ResizeFilter",
]
