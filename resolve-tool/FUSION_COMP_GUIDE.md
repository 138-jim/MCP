# Fusion Composition Programming Guide

Reference for programmatically authoring DaVinci Resolve Fusion `.comp` files.

## Part 1: Grammar & Rules

### 1. Overview

Fusion `.comp` files are plain-text files containing a single Lua table literal. DaVinci Resolve's Fusion page parses these to build node graphs for compositing, effects, and motion graphics. The same Lua table syntax is used for `.setting` files (macros and presets), though this guide covers only `.comp` files.

Key facts:

- The file is **not** a Lua script. It is a **Lua table constructor** -- a data structure, not executable code. There is no `local`, no `function`, no control flow.
- Fusion extends standard Lua table syntax with a few constructs: named constructors like `Input {}`, `FuID {}`, `Gradient {}`, `BezierSpline {}`, and the `ordered()` function.
- String values use double quotes: `"Output"`. Lua long-strings (`[[ ]]`) are also valid but rarely used.
- Numeric values are standard Lua numbers: integers (`1920`), floats (`0.5`), negative (`-1.0`), scientific notation (`1e-3`).
- Boolean values are Lua booleans: `true`, `false`.
- Trailing commas are permitted and conventional after every value.
- Comments use Lua syntax: `-- single line` and `--[[ block ]]`.
- Indentation is conventionally one tab per level. Fusion's own export uses tabs.
- Files must be saved with `.comp` extension for Resolve to recognize them.

### 2. File Structure

#### 2.1 The Composition Skeleton

Every `.comp` file has this top-level structure:

```lua
Composition {
    CurrentTime = 0,
    RenderRange = { 0, 100 },
    GlobalRange = { 0, 100 },
    Tools = {
        -- tool definitions go here
    },
}
```

**Top-level keys:**

| Key | Type | Description |
|-----|------|-------------|
| `CurrentTime` | number | Playhead position (frame number). Usually `0`. |
| `RenderRange` | `{ start, end }` | Frame range to render. Two-element array. |
| `GlobalRange` | `{ start, end }` | Total frame range of the composition. |
| `Tools` | table | Contains all tool (node) definitions. |

For clips imported onto timeline items in Resolve, `CurrentTime`, `RenderRange`, and `GlobalRange` are typically omitted -- Resolve sets them from the clip's timeline range. A minimal valid `.comp` for timeline use is:

```lua
Composition {
    Tools = {
        -- tool definitions
    },
}
```

#### 2.2 Tool Definition Pattern

Each tool in the `Tools` table follows this pattern:

```
InstanceName = ToolType {
    Inputs = {
        InputName = Input { ... },
        AnotherInput = Input { ... },
    },
    ViewInfo = OperatorInfo { Pos = { x, y } },
},
```

- **`InstanceName`** -- A unique identifier for this tool instance. Must be a valid Lua identifier (letters, digits, underscores; cannot start with a digit). Convention: `ToolType` + sequential number, e.g., `Merge1`, `Background2`, `Blur1`.
- **`ToolType`** -- The Fusion tool class. Examples: `Background`, `Merge`, `Blur`, `Transform`, `TextPlus`, `BezierSpline`.
- **`Inputs`** -- Table of named inputs. Each input is wrapped in `Input { }`.
- **`ViewInfo`** -- Node position in the Fusion flow view. `OperatorInfo { Pos = { x, y } }` where `x` and `y` are pixel coordinates. Layout left-to-right following signal flow. Spacing of ~110 horizontally and ~66 vertically is conventional.

#### 2.3 The `ordered()` Function

Fusion defines a special `ordered()` function that wraps a table to preserve insertion order of keys. Standard Lua tables do not guarantee key order. In `.comp` files for timeline clips, `ordered()` is **not required** -- Fusion parses them correctly without it. It appears primarily in `.setting` files exported by Fusion's UI.

If you encounter it in exported files, it looks like:

```lua
Tools = ordered() {
    Merge1 = Merge { ... },
    Background1 = Background { ... },
}
```

For programmatic `.comp` authoring, **omit `ordered()`** from the Tools table. It is not needed and adds unnecessary complexity.

#### 2.4 MediaIn / MediaOut Naming

When a `.comp` file is loaded onto a DaVinci Resolve timeline clip, the clip's video input and output are represented by specific tool types with specific names:

| Resolve Concept | Native Tool Type | .comp File Tool Type | Conventional Name |
|----------------|-----------------|---------------------|-------------------|
| Clip video input | `MediaIn` | `Loader` | `MediaIn1` |
| Clip video output | `MediaOut` | `Saver` | `MediaOut1` |

**Two tool type conventions exist:**

- **In Resolve's Fusion page**, the native tool types are `MediaIn` and `MediaOut`. These are what you see in the node editor.
- **In `.comp` files** intended for import, the tool types `Loader` and `Saver` are used. Resolve automatically converts `Loader` → `MediaIn` and `Saver` → `MediaOut` on import. This is the convention used throughout this guide and in all the templates below, because `.comp` files are the interchange format between Fusion Studio and Resolve.

The instance names must be `MediaIn1`/`MediaOut1` for Resolve to correctly wire the clip's video through the composition.

```lua
MediaIn1 = Loader {
    Inputs = {
        ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
    },
    ViewInfo = OperatorInfo { Pos = { 55, 82.5 } },
},
MediaOut1 = Saver {
    Inputs = {
        Input = Input {
            SourceOp = "Merge1",
            Source = "Output",
        },
    },
    ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
},
```

The `MediaOut1` Saver's `Input` input must be connected (via `SourceOp`/`Source`) to whatever tool should produce the final output. This is the last node in the chain.

The `["Gamut.SLogVersion"]` input on the Loader is a standard inclusion for color pipeline compatibility. It is conventional to include it.

#### 2.5 Bracket Notation for Dotted Input Names

Some Fusion inputs have dotted names (e.g., `Gamut.SLogVersion`). Since dots are not valid in Lua identifiers, these must use bracket notation with a string key:

```lua
["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
["Shading.1.Opacity"] = Input { Value = 1, },
["Shading.1.Color"] = Input { Value = { 1, 1, 1, 1 }, },
```

Simple input names that are valid Lua identifiers (no dots, no spaces) use plain key syntax:

```lua
Blend = Input { Value = 0.5, },
XBlurSize = Input { Value = 10, },
```

### 3. Input Types

Every input in the `Inputs` table is wrapped in `Input { }`. There are six forms of input value, plus the `Disabled` flag.

#### 3.1 Static Value

Sets a constant value for the input.

```lua
InputName = Input { Value = 1920, },
```

The value can be a number, string, boolean, or table (for points):

```lua
Width = Input { Value = 1920, },
StyledText = Input { Value = "Hello World", },
UseFrameFormatSettings = Input { Value = 1, },
Center = Input { Value = { 0.5, 0.5 }, },
```

Note: Fusion uses `1`/`0` for boolean-like inputs, not `true`/`false`. `Value = 1` means enabled; `Value = 0` means disabled.

#### 3.2 Connection (SourceOp / Source)

Connects this input to another tool's output port.

```lua
Background = Input {
    SourceOp = "Background1",
    Source = "Output",
},
```

- `SourceOp` -- string, the instance name of the source tool.
- `Source` -- string, the name of the output port on the source tool.

A connection input has **no `Value` key**. `SourceOp` and `Source` always appear together.

#### 3.3 Expression

Sets a per-frame dynamic value using a string expression evaluated every frame.

```lua
Blend = Input { Expression = "iif(time < 30, time / 30, 1.0)", },
```

The expression is a string containing Fusion's expression language (see Section 5). An expression input has **no `Value` key** -- `Expression` replaces it.

#### 3.4 FuID

Selects an enum/dropdown value by its internal string identifier.

```lua
ApplyMode = Input { Value = FuID { "Screen" }, },
["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
Type = Input { Value = FuID { "Gradient" }, },
```

`FuID { "StringValue" }` is a named constructor. The string inside must match one of the tool's predefined enum values exactly.

#### 3.5 Point

Sets a 2D position as a two-element table.

```lua
Center = Input { Value = { 0.5, 0.5 }, },
```

Point coordinates are normalized: `{ 0, 0 }` is bottom-left, `{ 1, 1 }` is top-right, `{ 0.5, 0.5 }` is center. This is the standard form inside `Input {}`. In expressions, use `Point(x, y)` instead (see Section 5).

#### 3.6 Gradient

Defines a color gradient with color stops keyed by position (0.0 to 1.0).

```lua
Gradient = Input {
    Value = Gradient {
        Colors = {
            [0.0] = { 0, 0, 0, 1 },
            [0.5] = { 1, 0, 0, 1 },
            [1.0] = { 1, 1, 1, 1 },
        },
    },
},
```

Each color stop is `[position] = { R, G, B, A }` where all values are 0.0 to 1.0. Position `0.0` is the start, `1.0` is the end.

#### 3.7 Disabled Flag

Any input can be disabled by adding `Disabled = true`:

```lua
Blend = Input { Value = 0.75, Disabled = true, },
```

A disabled input retains its value but is ignored by Fusion (the tool uses its default instead). This is distinct from setting `Value = 0`.

### 4. Connection Rules

#### 4.1 SourceOp and Source

Every connection requires both keys:

```lua
Foreground = Input {
    SourceOp = "MediaIn1",    -- instance name of the source tool
    Source = "Output",         -- output port name on that tool
},
```

`SourceOp` references tools by their instance name (as defined in the `Tools` table). `Source` references a specific output port on that tool.

#### 4.2 Standard Output Port Names

Different tool categories expose different output port names:

| Output Port | Used By | Description |
|-------------|---------|-------------|
| `"Output"` | Most image-producing tools (Merge, Background, Blur, Transform, TextPlus, BrightnessContrast, etc.) | The primary image output |
| `"Mask"` | Mask tools (RectangleMask, EllipseMask, PolygonMask, BSplineMask, BitmapMask) | Mask/matte output |
| `"SceneOutput"` | 3D tools (Merge3D, Shape3D, Camera3D, etc.) | 3D scene output |
| `"MaterialOutput"` | Material tools (MtlBlinn, MtlPhong, MtlCookTorrance) | Material output |
| `"Value"` | Modifiers (BezierSpline, Expression, Calculation, etc.) | Numeric/data output |

When connecting tools, use the appropriate output port name. The vast majority of 2D compositing connections use `"Output"`.

#### 4.3 EffectMask Input

Any image-producing tool can accept an effect mask. The input name is always `EffectMask`:

```lua
BrightnessContrast1 = BrightnessContrast {
    Inputs = {
        Gain = Input { Value = 0.5, },
        Input = Input {
            SourceOp = "MediaIn1",
            Source = "Output",
        },
        EffectMask = Input {
            SourceOp = "EllipseMask1",
            Source = "Mask",
        },
    },
},
```

Note that mask tools output on port `"Mask"`, not `"Output"`. The `EffectMask` input limits the tool's effect to the area defined by the mask.

#### 4.4 Merge Tool Connections

The `Merge` tool has two primary image inputs with specific names:

```lua
Merge1 = Merge {
    Inputs = {
        Background = Input {
            SourceOp = "Background1",
            Source = "Output",
        },
        Foreground = Input {
            SourceOp = "MediaIn1",
            Source = "Output",
        },
    },
},
```

`Background` is the bottom/base layer. `Foreground` is the top layer composited over it. The result comes out of `Merge1`'s `"Output"` port.

### 5. Expression Syntax

Expressions are strings assigned to the `Expression` key of an `Input`. They are evaluated every frame to produce a dynamic value.

#### 5.1 Variables

| Variable | Type | Description |
|----------|------|-------------|
| `time` | number | Current frame number being rendered |
| `comp.RenderStart` | number | First frame of the composition's render range |
| `comp.RenderEnd` | number | Last frame of the composition's render range |
| `comp.HiQ` | boolean | `true` when rendering in High Quality mode, `false` in draft/proxy |

`time` is the most commonly used variable. It corresponds to the frame number on the timeline (not seconds).

#### 5.2 Functions

