# Fusion Composition Programming Guide — Design Spec

## Purpose

Create a comprehensive reference document (`FUSION_COMP_GUIDE.md`) that enables an LLM agent to programmatically author valid DaVinci Resolve Fusion `.comp` files. The guide covers the full Fusion toolkit: grammar, tool reference, expression syntax, and complete working templates.

## Audience

LLM agents operating via the MCP server. Not a human tutorial — optimized for machine consumption with precise syntax, complete examples, and explicit rules.

## Deliverable

A single markdown file at `resolve-tool/FUSION_COMP_GUIDE.md`, served as MCP resource `resolve://fusion-comp-guide`. No changes to existing tools, resources, or documentation.

---

## Document Structure

The guide uses a **layered architecture**: compact grammar rules up front (always useful), categorized tool reference in the middle (lookup as needed), template library at the end (copy and modify).

### Part 1: Grammar & Rules

#### 1.1 Overview
- `.comp` files are plain-text Lua table definitions
- Used for Fusion compositions in DaVinci Resolve
- Same syntax as `.setting` files (macros/presets)

#### 1.2 File Structure
The canonical `.comp` skeleton:

```lua
Composition {
    CurrentTime = 0,
    RenderRange = { 0, 100 },
    Tools = {
        ToolName = ToolType {
            Inputs = { ... },
            ViewInfo = OperatorInfo { Pos = { x, y } },
        },
    },
}
```

Cover:
- Top-level `Composition {}` wrapper and its keys (`CurrentTime`, `RenderRange`, `GlobalRange`, `Tools`)
- Tool definition pattern: `InstanceName = ToolType { Inputs = {}, ViewInfo = ... }`
- The `ordered()` function (Fusion-specific Lua extension for preserving key order)
- MediaIn/MediaOut in Resolve context: `MediaIn1 = Loader { ... }`, `MediaOut1 = Saver { ... }`
- Bracket notation for dotted input names: `["Gamut.SLogVersion"]`

#### 1.3 Input Types
Six forms of `Input {}`:

| Form | Syntax | Use |
|------|--------|-----|
| Static value | `Input { Value = 1920 }` | Constants |
| Connection | `Input { SourceOp = "Name", Source = "Output" }` | Node links |
| Expression | `Input { Expression = "time / 30" }` | Per-frame dynamic values |
| FuID | `Input { Value = FuID { "Screen" } }` | Enum/dropdown values |
| Point | `Input { Value = { 0.5, 0.5 } }` | 2D positions |
| Gradient | `Input { Value = Gradient { Colors = { [0] = {R,G,B,A}, ... } } }` | Color gradients |

Plus: `Disabled = true` for inactive inputs.

#### 1.4 Connection Rules
- Connections use `SourceOp` (source tool name) + `Source` (output port name)
- Standard output port names:
  - `"Output"` — image output from most tools
  - `"Mask"` — from mask tools (RectangleMask, EllipseMask, etc.)
  - `"SceneOutput"` — from 3D tools
  - `"MaterialOutput"` — from material tools
  - `"Value"` — from modifiers (BezierSpline, etc.)
- Effect masks connect via the `EffectMask` input name

#### 1.5 Expression Syntax
Variables:
- `time` — current frame number
- `comp.RenderStart`, `comp.RenderEnd` — composition frame range
- `comp.HiQ` — high quality mode boolean

Functions:
- `iif(condition, true_val, false_val)` — inline conditional
- Full Lua math: `abs`, `floor`, `ceil`, `min`, `max`, `sin`, `cos`, `tan`, `sqrt`, `pow`, `exp`, `log`, `random`, `pi`
- `Point(x, y)` — construct point value
- `deg(x)`, `rad(x)` — degree/radian conversion

References:
- `ToolName.InputName` — reference another tool's value
- `ToolName.InputName.X` / `.Y` — sub-components of Point
- `comp:GetPrefs("Comp.FrameFormat.Rate")` — frame rate

Common patterns table:
- Linear ramp: `time / duration`
- Ease in: `(time / duration) ^ 2`
- Normalized progress: `(time - comp.RenderStart) / (comp.RenderEnd - comp.RenderStart)`
- Conditional ramp: `iif(time < N, time / N, 1.0)`
- Fade in + out: `iif(time < N, time/N, iif(time > (comp.RenderEnd - N), (comp.RenderEnd - time)/N, 1.0))`

