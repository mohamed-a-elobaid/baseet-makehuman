# batch_body_grid.py
#
# Paste into MakeHuman: Utilities > Scripting, then Execute tab > Execute.
#
# NOTE: MakeHuman runs scripts with exec() inside a function. On Python 3,
# top-level imports and defs are NOT visible inside functions. Put ALL
# imports and helpers inside main().
#
# Output: OUT_DIR/m{muscle}_f{fat}_{gender}_{age}.png
# Example: m50_f30_male_middle.png
#
# -----------------------------------------------------------------------------
# WHY THIS VERSION IS DIFFERENT (fixes the unusable smoke images)
# -----------------------------------------------------------------------------
# The previous script used MHScript.setZoom(70.0) + MHScript.screenShot().
# Two fatal problems:
#   1. MHScript.setZoom() writes straight to OrbitalCamera.zoomFactor, which is
#      CLAMPED to maxZoomFactor=15.0. So 70 -> 15 = maximum zoom-IN = extreme
#      close-ups of skin. (OrbitalCamera zoom: <1.0 = zoom OUT, >1.0 = zoom IN,
#      1.0 = auto-fit to bounding box.)
#   2. MHScript.screenShot() calls mh.grabScreen(1,1,W-3,H-3,path), i.e. it
#      grabs the ENTIRE app window INCLUDING all UI panels and grid chrome.
#
# This version instead:
#   - Drives G.app.modelCamera (OrbitalCamera) directly for a locked front
#     view at a sane zoom (0.9 = full body with a small margin).
#   - Renders OFF-SCREEN via mh2opengl.Render() at a fixed resolution with
#     anti-aliasing and a neutral gray background. No UI in frame, ever.
#     (renderToBuffer temporarily repoints G.windowWidth/Height to the render
#     size, so the camera aspect automatically matches the output image.)
#   - Saves the rendered image from the Rendering > Viewer task.
#   - Falls back to a UI-hidden viewport grab if the GPU lacks render-to-FBO.
# -----------------------------------------------------------------------------