**Conditional:**

| Function | Description |
|----------|-------------|
| `iif(condition, true_value, false_value)` | Inline conditional. Returns `true_value` if `condition` is nonzero/true, otherwise `false_value`. Can be nested. |

**Lua math (available without `math.` prefix):**

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `sin(x)` | Sine (x in radians) |
| `cos(x)` | Cosine (x in radians) |
| `tan(x)` | Tangent (x in radians) |
| `sqrt(x)` | Square root |
| `log(x)` | Natural logarithm |
| `exp(x)` | e raised to the power x |
| `pi` | The constant 3.14159... |

**Use `math.` prefix for these (may not work without it):**

| Function | Description |
|----------|-------------|
| `math.floor(x)` | Round down to integer |
| `math.ceil(x)` | Round up to integer |
| `math.min(a, b)` | Minimum of two values |
| `math.max(a, b)` | Maximum of two values |
| `math.random()` | Random number 0.0 to 1.0 (per-frame, non-deterministic) |
| `math.pow(base, exp)` | Exponentiation (also available as `base ^ exp`) |

**Note:** Trig functions and `abs` reliably work without prefix. For `floor`, `ceil`, `min`, `max`, `random`, and `pow`, use the `math.` prefix to be safe across Fusion versions.

**Point and angle:**

| Function | Description |
|----------|-------------|
| `Point(x, y)` | Construct a 2D point value in an expression |
| `deg(x)` | Convert radians to degrees |
| `rad(x)` | Convert degrees to radians |

#### 5.3 References to Other Tools

Expressions can read the current value of any input on any tool in the composition:

| Syntax | Description |
|--------|-------------|
| `ToolName.InputName` | Read the value of an input |
| `ToolName.InputName.X` | X component of a Point input |
| `ToolName.InputName.Y` | Y component of a Point input |

Example: `"Transform1.Size * 2"` reads Transform1's Size input and doubles it.

**Comp preferences:**

```
comp:GetPrefs("Comp.FrameFormat.Rate")
```

Returns the composition's frame rate. Useful for time-to-frame conversions.

#### 5.4 Common Expression Patterns

These patterns cover the most frequent use cases. All are valid `Expression` strings.

**Linear ramp (0 to 1 over N frames from start):**

```lua
Expression = "time / 30",
```

Reaches 1.0 at frame 30, continues increasing after.

**Clamped linear ramp (0 to 1, then holds at 1):**

```lua
Expression = "iif(time < 30, time / 30, 1.0)",
```

**Normalized progress (0 to 1 over entire composition):**

```lua
Expression = "(time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart)",
```

Always 0.0 at first frame, 1.0 at last frame, regardless of comp length.

**Conditional ramp (ramp only in first N frames):**

```lua
Expression = "iif(time < (comp.RenderStart + 30), (time - comp.RenderStart) / 30, 1.0)",
```

Ramps from 0 to 1 over the first 30 frames relative to render start, then holds at 1.

**Reverse ramp (1 to 0 over last N frames):**

```lua
Expression = "iif(time > (comp.RenderEnd - 30), (comp.RenderEnd - time) / 30, 1.0)",
```

Holds at 1, then ramps down to 0 over the final 30 frames.

**Fade in + fade out (ramp up at start, ramp down at end):**

```lua
Expression = "iif(time < 15, time / 15, iif(time > (comp.RenderEnd - 15), (comp.RenderEnd - time) / 15, 1.0))",
```

Ramps 0 to 1 over first 15 frames, holds at 1, ramps 1 to 0 over last 15 frames.

**Ease in (quadratic):**

```lua
Expression = "(time / 30) ^ 2",
```

Starts slow, accelerates. Substitute `3` for cubic ease, etc.

**Ease out (inverse quadratic):**

```lua
Expression = "1 - ((30 - time) / 30) ^ 2",
```

**Ease in-out (smoothstep):**

```lua
Expression = "iif(time < 30, 3 * (time/30)^2 - 2 * (time/30)^3, 1.0)",
```

**Oscillation (sine wave):**

```lua
Expression = "0.5 + 0.5 * sin(time * pi / 15)",
```

Oscillates between 0 and 1 with a period of 30 frames.

**Countdown (decreasing integer):**

```lua
Expression = "math.floor((comp.RenderEnd - time) / comp:GetPrefs(\"Comp.FrameFormat.Rate\"))",
```

Counts down in whole seconds. Note escaped quotes inside the expression string.

**Ping-pong (triangle wave):**

```lua
Expression = "abs((time % 60) - 30) / 30",
```

Ramps 0 to 1 over 30 frames, then 1 to 0 over 30 frames, repeating.

### 6. Keyframe / BezierSpline Syntax

Keyframed animation uses **modifier tools** -- special tools defined as siblings in the `Tools` table, referenced from the animated input via `SourceOp`/`Source`.

#### 6.1 The Modifier Pattern

A keyframed input has two parts:

1. The input references the modifier by name, with `Source = "Value"`:

```lua
-- Inside the tool's Inputs:
Blend = Input {
    SourceOp = "Blend_Anim",
    Source = "Value",
},
```

2. The modifier is defined as a sibling entry in the `Tools` table:

```lua
-- Sibling in Tools table (same level as other tools):
Blend_Anim = BezierSpline {
    SplineColor = { Red = 225, Green = 0, Blue = 225 },
    KeyFrames = {
        [0] = { 0.0, RH = { 10, 0.0 } },
        [30] = { 1.0, LH = { 20, 1.0 } },
    },
},
```

The modifier's output port is always `"Value"`. The convention for modifier instance names is `InputName_Anim` or `ToolName_InputName`, but any valid identifier works as long as `SourceOp` matches.

#### 6.2 BezierSpline

`BezierSpline` is the standard keyframe modifier. It defines a curve with control points.

```lua
MyAnimation = BezierSpline {
    SplineColor = { Red = 225, Green = 0, Blue = 225 },
    KeyFrames = {
        [0]  = { 0.0, RH = { 10, 0.333 }, Flags = { Linear = true } },
        [30] = { 1.0, LH = { 20, 0.667 }, RH = { 40, 1.0 } },
        [60] = { 0.5, LH = { 50, 0.75 } },
    },
},
```

**Structure:**

| Key | Type | Description |
|-----|------|-------------|
| `SplineColor` | `{ Red, Green, Blue }` | Color of the spline in Fusion's spline editor. Values 0--255. Optional but conventional. |
| `KeyFrames` | table | Keyed by frame number. Each entry defines a keyframe. |

**Keyframe entry format:**

```
[frame] = { value, LH = { x, y }, RH = { x, y }, Flags = { Linear = true } },
```

| Field | Required | Description |
|-------|----------|-------------|
| `value` | Yes | The first (positional) element. The value at this keyframe. |
| `LH` | No | Left handle: `{ x, y }` where `x` is absolute frame, `y` is absolute value. Controls the curve arriving at this keyframe. |
| `RH` | No | Right handle: `{ x, y }`. Controls the curve leaving this keyframe. |
| `Flags` | No | Table of flags. `{ Linear = true }` makes the segment linear (no bezier curve). Other flags: `{ Loop = true }`, `{ PingPong = true }`. |

**Handle coordinates are absolute, not relative.** `LH = { 20, 0.667 }` means the left handle is at frame 20 with value 0.667.

**Rules:**

- The first keyframe typically has only `RH` (no left handle since there is nothing before it).
- The last keyframe typically has only `LH` (no right handle since there is nothing after it).
- Middle keyframes can have both `LH` and `RH`.
- Omitting handles defaults to smooth (automatic tangent) interpolation.
- `Flags = { Linear = true }` on a keyframe makes the curve segment from the previous keyframe to this one linear.

**Minimal linear animation (two keyframes, linear):**

```lua
FadeIn = BezierSpline {
    SplineColor = { Red = 204, Green = 0, Blue = 204 },
    KeyFrames = {
        [0]  = { 0.0, RH = { 15, 0.5 }, Flags = { Linear = true } },
        [30] = { 1.0, LH = { 15, 0.5 }, Flags = { Linear = true } },
    },
},
```

#### 6.3 LUTBezier

`LUTBezier` is a lookup-table spline modifier used for value remapping (e.g., particle size over life, color curves). Unlike `BezierSpline` which animates over time (frames), `LUTBezier` maps an input range to an output range.

```lua
SizeOverLife = LUTBezier {
    KeyColorSplines = { [0] = { 0, 0.5, 1 } },
    SplineColor = { Red = 192, Green = 128, Blue = 64 },
    NameSet = true,
    KeyFrames = {
        [0.0] = { 0.0, RH = { 0.333, 0.333 } },
        [0.5] = { 1.0, LH = { 0.333, 0.667 }, RH = { 0.667, 0.667 } },
        [1.0] = { 0.2, LH = { 0.667, 0.333 } },
    },
},
```

The key difference from `BezierSpline`: keys in `KeyFrames` are normalized input values (0.0 to 1.0) rather than frame numbers. The structure of each keyframe entry is identical.

### 7. Data Types

#### 7.1 Points

In `Input {}` values, points are plain two-element tables:

```lua
Center = Input { Value = { 0.5, 0.5 }, },
```

In expressions, points are constructed with the `Point()` function:

```lua
Center = Input { Expression = "Point(0.5, 0.5 + sin(time/10) * 0.1)", },
```

Coordinates are normalized 0.0 to 1.0 where `{0, 0}` is bottom-left and `{1, 1}` is top-right.

#### 7.2 Colors

Colors appear in several different contexts with different representations:

**Tool input colors (per-channel inputs, 0.0--1.0):**

Background, Merge, and similar tools use separate inputs for each channel:

```lua
["TopLeftRed"] = Input { Value = 0, },
["TopLeftGreen"] = Input { Value = 0, },
["TopLeftBlue"] = Input { Value = 0, },
["TopLeftAlpha"] = Input { Value = 1, },
```

Values are floating point, 0.0 to 1.0.

**Tile color metadata (0.0--1.0):**

Tool tile colors in ViewInfo use an `{ R, G, B }` table:

```lua
Colors = { TileColor = { R = 0.278, G = 0.509, B = 0.290 }, },
```

Values are floating point, 0.0 to 1.0.

**SplineColor (0--255):**

BezierSpline and LUTBezier use integer RGB in the 0--255 range:

```lua
SplineColor = { Red = 225, Green = 0, Blue = 225 },
```

These are the display colors for curves in Fusion's spline editor, not image data.

**Gradient colors (0.0--1.0 RGBA, keyed by position):**

```lua
Value = Gradient {
    Colors = {
        [0.0] = { 0, 0, 0, 1 },
        [1.0] = { 1, 1, 1, 1 },
    },
},
```

Each entry is `[position] = { R, G, B, A }`, all values 0.0 to 1.0.

**TextPlus shading colors (four-element table):**

```lua
["Shading.1.Color"] = Input { Value = { 1, 0.8, 0, 1 }, },
```

Four-element table `{ R, G, B, A }`, values 0.0 to 1.0.

#### 7.3 FuID

`FuID` is a named constructor for enum/dropdown identifiers. It wraps a single string:

```lua
ApplyMode = Input { Value = FuID { "Screen" }, },
Type = Input { Value = FuID { "Gradient" }, },
["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
```

The string must match one of the predefined enum values for that input exactly. Common FuID values vary by tool -- for example, Merge's `ApplyMode` accepts `"Merge"`, `"Screen"`, `"Multiply"`, `"Overlay"`, etc.

#### 7.4 Gradient

The `Gradient` constructor defines a multi-stop color gradient:

```lua
GradientInput = Input {
    Value = Gradient {
        Colors = {
            [0.0] = { 0, 0, 0, 1 },
            [0.25] = { 0.5, 0, 0, 1 },
            [0.75] = { 0, 0, 0.5, 1 },
            [1.0] = { 1, 1, 1, 1 },
        },
    },
},
```

- Position keys range from `0.0` (start) to `1.0` (end).
- Color values are `{ R, G, B, A }`, each 0.0 to 1.0.
- Any number of color stops can be defined.
- Fusion interpolates linearly between stops.

