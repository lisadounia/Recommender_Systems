
from collections import defaultdict
import heapq
import numpy as np
import random as rd
from surprise import AlgoBase
from surprise import KNNWithMeans
from surprise import SVD
from surprise.prediction_algorithms.predictions import PredictionImpossible
from loaders import load_items
from constants import Constant as C
import pandas as pd
from sklearn import linear_model
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD



def get_top_n(predictions, n):
    """Return the top-N recommendation for each user from a set of predictions.
    Source: inspired by https://github.com/NicolasHug/Surprise/blob/master/examples/top_n_recommendations.py
    and modified by cvandekerckh for random tie breaking

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.
    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    rd.seed(0)

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        rd.shuffle(user_ratings)
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


#-------------------------------------- Latent based ------------------------------------------
class ModelSVDOptimized(SVD):
    def __init__(self):
        # Appel du constructeur de SVD avec les meilleurs hyperparamètres
        SVD.__init__(self, n_factors=90, reg_all=0.05, lr_all=0.01)






#-------------------------------------- User based ------------------------------------------

class UserBased(AlgoBase):
    def __init__(self,engine='custom', k=3, min_k=1, sim_options={}, **kwargs):
        AlgoBase.__init__(self, sim_options=sim_options, **kwargs)
        self.k = k
        self.min_k = min_k
        self.engine = engine
        if engine == 'knn':
            self.algo = KNNWithMeans(k=k, min_k=min_k, sim_options=self.sim_options)

    def fit(self, trainset):
        AlgoBase.fit(self, trainset)
        self.trainset = trainset
        self.ratings_matrix = self.compute_rating_matrix()
        self.similarity_matrix = self.compute_similarity_matrix()
        self.mean_ratings = []
        for i in range(self.trainset.n_users):
            user_ratings = trainset.ur[i]
            if user_ratings : 
                mean = sum(r for (_, r) in user_ratings) / len(user_ratings)
            else :
                mean = 0
            self.mean_ratings.append(mean)
        return self

    def estimate(self, u, i):
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unknown.')
        
        estimate = self.mean_ratings[u]
        voisins = []
        for neighbor_inner_id, similarity in enumerate(self.sim[u]):
            if not np.isnan(self.ratings_matrix[neighbor_inner_id, i]):
                rating= self.ratings_matrix[neighbor_inner_id, i]
                heapq.heappush(voisins, (-similarity, rating, neighbor_inner_id))
        # -- implement here the estimate function --
        actual_k = 0
        weighted_sum = 0
        sim_sum = 0
        while voisins and actual_k < self.k : 
            similarity, rating, neighbor_inner_id = heapq.heappop(voisins)
            similarity = -similarity  # revert to positive similarity
            neighbor_mean = self.mean_ratings[neighbor_inner_id]
            weighted_sum += similarity * (rating - neighbor_mean) 
            sim_sum += abs(similarity)
            actual_k += 1
        if actual_k >= self.min_k and sim_sum > 0:
            estimate += (weighted_sum / sim_sum)
            

        return estimate

    def compute_rating_matrix(self):
        m = self.trainset.n_users
        n = self.trainset.n_items
        self.ratings_matrix = np.empty((m, n))
        self.ratings_matrix[:] = np.nan  # initialiser à NaN
        for inner_uid in range(m):
            for (inner_iid, rating) in self.trainset.ur[inner_uid]:
                self.ratings_matrix[inner_uid, inner_iid] = rating
        return self.ratings_matrix

    def compute_similarity_matrix(self):
        m = self.trainset.n_users
        self.sim = np.eye(m)  # initialiser la matrice de similarité à une matrice identité
        min_support =  self.sim_options.get('min_support', 1)   
        sim_name = self.sim_options.get('name', 'msd')  # 'msd' par défaut
        for u in range(m):
            for v in range(u + 1, m):
             ratings_u = self.ratings_matrix[u]
             ratings_v = self.ratings_matrix[v]
             common_mask = ~np.isnan(ratings_u) & ~np.isnan(ratings_v)
             support = np.sum(common_mask)
             if support >= min_support:
                if sim_name == 'jaccard':
                    mask_u = ~np.isnan(ratings_u)
                    mask_v = ~np.isnan(ratings_v)
                    union = np.sum(mask_u | mask_v)
                    intersection = np.sum(mask_u & mask_v)
                    sim = intersection / union if union > 0 else 0
                    self.sim[u, v] = sim
                    self.sim[v, u] = sim
                else : 
                    
                    diff = ratings_u[common_mask] - ratings_v[common_mask]
                    msd = np.mean(diff ** 2)
                    sim = 1 / (1 + msd)  # conversion MSD → similarité (valeur entre 0 et 1)
                    self.sim[u, v] = sim
                    self.sim[v, u] = sim  # matrice symétrique
        return self.sim






#-------------------------------------- Content based ------------------------------------------

class ContentBased(AlgoBase):
    def __init__(self, features_method, regressor_method):
        AlgoBase.__init__(self)
        self.regressor_method = regressor_method
        self.content_features = self.create_content_features(features_method)

    def create_content_features(self, features_method):
        df_items = load_items()
        if 'movieId' not in df_items.columns and df_items.index.name == 'movieId':
            df_items.reset_index(inplace=True)

        if features_method is None:
            df_features = None
        elif features_method == "date":
            df = pd.read_csv(C.CONTENT_PATH / C.ITEMS_WITH_DATE_FILENAME)
            df_features = df[[C.ITEM_ID_COL, 'date']].set_index(C.ITEM_ID_COL)

        #genome
        elif features_method == "genome-top-tags":
            df_tags = pd.read_csv(C.CONTENT_PATH / "genome-tags.csv")
            df_scores = pd.read_csv(C.CONTENT_PATH / "genome-scores.csv")
            df_top_scores = df_scores[df_scores['relevance'] > 0.8]
            df_top = df_top_scores.merge(df_tags, on="tagId")
            df_features = df_top.pivot_table(
                index="movieId",
                columns="tag",
                values="relevance",
                fill_value=0
            )
            return (df_features > 0).astype(int)



        #visuals dataset
        elif features_method == "visual":
            df_features = ( pd.read_csv(C.CONTENT_PATH / "visual_features_prepared.csv").set_index(C.ITEM_ID_COL) )

        #movie genres features (and potentially weight them with a TF-IDF Vectorizer)
        
        elif features_method == "genres":
            df = df_items[[C.ITEM_ID_COL, C.GENRES_COL]].copy()
            df[C.GENRES_COL] = df[C.GENRES_COL].fillna('').apply(lambda x: x.replace('|', ' '))
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(df[C.GENRES_COL])
            df_features = pd.DataFrame(tfidf_matrix.toarray(), index=df[C.ITEM_ID_COL], columns=vectorizer.get_feature_names_out())
        

        elif features_method == "date+visual":
            df_date = pd.read_csv(C.CONTENT_PATH / C.ITEMS_WITH_DATE_FILENAME)[[C.ITEM_ID_COL, 'date']]
            df_visual = pd.read_csv(C.CONTENT_PATH / "visual_features_prepared.csv")
            
            df_merged = pd.merge(df_date, df_visual, on=C.ITEM_ID_COL, how="outer")
            df_features = df_merged.set_index(C.ITEM_ID_COL)
            df_features = df_features.fillna(0.0)

        elif features_method == "date+visual+genres":
            df_date = pd.read_csv(C.CONTENT_PATH / C.ITEMS_WITH_DATE_FILENAME)[[C.ITEM_ID_COL, 'date', 'genres']]
            df_visual = pd.read_csv(C.CONTENT_PATH / "visual_features_prepared.csv")

            df_genres_onehot = df_date['genres'].str.get_dummies(sep='|')
            df_genres_onehot[C.ITEM_ID_COL] = df_date[C.ITEM_ID_COL]

            df_merged = df_date[[C.ITEM_ID_COL, 'date']].merge(df_visual, on=C.ITEM_ID_COL, how="outer").merge(df_genres_onehot, on=C.ITEM_ID_COL, how="outer" )

            df_features = df_merged.set_index(C.ITEM_ID_COL).fillna(0.0)
        elif features_method == "mixed-features":
            from sklearn.preprocessing import StandardScaler

            df_items = df_items.reset_index()

            # One-hot encoding des genres (pas de TF-IDF)
            df_genres_onehot = df_items['genres'].fillna('').str.get_dummies(sep='|')
            df_genres_onehot["movieId"] = df_items["movieId"]

            # GENOME TAGS (filtrés, réduits)
            df_tags = pd.read_csv(C.CONTENT_PATH / "genome-tags.csv")
            df_scores = pd.read_csv(C.CONTENT_PATH / "genome-scores.csv")
            df_scores = df_scores[df_scores['relevance'] >= 0.6]  # seuil strict
            df_topn = df_scores.groupby('movieId').apply(lambda x: x.nlargest(20, 'relevance')).reset_index(drop=True)
            df_topn = df_topn.merge(df_tags, on="tagId")
            df_genome_matrix = df_topn.pivot_table(
                index="movieId", columns="tag", values="relevance", fill_value=0.0
            )

            # YEAR (extrait proprement et standardisé)
            df_items['year'] = df_items['title'].str.extract(r'\((\d{4})\)').astype(float)
            df_year = df_items.set_index('movieId')[['year']].fillna(0)

            scaler_year = StandardScaler()
            df_year[['year']] = scaler_year.fit_transform(df_year[['year']])
            self.scaler_year = scaler_year  # facultatif, pour réutilisation ultérieure

            # Concaténation : genres one-hot + genome tags + year
            df_merged = df_genres_onehot.set_index(C.ITEM_ID_COL).join(df_genome_matrix, how='outer').join(df_year, how='outer').fillna(0)

            # Homogénéiser les noms de colonnes
            df_merged.columns = df_merged.columns.astype(str)

            # SCALING + SVD global
            scaler = StandardScaler()
            df_scaled = pd.DataFrame(scaler.fit_transform(df_merged), index=df_merged.index)

            if df_scaled.shape[1] > 50:
                svd = TruncatedSVD(n_components=20, random_state=42)
                df_reduced = pd.DataFrame(svd.fit_transform(df_scaled), index=df_scaled.index)
                self.svd = svd
            else:
                df_reduced = df_scaled
                self.svd = None

            self.scaler = scaler
        return df_reduced
    def fit(self, trainset):
        """Profile Learner"""
        AlgoBase.fit(self, trainset)
        
        # Preallocate user profiles
        self.user_profile = {u: None for u in trainset.all_users()}
        self.user_profile_explain = {u: None for u in trainset.all_users()}

        for u in self.user_profile:
            user_ratings = self.trainset.ur[u]  # liste de (inner_item_id, rating)
            df_user = pd.DataFrame(user_ratings, columns=['inner_id', 'rating'])
            df_user['raw_id'] = df_user['inner_id'].map(self.trainset.to_raw_iid)
            df_user = df_user.merge(
                self.content_features,
                how="left",
                left_on="raw_id",
                right_index=True
            )
            df_user = df_user.fillna(0.0)
            X = df_user.drop(columns=['inner_id', 'rating', 'raw_id']).values  # 2D numpy array
            y = df_user['rating'].values  # 1D numpy array

            if self.regressor_method == 'linear_regression':
                model = linear_model.LinearRegression(fit_intercept= True)
            elif self.regressor_method == 'ridge_regression':
                model = Ridge(
                            alpha=500.0,
                            fit_intercept=True,
                            solver='sag',
                            tol=0.001,
                            random_state=42)
                
            elif self.regressor_method == 'random_forest':
                model = RandomForestRegressor(
                    n_estimators=500,
                    max_depth=7,
                    min_samples_leaf=2,
                    max_features=0.8,
                    bootstrap=True,
                    oob_score=True,
                    random_state=42,
                    n_jobs=-1    
                )
            elif self.regressor_method == 'gradient_boosting':
                model = GradientBoostingRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=2,
                    subsample=0.7,
                    min_samples_leaf=2,
                    max_features="sqrt",
                    random_state=42,
                )
            elif self.regressor_method == 'knn_regressor':
                model = KNeighborsRegressor(n_neighbors=3)
            else:
                raise NotImplementedError(f'Regressor method {self.regressor_method} not implemented in fit().')

            model.fit(X, y)
            # --------- user profil ----------
            feature_matrix = df_user.drop(columns=['inner_id', 'rating', 'raw_id']).values
            weights = df_user['rating'].values.reshape(-1, 1)

            # Moyenne pondérée des features
            weighted_sum = (feature_matrix * weights).sum(axis=0)
            feature_importance = weighted_sum / weights.sum()

            # Normalisation dans [0, 1]
            min_val = feature_importance.min()
            max_val = feature_importance.max()
            if max_val > min_val:
                normalized_importance = (feature_importance - min_val) / (max_val - min_val)
            else:
                normalized_importance = feature_importance  # si tout est constant

            # Stocker le résultat dans le dictionnaire
            self.user_profile_explain[u] = { feature: round(score, 3) for feature, score in zip(self.content_features.columns, normalized_importance) }
            self.user_profile[u] = model
            
    def estimate(self, u, i):
        """Scoring component used for item filtering"""
        # First, handle cases for unknown users and items
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unknown.')

        if self.regressor_method in [ 'linear_regression', 'ridge_regression', 'random_forest', 'gradient_boosting', 'knn_regressor']:
            model = self.user_profile[u]
            item_id = self.trainset.to_raw_iid(i)

            if item_id in self.content_features.index:
                item_features = (
                    self.content_features.loc[item_id]
                    .values.reshape(1, -1)
                )
            else:
                item_features = np.zeros(
                    (1, self.content_features.shape[1]), dtype=float
                )

            score = model.predict(item_features)[0]

        else:
            raise NotImplementedError(f'Regressor method {self.regressor_method} not handled in estimate().')

        return score
     
    def explain(self, u):
    #Return a dictionary with the importance score of each feature for user u
        if u not in self.user_profile_explain:
            raise ValueError(f"No explanation available for user {u}")
        return self.user_profile_explain[u]





