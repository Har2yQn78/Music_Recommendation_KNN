import pandas as pd
import sqlite3
import random
from sklearn.model_selection import train_test_split
from recommender import popularity_recommender_py, item_similarity_recommender_py

# Load data
triplets_file = 'data/train_triplets.txt'
songs_metadata_file = 'data/track_metadata.db'

triplets_df_chunk = pd.read_csv(triplets_file, sep='\t', names=['user_id', 'song_id', 'listen_count'], nrows=500000)

# Load songs metadata from SQLite database
conn = sqlite3.connect(songs_metadata_file)
metadata_df = pd.read_sql_query('SELECT song_id, title, release, artist_name FROM songs', conn)
conn.close()

# Merge data
combined_df_chunk = pd.merge(triplets_df_chunk, metadata_df, on='song_id', how='inner')
combined_df_chunk = combined_df_chunk.loc[:, ~combined_df_chunk.columns.duplicated()]

# Preprocess data
combined_df_chunk['song_artist'] = combined_df_chunk['title'] + ' - ' + combined_df_chunk['artist_name']
subset_df_chunk = combined_df_chunk.head(10000)
grouped_df_chunk = subset_df_chunk.groupby('song_artist')['listen_count'].sum().reset_index()
total_listens_chunk = grouped_df_chunk['listen_count'].sum()
grouped_df_chunk['percentage'] = (grouped_df_chunk['listen_count'] / total_listens_chunk) * 100
sorted_df_chunk = grouped_df_chunk.sort_values(by='percentage', ascending=True)

# Split data
train_data, test_data = train_test_split(combined_df_chunk, test_size=0.2, random_state=42)

# Create popularity-based recommender
popularity_model = popularity_recommender_py()
popularity_model.create(train_data, 'user_id', 'song_id')

# Create item similarity-based recommender
item_similarity_model = item_similarity_recommender_py()
item_similarity_model.create(train_data, 'user_id', 'song_id')

# Get a random user_id
random_user_id = random.choice(train_data['user_id'].unique())
print(f"Random user_id: {random_user_id}")

# Print songs for the user in training data
user_items = item_similarity_model.get_user_items(random_user_id)
print("------------------------------------------------------------------------------------")
print(f"Training data songs for the user user_id: {random_user_id}:")
print("------------------------------------------------------------------------------------")
for user_item in user_items:
    print(user_item)

print("----------------------------------------------------------------------")
print("Recommendation process going on:")
print("----------------------------------------------------------------------")

# Recommend songs for the user using personalized model
recommendations = item_similarity_model.recommend(random_user_id)
print("Recommendations:")
for idx, row in recommendations.iterrows():
    print(f"Song: {row['song']}, Score: {row['score']}")

# Get similar items for a given song
song = 'U Smile - Justin Bieber'
similar_songs = item_similarity_model.get_similar_items([song])
print(f"Similar songs to '{song}':")
for idx, row in similar_songs.iterrows():
    print(f"Song: {row['song']}, Score: {row['score']}")