---

*End of Part 1: Grammar & Rules.*

## Part 2: Tool Reference

Categorized reference of Fusion tools for programmatic `.comp` authoring. Each tool listing shows the internal tool type ID used in `.comp` files, key inputs with types and defaults, and minimal usage snippets.

Conventions used throughout:
- **Type** column: `Number`, `Point` (`{x,y}`), `Text` (string), `Image` (connection), `Mask` (connection), `FuID` (enum), `Gradient`
- **Default** column shows the value Fusion uses when the input is omitted
- All numeric ranges are inclusive
- Point values use normalized coordinates: `{0.5, 0.5}` = center
- Color channel values are 0.0--1.0 unless noted otherwise
- Connections use `Input { SourceOp = "ToolName", Source = "Output" }` (or `"Mask"`, `"SceneOutput"`, etc.)

---

### 1. I/O

#### Loader (MediaIn)

Internal ID: `Loader`

In DaVinci Resolve timelines, `MediaIn1 = Loader { ... }` represents the incoming clip. In standalone `.comp` files, Loader reads from disk via its Clips table.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Clips | Table | (none) | File path entries (see below) |
| GlobalIn | Number | 0 | First frame of global range |
| GlobalOut | Number | 0 | Last frame of global range |
| Width | Number | 0 | Override width (0 = from file) |
| Height | Number | 0 | Override height (0 = from file) |
| Depth | Number | 0 | Bit depth: 0=Default, 1=int8, 2=int16, 3=float16, 4=float32 |
| EMultiFrame | Number | 0 | Frame number to hold (single-frame mode) |
| PostMultiplyByAlpha | Number | 1 | Pre-multiply alpha on load |
| Loop | Number | 0 | Loop mode: 0=None, 1=Loop, 2=PingPong, 3=Hold |

**Clips table syntax:**

```lua
MediaIn1 = Loader {
    Clips = {
        Clip {
            ID = "Clip1",
            Filename = "/path/to/image.####.exr",
            FormatID = "OpenEXRFormat",
            StartFrame = 0,
            Length = 100,
            TrimIn = 0,
            TrimOut = 99,
            GlobalStart = 0,
            GlobalEnd = 99,
        },
    },
    Inputs = {
        ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" } },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 0 } },
},
```

**Resolve timeline usage (no Clips needed):**

```lua
MediaIn1 = Loader {
    Inputs = {
        GlobalIn = Input { Value = 0 },
        GlobalOut = Input { Value = 100 },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 0 } },
},
```

#### Saver (MediaOut)

Internal ID: `Saver`

In DaVinci Resolve timelines, `MediaOut1 = Saver { ... }` sends the result back to the timeline. In standalone `.comp` files, Saver writes to disk.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image connection |
| Clip | Table | (none) | Output file path and format |
| OutputFormat | FuID | `"OpenEXRFormat"` | File format |
| CreateDir | Number | 1 | Auto-create output directories |
| ProcessRed | Number | 1 | Write red channel |
| ProcessGreen | Number | 1 | Write green channel |
| ProcessBlue | Number | 1 | Write blue channel |
| ProcessAlpha | Number | 1 | Write alpha channel |

```lua
MediaOut1 = Saver {
    Inputs = {
        Input = Input { SourceOp = "Merge1", Source = "Output" },
    },
    ViewInfo = OperatorInfo { Pos = { 660, 0 } },
},
```

**Standalone file output:**

```lua
Saver1 = Saver {
    Inputs = {
        Clip = Input {
            Value = Clip {
                Filename = "/output/render.####.exr",
                FormatID = "OpenEXRFormat",
            },
        },
        Input = Input { SourceOp = "Merge1", Source = "Output" },
        OutputFormat = Input { Value = FuID { "OpenEXRFormat" } },
    },
    ViewInfo = OperatorInfo { Pos = { 660, 0 } },
},
```

---

### 2. Generators

#### Background

Internal ID: `Background`

Generates a solid color, gradient, or four-corner gradient image.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| UseFrameFormatSettings | Number | 0 | 1 = use comp resolution; 0 = use Width/Height |
| Width | Number | 1920 | Output width in pixels |
| Height | Number | 1080 | Output height in pixels |
| Depth | Number | 0 | Bit depth: 0=Default, 1=int8, 2=int16, 3=float16, 4=float32 |
| Type | FuID | `"Solid"` | Fill type (see table below) |
| TopLeftRed | Number | 0.0 | Red component (top-left / solid color) |
| TopLeftGreen | Number | 0.0 | Green component |
| TopLeftBlue | Number | 0.0 | Blue component |
| TopLeftAlpha | Number | 1.0 | Alpha component |
| GlobalIn | Number | 0 | First frame |
| GlobalOut | Number | 0 | Last frame |
| EffectMask | Mask | (none) | Optional mask connection |

**Type values:**

| Value | FuID | Description |
|-------|------|-------------|
| 0 | `"Solid"` | Uniform solid color |
| 1 | `"Horizontal"` | Left-to-right two-color gradient |
| 2 | `"Vertical"` | Top-to-bottom two-color gradient |
| 3 | `"FourCorner"` | Independent color per corner |
| 4 | `"Gradient"` | Configurable gradient with multiple stops |

**Additional inputs for Type = `"Horizontal"` or `"Vertical"` (two-color):**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| TopRightRed | Number | 1.0 | Second color red |
| TopRightGreen | Number | 1.0 | Second color green |
| TopRightBlue | Number | 1.0 | Second color blue |
| TopRightAlpha | Number | 1.0 | Second color alpha |

**Additional inputs for Type = `"FourCorner"`:**

All four corners are independently controlled:
- `TopLeftRed/Green/Blue/Alpha` (top-left)
- `TopRightRed/Green/Blue/Alpha` (top-right)
- `BottomLeftRed/Green/Blue/Alpha` (bottom-left)
- `BottomRightRed/Green/Blue/Alpha` (bottom-right)

**Additional inputs for Type = `"Gradient"`:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Gradient | Gradient | (none) | Gradient color stops |
| GradientType | FuID | `"Linear"` | `"Linear"`, `"Reflect"`, `"Square"`, `"Cross"`, `"Radial"`, `"Angle"` |
| Offset | Number | 0.0 | Gradient offset (0.0--1.0) |
| Repeat | FuID | `"Once"` | `"Once"`, `"Repeat"`, `"PingPong"` |
| Start | Point | {0.0, 0.5} | Gradient start position |
| End | Point | {1.0, 0.5} | Gradient end position |

```lua
Background1 = Background {
    Inputs = {
        UseFrameFormatSettings = Input { Value = 1 },
        TopLeftRed = Input { Value = 0 },
        TopLeftGreen = Input { Value = 0 },
        TopLeftBlue = Input { Value = 0 },
        TopLeftAlpha = Input { Value = 1 },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 60 } },
},
```

**Gradient example:**

```lua
Background1 = Background {
    Inputs = {
        UseFrameFormatSettings = Input { Value = 1 },
        Type = Input { Value = FuID { "Gradient" } },
        GradientType = Input { Value = FuID { "Linear" } },
        Start = Input { Value = { 0.5, 0.0 } },
        End = Input { Value = { 0.5, 1.0 } },
        Gradient = Input {
            Value = Gradient {
                Colors = {
                    [0.0] = { 0, 0, 0, 1 },
                    [1.0] = { 0, 0, 1, 1 },
                },
            },
        },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 60 } },
},
```

---

### 3. Composite

#### Merge

Internal ID: `Merge`

Composites a foreground image over a background image. This is the primary compositing tool.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Background | Image | (none) | Background image connection |
| Foreground | Image | (none) | Foreground image connection |
| EffectMask | Mask | (none) | Optional mask limiting the merge area |
| Center | Point | {0.5, 0.5} | Position of foreground relative to background |
| Size | Number | 1.0 | Scale of foreground (1.0 = 100%) |
| Angle | Number | 0.0 | Rotation of foreground in degrees |
| Blend | Number | 1.0 | Opacity of the foreground (0.0--1.0) |
| ApplyMode | FuID | `"Merge"` | Blend mode (see table below) |
| Operator | FuID | `"Over"` | Alpha compositing operator |
| SubtractiveAdditive | Number | 0.0 | 0.0 = Subtractive, 1.0 = Additive blending |
| AlphaGain | Number | 1.0 | Multiplier for foreground alpha |
| BurnIn | Number | 0.0 | Burn-in darkness amount |
| PerformDepthMerge | Number | 0 | Enable Z-depth-based compositing |
| FlattenTransform | Number | 0 | Concatenate transforms for quality |

**ApplyMode Table (Blend Modes):**

| Value | Mode | FuID |
|-------|------|------|
| 0 | Normal | `"Merge"` |
| 1 | Screen | `"Screen"` |
| 2 | Dissolve | `"Dissolve"` |
| 3 | Multiply | `"Multiply"` |
| 4 | Overlay | `"Overlay"` |
| 5 | Soft Light | `"SoftLight"` |
| 6 | Hard Light | `"HardLight"` |
| 7 | Color Dodge | `"ColorDodge"` |
| 8 | Color Burn | `"ColorBurn"` |
| 9 | Darken | `"Darken"` |
| 10 | Lighten | `"Lighten"` |
| 11 | Difference | `"Difference"` |
| 12 | Exclusion | `"Exclusion"` |
| 13 | Hue | `"Hue"` |
| 14 | Saturation | `"Saturation"` |
| 15 | Color | `"Color"` |
| 16 | Luminosity | `"Luminosity"` |

**Operator Modes (Alpha Compositing):**

| FuID | Description |
|------|-------------|
| `"Over"` | Standard alpha composite: foreground over background |
| `"In"` | Output only where both foreground and background alpha overlap |
| `"Held Out"` | Output foreground only where background alpha is absent |
| `"Atop"` | Foreground appears only within background alpha region |
| `"XOr"` | Output where either has alpha but not both |

```lua
Merge1 = Merge {
    Inputs = {
        Background = Input { SourceOp = "MediaIn1", Source = "Output" },
        Foreground = Input { SourceOp = "TextPlus1", Source = "Output" },
        Blend = Input { Value = 0.8 },
        Center = Input { Value = { 0.5, 0.5 } },
    },
    ViewInfo = OperatorInfo { Pos = { 440, 0 } },
},
```

**Screen blend example:**

```lua
Merge1 = Merge {
    Inputs = {
        Background = Input { SourceOp = "MediaIn1", Source = "Output" },
        Foreground = Input { SourceOp = "Glow1", Source = "Output" },
        ApplyMode = Input { Value = FuID { "Screen" } },
        Blend = Input { Value = 0.7 },
    },
    ViewInfo = OperatorInfo { Pos = { 440, 0 } },
},
```

---

### 4. Text

#### TextPlus

Internal ID: `TextPlus`

Full-featured text generator with multi-element shading, layout controls, and per-character transforms.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| StyledText | Text | `""` | The text string to render |
| Font | Text | `"Open Sans"` | Font family name |
| Style | Text | `"Bold"` | Font style (e.g., `"Regular"`, `"Bold"`, `"Italic"`, `"Bold Italic"`) |
| Size | Number | 0.05 | Font size in normalized screen height (0.0--1.0) |
| Center | Point | {0.5, 0.5} | Text anchor position |
| Direction | FuID | `"x"` | Text flow: `"x"` (horizontal), `"y"` (vertical) |
| LineDirection | FuID | `"x"` | Line advance direction |
| HorizontalJustificationNew | Number | 1 | 0=Left, 1=Center, 2=Right |
| VerticalJustificationNew | Number | 1 | 0=Top, 1=Center, 2=Bottom |
| UseFrameFormatSettings | Number | 0 | 1 = use comp resolution |
| Width | Number | 1920 | Output width (when UseFrameFormatSettings=0) |
| Height | Number | 1080 | Output height (when UseFrameFormatSettings=0) |
| Enabled1 | Number | 1 | Enable shading element 1 (fill) |
| Enabled2 | Number | 0 | Enable shading element 2 (outline) |
| Red1 | Number | 1.0 | Fill color red |
| Green1 | Number | 1.0 | Fill color green |
| Blue1 | Number | 1.0 | Fill color blue |
| Alpha1 | Number | 1.0 | Fill color alpha |
| GlobalIn | Number | 0 | First frame |
| GlobalOut | Number | 0 | Last frame |
| EffectMask | Mask | (none) | Optional mask connection |

