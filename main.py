import pandas as pd
import sqlite3
from item_similarity_recommender import item_similarity_recommender_py

# Connect to the SQLite database
conn = sqlite3.connect('data/track_metadata.db')

# Query the song metadata
song_metadata_query = "SELECT track_id as song_id, title, artist_name FROM songs"
song_metadata = pd.read_sql_query(song_metadata_query, conn)

# Display the first few rows of the song metadata
print("Song metadata sample:")
print(song_metadata.head())

# Load the user-song interaction data
data_path = "data/train_triplets.txt"
df = pd.read_csv(data_path, delimiter='\t', header=None, names=['user_id', 'song_id', 'listen_count'])

# Display the first few rows of the interaction dataset
print("Dataset sample:")
print(df.head())

# Get a list of unique user IDs
users = df['user_id'].unique()

# Choose a random user ID
random_user_id = users[5]  # Example: you can change this index to pick a different user
print(f"Random user_id: {random_user_id}")

# Create the recommender system instance
is_model = item_similarity_recommender_py()
is_model.create(df, 'user_id', 'song_id')
is_model.set_song_metadata(song_metadata)  # Set the song metadata

# Print the songs for the user in the training data
user_id = random_user_id
user_items = is_model.get_user_items(user_id)

print("------------------------------------------------------------------------------------")
print(f"Training data songs for the user user_id: {user_id}:")
print("------------------------------------------------------------------------------------")
for user_item in user_items:
    song_info = song_metadata[song_metadata['song_id'] == user_item]
    if not song_info.empty:
        song_name = song_info['title'].values[0]
        artist_name = song_info['artist_name'].values[0]
        print(f"{user_item}: {song_name} by {artist_name}")

print("----------------------------------------------------------------------")
print("Recommendation process going on:")
print("----------------------------------------------------------------------")

# Recommend songs for the user using the personalized model
is_model.recommend(user_id)

# Close the database connection
conn.close()
