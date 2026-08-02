# How to export body images

Do not edit MakeHuman source. Run `scripts/batch_body_grid.py` inside the app.

## Sources used for the script API

| API | Used for | Source |
|-----|----------|--------|
| `MHScript.screenShot` | PNG capture | Built-in `7_scripting.py` |
| `MHScript.setMaterial` | Caucasian skins | Same (`data/skins/.../*.mhmat`) |
| `MHScript.updateModelingParameters` | Gender/age/muscle/weight in one apply | Same (faster than one-by-one) |
| `gui3d.app.mhapi.assets` | Unequip hair | [MHAPI assets](https://github.com/makehumancommunity/community-plugins-mhapi) / Context7 `/makehumancommunity/makehuman` |
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
| Smoke | 24 |
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

If you see `ensure_out_dir is not defined`: the old script used top-level functions. MakeHuman's `exec()` breaks that on Python 3. Use the current file (everything inside `main()`).

After QA: set `SMOKE_TEST = False`, keep `STEP = 5`, Execute again.

## Smoke QA

- No hair
- Caucasian skin looks normal
- Male/female differ
- Muscle and fat extremes look different
- Framing consistent