def main():
    import os
    import time
    import gui3d
    import mh
    from core import G

    # --- config ---
    OUT_DIR = "/Volumes/abdelhag/baseet/body-comp-project/02-media/raw"
    SMOKE_TEST = True
    STEP = 5
    PAUSE_SEC = 0.30          # let mesh + camera settle before each render

    # Render output (portrait 2:3 fits a standing full body).
    RENDER_WIDTH = 1024
    RENDER_HEIGHT = 1536
    ANTI_ALIAS = True

    # OrbitalCamera framing. zoomFactor: 1.0 = auto-fit bounding box,
    # <1.0 = zoom out (more margin), >1.0 = zoom in. 0.9 gives a small margin.
    CAMERA_ZOOM = 0.9
    CAMERA_H_ROTATION = 0.0   # 0 = front view
    CAMERA_V_INCLINATION = 0.0  # 0 = level
    CAMERA_TRANSLATION = [0.0, 0.0, 0.0]

    # Body defaults (Caucasian, average height/proportions).
    HEIGHT = 0.5
    PROPORTIONS = 0.5
    CAUCASIAN = 1.0
    AFRICAN = 0.0
    ASIAN = 0.0

    AGE_GROUPS = [
        ("young", 25, "young"),
        ("adult", 35, "middleage"),
        ("middle", 50, "middleage"),
        ("older", 65, "old"),
    ]
    GENDERS = [
        ("male", 1.0),
        ("female", 0.0),
    ]

    mhapi = gui3d.app.mhapi
    human = gui3d.app.selectedHuman
    assets = mhapi.assets
    locations = mhapi.locations
    cam = G.app.modelCamera  # OrbitalCamera

    # --- helpers ---
    def ensure_out_dir():
        if not os.path.isdir(OUT_DIR):
            os.makedirs(OUT_DIR)

    def percent_values():
        if SMOKE_TEST:
            return [1, 50, 100]
        return list(range(1, 101, STEP))

    def make_filename(muscle, fat, gender, age):
        return "m%d_f%d_%s_%s.png" % (int(muscle), int(fat), gender, age)

    def fix_camera():
        # Lock the orbital camera to a front, level, centered, full-body view.
        cam.setHorizontalRotation(CAMERA_H_ROTATION)
        cam.setVerticalInclination(CAMERA_V_INCLINATION)
        try:
            cam.setPosition(CAMERA_TRANSLATION)
        except Exception:
            # setPosition clamps internally; ignore if signature differs.
            pass
        cam.setZoomFactor(CAMERA_ZOOM)
        cam.updateCamera()
        mh.redraw()

    def clear_hair():
        try:
            equipped = assets.getEquippedHair()
            if equipped:
                assets.unequipHair(equipped)
        except Exception as err:
            print("WARN mhapi unequipHair:", err)
        try:
            human.setHairProxy(None)
        except Exception as err:
            print("WARN setHairProxy(None):", err)

    def skin_path(skin_prefix, gender):
        folder = "%s_caucasian_%s" % (skin_prefix, gender)
        filename = "%s_caucasian_%s.mhmat" % (skin_prefix, gender)
        return "data/skins/%s/%s" % (folder, filename)

    def apply_skin(skin_prefix, gender):
        rel = skin_path(skin_prefix, gender)
        try:
            MHScript.setMaterial(rel)
            return
        except Exception as err:
            print("WARN setMaterial relative failed (%s): %s" % (rel, err))
        try:
            abs_path = locations.getSystemDataPath(
                "skins/%s_caucasian_%s/%s_caucasian_%s.mhmat"
                % (skin_prefix, gender, skin_prefix, gender)
            )
            MHScript.setMaterial(abs_path)
        except Exception as err:
            print("WARN setMaterial absolute failed: %s" % err)

    def age_years_to_slider(years):
        years = float(years)
        if years < 25.0:
            return (years - 1.0) / ((25.0 - 1.0) * 2.0)
        return ((years - 25.0) / ((90.0 - 25.0) * 2.0)) + 0.5

    def set_body(gender_value, muscle_value, fat_value, age_years):
        MHScript.updateModelingParameters({
            "macrodetails/Gender": gender_value,
            "macrodetails/Age": age_years_to_slider(age_years),
            "macrodetails/African": AFRICAN,
            "macrodetails/Asian": ASIAN,
            "macrodetails/Caucasian": CAUCASIAN,
            "macrodetails-universal/Muscle": muscle_value,
            "macrodetails-universal/Weight": fat_value,
            "macrodetails-height/Height": HEIGHT,
            "macrodetails-proportions/BodyProportions": PROPORTIONS,
        })

    def get_viewer():
        try:
            return gui3d.app.getCategory('Rendering').getTaskByName('Viewer')
        except Exception as err:
            print("WARN could not get Rendering/Viewer:", err)
            return None

    def render_offscreen(out_path):
        # Off-screen render via FBO: no UI, fixed resolution, AA, gray bg.
        import mh2opengl
        settings = {
            "scene": G.app.scene,
            "AA": ANTI_ALIAS,
            "dimensions": (RENDER_WIDTH, RENDER_HEIGHT),
            "lightmapSSS": False,
        }
        mh2opengl.Render(settings)
        viewer = get_viewer()
        if viewer is None or viewer.image is None:
            raise RuntimeError("Viewer image not available after render")
        viewer.image.save(out_path)

    def hide_docks():
        # Best-effort: hide QDockWidget panels so a fallback grab is cleaner.
        hidden = []
        try:
            mainwin = G.app.mainwin
            for child in list(mainwin.children()):
                try:
                    from PyQt5.QtWidgets import QDockWidget
                except Exception:
                    break
                if isinstance(child, QDockWidget) and child.isVisible():
                    child.hide()
                    hidden.append(child)
        except Exception as err:
            print("WARN hide_docks:", err)
        return hidden

    def show_docks(hidden):
        for child in hidden:
            try:
                child.show()
            except Exception:
                pass

    def grab_viewport(out_path):
        # Fallback when render-to-FBO is unavailable. Hides UI first.
        hidden = hide_docks()
        try:
            mh.redraw()
            time.sleep(0.1)
            w = G.windowWidth
            h = G.windowHeight
            mh.grabScreen(0, 0, w, h, out_path)
        finally:
            show_docks(hidden)

    def save_image(out_path):
        if mh.hasRenderToRenderbuffer():
            render_offscreen(out_path)
        else:
            print("WARN no render-to-FBO; falling back to viewport grab")
            grab_viewport(out_path)

    # --- run ---
    ensure_out_dir()
    muscles = percent_values()
    fats = percent_values()
    clear_hair()
    fix_camera()

    total = len(muscles) * len(fats) * len(GENDERS) * len(AGE_GROUPS)
    done = 0
    age_labels = [item[0] for item in AGE_GROUPS]

    print("BATCH out=%s" % OUT_DIR)
    print(
        "smoke=%s step=%s total=%s ages=%s render=%dx%d AA=%s zoom=%.2f"
        % (SMOKE_TEST, STEP, total, age_labels,
           RENDER_WIDTH, RENDER_HEIGHT, ANTI_ALIAS, CAMERA_ZOOM)
    )
    print("render-to-FBO available: %s" % mh.hasRenderToRenderbuffer())

    for age_name, age_years, skin_prefix in AGE_GROUPS:
        for gender_name, gender_value in GENDERS:
            apply_skin(skin_prefix, gender_name)
            clear_hair()
            for muscle in muscles:
                for fat in fats:
                    set_body(
                        gender_value,
                        muscle / 100.0,
                        fat / 100.0,
                        age_years,
                    )
                    # Re-fit the orbital camera to the new bounding box,
                    # then re-assert our locked framing (zoom/rotation).
                    cam.updateCamera()
                    fix_camera()
                    time.sleep(PAUSE_SEC)

                    out_path = os.path.join(
                        OUT_DIR,
                        make_filename(muscle, fat, gender_name, age_name),
                    )
                    try:
                        save_image(out_path)
                    except Exception as err:
                        print("ERR saving %s: %s" % (out_path, err))
                        # Last-resort: viewport screenshot so the cell isn't blank.
                        try:
                            MHScript.screenShot(out_path)
                        except Exception as err2:
                            print("ERR fallback screenShot failed: %s" % err2)

                    done += 1
                    if done % 10 == 0 or done == total:
                        print(
                            "%d/%d %s"
                            % (done, total, os.path.basename(out_path))
                        )

    print("DONE wrote %d PNGs to %s" % (done, OUT_DIR))
    if SMOKE_TEST:
        print("QA smoke images, then set SMOKE_TEST=False and run again.")
    else:
        print("Full grid finished. Next: compress to webp (Phase 2).")


main()
