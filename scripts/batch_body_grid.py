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


def main():
    import os
    import time
    import gui3d

    # --- config ---
    OUT_DIR = "/Volumes/abdelhag/baseet/body-comp-project/02-media/raw"
    SMOKE_TEST = True
    STEP = 5
    PAUSE_SEC = 0.12

    ZOOM = 70.0
    ROT_X = 0.0
    ROT_Y = 0.0
    ROT_Z = 0.0

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
        MHScript.setRotationX(ROT_X)
        MHScript.setRotationY(ROT_Y)
        MHScript.setRotationZ(ROT_Z)
        MHScript.setZoom(ZOOM)

    def clear_hair():
        try:
            equipped = assets.getEquippedHair()
            if equipped:
                assets.unequipHair(equipped)
                return
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
        "smoke=%s step=%s total=%s ages=%s"
        % (SMOKE_TEST, STEP, total, age_labels)
    )

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
                    time.sleep(PAUSE_SEC)
                    out_path = os.path.join(
                        OUT_DIR,
                        make_filename(muscle, fat, gender_name, age_name),
                    )
                    MHScript.screenShot(out_path)
                    done += 1
                    if done % 25 == 0 or done == total:
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
