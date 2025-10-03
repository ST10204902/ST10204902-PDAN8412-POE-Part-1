# ST10204902 PDAN8412 POE Part 1

The project files (including dataset and processed parquet splits) exceeds GitHub's upload limits. Use the OneDrive link below to retrieve the full submission bundle that reproduces every notebook output. Install the requirements, extract the archive locally, and run the notebook from within the project root.

[OneDrive Link](https://1drv.ms/f/c/99a6b5061266db4c/ElUOjUnAzy1OizGOvFEdBEwBanfMGe4xuoIduSooGQfcEw?e=xxQ9mF)

---

## Project Overview
- Victorian-era authorship attribution on 53,678 prose passages covering 45 authors.
- Spark-based ingestion, cleaning, and stylometric feature engineering with reproducible parquet splits.
- Baseline TF-IDF + SGD classifier plus three TensorFlow sequence models (BiLSTM, attention BiLSTM, convolutional BiGRU).
- Stage flags in `run_me.ipynb` toggle between full retraining and fast-run modes that load cached artifacts.

---

## Required Software
- Python 3.10 (matching the `tf210` environment).
- CUDA-capable GPU (optional but recommended) with compatible drivers.
- TensorFlow 2.10, Keras, and dependencies (handled by `run_me.ipynb`).
- Apache Spark 4 with PySpark bindings.
- Java JDK 17 [Available for Windows here](https://adoptium.net/download?link=https%3A%2F%2Fgithub.com%2Fadoptium%2Ftemurin17-binaries%2Freleases%2Fdownload%2Fjdk-17.0.16%252B8%2FOpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8.msi&vendor=Adoptium) for Spark.
- All other libraries installed by running the notebook at least once in the correct environment. Setup config details are in `run_me.ipynb`.

Launch the notebook inside the configured environment and execute `run_me.ipynb` with the stage flags set according to your needs.

---

## Repository Layout
```
.
├── artifacts/        # cached vocabularies, label maps, feature rankings, validation predictions
├── data/             # raw CSV + processed parquet splits (generated via ensure_dataset.py)
├── models/           # persisted TF-IDF pipeline and Keras checkpoints/histories
├── reports/          # EDA plots/tables and evaluation metrics (JSON/CSV/PNG/GEXF)
├── scripts/
│   └── ensure_dataset.py   # dataset download + pruning helper
├── run_me.ipynb      # primary pipeline notebook (EDA -> feature engineering -> training -> evaluation)
├── requirements.txt  # Python package lock for the tf210 environment
└── README.md
```

---

## Stage Flags (run_me.ipynb)
These toggles appear in the "Configuration" cell. Suggested values assume the OneDrive bundle has been extracted so cached artifacts are available.

| Flag | Purpose | Suggested value (first run with artifacts) |
|------|---------|---------------------------------------------|
| `RUN_EDA` | regenerate Spark EDA tables/plots | `False` |
| `RUN_DATA_PREPROCESSING` | rebuild clean parquet splits | `False` |
| `RUN_FEATURE_ENGINEERING` | refit TextVectorization & chi-square selection | `False` |
| `RUN_MODEL_TRAINING` | retrain baseline + neural models | `False` |
| `RUN_MODEL_EVALUATION` | load metrics, ROC curves, plots | `True` |
| `RUN_MODEL_BILSTM` | include BiLSTM when training is enabled | `False` |
| `RUN_MODEL_ATTENTION_LSTM` | include attention BiLSTM | `False` |
| `RUN_MODEL_BIGRU_CAPSULE` | include convolutional BiGRU | `False` |

Set any flag to `True` if artifacts are missing or you wish to regenerate a stage.


