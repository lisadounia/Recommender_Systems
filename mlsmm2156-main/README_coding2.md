# 🎬 Recommender System – The Evaluator Block

This project was developed for the course *MLSMM2156 – Recommender Systems* (UCLouvain, 2021–2022). It implements an **Evaluator Block** to assess collaborative filtering models using the [Surprise](https://surprise.readthedocs.io/en/stable/) library. The system supports multiple evaluation strategies and key performance metrics to compare model quality.

---

## 👥 Team — Group 5

- **Cyril D.**
- **Hamza E.**
- **Inas N.**
- **Lisa D.**

---

## 🧠 Project Goals

The Evaluator Block allows us to:
- Compare baseline recommender models (e.g. KNN, SVD)
- Use different evaluation strategies: random split, leave-one-out (LOO), and full-dataset
- Calculate performance metrics: MAE, RMSE, Hit Rate, and Novelty
- Export evaluation results in structured, dated reports

The system is modular and easily extendable.

---

## 📓 Main Notebook: `evaluator.ipynb`

All evaluation logic is implemented and executed in the Jupyter notebook `evaluator.ipynb`.

This notebook:
- Loads and processes the ratings data
- Triggers the evaluation for all three validation strategies
- Computes the required metrics
- Generates the final evaluation report
- Calls helper functions defined in other Python modules (see below)

> 📌 Make sure to run all cells in `evaluator.ipynb` in sequence to ensure full pipeline execution and report generation.

---

## 🗂️ Supporting Files

To support the evaluation process, the following files were updated or added:

| File            | Status       | Changes Made |
|-----------------|--------------|--------------|
| `loaders.py`    | ✅ Modified  | - Added `surprise_format` parameter to `load_ratings()` using `Reader` and `.load_from_df()`<br>- Implemented `export_evaluation_report(df)` to save `.csv` files in `/evaluation/` |
| `constants.py`  | ✅ Modified  | - Defined:<br>```python<br>RATINGS_SCALE = (1, 5)<br>EVALUATION_PATH = "evaluation/"<br>``` |
| `configs.py`    | ✅ Modified  | - Defined baseline models and parameters<br>- Set `top_n_value`<br>- Registered metrics in `available_metrics` dictionary |
| `models.py`     | ✅ Modified  | - Added:<br>```python<br>def get_top_n(predictions, n=10):<br>    # Extracts top-N recommendations per user<br>``` |
| `evaluation/`   | ✅ Created   | - Folder for exported reports named by date (e.g. `2025_04_30.csv`) |

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
