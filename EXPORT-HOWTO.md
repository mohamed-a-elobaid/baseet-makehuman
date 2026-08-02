# How to export body images

Do not edit MakeHuman source. Run `scripts/batch_body_grid.py` inside the app.

## What changed (v2 — usable images)

The first attempt produced unusable close-ups with UI chrome. Two root causes,
both fixed in `scripts/batch_body_grid.py`:

1. **Zoom was wrong.** `MHScript.setZoom(70.0)` writes to
   `OrbitalCamera.zoomFactor`, which is **clamped to `maxZoomFactor=15.0`**.
   So 70 became 15 = maximum zoom-IN = skin close-ups. `OrbitalCamera` zoom is
   the opposite of what the old `setZoom` docstring implies:
   `< 1.0` = zoom **out** (more margin), `1.0` = auto-fit bounding box,
   `> 1.0` = zoom **in**. The script now drives `G.app.modelCamera` directly
   at `CAMERA_ZOOM = 0.9` (full body + small margin).

2. **Screenshot grabbed the whole window.** `MHScript.screenShot()` calls
   `mh.grabScreen(1, 1, W-3, H-3, path)` — the entire app window including UI
   panels and grid. The script now renders **off-screen** with
   `mh2opengl.Render()` at a fixed resolution (1024×1536 portrait) with
   anti-aliasing and a neutral gray background. `renderToBuffer` temporarily
   repoints `G.windowWidth/Height` to the render size, so the camera aspect
   automatically matches the output image. The rendered image is saved from
   the **Rendering > Viewer** task. A UI-hidden viewport grab is used as a
   fallback only if the GPU lacks render-to-FBO.

### Tuning knobs (top of `main()`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `RENDER_WIDTH / RENDER_HEIGHT` | 1024 × 1536 | Off-screen render size (portrait 2:3). Raise for sharper, lower for speed. |
| `ANTI_ALIAS` | `True` | 2× supersampling AA. Disable to ~4× the render speed. |
| `CAMERA_ZOOM` | `0.9` | OrbitalCamera zoom factor. `1.0` = tight fit, `<1.0` = more margin, `>1.0` = zoom in. |
| `CAMERA_H_ROTATION` | `0.0` | Horizontal orbit (0 = front, 90 = left, 180 = back). |
| `CAMERA_V_INCLINATION` | `0.0` | Vertical tilt (0 = level, + = from above, − = from below; clamped to ±90). |
| `CAMERA_TRANSLATION` | `[0,0,0]` | Pan offset, clamped to ±1 of the bounding box. |
| `PAUSE_SEC` | `0.30` | Settle time before each render. Increase if frames look half-updated. |

## Sources used for the script API

| API | Used for | Source |
|-----|----------|--------|
| `G.app.modelCamera` (OrbitalCamera) | Locked front camera, zoom, framing | `lib/camera.py` |
| `cam.setHorizontalRotation / setVerticalInclination / setZoomFactor / setPosition / updateCamera` | Camera control | `lib/camera.py` |
| `mh2opengl.Render(settings)` | Off-screen render (no UI, AA, gray bg) | `plugins/4_rendering_opengl/mh2opengl.py` |
| `mh.renderToBuffer / hasRenderToRenderbuffer` | FBO render + capability check | `lib/glmodule.py` |
| `gui3d.app.getCategory('Rendering').getTaskByName('Viewer').image.save` | Save rendered image | `plugins/4_rendering_9_viewer.py` |
| `MHScript.updateModelingParameters` | Gender/age/muscle/weight in one apply | Built-in `plugins/7_scripting.py` |
| `MHScript.setMaterial` | Caucasian skins (`data/skins/.../*.mhmat`) | Same |
| `gui3d.app.mhapi.assets` | Unequip hair | [MHAPI assets](https://github.com/makehumancommunity/community-plugins-mhapi) |
| `gui3d.app.mhapi.locations` | Absolute skin path fallback | Same |
| `human.setGender` convention | `0.0` female, `1.0` male | `apps/human.py` |

Context7 library: `/makehumancommunity/makehuman`
Community modeling docs: [Modeling the body](https://static.makehumancommunity.org/makehuman/docs/modeling_the_body.html)

## Grid

| Axis | Values |
|------|--------|
| Gender | male, female |
| Muscle | 1-100 |
| Fat | 1-100 (Weight slider) |
| Age | young 25, adult 35, middle 50, older 65 |

Fixed: Caucasian, average height/proportions, no hair, age-matched skin.

Filename: `m50_f30_male_middle.png`

| Mode | Approx images |
|------|----------------|
| Smoke | 72 |
| `STEP=5` | 3200 |
| `STEP=1` | 80000 |

## Run

```bash
cd /Volumes/abdelhag/baseet/body-comp-project/01-makehuman
./launch.sh
```

1. Copy **all** of `scripts/batch_body_grid.py` (must include `def main():` through `main()`)
2. MakeHuman: **Utilities > Scripting** > paste (replace any old text first)
3. Keep `SMOKE_TEST = True` inside `main()`
4. **Execute** tab > **Execute**
5. Check `/Volumes/abdelhag/baseet/body-comp-project/02-media/raw/`

The script prints `render-to-FBO available: True/False`. If `True` (expected on
modern GPUs), each image is a clean 1024×1536 render on a gray background. If
`False`, it falls back to hiding dock panels and grabbing the viewport.

If you see `ensure_out_dir is not defined`: the old script used top-level
functions. MakeHuman's `exec()` breaks that on Python 3. Use the current file
(everything inside `main()`).

After QA: set `SMOKE_TEST = False`, keep `STEP = 5`, Execute again.

## Smoke QA

- No hair
- Caucasian skin looks normal
- Male/female differ
- Muscle and fat extremes look different
- **Full body in frame** (head to feet, small margin) — the main fix
- **No UI panels / grid chrome** in the image — the main fix
- Consistent framing across all 72 images
- Neutral gray background

If framing is too tight/loose, adjust `CAMERA_ZOOM` (lower = more margin).
If you want a different angle, change `CAMERA_H_ROTATION` / `CAMERA_V_INCLINATION`.