**Shading Elements (1--8):**

TextPlus has 8 shading layers. Element 1 is the text fill by default. Elements 2--8 can be outlines, shadows, borders, etc. Each element N has these inputs (replace `N` with the element number):

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| EnabledN | Number | varies | 1 = enabled, 0 = disabled |
| RedN | Number | varies | Color red |
| GreenN | Number | varies | Color green |
| BlueN | Number | varies | Color blue |
| AlphaN | Number | varies | Color alpha |
| OpacityN | Number | 1.0 | Layer opacity (0.0--1.0) |
| TypeN | Number | varies | 0=Text Fill, 1=Text Outline, 2=Border Fill, 3=Border Outline |
| ThicknessN | Number | 0.0 | Outline/border thickness |
| SoftnessXN | Number | 0.0 | Horizontal softness |
| SoftnessYN | Number | 0.0 | Vertical softness |
| OffsetXN | Number | 0.0 | Horizontal offset (use to create shadow effects) |
| OffsetYN | Number | 0.0 | Vertical offset (use to create shadow effects) |
| ElementShapeN | Number | varies | 0=Text, 1=Round Rectangle, 2=Rectangle, 3=Triangle |

**Text layout inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| LineSpacingNew | Number | 1.0 | Line spacing multiplier |
| CharacterSpacingNew | Number | 1.0 | Character spacing multiplier |
| TransformRotation | Number | 0.0 | Rotation angle (degrees) |
| ManualFontKerningPlacement | Number | 0 | 1 = enable manual kerning |

```lua
TextPlus1 = TextPlus {
    Inputs = {
        StyledText = Input { Value = "HELLO WORLD" },
        Font = Input { Value = "Open Sans" },
        Style = Input { Value = "Bold" },
        Size = Input { Value = 0.1 },
        Center = Input { Value = { 0.5, 0.5 } },
        UseFrameFormatSettings = Input { Value = 1 },
        HorizontalJustificationNew = Input { Value = 1 },
        VerticalJustificationNew = Input { Value = 1 },
        Red1 = Input { Value = 1 },
        Green1 = Input { Value = 1 },
        Blue1 = Input { Value = 1 },
        Alpha1 = Input { Value = 1 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 60 } },
},
```

**Text with outline (element 2):**

```lua
TextPlus1 = TextPlus {
    Inputs = {
        StyledText = Input { Value = "OUTLINED" },
        Font = Input { Value = "Arial" },
        Style = Input { Value = "Bold" },
        Size = Input { Value = 0.08 },
        Center = Input { Value = { 0.5, 0.5 } },
        UseFrameFormatSettings = Input { Value = 1 },
        Red1 = Input { Value = 1 },
        Green1 = Input { Value = 1 },
        Blue1 = Input { Value = 1 },
        Enabled2 = Input { Value = 1 },
        Red2 = Input { Value = 0 },
        Green2 = Input { Value = 0 },
        Blue2 = Input { Value = 0 },
        Thickness2 = Input { Value = 0.15 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 60 } },
},
```

---

### 5. Transform

#### Transform

Internal ID: `Transform`

Applies 2D spatial transformations: position, scale, rotation, flip.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image connection |
| Center | Point | {0.5, 0.5} | Transform center / position |
| Pivot | Point | {0.5, 0.5} | Rotation/scale pivot point |
| Size | Number | 1.0 | Uniform scale (1.0 = 100%) |
| Aspect | Number | 1.0 | Aspect ratio adjustment |
| Angle | Number | 0.0 | Rotation in degrees |
| FlipHoriz | Number | 0 | 1 = flip horizontally |
| FlipVert | Number | 0 | 1 = flip vertically |
| Edges | FuID | `"Canvas"` | Edge handling mode (see table) |
| InvertTransform | Number | 0 | 1 = invert the transform |
| FlattenTransform | Number | 0 | 1 = concatenate (better quality for chained transforms) |
| EffectMask | Mask | (none) | Optional mask connection |

**Edges modes:**

| Value | FuID | Description |
|-------|------|-------------|
| 0 | `"Canvas"` | Transparent outside canvas |
| 1 | `"Wrap"` | Tile/wrap edges |
| 2 | `"Duplicate"` | Extend edge pixels |
| 3 | `"Mirror"` | Mirror at edges |

