from pre_compute import *
import pickle


def top_popular_each_genre(precomputed_res: dict, item_id, device_id):
    if item_id in precomputed_res:
        return f"Top 10 Popular {precomputed_res[item_id]}"
    return None


def top_trending_each_genre(precomputed_res: dict, item_id, device_id):
    if item_id in precomputed_res:
        return f"Top 10 Trending {precomputed_res[item_id]}"
    return None


# method 1: whatever user watched > recommend based on that 
def top_among_history(precomputed_res: dict, item_id, device_id):
    if device_id in precomputed_res["user_history"]:
        user_history = precomputed_res["user_history"][device_id]
        for h in user_history:
            if h in precomputed_res["top_item_each_source_dict"]:
                if item_id in precomputed_res["top_item_each_source_dict"][h]:
                    if h in precomputed_res['item_name']:
                        item_name = precomputed_res['item_name'][h]
                    else:
                        item_name = "Unknown Item Name"
                    return f"Top10 In Users Watched \n {item_name}"
    return None


# method 2: recommending based on positive signals (explicit or implicit)
def top_among_history_positive(precomputed_res: dict, item_id, device_id):
    messages = []
    if device_id in precomputed_res["user_history"]:
        user_history = precomputed_res["user_history"][device_id]
        

        combined_history = {
            "liked": user_history.get("liked_item_list", []),

            # extracting only the items with positive watch signal aka 80%+ watchtime 
            "completed": [k for k, v in user_history.get("completion_item_list", {}).items() if v >=0.8]
        }
        
        for history_type, history_items in combined_history.items():
            for history_item in history_items:
                if history_item in precomputed_res["top_item_each_source_dict"]:
                    if item_id in precomputed_res["top_item_each_source_dict"][history_item]:
                        item_name = precomputed_res['item_name'].get(history_item, "Unknown Item Name")
                        if history_type == "liked":
                            messages.append(f"This item is popular among users who liked '{item_name}'")
                        else: 
                            messages.append(f"This item is popular among users who completed '{item_name}'")
    
    return " ".join(messages) if messages else None



##  if want to use original method 
# explanation_generator_list = [(top_popular_each_genre_precompute, top_popular_each_genre),
#                               (top_trending_each_genre_precompute, top_trending_each_genre),
#                               (top_popular_each_source_title_precompute, top_among_history)]

explanation_generator_list = [(top_popular_each_genre_precompute, top_popular_each_genre),
                              (top_trending_each_genre_precompute, top_trending_each_genre),
                              (top_popular_each_source_title_precompute, top_among_history_positive)]


# Load the pre-computed result
precomputed_res_dict = dict()
for precomputed_func, _ in explanation_generator_list:
    pickle_name = f"{precomputed_func.__name__}.pickle"
    try:
        with open(pickle_name, 'rb') as file:
            precomputed_res_dict[precomputed_func.__name__] = pickle.load(file)
    except FileNotFoundError:
        print(f"FileNotFoundError: {pickle_name} not found.")
        precomputed_res_dict[precomputed_func.__name__] = {}


def get_explanations(item_id, device_id):
    explanation_func_list = []
    for precomputed_func, generator in explanation_generator_list:
        precomputed_res = precomputed_res_dict[precomputed_func.__name__]
        reason = generator(precomputed_res, item_id=item_id, device_id=device_id)
        if reason:
            explanation_func_list.append(reason)
    return explanation_func_list