#### 1.6 Keyframe / BezierSpline Syntax
Modifiers are defined as sibling entries in the `Tools` table, referenced via `SourceOp`/`Source = "Value"`:

```lua
-- Tool references the modifier:
Blend = Input { SourceOp = "Blend_Anim", Source = "Value" },

-- Modifier definition (sibling of tools):
Blend_Anim = BezierSpline {
    SplineColor = { Red = 225, Green = 0, Blue = 225 },
    KeyFrames = {
        [0] = { 0.0, RH = { 10, 0.0 } },
        [30] = { 1.0, LH = { 20, 1.0 } },
    },
}
```

Keyframe entry: `[frame] = { value, LH = {x,y}, RH = {x,y}, Flags = { Linear = true } }`

Also cover `LUTBezier` for lookup-table splines (particle size-over-life, etc.).

#### 1.7 Data Types
- Points: `{ x, y }` in inputs, `Point(x, y)` in expressions
- Colors in inputs: separate `TopLeftRed`, `TopLeftGreen`, `TopLeftBlue`, `TopLeftAlpha` keys (0.0–1.0)
- Colors in tile metadata: `{ R = 0.278, G = 0.509, B = 0.290 }` (0.0–1.0)
- SplineColor: `{ Red = 225, Green = 0, Blue = 225 }` (0–255)
- Gradient colors: `{ R, G, B, A }` keyed by position 0.0–1.0
- FuID: `FuID { "StringValue" }` for enum dropdowns

---

### Part 2: Tool Reference

Categorized reference. Each tool gets: internal ID, key inputs with types/defaults, and a minimal 3–5 line usage snippet. High-use tools get full input tables; rare tools get ID + one-liner.

#### Full-depth coverage (complete input tables + snippet):
1. **I/O** — `Loader` (MediaIn), `Saver` (MediaOut)
2. **Generators** — `Background` (Type, Width, Height, color inputs)
3. **Composite** — `Merge` (Background, Foreground, Blend, ApplyMode with full mode table, Operator modes, Center, Size, Angle, EffectMask)
4. **Text** — `TextPlus` (StyledText, Font, Style, Size, Center, layout, shading elements 1–8 with Opacity/Thickness/Softness/Offset, UseFrameFormatSettings)
5. **Transform** — `Transform` (Center, Pivot, Size, Aspect, Angle, Flip, Edges)
6. **Blur/Filter** — `Blur` (XBlurSize, YBlurSize), `DirectionalBlur`, `Glow` (Gain, GlowSize), `SoftGlow`
7. **Color** — `BrightnessContrast` (Gain, Brightness, Contrast, Gamma, Saturation, Lift), `ColorCorrector`
8. **Masks** — `RectangleMask`, `EllipseMask` (Center, Width, Height, Angle, SoftEdge, Level, CornerRadius)
9. **Matte/Keying** — `DeltaKeyer`, `MatteControl`
10. **Particle System** — `pEmitter` (Number, Lifespan, Velocity, Angle, style/region), `pRender`, `pDirectionalForce`, `pTurbulence`, `pBounce`, `pSpawn`, `pKill`
11. **CustomTool** — Image inputs (c1–c3, m1), numeric inputs (n1–n8), point inputs (p1–p4), setup/intermediate/channel expressions, pixel sampling functions

#### Light-depth coverage (ID + one-liner + key inputs only):
12. **Effects** — `Highlight`, `Shadow`, `Rays`, `Trails`, `Duplicate`, `HotSpot`, `PseudoColor`
13. **Warp** — `Displace`, `CornerPositioner`, `GridWarp`, `LensDistort`, `Drip`, `Vortex`, `Dent`
14. **Additional Blur/Filter** — `Defocus`, `Sharpen`, `UnsharpMask`, `VariBlur`, `ErodeDilate`
15. **Additional Color** — `ColorCurves`, `ColorGain`, `ColorMatrix`, `ColorSpace`, `Gamut`, `HueCurves`, `WhiteBalance`
16. **Additional Generators** — `FastNoise`, `Plasma`, `Mandelbrot`, `DaySky`
17. **3D** — `Shape3D`, `Merge3D`, `Camera3D`, `Renderer3D`, lights (`AmbientLight`, `DirectionalLight`, `PointLight`, `SpotLight`), materials (`MtlBlinn`, `MtlPhong`), textures (`Texture2D`, `BumpMap`)
18. **Shape (Vector)** — `sRectangle`, `sEllipse`, `sNGon`, `sStar`, `sMerge`, `sRender`, `sTransform`, `sOutline`, `sExpand`
19. **LUT** — `FileLUT`, `LUTCubeApply`
20. **Misc** — `ChangeDepth`, `TimeSpeed`, `TimeStretcher`, `PipeRouter`, `Tracker`, `Paint`

