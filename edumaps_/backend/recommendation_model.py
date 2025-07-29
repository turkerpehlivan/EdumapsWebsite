# backend/recommendation_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors
from models import db, User, School, UserActivity, Review
import json


class RecommendationModel:
    def __init__(self):
        self.schools_df = None
        self.user_activity_df = None
        self.reviews_df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.school_id_to_index = {}
        self.index_to_school_id = {}
        self.user_school_matrix = None
        self.nn_model = None

    def load_data(self, app):
        # Uygulama bağlamı içinde veritabanından veriyi yükle
        with app.app_context():
            schools = School.query.all()
            self.schools_df = pd.DataFrame([{
                'id': s.id,
                'name': s.name,
                'city': s.city,
                'district': s.district,
                'price_range': s.price_range,
                'success_rate': s.success_rate,
                'average_rating': s.average_rating,
                'description': s.description,
                'features': s.features
            } for s in schools])

            user_activities = UserActivity.query.all()
            self.user_activity_df = pd.DataFrame([{
                'user_id': ua.user_id,
                'school_id': ua.school_id,
                'activity_type': ua.activity_type,
                'time_spent_seconds': ua.time_spent_seconds,
                'search_query': ua.search_query,
                'timestamp': ua.timestamp
            } for ua in user_activities])

            reviews = Review.query.all()
            self.reviews_df = pd.DataFrame([{
                'user_id': r.user_id,
                'school_id': r.school_id,
                'rating': r.rating,
                'comment': r.comment,
                'physical_facilities_rating': r.physical_facilities_rating,
                'teacher_quality_rating': r.teacher_quality_rating,
                'transportation_rating': r.transportation_rating
            } for r in reviews])

            if not self.schools_df.empty:
                self.schools_df['description'] = self.schools_df['description'].fillna('')
                self.schools_df['price_range'] = self.schools_df['price_range'].fillna('')
                # JSON alanı zaten dict olarak geliyor, stringe çevirmeye gerek yok
                self.schools_df['features_str'] = self.schools_df['features'].apply(
                    lambda x: json.dumps(x) if x else '')

    def preprocess_data(self):
        if self.schools_df.empty:
            print("Okul verisi yüklenmedi, ön işleme yapılamaz.")
            return

        self.schools_df['content'] = self.schools_df['name'] + ' ' + \
                                     self.schools_df['city'] + ' ' + \
                                     self.schools_df['district'] + ' ' + \
                                     self.schools_df['description'] + ' ' + \
                                     self.schools_df['price_range'] + ' ' + \
                                     self.schools_df['features_str']  # Yeni stringe çevrilmiş alan

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS  # İngilizce durak kelimeler, örnek olarak

        # Türkçe durak kelimeler için manuel bir liste oluşturun veya bir yerden yükleyin
        # Bu liste daha kapsamlı olabilir, ben sadece örnek bir başlangıç veriyorum:
        TURKISH_STOP_WORDS = [
            "bir", "çok", "ve", "ile", "için", "bu", "da", "de", "e", "fakat", "falan", "filan",
            "gibi", "hakkında", "hale", "hem", "hiç", "ise", "itibaren", "işte", "kadar", "kanımca",
            "ki", "kim", "kime", "kimi", "kimin", "niye", "o", "oysa", "oysaki", "yani", "ya da"
            # Buraya daha fazla Türkçe durak kelime ekleyebilirsiniz
        ]

        # TfidfVectorizer'ı güncellenmiş stop_words parametresiyle kullanın
        self.tfidf_vectorizer = TfidfVectorizer(stop_words=TURKISH_STOP_WORDS)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.schools_df['content'])

        if not self.user_activity_df.empty:
            view_activities = self.user_activity_df[self.user_activity_df['activity_type'] == 'view'].copy()
            if not view_activities.empty:
                view_activities['score'] = view_activities['time_spent_seconds'].apply(lambda x: min(x / 60, 5))
                merged_data = pd.concat([
                    view_activities[['user_id', 'school_id', 'score']].rename(columns={'score': 'rating'}),
                    self.reviews_df[['user_id', 'school_id', 'rating']]
                ])
                # Duplicate entries can happen if a user views and reviews a school. Use max rating.
                self.user_school_matrix = merged_data.groupby(['user_id', 'school_id'])['rating'].max().unstack(
                    fill_value=0)
                if not self.user_school_matrix.empty:
                    self.nn_model = NearestNeighbors(metric='cosine', algorithm='brute')
                    self.nn_model.fit(self.user_school_matrix.T)  # Item-based collaborative filtering

        self.school_id_to_index = {school_id: i for i, school_id in enumerate(self.schools_df['id'])}
        self.index_to_school_id = {i: school_id for i, school_id in enumerate(self.schools_df['id'])}

    def get_content_based_recommendations(self, school_id, num_recommendations=5):
        if self.schools_df.empty or school_id not in self.schools_df['id'].values:
            return []

        # Eğer school_id_to_index haritası boşsa veya ilgili ID'yi içermiyorsa kontrol et
        if not self.school_id_to_index or school_id not in self.school_id_to_index:
            # Bu durum genellikle veri setinin boş veya modelin initialize edilmediği anlamına gelir
            # Loglama yapılabilir veya uygun bir hata mesajı döndürülebilir
            print(f"Uyarı: get_content_based_recommendations: school_id {school_id} için indeks bulunamadı.")
            return []

        idx = self.schools_df[self.schools_df['id'] == school_id].index[0]
        cosine_similarities = linear_kernel(self.tfidf_matrix[idx:idx + 1], self.tfidf_matrix).flatten()
        related_schools_indices = cosine_similarities.argsort()[:-num_recommendations - 2:-1]  # Kendisi hariç
        recommended_schools_ids = [self.schools_df.iloc[i]['id'] for i in related_schools_indices if i != idx]
        return recommended_schools_ids[:num_recommendations]

    def get_collaborative_recommendations_for_user(self, user_id, num_recommendations=5):
        if self.user_school_matrix is None or user_id not in self.user_school_matrix.index:
            return []

        user_ratings = self.user_school_matrix.loc[user_id]
        rated_schools = user_ratings[user_ratings > 0].index.tolist()

        if not rated_schools:
            return []

        recommended_schools = set()
        for school_id in rated_schools:
            if school_id in self.school_id_to_index:
                # Sütunun varlığını kontrol et
                if school_id not in self.user_school_matrix.columns:
                    continue  # Yoksa atla

                # school_id'ye ait tek bir sütunu al ve reshape et
                school_vector = self.user_school_matrix.loc[:, school_id].values.reshape(1, -1)

                # nn_model'in fit edildiğinden ve school_vector'ın doğru boyutta olduğundan emin olun
                if self.nn_model and school_vector.shape[1] == self.user_school_matrix.shape[0]:
                    distances, indices = self.nn_model.kneighbors(school_vector, n_neighbors=num_recommendations + 1)

                    for i in range(1, len(indices.flatten())):
                        sim_school_id = self.user_school_matrix.columns[indices.flatten()[i]]
                        if sim_school_id not in rated_schools:
                            recommended_schools.add(sim_school_id)
                            if len(recommended_schools) >= num_recommendations:
                                break
            if len(recommended_schools) >= num_recommendations:
                break
        return list(recommended_schools)[:num_recommendations]

    def get_personalized_recommendations(self, app, user_id, num_recommendations=10):
        if self.schools_df.empty:
            print("Okul verisi bulunamadığından öneri yapılamıyor.")
            return []

        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return []

            user_preferences = user.preferences if user.preferences else {}

            viewed_schools_ids = self.user_activity_df[
                (self.user_activity_df['user_id'] == user_id) &
                (self.user_activity_df['activity_type'] == 'view')
                ]['school_id'].unique().tolist()

            content_based_recs = set()
            for school_id in viewed_schools_ids:
                content_based_recs.update(
                    self.get_content_based_recommendations(school_id, num_recommendations=num_recommendations // 2))

            collaborative_recs = set(
                self.get_collaborative_recommendations_for_user(user_id, num_recommendations=num_recommendations // 2))

            # Kullanıcı tercihlerine göre okullara puanlama yap
            all_schools_for_scoring = self.schools_df.copy()
            all_schools_for_scoring['score'] = 0.0  # Başlangıç puanı

            if user_preferences:
                if 'budget' in user_preferences and user_preferences['budget']:
                    # Bütçeye göre puanlama
                    if user_preferences['budget'] == 'low':
                        all_schools_for_scoring.loc[all_schools_for_scoring['price_range'] == 'Low', 'score'] += 1
                    elif user_preferences['budget'] == 'medium':
                        all_schools_for_scoring.loc[all_schools_for_scoring['price_range'] == 'Medium', 'score'] += 1
                    elif user_preferences['budget'] == 'high':
                        all_schools_for_scoring.loc[all_schools_for_scoring['price_range'] == 'High', 'score'] += 1

                if 'priority_features' in user_preferences and user_preferences['priority_features']:
                    # Öncelikli özelliklere göre puanlama
                    for feature in user_preferences['priority_features']:
                        all_schools_for_scoring['score'] += all_schools_for_scoring['features'].apply(
                            # JSON objesi içinde anahtarın varlığını ve değerini kontrol et
                            lambda x: 1 if x and feature in x and x[feature] == True else 0
                        )

            # İçerik ve İşbirlikçi filtrelemeden gelen önerileri birleştir
            final_recommendations_ids = list(content_based_recs.union(collaborative_recs))

            # Kullanıcının zaten görüntülediği okulları önerilerden çıkar
            final_recommendations_ids = [
                sid for sid in final_recommendations_ids
                if sid not in viewed_schools_ids
            ]

            # Eğer tercih puanlaması için okullar varsa ve önerilen okullar boş değilse
            if not all_schools_for_scoring.empty and final_recommendations_ids:
                # Önerilen okulları tercih puanına göre sırala
                recommendation_scores = {
                    sid: all_schools_for_scoring[all_schools_for_scoring['id'] == sid]['score'].values[0]
                    for sid in final_recommendations_ids if sid in all_schools_for_scoring['id'].values
                }
                final_recommendations_ids.sort(key=lambda x: recommendation_scores.get(x, 0), reverse=True)
            elif not all_schools_for_scoring.empty and not final_recommendations_ids:
                # Eğer hiç içerik/işbirlikçi önerisi bulunamazsa, genel tercih puanına göre en iyi okulları getir
                scored_schools = all_schools_for_scoring.sort_values(by='score', ascending=False)
                final_recommendations_ids = scored_schools['id'].head(num_recommendations).tolist()

            # Eğer hala yeterli sayıda öneri yoksa, popüler okullardan tamamla
            if len(final_recommendations_ids) < num_recommendations and not self.schools_df.empty:
                popular_schools = self.schools_df.sort_values(by='average_rating', ascending=False)
                for sid in popular_schools['id']:
                    if sid not in viewed_schools_ids and sid not in final_recommendations_ids:
                        final_recommendations_ids.append(sid)
                    if len(final_recommendations_ids) >= num_recommendations:
                        break

            return final_recommendations_ids[:num_recommendations]