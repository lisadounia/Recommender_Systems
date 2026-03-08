# Movie Recommender System

A modular movie recommendation system built on the **MovieLens dataset**, combining multiple recommendation approaches and deployed through an **interactive Streamlit application**.  
The project compares different algorithms and evaluates their performance using standard recommender system metrics.

---

## Demo


[![Watch the demo](https://img.youtube.com/vi/qFKSxxUZ-hM/0.jpg)](https://youtu.be/qFKSxxUZ-hM)

---

## Key Features

- Personalized movie recommendations
- Multiple recommendation algorithms
- Interactive web interface
- Modular Python architecture
- Evaluation using standard recommender system metrics

---

## Models Implemented

**User-Based Collaborative Filtering**
- KNNWithMeans (MSD similarity)
- Custom implementation using Jaccard similarity

**Content-Based Filtering**
- Uses movie metadata (genres, genome tags, release year)
- Ridge regression for rating prediction

**Latent Factor Model**
- Matrix factorization (FunkSVD)
- Implemented with the Surprise library

The **latent factor model achieved the best predictive performance** with an RMSE of **0.797**.

---

## Evaluation Metrics

Models were evaluated using:

- RMSE
- MAE
- Hit Rate
- Novelty
- Diversity

---

## Tech Stack

- Python
- scikit-learn
- Surprise
- Pandas
- Streamlit

---

## Project Structure

```text
app.py          # Streamlit interface
models.py       # Model training
recs.py         # Recommendation generation
evaluator.py    # Model evaluation
metrics.py      # Diversity metrics
loaders.py      # Data loading
configs.py      # Model configuration
constants.py    # Global constants
analytics.py    # Dataset statistics
```

--

## Authors

**Group 5 – UCLouvain**

- C. Demolin  
- L. Dounia  
- H. En-Naimi  
- I. Nanat  

Course: **MLSMM2156 – Recommender Systems**  
