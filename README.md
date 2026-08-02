# 01-makehuman

Our MakeHuman wrapper for the body-composition survey: launch script, Python deps, and the batch grid exporter.

Upstream MakeHuman and MHAPI live under `upstream/` (gitignored here; each has its own clone). Local numpy compatibility patches stay in the MakeHuman upstream working tree.

## Setup

```bash
# From this directory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Clone upstreams (once) if missing
mkdir -p upstream
git clone https://github.com/makehumancommunity/makehuman.git upstream/makehuman
git clone https://github.com/makehumancommunity/community-plugins-mhapi.git upstream/mhapi

# Install MHAPI into MakeHuman plugins (copy or symlink)
# cp -R upstream/mhapi/1_mhapi upstream/makehuman/makehuman/plugins/

cd upstream/makehuman/makehuman
python3 download_assets_git.py   # needs Git LFS
```

## Launch

```bash
./launch.sh
```

Runs `upstream/makehuman/makehuman/makehuman.py` with this folder’s `.venv`.

## Batch export

Step-by-step: **[EXPORT-HOWTO.md](EXPORT-HOWTO.md)**

In MakeHuman: Utilities → Scripting → paste `scripts/batch_body_grid.py` → Execute.  
Grid: muscle × fat × gender × 4 ages; Caucasian; bald; age-matched skins.  
Outputs to `../02-media/raw/` (`SMOKE_TEST=True` first).
