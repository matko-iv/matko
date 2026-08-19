# Run the Vrijeme pipeline on a clean Windows PC

This guide starts with a Windows 11 computer that has no development tools
installed. It covers the safe, fast forecast-only run first, then optional GPU
training and the DGMR/ITALIAMETEO calibration workflow.

## 1. What the new PC needs

For a normal `--skip-training` forecast:

- Windows 11, internet access, and roughly 2 GB free disk space.
- No GPU is required. Saved production models are included in the repository.
- The checkout contains about 300 MB of models and about 300 MB of historical
  CSV data.

For full retraining:

- 16 GB RAM is recommended.
- An NVIDIA GPU with a current NVIDIA driver is strongly recommended.
- Keep at least 5 GB free for temporary artifacts and model snapshots.

The DGMR radar archive is not part of this repository. The full replay needs
the prepared archive (normally `F:\dgmr_train_s11`) and the separate
`budva-radar` repository. The lighter ITALIAMETEO lead calibration needs only
the approximately 1 MB replay cases CSV produced by that full replay.

## 2. Install Git, Python, and optional Node.js

Open PowerShell. The following commands use `winget`, which is included with
current Windows 11 installations:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id OpenJS.NodeJS.LTS -e
```

Node.js is optional; it is used only for the browser/nowcast JavaScript test.
Close PowerShell after installation and open a new PowerShell window so the new
programs are added to `PATH`.

Verify the installations:

```powershell
git --version
py -3.12 --version
node --version
```

If `winget` is unavailable, install Git for Windows, 64-bit Python 3.12, and
optionally Node.js LTS from their official websites. During the Python install,
enable **Add Python to PATH**.

## 3. Clone the complete repository

Choose a folder with enough free space:

```powershell
New-Item -ItemType Directory -Force C:\Weather | Out-Null
Set-Location C:\Weather
git clone https://github.com/matko-iv/vrijeme.git
Set-Location C:\Weather\vrijeme
```

Confirm that the saved production model metadata exists:

```powershell
Test-Path .\trained_models_v2\training_results.json
Test-Path .\trained_models_v2\onset_hazard.json
Test-Path .\wu_data\merged_observations.csv
```

All three commands should print `True`. If model files are missing, do not use
`--skip-training`; obtain a complete clone/artifact copy first.

## 4. Create an isolated Python environment

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`Set-ExecutionPolicy -Scope Process` affects only the current PowerShell
window. Each new terminal must activate `.venv` again.

## 5. Run deterministic checks before forecasting

First force CPU mode. This verifies model loading and actual fit/predict backend
operation without depending on GPU drivers:

```powershell
python forecast_48h_v3.py --cpu --check-device
python -m unittest test_forecast_core
python test_gemini_narrative.py
python test_narrative_variants.py
```

If Node.js was installed, also run:

```powershell
node test_nowcast_hourly.js
```

Do not continue if the Python tests fail or model artifacts cannot be loaded.

## 6. Generate a forecast without retraining

This is the recommended first real run on a new PC:

```powershell
$env:FC_DEVICE = 'cpu'
python forecast_48h_v3.py --cpu --skip-training
```

This downloads current Open-Meteo forecasts, loads the checked-in trained
models, and writes:

- `forecast_output\forecast_48h.json`
- `forecast_output\forecast_48h.csv`

Validate the result:

```powershell
$forecast = Get-Content .\forecast_output\forecast_48h.json -Raw | ConvertFrom-Json
$forecast.generated
$forecast.hourly_forecast.Count
$forecast.hourly_forecast | Select-Object -First 3 datetime,rain_signal,rain_onset_signal,rain_onset_hazard
```

The hourly count should be 48. A missing optional API key must not prevent the
core forecast: without Gemini the pipeline uses deterministic narratives, and
without a WU API key it skips the live-station nowcast.

## 7. Optional API keys and SKALA input

Set optional keys only in the PowerShell session that needs them:

```powershell
$env:GEMINI_API_KEY = 'your-key'
$env:WU_API_KEY = 'your-weather-underground-key'
$env:WU_STATION_ID = 'IBUDVA5'
```

Do not put keys in source files or commit them to Git.

SKALA is optional. The pipeline reads a recent `docs\radar_status.json`. Copy or
sync that file from the `budva-radar` pipeline before running the forecast. If
the file is absent or stale, the +48 h forecast still runs and simply omits
SKALA support.

## 8. Optional NVIDIA GPU setup and full retraining

Install the current NVIDIA driver for the GPU, restart Windows, then verify:

```powershell
nvidia-smi
.\.venv\Scripts\Activate.ps1
python forecast_48h_v3.py --gpu --check-device
```

The second command must complete real XGBoost, CatBoost, and LightGBM
fit/predict probes. Seeing the GPU in Task Manager or `nvidia-smi` alone is not
proof that model training uses it. If the probe fails, use CPU inference and fix
the reported backend before attempting training.

Full training overwrites artifacts in `trained_models_v2`. Create a new Git
branch first and ensure unrelated local work is committed or backed up:

```powershell
git switch -c local-retrain
$env:FC_DEVICE = 'cuda'
$env:FC_GPU_ID = '0'
$env:FC_TRIALS = '15'
python forecast_48h_v3.py --gpu
```

`FC_TRIALS=15` is a quicker experimental retrain. Use `FC_TRIALS=50` for the
full production search. Do not add `--aux-diagnostics` unless the extra
CatBoost/LightGBM/Ridge diagnostic candidates are explicitly needed.

After training, run all tests again and independently check that
`forecast_output\forecast_48h.json` was regenerated. Training completion and
forecast-output completion are separate checks.

## 9. Reproduce the DGMR/ITALIAMETEO comparison

### Fast lead calibration without rereading radar

Copy these two files from the PC that completed the radar replay:

- `analysis_output\dgmr_archive_replay_20260814_cases.csv`
- `fit_italiameteo_dgmr_lead_calibration.py`

Then run:

```powershell
python fit_italiameteo_dgmr_lead_calibration.py
```

The script downloads ITALIAMETEO forecasts at approximate forecast-age anchors
of 0, 24, and 48 hours, uses 2025 for chronological fitting/threshold selection,
uses 2026 as the untouched test period, and writes:

`analysis_output\italiameteo_dgmr_lead_calibration.json`

This is a small CPU/network job and does not access the 30 GB radar archive.

### Full DGMR replay

The full replay additionally requires:

- Prepared shards and manifests in `F:\dgmr_train_s11`.
- A local clone of `budva-radar` containing `nowcast.py` and `tracking.py`.

Example layout:

```text
C:\Weather\vrijeme
C:\Weather\budva-radar
F:\dgmr_train_s11\dataset_manifest.json
F:\dgmr_train_s11\frames_manifest.json
F:\dgmr_train_s11\budva-000000.tar ...
```

Run it explicitly only when the approximately 30 GB sequential read and long
runtime are intended:

```powershell
python verify_dgmr_archive_signals.py `
  --archive F:\dgmr_train_s11 `
  --radar-repo C:\Weather\budva-radar
