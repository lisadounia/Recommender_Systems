import random as rd
from collections import defaultdict
from surprise import PredictionImpossible
from loaders import load_ratings
from constants import Constant
import pandas as pd

# Fonction utilitaire pour extraire le top-N des prédictions par utilisateur
def get_top_n(predictions, n):
    rd.seed(0)
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))
    for uid, user_ratings in top_n.items():
        rd.shuffle(user_ratings)
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n

# Fonction principale de génération des recommandations top-100
def generate_top_100(model, file_name):
    sp_ratings = load_ratings(surprise_format=True)
    trainset = sp_ratings.build_full_trainset()
    model.fit(trainset)

    all_items = trainset.all_items()
    results = []

    # Boucle sur une plage d'IDs utilisateurs (au format int)
    for user_raw_id in range(300001, 300011):
        try:
            user_inner_id = trainset.to_inner_uid(user_raw_id)
        except ValueError:
            print(f"[WARN] User {user_raw_id} not in trainset.")
            continue

        # Identifier les items non notés par l'utilisateur
        rated_items = set(j for (j, _) in trainset.ur[user_inner_id])
        unseen_items = [i for i in all_items if i not in rated_items]

        # Générer les prédictions
        predictions = []
        for item_inner_id in unseen_items:
            try:
                raw_item_id = trainset.to_raw_iid(item_inner_id)
                pred = model.predict(user_raw_id, raw_item_id)
                predictions.append(pred)
            except PredictionImpossible:
                continue
            except Exception as e:
                print(f"[ERROR] {e} for user {user_raw_id}, item {item_inner_id}")
                continue

        if not predictions:
            continue

        # Extraire les top-N prédictions
        top_n = get_top_n(predictions, n=100)
        for item_id, est_rating in top_n[user_raw_id]:
            results.append([user_raw_id, item_id, round(est_rating, 3)])

    # Sauvegarder le fichier CSV dans le dossier recs
    recs_path = Constant.DATA_PATH / "recs" / file_name
    recs_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results, columns=["user_id", "item_id", "estimated_rating"])
    df.to_csv(recs_path, index=False)
    print(f"\n File '{file_name}' generated successfully in 'recs' folder.")


# Exemple d'exécution pour plusieurs modèles
if __name__ == "__main__":
    from models import ModelSVDOptimized, ContentBased, UserBased

    latent_model = ModelSVDOptimized()
    generate_top_100(latent_model, "top_100_latent.csv")

    content_model = ContentBased(features_method="mixed-features", regressor_method="ridge_regression")
    generate_top_100(content_model, "top_100_content.csv")

    user_model = UserBased(engine='knn', k=50, min_k=2, sim_options={"name": "msd", "user_based": True, "min_support": 3})
    generate_top_100(user_model, "top_100_user.csv")
