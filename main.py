import pandas as pd
from item_similarity_recommender import item_similarity_recommender_py

# Load your training data
train_data = pd.read_csv('path_to_your_training_data.csv')

# Create an instance of item similarity based recommender class
is_model = item_similarity_recommender_py()
is_model.create(train_data, 'user_id', 'song_id')

# Recommend songs for a user
user_id = 'some_user_id'  # Replace with actual user ID
recommendations = is_model.recommend(user_id)
print(recommendations)
