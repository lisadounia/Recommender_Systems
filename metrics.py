import pandas as pd
import re
from itertools import combinations
from constants import Constant as C

movies_path = C.CONTENT_PATH / C.ITEMS_FILENAME
movies_df = pd.read_csv(movies_path)

movie_genres = movies_df.set_index(C.ITEM_ID_COL)[C.GENRES_COL] \
    .dropna().astype(str).apply(lambda x: set(x.split('|')))

def extract_decade(title):
    if pd.isna(title):
        return None
    match = re.search(r"\((\d{4})\)", title)
    if match:
        year = int(match.group(1))
        decade = (year // 10) * 10
        return f"year_{decade}s"
    return None

movie_decades = movies_df.set_index(C.ITEM_ID_COL)[C.LABEL_COL].apply(extract_decade)

def combined_features(iid):
    genres = movie_genres.get(iid, set())
    decade = movie_decades.get(iid)
    return genres | {decade} if decade else genres

def jaccard_distance(set1, set2):
    if not set1 or not set2:
        return 0
    return 1 - len(set1 & set2) / len(set1 | set2)

def compute_intra_diversity(item_ids):
    sets = [combined_features(i) for i in item_ids]
    pairs = combinations(sets, 2)
    distances = [jaccard_distance(s1, s2) for s1, s2 in pairs]
    return sum(distances) / len(distances) if distances else 0

def compute_inter_diversity(user_items_dict):
    user_ids = list(user_items_dict.keys())
    pairs = combinations(user_ids, 2)
    distances = []
    for u1, u2 in pairs:
        set1 = set(user_items_dict[u1])
        set2 = set(user_items_dict[u2])
        distances.append(jaccard_distance(set1, set2))
    return sum(distances) / len(distances) if distances else 0

models = {
    #"latent": "top_100_latent.csv",
    #"content": "top_100_content.csv",
    "user": "top_100_user.csv"
}

for model_name, filename in models.items():
    path = C.DATA_PATH / "recs" / filename
    df = pd.read_csv(path)

    if "item_id" in df.columns:
        df.rename(columns={"item_id": "movieId"}, inplace=True)

    user_ids = range(300001, 300005)
    intra_scores = []
    user_items_dict = {}

    for uid in user_ids:
        items = df[df["user_id"] == uid]["movieId"].tolist()
        user_items_dict[uid] = items
        intra = compute_intra_diversity(items)
        intra_scores.append({
            "user_id": uid,
            "intra_diversity_genre+decade": round(intra, 4)
        })

    inter = compute_inter_diversity(user_items_dict)
    intra_df = pd.DataFrame(intra_scores)
    intra_df["inter_diversity"] = round(inter, 4)

    output_csv = C.DATA_PATH / "recs" / f"{model_name}_diversity_user.csv"
    intra_df.to_csv(output_csv, index=False)
    print(f" {model_name} diversity exported to: {output_csv}")
