# 🎬 Recommender System – The Evaluator Block

Welcome to our **Evaluator Block** — a project developed as part of the course *MLSMM2156 – Recommender Systems* (UCLouvain, 2021–2022). This module is designed to **evaluate collaborative filtering models** using multiple validation strategies and performance metrics, all built around the [Surprise](https://surprise.readthedocs.io/en/stable/) library.

---

## 👨‍👩‍👧‍👦 Team — Group 5

- **Cyril D.**
- **Hamza E.**
- **Inas N.**
- **Lisa D.**

---

## 🧠 What Is This Project About?

In a recommender system, evaluation is key. This project helps you:
- Run and compare several **baseline models** (e.g., KNN, SVD).
- Use multiple **validation strategies** (random split, leave-one-out, full dataset).
- Compute relevant **recommendation metrics** (MAE, RMSE, Hit Rate, Novelty).
- **Generate and export** daily evaluation reports for tracking progress and experiments.

Everything is modular, reproducible, and designed for extension.

---

## 🗂️ Folder & File Overview

| File / Folder        | Description |
|----------------------|-------------|
| `evaluator.ipynb`    | The main notebook to run evaluations and generate the report. |
| `loaders.py`         | Loads data and exports evaluation results. Contains the `load_ratings()` and `export_evaluation_report()` functions. |
| `models.py`          | Utility functions, including `get_top_n()` to extract Top-N recommendations from predictions. |
| `metrics.py`         | Custom metric implementations: RMSE, Hit Rate, and Novelty. |
| `configs.py`         | Central configuration file for model selection, evaluation strategies, and metric inclusion. |
| `constants.py`       | Global constants such as `RATINGS_SCALE` and `EVALUATION_PATH`. |
| `evaluation/`        | Folder where daily evaluation reports (CSV files) are saved. Example: `evaluation/2025_04_30.csv` |

---

## 🏗️ How Does It Work?

### 1. 📥 Data Loading
- Use the function `load_ratings(surprise_format=True)` (in `loaders.py`).
- It loads a ratings CSV file and, if `surprise_format=True`, converts it into a `surprise.Dataset` using `.load_from_df()` and a `Reader` object.
- The expected column format is: `userID`, `itemID`, `rating`.

### 2. 🧪 Evaluation Strategies (Implemented in `evaluator.ipynb`)
| Strategy | Description | Function |
|---------|-------------|----------|
| **Split** | Random 75% train / 25% test | `generate_split_predictions()` |
| **LOO** | Leave-one-out per user | `generate_loo_top_n()` |
| **Full** | Use entire dataset, no split | `generate_full_top_n()` |

Each strategy evaluates models either on direct predictions or on top-N recommendation quality.

### 3. 📊 Metrics Computed (In `metrics.py`)
| Metric | Type | Description |
|--------|------|-------------|
| **MAE / RMSE** | Split | Standard accuracy metrics from `surprise.accuracy` |
| **Hit Rate** | LOO | Measures if left-out items appear in Top-N |
| **Novelty** | Full | Measures how "unpopular" the recommended items are |

These are plugged into the `available_metrics` dictionary and triggered during evaluation via `create_evaluation_report()`.

### 4. 📝 Report Exporting
Once evaluation is done:
- The report is saved as a CSV file using `export_evaluation_report(df)` in `loaders.py`.
- Files are saved inside the `/evaluation/` folder.
- Naming follows this pattern: `YYYY_MM_DD.csv` (e.g., `2025_04_30.csv`), for easy tracking and versioning.

The export path is defined in `constants.py`:
```python
EVALUATION_PATH = "evaluation/"

## 🔍 Files Modified - Make sure you updated those files

To make the evaluator functional and modular, the following **supporting files** were updated or added. These contain helper functions, constants, configurations, and export logic used by the main notebook.

| File / Folder        | Status       | Purpose and Modifications |
|----------------------|--------------|-----------------------------|
| `loaders.py`         | ✅ Modified  | - Added `surprise_format` parameter to `load_ratings()` to return a Surprise `Dataset` using `Reader` and `.load_from_df()`.<br>- Added `export_evaluation_report(df)` to export reports as `.csv` to `/evaluation/` folder with today's date. |
| `constants.py`       | ✅ Modified  | - Added global constants:<br>```python<br>RATINGS_SCALE = (1, 5)<br>EVALUATION_PATH = "evaluation/"<br>```<br>- These are used in both `loaders.py` and model evaluation logic. |
| `configs.py`         | ✅ Modified  | - Defined baseline models (e.g. KNNBasic, SVD) and their parameters.<br>- Added metric configuration per evaluation type in the `available_metrics` dictionary (e.g., RMSE for split, Hit Rate for LOO, Novelty for full).<br>- Added `top_n_value` setting for top-N recommendations. |
| `models.py`          | ✅ Modified  | - Added utility function:<br>```python<br>def get_top_n(predictions, n=10):<br>    # Extract top-n predictions per user<br>```<br>- Used for generating top-N results in both LOO and full-dataset evaluations. |
| `evaluation/`        | ✅ Created   | - Output directory used to store evaluation reports exported via `export_evaluation_report()`.<br>- Files are automatically named with the current date: `YYYY_MM_DD.csv`. |
