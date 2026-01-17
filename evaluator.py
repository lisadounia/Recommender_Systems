from configs import EvalConfig
from constants import Constant as C
from loaders import export_evaluation_report
from loaders import load_ratings
from models import ContentBased
from models import get_top_n
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise import accuracy
from surprise import model_selection
import numpy as np
import pandas as pd


def generate_split_predictions(algo, ratings_dataset, eval_config):
    trainset, testset = model_selection.train_test_split(ratings_dataset, test_size=eval_config.test_size)
    algo.fit(trainset)
    predictions = algo.test(testset)
    return predictions


def generate_loo_top_n(algo, ratings_dataset, eval_config):
    """Generate top-n recommendations for each user on a random Leave-one-out split (LOO)"""
    # -- implement the function generate_loo_top_n --
    loo = model_selection.LeaveOneOut(n_splits=1, random_state=1)
    trainset, testset = next(loo.split(ratings_dataset))
    algo.fit(trainset)
    anti_test_set = trainset.build_anti_testset()
    predictions = algo.test(anti_test_set)
    anti_testset_top_n = get_top_n(predictions, n=eval_config.top_n_value)


    return anti_testset_top_n, testset


def generate_full_top_n(algo, ratings_dataset, eval_config):
    """Generate top-n recommendations for each user with full training set (LOO)"""
    # -- implement the function generate_full_top_n --
    full_train_set = ratings_dataset.build_full_trainset()
    algo.fit(full_train_set)
    anti_test_set = full_train_set.build_anti_testset()
    predictions = algo.test(anti_test_set)
    anti_testset_top_n = get_top_n(predictions, n=eval_config.top_n_value)
    return anti_testset_top_n


def precompute_information():
    """ Returns a dictionary that precomputes relevant information for evaluating in full mode

    Dictionary keys:
    - precomputed_dict["item_to_rank"] : contains a dictionary mapping movie ids to rankings
    - (-- for your project, add other relevant information here -- )
    """
    df_ratings = load_ratings()
    #group by item id and count the number of ratings
    df_ratings = df_ratings.groupby(C.ITEM_ID_COL).count().reset_index()
    df_ratings = df_ratings.sort_values(by=C.RATING_COL, ascending=False)
    #create a diconary mapping movie ids to rankings
    item_to_rank = {}
    for rank, row in enumerate(df_ratings.itertuples(index=False), start=1):
        item_id = getattr(row, C.ITEM_ID_COL)
        item_to_rank[item_id] = rank



    precomputed_dict = {}
    precomputed_dict["item_to_rank"] = item_to_rank
    return precomputed_dict


def create_evaluation_report(eval_config, sp_ratings, precomputed_dict, available_metrics):
    """ Create a DataFrame evaluating various models on metrics specified in an evaluation config.
    """
    algo = SVD()
    evaluation_dict = {}
    for model_name, model, arguments in eval_config.models:
        print(f'Handling model {model_name}')
        algo = model(**arguments)
        evaluation_dict[model_name] = {}

        # Type 1 : split evaluations
        if len(eval_config.split_metrics) > 0:
            print('Training split predictions')
            predictions = generate_split_predictions(algo, sp_ratings, eval_config)
            for metric in eval_config.split_metrics:
                print(f'- computing metric {metric}')
                assert metric in available_metrics['split']
                evaluation_function, parameters =  available_metrics["split"][metric]
                evaluation_dict[model_name][metric] = evaluation_function(predictions, **parameters)
                print(metric)
                print(predictions)


        # Type 2 : loo evaluations
        if len(eval_config.loo_metrics) > 0:
            print('Training loo predictions')
            anti_testset_top_n, testset = generate_loo_top_n(algo, sp_ratings, eval_config)
            for metric in eval_config.loo_metrics:
                assert metric in available_metrics['loo']
                evaluation_function, parameters =  available_metrics["loo"][metric]
                evaluation_dict[model_name][metric] = evaluation_function(anti_testset_top_n, testset, **parameters)

        # Type 3 : full evaluations
        if len(eval_config.full_metrics) > 0:
            print('Training full predictions')
            anti_testset_top_n = generate_full_top_n(algo, sp_ratings, eval_config)
            for metric in eval_config.full_metrics:
                assert metric in available_metrics['full']
                evaluation_function, parameters =  available_metrics["full"][metric]
                evaluation_dict[model_name][metric] = evaluation_function(
                    anti_testset_top_n,
                    **precomputed_dict,
                    **parameters
                )

    return pd.DataFrame.from_dict(evaluation_dict).T


