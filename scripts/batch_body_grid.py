# batch_body_grid.py
# MakeHuman Scripting Console script — Option A body-comp grid exporter
#
# HOW TO RUN:
#   1. Launch MakeHuman (see PLAN.md)
#   2. Hide UI panels as much as possible; set a clean front view
#   3. Utilities → Scripting → paste this file (or load it)
#   4. Set SMOKE_TEST = True for a quick 6-image run first
#   5. Execute tab → Execute
#
# Outputs PNG screenshots to 02-media/raw/ named:
#   m{muscle}_f{fat}_{gender}.png
# e.g. m50_f30_male.png
#
# MakeHuman "Weight" = survey "fat". Values are 0–100 step 5 → API 0.0–1.0.

from __future__ import print_function
import os
import time

# --- config -----------------------------------------------------------------
# Absolute path to this project's media/raw folder (edit if your mount differs)
OUT_DIR = "/Volumes/abdelhag/baseet/body-comp-project/02-media/raw"

# True = only a few combos for QA; False = full 21×21×2 = 882 images
SMOKE_TEST = True

STEP = 5  # muscle/fat grid step (percent)
PAUSE_SEC = 0.15  # let mesh/redraw settle before grab

# Fixed camera (front, full body). Tweak after printCameraInfo() once.
ZOOM = 70.0
ROT_X = 0.0
ROT_Y = 0.0
ROT_Z = 0.0

# Lock non-varying macros so the grid only changes muscle/weight/gender
AGE = 0.5          # adult
HEIGHT = 0.5
PROPORTIONS = 0.5
CAUCASIAN = 1.0
AFRICAN = 0.0
ASIAN = 0.0
# ----------------------------------------------------------------------------

def _ensure_out():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

def _snap_range():
    if SMOKE_TEST:
        # corners + midpoints for quick visual QA
        return [0, 50, 100], [0, 50, 100]
    vals = list(range(0, 101, STEP))
    return vals, vals

def _filename(muscle_pct, fat_pct, gender_name):
    return "m{0}_f{1}_{2}.png".format(int(muscle_pct), int(fat_pct), gender_name)

def _fix_camera():
    MHScript.setRotationX(ROT_X)
    MHScript.setRotationY(ROT_Y)
    MHScript.setRotationZ(ROT_Z)
    MHScript.setZoom(ZOOM)
    MHScript.printCameraInfo()

def _set_body(gender_f, muscle_f, weight_f):
    """gender_f/muscle_f/weight_f in 0.0–1.0"""
    human = gui3d.app.selectedHuman
    # Batch macros once via updateModelingParameters (single applyAllTargets)
    MHScript.updateModelingParameters({
        "macrodetails/Gender": gender_f,
        "macrodetails/Age": AGE,
        "macrodetails/African": AFRICAN,
        "macrodetails/Asian": ASIAN,
        "macrodetails/Caucasian": CAUCASIAN,
        "macrodetails-universal/Muscle": muscle_f,
        "macrodetails-universal/Weight": weight_f,
        "macrodetails-height/Height": HEIGHT,
        "macrodetails-proportions/BodyProportions": PROPORTIONS,
    })

def run_batch():
    _ensure_out()
    muscles, fats = _snap_range()
    genders = [("male", 1.0), ("female", 0.0)]

    _fix_camera()

    total = len(muscles) * len(fats) * len(genders)
    done = 0
    print("BATCH start → {0}  ({1} images, smoke={2})".format(OUT_DIR, total, SMOKE_TEST))

    for gender_name, gender_f in genders:
        for m in muscles:
            for f in fats:
                muscle_f = m / 100.0
                weight_f = f / 100.0
                _set_body(gender_f, muscle_f, weight_f)
                time.sleep(PAUSE_SEC)
                path = os.path.join(OUT_DIR, _filename(m, f, gender_name))
                MHScript.screenShot(path)
                done += 1
                if done % 10 == 0 or done == total:
                    print("  {0}/{1}  last={2}".format(done, total, path))

    print("BATCH done. Wrote {0} PNGs to {1}".format(done, OUT_DIR))
    print("Next: set SMOKE_TEST=False for full grid, then compress in Phase 2.")

run_batch()