```lua
Transform1 = Transform {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        Center = Input { Value = { 0.75, 0.75 } },
        Size = Input { Value = 0.25 },
        Angle = Input { Value = 15 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

---

### 6. Blur / Filter

#### Blur

Internal ID: `Blur`

Gaussian blur with independent X/Y control.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image connection |
| XBlurSize | Number | 1.0 | Horizontal blur radius |
| YBlurSize | Number | 1.0 | Vertical blur radius |
| LockXY | Number | 1 | 1 = lock X and Y sizes |
| BlendMethod | FuID | `"Normal"` | `"Normal"`, `"Bright"`, `"Dark"` |
| Red | Number | 1 | Apply to red channel |
| Green | Number | 1 | Apply to green channel |
| Blue | Number | 1 | Apply to blue channel |
| Alpha | Number | 1 | Apply to alpha channel |
| EffectMask | Mask | (none) | Optional mask |

```lua
Blur1 = Blur {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        XBlurSize = Input { Value = 10 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

#### DirectionalBlur

Internal ID: `DirectionalBlur`

Blur along a specified direction from a center point.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| Center | Point | {0.5, 0.5} | Blur center point |
| Length | Number | 0.1 | Blur length |
| Angle | Number | 0.0 | Blur angle in degrees (for linear type) |
| Type | FuID | `"Linear"` | `"Linear"`, `"Radial"`, `"Centered"`, `"Zoom"` |
| Glow | Number | 0.0 | Glow amount added to blur |
| Red | Number | 1 | Apply to red channel |
| Green | Number | 1 | Apply to green channel |
| Blue | Number | 1 | Apply to blue channel |
| Alpha | Number | 1 | Apply to alpha channel |
| EffectMask | Mask | (none) | Optional mask |

```lua
DirectionalBlur1 = DirectionalBlur {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        Type = Input { Value = FuID { "Zoom" } },
        Center = Input { Value = { 0.5, 0.5 } },
        Length = Input { Value = 0.15 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

#### Glow

Internal ID: `Glow`

Adds a luminance-based glow effect.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| Gain | Number | 1.0 | Glow brightness multiplier |
| GlowSize | Number | 5.0 | Glow spread radius |
| Blend | Number | 1.0 | Blend amount (0.0--1.0) |
| Red | Number | 1 | Apply to red channel |
| Green | Number | 1 | Apply to green channel |
| Blue | Number | 1 | Apply to blue channel |
| Alpha | Number | 0 | Apply to alpha channel |
| EffectMask | Mask | (none) | Optional mask |

```lua
Glow1 = Glow {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        Gain = Input { Value = 2.0 },
        GlowSize = Input { Value = 10 },
        Blend = Input { Value = 0.5 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

#### SoftGlow

Internal ID: `SoftGlow`

A softer, more subtle glow variant.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| Gain | Number | 1.0 | Glow brightness |
| Threshold | Number | 0.5 | Luminance threshold for glow (0.0--1.0) |
| XGlowSize | Number | 5.0 | Horizontal glow size |
| YGlowSize | Number | 5.0 | Vertical glow size |
| LockXY | Number | 1 | 1 = lock X and Y sizes |
| ColorScale | Number | 1.0 | Color saturation of glow |
| Blend | Number | 1.0 | Blend amount (0.0--1.0) |
| EffectMask | Mask | (none) | Optional mask |

```lua
SoftGlow1 = SoftGlow {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        Gain = Input { Value = 1.5 },
        Threshold = Input { Value = 0.7 },
        XGlowSize = Input { Value = 8 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

---

### 7. Color

#### BrightnessContrast

Internal ID: `BrightnessContrast`

Simple color correction: gain, brightness, contrast, gamma, saturation, and lift.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| Gain | Number | 1.0 | Overall luminance multiplier |
| Brightness | Number | 0.0 | Additive brightness offset (-1.0 to 1.0) |
| Contrast | Number | 0.0 | Contrast adjustment (-1.0 to 1.0) |
| Gamma | Number | 1.0 | Gamma correction (>0) |
| Saturation | Number | 1.0 | Color saturation (0.0 = grayscale) |
| Lift | Number | 0.0 | Shadow lift (-1.0 to 1.0) |
| ClipBlack | Number | 0 | Checkbox (0/1): clip out-of-range values below black |
| ClipWhite | Number | 0 | Checkbox (0/1): clip out-of-range values above white |
| Low | Number | 0.0 | Low end of the output range |
| High | Number | 1.0 | High end of the output range |
| Red | Number | 1 | Apply to red channel |
| Green | Number | 1 | Apply to green channel |
| Blue | Number | 1 | Apply to blue channel |
| Alpha | Number | 0 | Apply to alpha channel |
| EffectMask | Mask | (none) | Optional mask |

```lua
BrightnessContrast1 = BrightnessContrast {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        Gain = Input { Value = 1.2 },
        Contrast = Input { Value = 0.1 },
        Saturation = Input { Value = 0.8 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

#### ColorCorrector

Internal ID: `ColorCorrector`

Full-featured color corrector with separate lift/gamma/gain controls for master and per-channel, plus saturation and tint.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| MasterRGBGain | Number | 1.0 | Master gain (overall) |
| MasterRGBGamma | Number | 1.0 | Master gamma (midtones) |
| MasterRGBLift | Number | 0.0 | Master lift (shadows) |
| RedGain | Number | 1.0 | Red channel gain |
| GreenGain | Number | 1.0 | Green channel gain |
| BlueGain | Number | 1.0 | Blue channel gain |
| RedGamma | Number | 1.0 | Red channel gamma |
| GreenGamma | Number | 1.0 | Green channel gamma |
| BlueGamma | Number | 1.0 | Blue channel gamma |
| RedLift | Number | 0.0 | Red channel lift |
| GreenLift | Number | 0.0 | Green channel lift |
| BlueLift | Number | 0.0 | Blue channel lift |
| Saturation | Number | 1.0 | Overall saturation |
| MidTonesSaturation | Number | 1.0 | Midtone saturation |
| HighlightsSaturation | Number | 1.0 | Highlight saturation |
| ShadowsSaturation | Number | 1.0 | Shadow saturation |
| Tint | Number | 0.0 | Color tint angle |
| Strength | Number | 1.0 | Overall correction strength (0.0--1.0) |
| WheelHighlightsGain | Number | 1.0 | Highlight gain (wheel) |
| WheelShadowsGain | Number | 1.0 | Shadow gain (wheel) |
| ColorRanges | Table | (none) | Custom color range definitions |
| EffectMask | Mask | (none) | Optional mask |

```lua
ColorCorrector1 = ColorCorrector {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        MasterRGBGain = Input { Value = 1.1 },
        MasterRGBGamma = Input { Value = 0.95 },
        Saturation = Input { Value = 1.2 },
        Tint = Input { Value = 0.05 },
        Strength = Input { Value = 0.8 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

---

### 8. Masks

#### RectangleMask

Internal ID: `RectangleMask`

Generates a rectangular mask shape. Output connects via `Source = "Mask"`.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Center | Point | {0.5, 0.5} | Mask center position |
| Width | Number | 0.5 | Mask width (normalized, 0.0--1.0) |
| Height | Number | 0.5 | Mask height (normalized, 0.0--1.0) |
| Angle | Number | 0.0 | Rotation in degrees |
| CornerRadius | Number | 0.0 | Rounded corner radius |
| SoftEdge | Number | 0.0 | Edge feather amount |
| BorderWidth | Number | 0.0 | Border thickness (creates hollow rectangle) |
| Level | Number | 1.0 | Mask intensity (0.0--1.0) |
| Invert | Number | 0 | 1 = invert the mask |
| ClippingMode | FuID | `"Frame"` | `"Frame"` or `"None"` |
| OutputSize | FuID | `"Default"` | Output resolution |

```lua
RectangleMask1 = RectangleMask {
    Inputs = {
        Center = Input { Value = { 0.5, 0.9 } },
        Width = Input { Value = 0.6 },
        Height = Input { Value = 0.08 },
        CornerRadius = Input { Value = 0.02 },
        SoftEdge = Input { Value = 0.01 },
    },
    ViewInfo = OperatorInfo { Pos = { 330, 120 } },
},
```

Connect as effect mask:

```lua
EffectMask = Input { SourceOp = "RectangleMask1", Source = "Mask" },
```

#### EllipseMask

Internal ID: `EllipseMask`

Generates an elliptical (or circular) mask shape. Output connects via `Source = "Mask"`.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Center | Point | {0.5, 0.5} | Mask center position |
| Width | Number | 0.5 | Horizontal radius (normalized) |
| Height | Number | 0.5 | Vertical radius (normalized) |
| Angle | Number | 0.0 | Rotation in degrees |
| SoftEdge | Number | 0.0 | Edge feather amount |
| BorderWidth | Number | 0.0 | Border thickness (creates ring) |
| Level | Number | 1.0 | Mask intensity (0.0--1.0) |
| Invert | Number | 0 | 1 = invert the mask |
| ClippingMode | FuID | `"Frame"` | `"Frame"` or `"None"` |

```lua
EllipseMask1 = EllipseMask {
    Inputs = {
        Center = Input { Value = { 0.5, 0.5 } },
        Width = Input { Value = 0.4 },
        Height = Input { Value = 0.4 },
        SoftEdge = Input { Value = 0.1 },
    },
    ViewInfo = OperatorInfo { Pos = { 330, 120 } },
},
```

#### PolylineMask

Internal ID: `PolylineMask`

Freeform polygon mask defined by a set of control points. Points are defined in the `Polyline` sub-table. Primarily used for rotoscoping or complex shapes. Due to the verbose point data format, prefer RectangleMask or EllipseMask when a simple shape suffices.

Key inputs: `Center`, `SoftEdge`, `BorderWidth`, `Level`, `Invert`, `Polyline` (point table).

#### BSplineMask

Internal ID: `BSplineMask`

B-spline mask with smooth curves through control points. Similar to PolylineMask but with B-spline interpolation. Key inputs are the same as PolylineMask.

---

### 9. Matte / Keying

#### DeltaKeyer

Internal ID: `DeltaKeyer`

Advanced chroma keyer for green/blue screen removal. Produces a clean alpha matte.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image (green/blue screen footage) |
| BackgroundColor | Point | {0, 1, 0} | Key color (R, G, B) |
| GainRed | Number | 1.0 | Red gain for key extraction |
| GainGreen | Number | 1.0 | Green gain for key extraction |
| GainBlue | Number | 1.0 | Blue gain for key extraction |
| PreMatte | Number | 0.0 | Pre-matte blur to reduce noise |
| PostMatte | Number | 0.0 | Post-matte blur for edge smoothing |
| MatteBlur | Number | 0.0 | Additional matte blur |
| MatteGamma | Number | 1.0 | Matte gamma correction |
| MatteThresholdLow | Number | 0.0 | Low threshold: pixels below this are fully transparent |
| MatteThresholdHigh | Number | 0.5 | High threshold: pixels above this are fully opaque |
| SpillMethod | FuID | `"None"` | `"None"`, `"Complementary"`, `"LimitSaturation"`, `"SolidColor"` |
| SpillSuppression | Number | 1.0 | Spill suppression strength |
| FringeSize | Number | 0.0 | Edge fringe correction |
| FringeGamma | Number | 1.0 | Fringe gamma |
| EffectMask | Mask | (none) | Optional mask |

```lua
DeltaKeyer1 = DeltaKeyer {
    Inputs = {
        Input = Input { SourceOp = "MediaIn1", Source = "Output" },
        BackgroundColor = Input { Value = { 0, 1, 0 } },
        MatteThresholdHigh = Input { Value = 0.5 },
        SpillMethod = Input { Value = FuID { "Complementary" } },
        SpillSuppression = Input { Value = 1.0 },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

#### MatteControl

Internal ID: `MatteControl`

Manipulates and refines an existing alpha/matte channel.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Image | (none) | Source image |
| GarbageMatte | Image | (none) | Garbage matte connection (subtracts from alpha) |
| SolidMatte | Image | (none) | Solid matte connection (adds to alpha) |
| MatteThresholdLow | Number | 0.0 | Low alpha threshold |
| MatteThresholdHigh | Number | 1.0 | High alpha threshold |
| MatteBlur | Number | 0.0 | Blur the matte edges |
| MatteGamma | Number | 1.0 | Gamma correction on matte |
| InvertMatte | Number | 0 | 1 = invert the matte |
| PostMultiply | Number | 1 | 1 = post-multiply by alpha |
| EffectMask | Mask | (none) | Optional mask |

```lua
MatteControl1 = MatteControl {
    Inputs = {
        Input = Input { SourceOp = "DeltaKeyer1", Source = "Output" },
        MatteBlur = Input { Value = 2.0 },
        MatteGamma = Input { Value = 0.8 },
        MatteThresholdLow = Input { Value = 0.05 },
        MatteThresholdHigh = Input { Value = 0.95 },
    },
    ViewInfo = OperatorInfo { Pos = { 440, 0 } },
},
```

---

### 10. Particle System

Fusion's particle system uses a pipeline: emitter(s) feed into forces/modifiers, then into a renderer that produces a 2D image.

#### pEmitter

Internal ID: `pEmitter`

Creates particles with configurable velocity, lifespan, and visual properties.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Number | Number | 10 | Particles emitted per frame |
| NumberVariance | Number | 0 | Random variance on emission count |
| Lifespan | Number | 100 | Particle lifespan in frames |
| LifespanVariance | Number | 0 | Random variance on lifespan |
| Velocity | Number | 0.01 | Initial particle speed |
| VelocityVariance | Number | 0 | Random variance on velocity |
| Angle | Number | 0 | Emission angle in degrees |
| AngleVariance | Number | 360 | Angular spread (360 = emit in all directions) |
| RotationX | Number | 0 | Initial X rotation of particle |
| RotationY | Number | 0 | Initial Y rotation of particle |
| RotationZ | Number | 0 | Initial Z rotation of particle |
| SpinX | Number | 0 | X rotation speed per frame |
| SpinY | Number | 0 | Y rotation speed per frame |
| SpinZ | Number | 0 | Z rotation speed per frame |
| PositionVariance | Number | 0 | Random variance on emission position |
| Color | FuID | `"Use Style Color"` | Color source: `"Use Style Color"`, `"Use Color From Region"` |
| RandomSeed | Number | 0 | Random seed for reproducibility |
| GlobalIn | Number | 0 | First frame |
| GlobalOut | Number | 0 | Last frame |

**Style sub-inputs (particle appearance):**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Style | FuID | `"Point"` | Particle type: `"Point"`, `"Bitmap"`, `"Brush"`, `"Blob"`, `"Line"`, `"PointCluster"` |
| SizeX | Number | 0.01 | Particle width |
| SizeY | Number | 0.01 | Particle height |
| SizeVariance | Number | 0 | Random variance on size |
| ["Color.Red"] | Number | 1.0 | Particle color red (bracket notation required) |
| ["Color.Green"] | Number | 1.0 | Particle color green |
| ["Color.Blue"] | Number | 1.0 | Particle color blue |
| ["Color.Alpha"] | Number | 1.0 | Particle color alpha |
| FadeIn | Number | 0.0 | Fade-in time (fraction of lifespan, 0.0--1.0) |
| FadeOut | Number | 0.0 | Fade-out time (fraction of lifespan, 0.0--1.0) |
| SizeOverLife | LUT | (none) | Size curve over particle life (LUTBezier) |

**Region sub-inputs (emission shape):**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| RegionShape | FuID | `"Point"` | `"Point"`, `"Line"`, `"Rectangle"`, `"Ellipse"`, `"Bitmap"`, `"Mesh"` |
| RegionCenter | Point | {0.5, 0.5} | Region center position |
| RegionWidth | Number | 0.1 | Region width |
| RegionHeight | Number | 0.1 | Region height |

```lua
pEmitter1 = pEmitter {
    Inputs = {
        Number = Input { Value = 50 },
        Lifespan = Input { Value = 60 },
        Velocity = Input { Value = 0.02 },
        Angle = Input { Value = 90 },
        AngleVariance = Input { Value = 30 },
        Style = Input { Value = FuID { "Blob" } },
        SizeX = Input { Value = 0.005 },
        SizeY = Input { Value = 0.005 },
        Red = Input { Value = 1 },
        Green = Input { Value = 0.8 },
        Blue = Input { Value = 0.2 },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 0 } },
},
```

#### pRender

Internal ID: `pRender`

Renders the particle system to a 2D image. Connects to the output of emitters and forces.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream connection |
| Camera3D | 3D | (none) | Optional 3D camera connection |
| OutputWidth | Number | 1920 | Output width |
| OutputHeight | Number | 1080 | Output height |
| UseFrameFormatSettings | Number | 0 | 1 = use comp resolution |
| MotionBlur | Number | 0 | 1 = enable motion blur |
| MotionBlurSamples | Number | 10 | Number of blur samples |
| Depth | Number | 0 | Bit depth |
| GlobalIn | Number | 0 | First frame |
| GlobalOut | Number | 0 | Last frame |

```lua
pRender1 = pRender {
    Inputs = {
        Input = Input { SourceOp = "pEmitter1", Source = "Output" },
        UseFrameFormatSettings = Input { Value = 1 },
        MotionBlur = Input { Value = 1 },
    },
    ViewInfo = OperatorInfo { Pos = { 440, 0 } },
},
```

#### pDirectionalForce

Internal ID: `pDirectionalForce`

Applies a constant directional force (gravity, wind) to particles.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream |
| Direction | Number | 270 | Force direction in degrees (270 = downward) |
| Strength | Number | 0.001 | Force magnitude |

#### pTurbulence

Internal ID: `pTurbulence`

Adds turbulent/chaotic motion to particles.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream |
| XStrength | Number | 0.5 | Horizontal turbulence strength |
| YStrength | Number | 0.5 | Vertical turbulence strength |
| ZStrength | Number | 0.0 | Depth turbulence strength |
| Density | Number | 1.0 | Turbulence frequency/density |
| RandomSeed | Number | 0 | Random seed |

#### pBounce

Internal ID: `pBounce`

Bounces particles off a defined region.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream |
| Elasticity | Number | 0.5 | Bounce energy retention (0.0--1.0) |
| RegionShape | FuID | `"Line"` | Bounce region shape |
| RegionCenter | Point | {0.5, 0.0} | Region center |
| RegionWidth | Number | 1.0 | Region width |

#### pSpawn

Internal ID: `pSpawn`

Spawns new particles from existing ones.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream |
| Number | Number | 3 | Particles spawned per parent |
| Velocity | Number | 0.01 | Spawn velocity |
| VelocityVariance | Number | 0 | Velocity randomness |
| AngleVariance | Number | 360 | Angular spread |
| Lifespan | Number | 50 | Spawned particle lifespan |

#### pKill

Internal ID: `pKill`

Destroys particles that enter/exit a defined region or meet age criteria.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| Input | Particles | (none) | Particle stream |
| Mode | FuID | `"Age"` | `"Age"`, `"Region"` |
| Age | Number | 100 | Kill particles older than this |
| RegionShape | FuID | `"Rectangle"` | Kill region shape |
| RegionCenter | Point | {0.5, 0.5} | Region center |
| RegionWidth | Number | 0.5 | Region width |
| RegionHeight | Number | 0.5 | Region height |

---

### 11. CustomTool

Internal ID: `CustomTool`

Per-pixel image processing via mathematical expressions. Extremely flexible for procedural effects, channel manipulation, and custom compositing.

#### Image Inputs

| Input ID | Connection Variable | Description |
|----------|-------------------|-------------|
| Image1 | c1 | First image input |
| Image2 | c2 | Second image input |
| Image3 | c3 | Third image input |
| MaskImage | m1 | Mask image input |

#### Numeric Inputs

| Input | Variable | Type | Default | Description |
|-------|----------|------|---------|-------------|
| NumberIn1 | n1 | Number | 0 | First numeric slider |
| NumberIn2 | n2 | Number | 0 | Second numeric slider |
| NumberIn3 | n3 | Number | 0 | Third numeric slider |
| NumberIn4 | n4 | Number | 0 | Fourth numeric slider |
| NumberIn5 | n5 | Number | 0 | Fifth numeric slider |
| NumberIn6 | n6 | Number | 0 | Sixth numeric slider |
| NumberIn7 | n7 | Number | 0 | Seventh numeric slider |
| NumberIn8 | n8 | Number | 0 | Eighth numeric slider |

#### Point Inputs

| Input | Variable | Type | Default | Description |
|-------|----------|------|---------|-------------|
| PointIn1 | p1 | Point | {0.5, 0.5} | First point (p1x, p1y) |
| PointIn2 | p2 | Point | {0.5, 0.5} | Second point (p2x, p2y) |
| PointIn3 | p3 | Point | {0.5, 0.5} | Third point (p3x, p3y) |
| PointIn4 | p4 | Point | {0.5, 0.5} | Fourth point (p4x, p4y) |

#### LUT Inputs

| Input | Variable | Description |
|-------|----------|-------------|
| LUTIn1 | (via expression) | First lookup table input |
| LUTIn2 | (via expression) | Second lookup table input |
| LUTIn3 | (via expression) | Third lookup table input |
| LUTIn4 | (via expression) | Fourth lookup table input |

#### Expression Inputs

CustomTool evaluates expressions in a specific order. Each category has numbered slots:

**Setup expressions (s1--s4):** Evaluated once per frame before any pixel processing. Use for per-frame calculations.

| Input | Description |
|-------|-------------|
| SetupExpression1 | Setup expression evaluated first |
| SetupExpression2 | Setup expression evaluated second |
| SetupExpression3 | Setup expression evaluated third |
| SetupExpression4 | Setup expression evaluated fourth |

**Intermediate expressions (i1--i4):** Evaluated per-pixel before channel expressions. Use for shared per-pixel calculations.

| Input | Description |
|-------|-------------|
| IntermExpression1 | Intermediate expression 1 |
| IntermExpression2 | Intermediate expression 2 |
| IntermExpression3 | Intermediate expression 3 |
| IntermExpression4 | Intermediate expression 4 |

**Channel expressions:** Define the output pixel value for each channel.

| Input | Default Expression | Description |
|-------|-------------------|-------------|
| RedExpression | `"c1.r"` | Red channel output |
| GreenExpression | `"c1.g"` | Green channel output |
| BlueExpression | `"c1.b"` | Blue channel output |
| AlphaExpression | `"c1.a"` | Alpha channel output |
| ZExpression | `"c1.z"` | Z-depth channel output |
| UExpression | `"c1.u"` | U texture coordinate output |
| VExpression | `"c1.v"` | V texture coordinate output |

#### Built-in Variables

| Variable | Description |
|----------|-------------|
| r1, r2, r3 | Red channel of image c1, c2, c3 at current pixel |
| g1, g2, g3 | Green channel of image c1, c2, c3 at current pixel |
| b1, b2, b3 | Blue channel of image c1, c2, c3 at current pixel |
| a1, a2, a3 | Alpha channel of image c1, c2, c3 at current pixel |
| z1, z2, z3 | Z-depth of image c1, c2, c3 at current pixel |
| x | Current pixel X coordinate (normalized 0.0--1.0) |
| y | Current pixel Y coordinate (normalized 0.0--1.0) |
| w | Image width in pixels |
| h | Image height in pixels |
| time | Current frame number |
| n1--n8 | Numeric input values |
| p1x, p1y | Point 1 coordinates |
| p2x, p2y | Point 2 coordinates |
| p3x, p3y | Point 3 coordinates |
| p4x, p4y | Point 4 coordinates |
| s1--s4 | Setup expression results |
| i1--i4 | Intermediate expression results |

#### Pixel Sampling Functions

Sample pixel values from input images at arbitrary coordinates:

| Function | Description |
|----------|-------------|
| `getr1b(x,y)` | Sample c1 red, bilinear interpolation |
| `getr1d(x,y)` | Sample c1 red, default (no interpolation) |
| `getr1w(x,y)` | Sample c1 red, wrap mode |
| `getg1b(x,y)` | Sample c1 green, bilinear |
| `getb1b(x,y)` | Sample c1 blue, bilinear |
| `geta1b(x,y)` | Sample c1 alpha, bilinear |

Pattern: `get[channel][image][mode](x,y)` where:
- channel: `r`, `g`, `b`, `a`, `z`
- image: `1`, `2`, `3` (corresponding to c1, c2, c3)
- mode: `b` (bilinear), `d` (default), `w` (wrap)

```lua
CustomTool1 = CustomTool {
    Inputs = {
        Image1 = Input { SourceOp = "MediaIn1", Source = "Output" },
        NumberIn1 = Input { Value = 0.5 },
        RedExpression = Input { Value = "r1 * n1" },
        GreenExpression = Input { Value = "g1 * n1" },
        BlueExpression = Input { Value = "b1 * n1" },
        AlphaExpression = Input { Value = "a1" },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

**Vignette via CustomTool:**

```lua
CustomTool1 = CustomTool {
    Inputs = {
        Image1 = Input { SourceOp = "MediaIn1", Source = "Output" },
        NumberIn1 = Input { Value = 0.7 },
        SetupExpression1 = Input { Value = "" },
        IntermExpression1 = Input { Value = "sqrt((x-0.5)*(x-0.5) + (y-0.5)*(y-0.5))" },
        RedExpression = Input { Value = "r1 * (1 - i1 * n1)" },
        GreenExpression = Input { Value = "g1 * (1 - i1 * n1)" },
        BlueExpression = Input { Value = "b1 * (1 - i1 * n1)" },
        AlphaExpression = Input { Value = "a1" },
    },
    ViewInfo = OperatorInfo { Pos = { 220, 0 } },
},
```

---

### 12. Effects (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Highlight | `Highlight` | Adds bright highlights/specular bloom | Input, Low, High, Curve, Length |
| Shadow | `Shadow` | Creates drop shadow from alpha | Input, ShadowColor, Softness, Angle, Length, Alpha |
| Rays | `Rays` | Volumetric light ray effect | Input, Center, Length, Threshold, Strength, NumSteps |
| Trails | `Trails` | Motion trail/echo effect | Input, Restart, Reset |
| Duplicate | `Duplicate` | Creates grid copies of input | Input, Copies, Center, Angle, Pivot, TimeOffset |
| HotSpot | `HotSpot` | Lens flare / hot spot generator | Center, Size, Strength, OcclusionInput, Rays, SecondaryRays |
| PseudoColor | `PseudoColor` | Maps luminance to false color | Input, MapType, Colors (gradient), Softness |

---

### 13. Warp (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Displace | `Displace` | Displaces pixels based on a displacement map | Input, Foreground (map), XRefraction, YRefraction, LightPower |
| CornerPositioner | `CornerPositioner` | Four-corner pin deformation | Input, TopLeft, TopRight, BottomLeft, BottomRight (all Points) |
| GridWarp | `GridWarp` | Free-form mesh deformation | Input, SrcGridX, SrcGridY, DstGridX, DstGridY |
| LensDistort | `LensDistort` | Barrel/pincushion lens distortion | Input, Model (0=DERev,1=3DEClassic,2=PFBarrel), K1, K2, K3, Center |
| Drip | `Drip` | Ripple/drip water effect | Input, Center, Amplitude, Frequency, Phase, Damping |
| Vortex | `Vortex` | Rotational swirl distortion | Input, Center, Angle, Size |
| Dent | `Dent` | Spherical lens dent/bulge distortion | Input, Center, Size, Strength |

---

### 14. Additional Blur / Filter (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Defocus | `Defocus` | Lens defocus / bokeh blur | Input, DefocusSize, BloomLevel, BloomThreshold, Filter (Disk/Lens/NGon) |
| Sharpen | `Sharpen` | Simple sharpening | Input, Amount |
| UnsharpMask | `UnsharpMask` | Unsharp mask sharpening | Input, Size, Gain, Threshold |
| VariBlur | `VariBlur` | Variable blur driven by a blur map | Input, BlurImage (map connection), XBlurSize, YBlurSize, Method |
| ErodeDilate | `ErodeDilate` | Morphological erode/dilate | Input, XAmount, YAmount (negative = erode, positive = dilate), Filter |

---

### 15. Additional Color (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| ColorCurves | `ColorCurves` | Spline-based color correction curves | Input, Red/Green/Blue/Master (LUT splines) |
| ColorGain | `ColorGain` | Per-channel gain/offset/gamma | Input, GainRed, GainGreen, GainBlue, GammaRed, GammaGreen, GammaBlue, LiftRed, LiftGreen, LiftBlue |
| ColorMatrix | `ColorMatrix` | 3x3 color matrix transformation | Input, Matrix (9 values for RGB transformation) |
| ColorSpace | `ColorSpace` | Convert between color spaces | Input, InputSpace, OutputSpace (sRGB, Linear, Rec709, ACEScg, etc.) |
| Gamut | `Gamut` | Gamut conversion and mapping | Input, SourceSpace, OutputSpace, RemoveGamma, AddGamma, SLogVersion |
| HueCurves | `HueCurves` | Adjust saturation/luminance by hue | Input, Sat (LUT), Lum (LUT), SatVsSat (LUT) |
| WhiteBalance | `WhiteBalance` | White balance correction | Input, Temperature, Tint, GammaCorrection |

---

### 16. Additional Generators (Light Depth)

#### FastNoise

Internal ID: `FastNoise`

Procedural noise generator with multiple noise types.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| UseFrameFormatSettings | Number | 0 | 1 = use comp resolution |
| Width | Number | 1920 | Output width |
| Height | Number | 1080 | Output height |
| Detail | Number | 5 | Octaves of detail (1--10) |
| Brightness | Number | 0.0 | Brightness offset |
| Contrast | Number | 3.0 | Contrast multiplier |
| XScale | Number | 5.0 | Horizontal noise scale |
| YScale | Number | 5.0 | Vertical noise scale |
| LockXY | Number | 1 | 1 = lock X and Y scales |
| SeetheRate | Number | 0.0 | Animation speed per frame |
| Seethe | Number | 0.0 | Animation offset |
| Color | Number | 0 | 0 = grayscale, 1 = color |
| Type | FuID | `"Perlin"` | `"Perlin"`, `"Value"`, `"Gradient"`, `"Simplex"`, `"CellNoise"`, `"FBM"` |
| Discontinuous | Number | 0 | 1 = discontinuous noise |
| Invert | Number | 0 | 1 = invert output |
| Center | Point | {0.5, 0.5} | Noise center / pan |
| GlobalIn | Number | 0 | First frame |
| GlobalOut | Number | 0 | Last frame |

**Other generators:**

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Plasma | `Plasma` | Animated plasma generator | Width, Height, Scale, Phase, Complexity, Colors |
| Mandelbrot | `Mandelbrot` | Mandelbrot fractal generator | Width, Height, Center, Size, Iterations, Power, Bailout |
| DaySky | `DaySky` | Physically-based sky generator | Width, Height, SunPosition, Turbidity, SaturationScale, LuminanceScale |

---

### 17. 3D (Light Depth)

#### Geometry

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Shape3D | `Shape3D` | 3D primitive generator | Shape (0=Plane, 1=Cube, 2=Sphere, 3=Cylinder, 4=Cone, 5=Torus), Radius, SizeWidth, SizeHeight, SizeDepth, SubdivisionWidth, SubdivisionHeight, SubdivisionDepth, TranslationX/Y/Z, RotationX/Y/Z, ScaleX/Y/Z |
| Merge3D | `Merge3D` | Merges 3D scenes | SceneInput1, SceneInput2, ..SceneInputN (connections via `Source = "SceneOutput"`) |

#### Camera

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Camera3D | `Camera3D` | 3D camera | FLength (focal length mm), PlaneOfFocus, ApertureW, ApertureH, NearClip, FarClip, TranslationX/Y/Z, RotationX/Y/Z, PerspNearClip, PerspFarClip |

#### Renderer

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Renderer3D | `Renderer3D` | Renders 3D scene to 2D | SceneInput (connection), Width, Height, UseFrameFormatSettings, RendererType (FuID: `"RendererOpenGL"` or `"RendererSoftware"`). Lighting/shadow inputs are namespaced under renderer type: `["RendererOpenGL.LightingEnabled"]`, `["RendererOpenGL.ShadowsEnabled"]` |

#### Lights

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| AmbientLight | `AmbientLight` | Uniform ambient light | Red, Green, Blue, Intensity, TranslationX/Y/Z |
| DirectionalLight | `DirectionalLight` | Infinite directional light | Red, Green, Blue, Intensity, TranslationX/Y/Z, RotationX/Y/Z |
| PointLight | `PointLight` | Omni-directional point light | Red, Green, Blue, Intensity, TranslationX/Y/Z, DecayType (0=None, 1=Linear, 2=Quadratic) |
| SpotLight | `SpotLight` | Cone-shaped spot light | Red, Green, Blue, Intensity, ConeAngle, Penumbra, TranslationX/Y/Z, RotationX/Y/Z, DecayType |

#### Materials

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| MtlBlinn | `MtlBlinn` | Blinn-Phong material | DiffuseRed/Green/Blue, SpecularRed/Green/Blue, SpecularExponent, SpecularIntensity, Opacity, DiffuseColorImage (texture connection via `Source = "Output"`) |
| MtlPhong | `MtlPhong` | Phong material | DiffuseRed/Green/Blue, SpecularRed/Green/Blue, SpecularExponent, SpecularIntensity, Opacity |

Materials connect to Shape3D via `MaterialInput = Input { SourceOp = "MtlBlinn1", Source = "MaterialOutput" }`.

#### Textures

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| Texture2D | `Texture2D` | Projects 2D image onto 3D geometry | Input (image connection), UScale, VScale, UOffset, VOffset, WrapU, WrapV |
| BumpMap | `BumpMap` | Creates bump/normal map from image | Input (image connection), Height, BumpMapType |

---

### 18. Shape / Vector (Light Depth)

Vector shape tools produce shape data (not images). They must be rendered through `sRender` to produce an image.

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| sRectangle | `sRectangle` | Vector rectangle | Center, Width, Height, CornerRadius, Fill (color), BorderWidth, BorderColor |
| sEllipse | `sEllipse` | Vector ellipse | Center, Width, Height, Fill, BorderWidth, BorderColor |
| sNGon | `sNGon` | Regular N-sided polygon | Center, Radius, Sides, Rotation, Fill, BorderWidth |
| sStar | `sStar` | Star shape | Center, OuterRadius, InnerRadius, Points, Rotation, Fill |
| sMerge | `sMerge` | Merge vector shapes | Shape1, Shape2 (shape connections) |
| sRender | `sRender` | Render shapes to image | Input (shape connection), Width, Height, UseFrameFormatSettings |
| sTransform | `sTransform` | Transform vector shapes | Input (shape), Center, Size, Angle, Pivot |
| sOutline | `sOutline` | Outline/stroke a shape | Input (shape), Thickness, LineType, JoinType |
| sExpand | `sExpand` | Expand/contract shape | Input (shape), Amount, LineType, JoinType |

Shape connections use `Source = "Output"` between shape tools.

---

### 19. LUT (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| FileLUT | `FileLUT` | Loads and applies a LUT file | Input (image), LUTFile (file path string), Strength (0.0--1.0) |
| LUTCubeApply | `LUTCubeApply` | Applies a .cube LUT file | Input (image), LUTFile (file path), Strength, ColorSpaceConversion |

---

### 20. Misc (Light Depth)

| Tool | Internal ID | Description | Key Inputs |
|------|-------------|-------------|------------|
| ChangeDepth | `ChangeDepth` | Converts image bit depth | Input, Depth (1=int8, 2=int16, 3=float16, 4=float32) |
| TimeSpeed | `TimeSpeed` | Retimes footage via speed/offset | Input, Speed (1.0 = normal), Offset, InterpolationMethod (0=Nearest, 1=Blend) |
| TimeStretcher | `TimeStretcher` | Retimes footage via source time mapping | Input, SourceTime (expression or keyframed), InterpolationMethod |
| PipeRouter | `PipeRouter` | Pass-through node for routing (no processing) | Input |
| Tracker | `Tracker` | Motion tracker (track points on footage) | Input, TrackingOperation, PatternCenter1 (Point), SearchWidth1, SearchHeight1, PatternWidth1, PatternHeight1 |
| Paint | `Paint` | Multi-stroke paint tool | Input, BrushControls (complex sub-tables for strokes, shapes, cloning) |

## Part 3: Template Library

Complete, working `.comp` templates. Each can be used as-is or modified at `-- MODIFY:` comments.
All templates use `UseFrameFormatSettings = 1` for resolution independence and `comp.RenderEnd` for adaptive timing.

---

### Transitions

#### 1. Fade In from Color

Background (black by default) merged with MediaIn. Blend expression ramps from 0 to 1 over the first N frames, revealing the video.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: fade-in color (0-1 range, default black)
				["TopLeftRed"] = Input { Value = 0, },
				["TopLeftGreen"] = Input { Value = 0, },
				["TopLeftBlue"] = Input { Value = 0, },
				["TopLeftAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 30 to desired fade duration in frames
				Blend = Input { Expression = "iif(time < 30, time / 30, 1.0)", },
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 2. Fade Out to Color

Background (black by default) merged with MediaIn. Blend expression ramps from 1 to 0 over the last N frames, fading to color.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: fade-out color (0-1 range, default black)
				["TopLeftRed"] = Input { Value = 0, },
				["TopLeftGreen"] = Input { Value = 0, },
				["TopLeftBlue"] = Input { Value = 0, },
				["TopLeftAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 30 to desired fade duration in frames
				Blend = Input { Expression = "iif(time > (comp.RenderEnd - 30), (comp.RenderEnd - time) / 30, 1.0)", },
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 3. Dip to Color

Background merged with MediaIn. Blend ramps up for N frames (fade out to color), holds at zero briefly, then ramps back (fade in from color). Creates a dip-to-black or dip-to-white effect.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: dip color (0-1 range, default black)
				["TopLeftRed"] = Input { Value = 0, },
				["TopLeftGreen"] = Input { Value = 0, },
				["TopLeftBlue"] = Input { Value = 0, },
				["TopLeftAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 15 to desired ramp duration in frames (fade out over first 15, fade in over last 15)
				Blend = Input { Expression = "iif(time < 15, time / 15, iif(time > (comp.RenderEnd - 15), (comp.RenderEnd - time) / 15, 1.0))", },
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 4. Cross Dissolve from Transparent

Background with alpha=0 (transparent) merged with MediaIn. Blend ramps from 0 to 1 over N frames. When placed on a higher video track, reveals the clip beneath during the dissolve.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				TopLeftAlpha = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 30 to desired dissolve duration in frames
				Blend = Input { Expression = "iif(time < (comp.RenderStart + 30), (time - comp.RenderStart) / 30, 1.0)", },
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 5. Blur Out

MediaIn through Blur with expression-driven blur size. Blur ramps from 0 to max over the last N frames. Creates a defocus exit transition.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Blur1 = Blur {
			Inputs = {
				-- MODIFY: change 15.0 to desired max blur size, change 30 to desired duration in frames
				XBlurSize = Input { Expression = "iif(time > (comp.RenderEnd - 30), 15.0 * (time - (comp.RenderEnd - 30)) / 30, 0)", },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Blur1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 6. Blur In with Fade

MediaIn through a decreasing Blur, then Merge with increasing Blend over a transparent Background. Combines blur reduction with opacity fade-in over the first N frames.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				TopLeftAlpha = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Blur1 = Blur {
			Inputs = {
				-- MODIFY: change 15.0 to desired max blur size, change 30 to desired duration in frames
				XBlurSize = Input { Expression = "iif(time < (comp.RenderStart + 30), 15.0 * (1 - (time - comp.RenderStart) / 30), 0)", },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 30 to match the duration above
				Blend = Input { Expression = "iif(time < (comp.RenderStart + 30), (time - comp.RenderStart) / 30, 1.0)", },
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Blur1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 495, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 605, 82.5 } },
		},
	},
}
```

---

### Text & Titles

#### 7. Simple Text Overlay

TextPlus centered on screen, merged over MediaIn. White text at 0.08 size. Customize text, font, position, size, and color.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		TextPlus1 = TextPlus {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: text content
				StyledText = Input { Value = "Your Text Here", },
				-- MODIFY: font family
				Font = Input { Value = "Arial", },
				-- MODIFY: font style (e.g. "Bold", "Italic", "Regular")
				Style = Input { Value = "Bold", },
				-- MODIFY: text size (0-1 range, relative to frame height)
				Size = Input { Value = 0.08, },
				-- MODIFY: text position (0.5, 0.5 = center)
				Center = Input { Value = { 0.5, 0.5 }, },
				-- Shading element 1 (text fill): white
				-- MODIFY: text color (Red1, Green1, Blue1 range 0-1)
				Red1 = Input { Value = 1, },
				Green1 = Input { Value = 1, },
				Blue1 = Input { Value = 1, },
				Alpha1 = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "TextPlus1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 8. Lower Third with Bar

A colored rectangle bar at the bottom-left with text next to it, merged over MediaIn. The bar is a Background masked by a RectangleMask. The text sits just to the right of the bar.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		RectangleMask1 = RectangleMask {
			Inputs = {
				-- MODIFY: bar position and size
				Center = Input { Value = { 0.12, 0.12 }, },
				Width = Input { Value = 0.2, },
				Height = Input { Value = 0.04, },
				CornerRadius = Input { Value = 0.005, },
				SoftEdge = Input { Value = 0.001, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, -49.5 } },
		},
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: bar color (0-1 range, default blue accent)
				["TopLeftRed"] = Input { Value = 0.15, },
				["TopLeftGreen"] = Input { Value = 0.45, },
				["TopLeftBlue"] = Input { Value = 0.85, },
				["TopLeftAlpha"] = Input { Value = 1, },
				EffectMask = Input {
					SourceOp = "RectangleMask1",
					Source = "Mask",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		TextPlus1 = TextPlus {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: lower third text
				StyledText = Input { Value = "Speaker Name", },
				-- MODIFY: font family
				Font = Input { Value = "Arial", },
				Style = Input { Value = "Bold", },
				-- MODIFY: text size
				Size = Input { Value = 0.04, },
				-- MODIFY: text position (to the right of the bar)
				Center = Input { Value = { 0.35, 0.12 }, },
				HorizontalJustificationNew = Input { Value = 0, },
				Red1 = Input { Value = 1, },
				Green1 = Input { Value = 1, },
				Blue1 = Input { Value = 1, },
				Alpha1 = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 495, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		Merge2 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "TextPlus1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 495, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge2",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 605, 82.5 } },
		},
	},
}
```

#### 9. Animated Text Fade

TextPlus merged over MediaIn with a Blend expression that fades in over N frames, holds, then fades out over N frames before the end.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		TextPlus1 = TextPlus {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: text content
				StyledText = Input { Value = "Animated Title", },
				-- MODIFY: font family
				Font = Input { Value = "Arial", },
				Style = Input { Value = "Bold", },
				-- MODIFY: text size
				Size = Input { Value = 0.08, },
				-- MODIFY: text position
				Center = Input { Value = { 0.5, 0.5 }, },
				Red1 = Input { Value = 1, },
				Green1 = Input { Value = 1, },
				Blue1 = Input { Value = 1, },
				Alpha1 = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: change 20 to desired fade duration in frames (both in and out)
				Blend = Input { Expression = "iif(time < 20, time / 20, iif(time > (comp.RenderEnd - 20), (comp.RenderEnd - time) / 20, 1.0))", },
				Background = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "TextPlus1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

---

### Color Effects

#### 10. Vignette

MediaIn through BrightnessContrast with reduced Gain, masked by an inverted EllipseMask with a large soft edge. Darkens the edges while preserving the center.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		EllipseMask1 = EllipseMask {
			Inputs = {
				Center = Input { Value = { 0.5, 0.5 }, },
				-- MODIFY: mask width (larger = more center visible)
				Width = Input { Value = 0.9, },
				-- MODIFY: mask height
				Height = Input { Value = 0.9, },
				-- MODIFY: soft edge size (larger = more gradual falloff)
				SoftEdge = Input { Value = 0.4, },
				Invert = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		BrightnessContrast1 = BrightnessContrast {
			Inputs = {
				-- MODIFY: Gain reduction amount (0.0 = full black edges, 0.5 = moderate darken)
				Gain = Input { Value = 0.4, },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				EffectMask = Input {
					SourceOp = "EllipseMask1",
					Source = "Mask",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "BrightnessContrast1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 11. Desaturation Sweep

MediaIn through BrightnessContrast with an expression-driven Saturation that transitions from 1.0 (full color) to a target value over a specified duration.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		BrightnessContrast1 = BrightnessContrast {
			Inputs = {
				-- MODIFY: target saturation (0.0 = grayscale, 0.5 = half desaturated)
				-- MODIFY: timing — replace comp.RenderEnd with a frame count to sweep faster
				Saturation = Input { Expression = "iif(time < comp.RenderEnd, 1.0 - 1.0 * (1.0 - 0.0) * (time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart), 0.0)", },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "BrightnessContrast1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 12. Glow/Bloom

MediaIn splits: one path goes through Glow, then Merge in Screen mode blends the glow back over the original. Creates a soft bloom look.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Glow1 = Glow {
			Inputs = {
				-- MODIFY: glow size (default 10)
				GlowSize = Input { Value = 10, },
				-- MODIFY: glow intensity (default 1.0)
				Gain = Input { Value = 1.0, },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				-- MODIFY: blend amount for glow intensity (0-1)
				Blend = Input { Value = 0.5, },
				ApplyMode = Input { Value = FuID { "Screen" }, },
				Background = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Glow1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

---

### Motion/Transform

#### 13. Ken Burns

MediaIn through Transform with expression-driven Size (slow zoom) and Center (slow pan) over the full clip duration. Values interpolate linearly from start to end.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Transform1 = Transform {
			Inputs = {
				-- MODIFY: start size and end size (1.0 = 100%, 1.2 = 120% zoom)
				Size = Input { Expression = "1.0 + (1.2 - 1.0) * (time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart)", },
				-- MODIFY: start center X,Y and end center X,Y (0.5, 0.5 = centered)
				Center = Input { Expression = "Point(0.5 + (0.52 - 0.5) * (time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart), 0.5 + (0.48 - 0.5) * (time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart))", },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Transform1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

#### 14. Picture-in-Picture

Background serves as the base layer. MediaIn1 is scaled down and repositioned via Transform, then merged over the Background. Use this when you want to show one clip as a small inset.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: base background color (default black)
				["TopLeftRed"] = Input { Value = 0, },
				["TopLeftGreen"] = Input { Value = 0, },
				["TopLeftBlue"] = Input { Value = 0, },
				["TopLeftAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		Transform1 = Transform {
			Inputs = {
				-- MODIFY: PIP size (0.3 = 30% of frame)
				Size = Input { Value = 0.3, },
				-- MODIFY: PIP position (0.75, 0.75 = top-right area)
				Center = Input { Value = { 0.75, 0.75 }, },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Transform1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 495, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 605, 82.5 } },
		},
	},
}
```

#### 15. Zoom Blur Transition

MediaIn through DirectionalBlur with expression-driven Length that ramps up over the last N frames. Creates a motion-blur exit effect.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		DirectionalBlur1 = DirectionalBlur {
			Inputs = {
				-- MODIFY: direction type — "Zoom" for radial, "Linear" for directional
				Type = Input { Value = FuID { "Zoom" }, },
				-- MODIFY: change 0.15 to desired max blur length, change 30 to duration in frames
				Length = Input { Expression = "iif(time > (comp.RenderEnd - 30), 0.15 * (time - (comp.RenderEnd - 30)) / 30, 0)", },
				Center = Input { Value = { 0.5, 0.5 }, },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "DirectionalBlur1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

---

### Generators

#### 16. Animated Noise Background

FastNoise generator with expression-driven Seethe for continuous animation. No MediaIn needed — generates a procedural animated texture.

```lua
Composition {
	Tools = {
		FastNoise1 = FastNoise {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: noise detail level (1-10)
				Detail = Input { Value = 5, },
				-- MODIFY: contrast (0-5)
				Contrast = Input { Value = 1.5, },
				-- MODIFY: horizontal scale
				XScale = Input { Value = 15, },
				-- Expression-driven animation: Seethe increases over time
				-- MODIFY: change 0.03 to control animation speed (higher = faster)
				Seethe = Input { Expression = "time * 0.03", },
				SeetheRate = Input { Value = 0.15, },
				-- MODIFY: noise gradient colors (0-1 range, bracket notation required)
				["Gradient.Color1Red"] = Input { Value = 0.05, },
				["Gradient.Color1Green"] = Input { Value = 0.05, },
				["Gradient.Color1Blue"] = Input { Value = 0.15, },
				["Gradient.Color1Alpha"] = Input { Value = 1, },
				["Gradient.Color2Red"] = Input { Value = 0.2, },
				["Gradient.Color2Green"] = Input { Value = 0.3, },
				["Gradient.Color2Blue"] = Input { Value = 0.5, },
				["Gradient.Color2Alpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "FastNoise1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
	},
}
```

#### 17. Solid with Gradient

Background generator set to gradient mode (Type=4 for Four Corner gradient). Define four corner colors for smooth blends across the frame.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- Type 4 = Four Corner Gradient
				Type = Input { Value = FuID { "Corner" }, },
				-- MODIFY: top-left color (0-1 range)
				["TopLeftRed"] = Input { Value = 0.1, },
				["TopLeftGreen"] = Input { Value = 0.1, },
				["TopLeftBlue"] = Input { Value = 0.3, },
				["TopLeftAlpha"] = Input { Value = 1, },
				-- MODIFY: top-right color
				["TopRightRed"] = Input { Value = 0.2, },
				["TopRightGreen"] = Input { Value = 0.1, },
				["TopRightBlue"] = Input { Value = 0.4, },
				["TopRightAlpha"] = Input { Value = 1, },
				-- MODIFY: bottom-left color
				["BottomLeftRed"] = Input { Value = 0.0, },
				["BottomLeftGreen"] = Input { Value = 0.0, },
				["BottomLeftBlue"] = Input { Value = 0.1, },
				["BottomLeftAlpha"] = Input { Value = 1, },
				-- MODIFY: bottom-right color
				["BottomRightRed"] = Input { Value = 0.05, },
				["BottomRightGreen"] = Input { Value = 0.0, },
				["BottomRightBlue"] = Input { Value = 0.2, },
				["BottomRightAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
	},
}
```

---

### Particles

#### 18. Simple Particle Burst

pEmitter generates particles, pRender converts the particle system to a 2D image. Basic upward emission with customizable count, lifespan, velocity, color, and size.

```lua
Composition {
	Tools = {
		pEmitter1 = pEmitter {
			Inputs = {
				-- MODIFY: number of particles emitted per frame
				Number = Input { Value = 10, },
				-- MODIFY: particle lifespan in frames
				Lifespan = Input { Value = 100, },
				-- MODIFY: emission velocity (upward)
				Velocity = Input { Value = 0.01, },
				-- MODIFY: emission angle (0 = right, 90 = up, 180 = left, 270 = down)
				Angle = Input { Value = 90, },
				-- MODIFY: angle variance for spread
				AngleVariance = Input { Value = 30, },
				-- MODIFY: particle color (0-1 range, bracket notation required)
				["Color.Red"] = Input { Value = 1.0, },
				["Color.Green"] = Input { Value = 0.8, },
				["Color.Blue"] = Input { Value = 0.2, },
				["Color.Alpha"] = Input { Value = 1.0, },
				-- MODIFY: particle size
				Size = Input { Value = 0.02, },
				SizeVariance = Input { Value = 0.005, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		pRender1 = pRender {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				Input = Input {
					SourceOp = "pEmitter1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "pRender1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```

---

### Composite

#### 19. Green Screen Key

MediaIn through DeltaKeyer (chroma key), then merged over a Background (replacement background). The DeltaKeyer removes the green screen and the merge composites over a new solid color.

```lua
Composition {
	Tools = {
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: replacement background color (0-1 range)
				["TopLeftRed"] = Input { Value = 0.2, },
				["TopLeftGreen"] = Input { Value = 0.2, },
				["TopLeftBlue"] = Input { Value = 0.3, },
				["TopLeftAlpha"] = Input { Value = 1, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		DeltaKeyer1 = DeltaKeyer {
			Inputs = {
				-- MODIFY: key color (green screen default)
				["KeyColor.Red"] = Input { Value = 0.0, },
				["KeyColor.Green"] = Input { Value = 1.0, },
				["KeyColor.Blue"] = Input { Value = 0.0, },
				-- MODIFY: key range (increase to key more shades of green)
				Range = Input { Value = 0.1, },
				-- MODIFY: spill method — "None", "Complementary", "LimitSaturation", "SolidColor"
				SpillMethod = Input { Value = FuID { "Complementary" }, },
				SpillSuppression = Input { Value = 0.5, },
				FringeSize = Input { Value = 0.01, },
				Input = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "DeltaKeyer1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
			},
			ViewInfo = OperatorInfo { Pos = { 495, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 605, 82.5 } },
		},
	},
}
```

#### 20. Masked Overlay

A colored Background overlay merged over MediaIn, with a RectangleMask as EffectMask to restrict the overlay to a specific region. Useful for color bars, highlight boxes, or partial tints.

```lua
Composition {
	Tools = {
		MediaIn1 = Loader {
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 82.5 } },
		},
		RectangleMask1 = RectangleMask {
			Inputs = {
				-- MODIFY: mask center position
				Center = Input { Value = { 0.5, 0.5 }, },
				-- MODIFY: mask width (0-1 range)
				Width = Input { Value = 0.4, },
				-- MODIFY: mask height (0-1 range)
				Height = Input { Value = 0.3, },
				-- MODIFY: soft edge for feathered border
				SoftEdge = Input { Value = 0.02, },
				CornerRadius = Input { Value = 0.01, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, -16.5 } },
		},
		Background1 = Background {
			Inputs = {
				UseFrameFormatSettings = Input { Value = 1, },
				-- MODIFY: overlay color (0-1 range)
				["TopLeftRed"] = Input { Value = 1.0, },
				["TopLeftGreen"] = Input { Value = 0.85, },
				["TopLeftBlue"] = Input { Value = 0.0, },
				-- MODIFY: overlay opacity (reduce for semi-transparent)
				["TopLeftAlpha"] = Input { Value = 0.4, },
			},
			ViewInfo = OperatorInfo { Pos = { 385, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "MediaIn1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				PerformDepthMerge = Input { Value = 0, },
				EffectMask = Input {
					SourceOp = "RectangleMask1",
					Source = "Mask",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 385, 82.5 } },
		},
		MediaOut1 = Saver {
			Inputs = {
				Input = Input {
					SourceOp = "Merge1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 550, 82.5 } },
		},
	},
}
```