# # 2. Evaluation metrics
# Implement evaluation metrics for either rating predictions (split metrics) or for top-n recommendations (loo metric, full metric)

# In[13]:


def get_hit_rate(anti_testset_top_n, testset):
    """Compute the average hit over the users (loo metric)

    A hit (1) happens when the movie in the testset has been picked by the top-n recommender
    A fail (0) happens when the movie in the testset has not been picked by the top-n recommender
    """
    # -- implement the function get_hit_rate --
    hits = 0
    total = 0

    # Boucle sur chaque tuple du testset
    for (user, left_out_movie, _) in testset:
        # Récupérer les recommandations pour ce user
        user_top_n = anti_testset_top_n.get(user, [])

        # Récupérer juste les IDs de film recommandés
        recommended_movies = [movie_id for (movie_id, _) in user_top_n]

        # Vérifier si le film "laissé de côté" est dans les recommandations
        if left_out_movie in recommended_movies:
            hits += 1

        total += 1
    hit_rate = hits / total if total > 0 else 0
    return hit_rate


def get_novelty(anti_testset_top_n, item_to_rank):
    """Compute the average novelty of the top-n recommendation over the users (full metric)

    The novelty is defined as the average ranking of the movies recommended
    """
    # -- implement the function get_novelty --
    total_rank_sum = 0
    total_items = 0
    rows = []
    for user_id, item_list in anti_testset_top_n.items():
        for item_id, estimated_rating in item_list:
            rows.append((user_id, item_id, estimated_rating))
    df_topn_full = pd.DataFrame(rows, columns=['user', 'item', 'estimated_rating'])
    for _, row in df_topn_full.iterrows():
        item_id = row['item']
        rank = item_to_rank.get(item_id, 0)  # 0 si l’item n’est pas dans item_to_rank
        total_rank_sum += rank
        total_items += 1
    average_rank_sum = total_rank_sum / total_items

    return average_rank_sum


# # 3. Evaluation workflow
# Load data, evaluate models and save the experimental outcomes



AVAILABLE_METRICS = {
    "split": { "mae": (accuracy.mae, {'verbose': False}), "rmse" : (accuracy.rmse, {'verbose': False}), }
   ,"loo" : {"hit_rate" : (get_hit_rate, {})},
    "full" : {"novelty" : (get_novelty, {})}}


sp_ratings = load_ratings(surprise_format=True)
algo = SVD()
test = generate_split_predictions(algo, sp_ratings, EvalConfig)

top_n_loo_top,test_set_loo = generate_loo_top_n(algo, sp_ratings, EvalConfig)
rows = []
for user_id, item_list in top_n_loo_top.items():
    for item_id, estimated_rating in item_list:
        rows.append((user_id, item_id, estimated_rating))

df_topn = pd.DataFrame(rows, columns=['user', 'item', 'estimated_rating'])
df_topn.to_csv("top_n_loo.csv", index=False)


top_n_full = generate_full_top_n(algo, sp_ratings, EvalConfig)
rows = []
for user_id, item_list in top_n_full.items():
    for item_id, estimated_rating in item_list:
        rows.append((user_id, item_id, estimated_rating))
df_topn_full = pd.DataFrame(rows, columns=['user', 'item', 'estimated_rating'])

df_topn_full.to_csv("top_n_full.csv", index=False)
precomputed_dict = precompute_information()
evaluation_report = create_evaluation_report(EvalConfig, sp_ratings, precomputed_dict, AVAILABLE_METRICS)
display(evaluation_report)
export_evaluation_report(evaluation_report)