#### Merge ApplyMode Table
Full table of blend modes with FuID strings:

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

Operator modes: `Over`, `In`, `Held Out`, `Atop`, `XOr`

---

### Part 3: Template Library

Complete, working `Composition { Tools = { ... } }` blocks. Each template has:
- Brief description (1–2 lines)
- `-- MODIFY:` comments on values the LLM should change
- Sensible defaults that work at any resolution (using `UseFrameFormatSettings = 1` and `comp.RenderEnd` expressions)

#### Transitions (6 templates)
1. **Fade in from color** — Background + Merge with Blend expression ramp. Modify: color, duration frames
2. **Fade out to color** — Same pattern, reverse expression. Modify: color, duration frames
3. **Dip to color** — Combined in + out with midpoint. Modify: color, ramp frames
4. **Cross dissolve from transparent** — Background (alpha=0) + Merge blend ramp. Modify: duration
5. **Blur out** — Blur with expression-driven XBlurSize. Modify: blur size, duration
6. **Blur in with fade** — Blur (decreasing) + Merge blend (increasing). Modify: blur size, duration

#### Text & Titles (3 templates)
7. **Simple text overlay** — TextPlus → Merge over MediaIn. Modify: text, font, size, position, color
8. **Lower third with bar** — Background + RectangleMask + TextPlus → Merge. Modify: text, bar color/position/size, font
9. **Animated text fade** — TextPlus → Merge with Blend expression. Modify: text, font, fade duration

#### Color Effects (3 templates)
10. **Vignette** — BrightnessContrast with EllipseMask (inverted, soft edge). Modify: darkening amount, mask size/softness
11. **Desaturation sweep** — BrightnessContrast with animated Saturation expression. Modify: timing, target saturation
12. **Glow/bloom** — Glow → Merge in Screen mode over original. Modify: glow size, gain, blend

#### Motion/Transform (3 templates)
13. **Ken Burns** — Transform with expression-driven Center and Size for slow zoom/pan. Modify: start/end position, start/end zoom, duration
14. **Picture-in-picture** — Transform (scale down + reposition) → Merge over MediaIn. Modify: size, position, border
15. **Zoom blur transition** — DirectionalBlur with expression. Modify: blur amount, duration

#### Generators (2 templates)
16. **Animated noise background** — FastNoise with expression-driven parameters. Modify: scale, color, speed
17. **Solid with gradient** — Background with gradient type. Modify: colors, direction

#### Particles (1 template)
18. **Simple particle burst** — pEmitter → pRender. Modify: count, lifespan, velocity, color, size

#### Composite (2 templates)
19. **Green screen key** — DeltaKeyer → Merge over new background. Modify: key color, spill suppression
20. **Masked overlay** — Merge with RectangleMask as EffectMask. Modify: mask position/size/softness

---

## Quality Rules

1. Every template must be a syntactically valid `.comp` file that Fusion can parse
2. All templates use `UseFrameFormatSettings = Input { Value = 1 }` where applicable (resolution-independent)
3. Time-based expressions use `comp.RenderEnd`/`comp.RenderStart` rather than hardcoded frame counts where possible
4. `MediaIn1 = Loader` / `MediaOut1 = Saver` naming convention for Resolve compatibility
5. `ViewInfo` positions are laid out left-to-right following signal flow
6. No `ordered()` in the Tools table (not required for `.comp` files, only `.setting`)
7. Templates should work as-is — an LLM can use them directly with only `-- MODIFY:` values changed

## Out of Scope

- MCP tool API usage (covered by existing `MCP_TOOLS.md`)
- Fuse development (custom plugin authoring with the Fuse SDK)
- Fusion Studio standalone workflows
- Python scripting API for Fusion (covered by `resolve_lib` docs)
- Interactive Fusion page UI workflows
- `.setting` file specifics (macros, GroupOperator, MacroOperator, InstanceInput/InstanceOutput)

## File Location & Serving

- **File**: `resolve-tool/FUSION_COMP_GUIDE.md`
- **MCP resource**: `resolve://fusion-comp-guide`
- **Registration**: Add to `resolve-tool/src/resolve_mcp/server.py` alongside existing `resolve://guide`