```

Use `--limit 100` first for a bounded smoke test. The replay is CPU and storage
work; it does not use the GPU.

## 10. Check and stop processes safely

After any command returns, check for remaining Python processes:

```powershell
Get-Process python,python3 -ErrorAction SilentlyContinue |
  Select-Object Id,ProcessName,Path,StartTime
```

If a specific failed run remains, stop only the confirmed process ID:

```powershell
Stop-Process -Id 12345
```

Replace `12345` with the exact ID shown by the read-only check. Do not terminate
all Python processes blindly on a computer that may be running unrelated work.

## 11. Common failures

- `python` or `git` is not recognized: reopen PowerShell after installation.
- `Activate.ps1 cannot be loaded`: run the process-scoped execution-policy
  command from section 4, then activate again.
- Saved model file missing: make sure the complete repository and
  `trained_models_v2` directory were cloned; do not retrain merely to repair an
  incomplete copy.
- Open-Meteo request fails: verify internet access and retry later; preserve the
  previous valid forecast rather than publishing a partial result.
- GPU check fails: use `--cpu --skip-training` for forecasting. Do not assume
  CUDA is active from a configuration flag alone.
- LightGBM model format error: do not edit or line-ending-convert model `.txt`
  files. The repository's `trained_models_v2\.gitattributes` protects them.
- Only 0/24/48-hour historical ITALIAMETEO scores exist before April 2026:
  Open-Meteo fixed-offset previous runs support those anchors, while exact
  individual model runs for all hourly leads are available only from April
  2026 onward. Do not present interpolated +1...+48 calibration as exact
  lead-by-lead validation.
