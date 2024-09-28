import numpy as np
import pandas as pd

class item_similarity_recommender_py:
    def __init__(self):
        self.training_data = None
        self.user_id = None
        self.item_id = None
        self.cooccurence_matrix = None
        self.songs_dict = None
        self.rev_songs_dict = None
        self.item_similarity_recommendations = None
        self.song_metadata = None  # Add a variable to store song metadata

    def set_song_metadata(self, song_metadata):
        self.song_metadata = song_metadata

    def get_user_items(self, user):
        user_data = self.training_data[self.training_data[self.user_id] == user]
        user_items = list(user_data[self.item_id].unique())
        return user_items

    def get_item_users(self, item):
        item_data = self.training_data[self.training_data[self.item_id] == item]
        item_users = set(item_data[self.user_id].unique())
        return item_users

    def get_all_items_train_data(self):
        all_items = list(self.training_data[self.item_id].unique())
        return all_items

    def construct_cooccurence_matrix(self, user_songs, all_songs):
        user_songs_users = []
        for i in range(0, len(user_songs)):
            user_songs_users.append(self.get_item_users(user_songs[i]))
        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_songs), len(all_songs))), float)
        for i in range(0, len(all_songs)):
            users_i = self.get_item_users(all_songs[i])
            for j in range(0, len(user_songs)):
                users_j = user_songs_users[j]
                users_intersection = users_i.intersection(users_j)
                if len(users_intersection) != 0:
                    users_union = users_i.union(users_j)
                    cooccurence_matrix[j, i] = float(len(users_intersection)) / float(len(users_union))
                else:
                    cooccurence_matrix[j, i] = 0
        return cooccurence_matrix

    def generate_top_recommendations(self, user, cooccurence_matrix, all_songs, user_songs):
        user_sim_scores = cooccurence_matrix.sum(axis=0) / float(cooccurence_matrix.shape[0])
        user_sim_scores = np.array(user_sim_scores)[0].tolist()
        sort_index = sorted(((e, i) for i, e in enumerate(list(user_sim_scores))), reverse=True)
        columns = ['user_id', 'song', 'score', 'rank']
        df = pd.DataFrame(columns=columns)
        rank = 1
        for i in range(0, len(sort_index)):
            if not np.isnan(sort_index[i][0]) and all_songs[sort_index[i][1]] not in user_songs and rank <= 10:
                df.loc[len(df)] = [user, all_songs[sort_index[i][1]], sort_index[i][0], rank]
                rank = rank + 1
        return df

    def create(self, training_data, user_id, item_id):
        self.training_data = training_data
        self.user_id = user_id
        self.item_id = item_id

    def recommend(self, user, top_n=10):
        user_songs = self.get_user_items(user)
        all_songs = self.get_all_items_train_data()
        user_recommendations = []

        for song in all_songs:
            if song not in user_songs:
                user_recommendations.append(song)

        user_recommendations = sorted(user_recommendations, key=lambda x: self.get_similar_items([x]), reverse=True)
        return user_recommendations[:top_n]

    def get_similar_items(self, item_list):
        all_songs = self.get_all_items_train_data()
        cooccurence_matrix = self.construct_cooccurence_matrix(item_list, all_songs)
        user = ""
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, item_list)
        for index, row in df_recommendations.iterrows():
            song_id = row['song']
            song_info = self.song_metadata[self.song_metadata['song_id'] == song_id]
            song_name = song_info['title'].values[0]
            artist_name = song_info['artist_name'].values[0]
            print(f"{song_name} by {artist_name} (score: {row['score']:.2f})")
