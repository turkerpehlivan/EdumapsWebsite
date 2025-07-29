# backend/app.py
from flask import session
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from models import db, User, School, UserActivity, Review, ReviewReply, HelpfulVote, PendingReview, SchoolMedia, TeacherProfile
from recommendation_model import RecommendationModel
from datetime import datetime, timedelta
import os
from collections import defaultdict
from media_service import MediaService
from functools import wraps
from flask import request, jsonify


# Frontend klasörünün yolu (projenin kök dizininde `frontend` varsa)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,           # Statik dosyalar için
    template_folder=FRONTEND_DIR          # HTML şablonlar için
)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

# Rate limiting için basit in-memory store
rate_limit_store = defaultdict(list)

# Öneri modelini başlat
recommendation_system = RecommendationModel()

# Initialize media service
media_service = MediaService(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = None

        # Örneğin admin_id header'dan alınabilir (ya da request.json'dan)
        if request.method in ['POST', 'PUT', 'DELETE']:
            data = request.get_json(silent=True)
            if data:
                admin_id = data.get('admin_id')
        else:
            admin_id = request.args.get('admin_id')

        if not admin_id:
            return jsonify({'message': 'Admin yetkisi gerekli'}), 403

        user = User.query.get(admin_id)
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin yetkisi gerekli'}), 403

        return f(*args, **kwargs)
    return decorated_function


with app.app_context():
    db.create_all()
    try:
        recommendation_system.load_data(app)
        recommendation_system.preprocess_data()
        print("✓ Recommendation system başlatıldı")
    except Exception as e:
        print(f"⚠️ Recommendation system başlatılamadı: {e}")
        print("Uygulama yorum sistemi ile çalışmaya devam edecek")

# Ana sayfa: index.html göster
@app.route('/')
def index():
    return render_template('index.html')

# Admin paneli
@app.route('/admin.html')
def admin_panel():
    return render_template('admin.html')

# Test sayfası
@app.route('/test.html')
def test_page():
    return send_from_directory(FRONTEND_DIR, 'test.html')

# CSS dosyaları için route
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

# JS dosyaları için route
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

# Gerekirse statik dosya route'u
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# --------- API ENDPOINTLERİ AYNEN KALDI ---------

# Okul Ekleme API
@app.route('/api/schools', methods=['POST'])
def add_school():
    data = request.json
    if not data or not data.get('name') or not data.get('city'):
        return jsonify({'message': 'Okul adı ve şehir bilgisi gerekli'}), 400

    new_school = School(
        name=data['name'],
        city=data['city'],
        district=data.get('district', ''),
        price_range=data.get('price_range'),
        success_rate=data.get('success_rate'),
        average_rating=data.get('average_rating'),
        description=data.get('description'),
        features=data.get('features', {})
    )
    db.session.add(new_school)
    db.session.commit()

    with app.app_context():
        recommendation_system.load_data(app)
        recommendation_system.preprocess_data()

    return jsonify({'message': 'Okul başarıyla eklendi', 'school_id': new_school.id}), 201

# Okul Listeleme ve Filtreleme
@app.route('/api/schools', methods=['GET'])
def get_schools():
    query = request.args.get('query')
    city = request.args.get('city')
    district = request.args.get('district')

    schools_query = School.query

    if query:
        schools_query = schools_query.filter(
            (School.name.like(f'%{query}%')) |
            (School.description.like(f'%{query}%')) |
            (School.city.like(f'%{query}%')) |
            (School.district.like(f'%{query}%'))
        )
    if city:
        schools_query = schools_query.filter(School.city == city)
    if district:
        schools_query = schools_query.filter(School.district == district)

    schools = schools_query.all()
    output = [{
        'id': school.id,
        'name': school.name,
        'city': school.city,
        'district': school.district,
        'price_range': school.price_range,
        'success_rate': school.success_rate,
        'average_rating': school.average_rating,
        'description': school.description,
        'features': school.features
    } for school in schools]
    return jsonify(output)

# Okul Detay API
@app.route('/api/schools/<int:school_id>', methods=['GET'])
def get_school_detail(school_id):
    school = School.query.get(school_id)
    if not school:
        return jsonify({'message': 'Okul bulunamadı'}), 404

    reviews_data = [{
        'id': review.id,
        'user_id': review.user_id,
        'rating': review.rating,
        'comment': review.comment,
        'timestamp': review.timestamp.isoformat(),
        'physical_facilities_rating': review.physical_facilities_rating,
        'teacher_quality_rating': review.teacher_quality_rating,
        'transportation_rating': review.transportation_rating,
        'helpful_count': review.helpful_count or 0
    } for review in school.reviews if review.is_moderated]

    return jsonify({
        'id': school.id,
        'name': school.name,
        'city': school.city,
        'district': school.district,
        'price_range': school.price_range,
        'success_rate': school.success_rate,
        'average_rating': school.average_rating,
        'description': school.description,
        'features': school.features,
        'video_url': school.video_url,
        'reviews': reviews_data
    })

# Yorum Ekleme
@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    user_id = data.get('user_id')
    school_id = data.get('school_id')
    rating = data.get('rating')
    comment = data.get('comment')
    physical_facilities_rating = data.get('physical_facilities_rating')
    teacher_quality_rating = data.get('teacher_quality_rating')
    transportation_rating = data.get('transportation_rating')

    if not all([user_id, school_id, rating]):
        return jsonify({'message': 'Kullanıcı, okul ve puan gerekli'}), 400

    # Rate limiting kontrolü (kullanıcı başına saatte 3 yorum)
    if not check_rate_limit(user_id, 'review', limit=1000, window_minutes=60):
        return jsonify({'message': 'Çok fazla yorum gönderdiniz. Lütfen bir süre bekleyin.'}), 429

    # Aynı kullanıcının aynı okula birden fazla yorum yapmasını engelle (hem onaylanan hem bekleyen yorumları kontrol et)
    existing_review = Review.query.filter_by(user_id=user_id, school_id=school_id).first()
    existing_pending = PendingReview.query.filter_by(user_id=user_id, school_id=school_id).first()

    if existing_review or existing_pending:
        return jsonify({'message': 'Bu okul için zaten yorum yapmışsınız veya bekleyen yorumunuz var.'}), 409

    # Yorum temizleme ve spam kontrolü
    cleaned_comment = PendingReview.clean_comment(comment) if comment else None
    spam_score = PendingReview.calculate_spam_score(cleaned_comment) if cleaned_comment else 0.0

    # Yorumu geçici tabloya ekle (admin onayı bekleyecek)
    pending_review = PendingReview(
        user_id=user_id,
        school_id=school_id,
        rating=rating,
        comment=cleaned_comment,
        physical_facilities_rating=physical_facilities_rating,
        teacher_quality_rating=teacher_quality_rating,
        transportation_rating=transportation_rating,
        spam_score=spam_score,
        is_spam=spam_score > 0.7  # %70'den yüksek spam skoru varsa otomatik spam işaretle
    )
    db.session.add(pending_review)
    db.session.commit()

    return jsonify({
        'message': 'Yorumunuz gönderildi. Admin onayından sonra yayınlanacaktır.',
        'spam_detected': spam_score > 0.7
    }), 201

# Kullanıcı Aktivite Kaydı
@app.route('/api/user/activity', methods=['POST'])
def record_user_activity():
    data = request.json
    user_id = data.get('user_id')
    school_id = data.get('school_id')
    activity_type = data.get('activity_type')
    time_spent_seconds = data.get('time_spent_seconds', 0)
    search_query = data.get('search_query')

    if not all([user_id, school_id, activity_type]):
        if activity_type == 'search' and user_id and activity_type and search_query:
            new_activity = UserActivity(
                user_id=user_id,
                school_id=None,
                activity_type=activity_type,
                time_spent_seconds=time_spent_seconds,
                search_query=search_query
            )
            db.session.add(new_activity)
            db.session.commit()
            return jsonify({'message': 'Arama aktivitesi kaydedildi.'}), 201
        else:
            return jsonify({'message': 'Gerekli bilgiler eksik'}), 400

    new_activity = UserActivity(
        user_id=user_id,
        school_id=school_id,
        activity_type=activity_type,
        time_spent_seconds=time_spent_seconds,
        search_query=search_query
    )
    db.session.add(new_activity)
    db.session.commit()
    with app.app_context():
        recommendation_system.load_data(app)
        recommendation_system.preprocess_data()
    return jsonify({'message': 'Kullanıcı aktivitesi kaydedildi.'}), 201

# Kullanıcı Tercih Güncelleme
@app.route('/api/user/preferences', methods=['PUT'])
def update_user_preferences():
    data = request.json
    user_id = data.get('user_id')
    preferences = data.get('preferences')

    if not all([user_id, preferences]):
        return jsonify({'message': 'Kullanıcı ID ve tercihler gerekli'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    user.preferences = preferences
    db.session.commit()
    with app.app_context():
        recommendation_system.load_data(app)
        recommendation_system.preprocess_data()
    return jsonify({'message': 'Kullanıcı tercihleri güncellendi.'}), 200

@app.route('/api/users/<int:user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404
    return jsonify({'user_id': user.id, 'preferences': user.preferences}), 200

# Kullanıcı Kayıt ve Giriş
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Kullanıcı adı, e-posta ve şifre gerekli'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Kullanıcı adı veya e-posta zaten kullanımda'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Kullanıcı başarıyla kaydedildi.', 'user_id': new_user.id}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    print("🔐 Login request received")
    data = request.json
    print(f"🔐 Request data: {data}")

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful", "user_id": user.id, "username": user.username})
    else:
        return jsonify({"error": "Invalid email or password"}), 401



@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({
            'user_id': session['user_id'],
            'username': session.get('username'),
            'email': session.get('email')
        }), 200
    else:
        return jsonify({'message': 'Kullanıcı oturumu bulunamadı'}), 401

# Öneri API
@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    with app.app_context():
        recommendation_system.load_data(app)
        recommendation_system.preprocess_data()

    recommended_school_ids = recommendation_system.get_personalized_recommendations(app, user_id)
    recommended_schools = School.query.filter(School.id.in_(recommended_school_ids)).all()

    output = [{
        'id': school.id,
        'name': school.name,
        'city': school.city,
        'district': school.district,
        'price_range': school.price_range,
        'success_rate': school.success_rate,
        'average_rating': school.average_rating,
        'description': school.description,
        'features': school.features
    } for school in recommended_schools]
    return jsonify(output)

# --------- YARDIMCI FONKSİYONLAR ---------


def check_rate_limit(user_id, action, limit=5, window_minutes=60):
    """Rate limiting kontrolü"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    # Kullanıcının bu action için geçmiş isteklerini al
    key = f"{user_id}_{action}"
    requests = rate_limit_store[key]

    # Eski istekleri temizle
    rate_limit_store[key] = [req_time for req_time in requests if req_time > window_start]

    # Limit kontrolü
    if len(rate_limit_store[key]) >= limit:
        return False

    # Yeni isteği ekle
    rate_limit_store[key].append(now)
    return True

# --------- ADMIN API'LERİ ---------

# Admin kontrolü için yardımcı fonksiyon
def check_admin_permission(user_id):
    user = User.query.get(user_id)
    return user and user.is_admin

def calculate_review_quality_score(review):
    """Yorum kalitesi skorunu hesapla (0-100 arası)"""
    score = 0

    # Yorum uzunluğu (0-25 puan)
    comment_length = len(review.comment) if review.comment else 0
    if comment_length >= 100:
        score += 25
    elif comment_length >= 50:
        score += 20
    elif comment_length >= 20:
        score += 15
    elif comment_length >= 10:
        score += 10

    # Detaylı puanlar verilmiş mi (0-20 puan)
    detailed_ratings = [
        review.physical_facilities_rating,
        review.teacher_quality_rating,
        review.transportation_rating
    ]
    detailed_count = sum(1 for rating in detailed_ratings if rating and rating > 0)
    score += detailed_count * 7  # Her detaylı puan için 7 puan

    # Faydalı oy sayısı (0-30 puan)
    helpful_count = review.helpful_count or 0
    if helpful_count >= 10:
        score += 30
    elif helpful_count >= 5:
        score += 25
    elif helpful_count >= 2:
        score += 20
    elif helpful_count >= 1:
        score += 15

    # Yorum yaşı (0-15 puan) - Yeni yorumlar daha az puan
    from datetime import datetime, timedelta
    days_old = (datetime.utcnow() - review.timestamp).days
    if days_old <= 7:
        score += 15
    elif days_old <= 30:
        score += 12
    elif days_old <= 90:
        score += 8
    elif days_old <= 365:
        score += 5

    # Spam skoru düşürme (0 ile -20 arası)
    spam_penalty = int(review.spam_score * 20)
    score -= spam_penalty

    # 0-100 arası sınırla
    return max(0, min(100, score))

# Bekleyen yorumları getir (Admin)
@app.route('/api/admin/reviews/pending', methods=['GET'])
def get_pending_reviews():
    admin_id = request.args.get('admin_id')
    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    # Sadece is_spam = False olan pendingleri getir
    pending_reviews = PendingReview.query.filter_by(is_spam=False).order_by(PendingReview.timestamp.desc()).all()

    reviews_data = []
    for review in pending_reviews:
        user = User.query.get(review.user_id)
        school = School.query.get(review.school_id)
        reviews_data.append({
            'id': review.id,
            'user_id': review.user_id,
            'username': user.username if user else 'Bilinmeyen',
            'school_id': review.school_id,
            'school_name': school.name if school else 'Bilinmeyen',
            'rating': review.rating,
            'comment': review.comment,
            'timestamp': review.timestamp.isoformat(),
            'physical_facilities_rating': review.physical_facilities_rating,
            'teacher_quality_rating': review.teacher_quality_rating,
            'transportation_rating': review.transportation_rating,
            'spam_score': review.spam_score,
            'is_spam': review.is_spam
        })

    return jsonify(reviews_data)

# Yorum onaylama (Admin)
@app.route('/api/admin/reviews/<int:review_id>/approve', methods=['POST'])
def approve_review(review_id):
    data = request.json
    admin_id = data.get('admin_id')

    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    # Pending review'ı bul
    pending_review = PendingReview.query.get(review_id)
    if not pending_review:
        return jsonify({'message': 'Bekleyen yorum bulunamadı'}), 404

    # Pending review'dan gerçek review'a taşı
    approved_review = Review(
        user_id=pending_review.user_id,
        school_id=pending_review.school_id,
        rating=pending_review.rating,
        comment=pending_review.comment,
        physical_facilities_rating=pending_review.physical_facilities_rating,
        teacher_quality_rating=pending_review.teacher_quality_rating,
        transportation_rating=pending_review.transportation_rating,
        is_moderated=True,
        moderated_by=admin_id,
        moderation_date=datetime.utcnow(),
        is_spam=False,
        spam_score=pending_review.spam_score,
        helpful_count=0
    )

    # Yeni review'ı ekle
    db.session.add(approved_review)

    # Pending review'ı sil
    db.session.delete(pending_review)

    db.session.commit()

    # Okul ortalama puanını güncelle
    school = School.query.get(approved_review.school_id)
    if school:
        approved_reviews = Review.query.filter_by(school_id=school.id, is_moderated=True).all()
        if approved_reviews:
            avg_rating = sum(r.rating for r in approved_reviews) / len(approved_reviews)
            school.average_rating = round(avg_rating, 1)
            db.session.commit()

    return jsonify({'message': 'Yorum onaylandı ve yayınlandı'}), 200

# Yorum reddetme (Admin)
@app.route('/api/admin/reviews/<int:review_id>/reject', methods=['POST'])
def reject_review(review_id):
    data = request.json
    admin_id = data.get('admin_id')

    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    # Pending review'ı bul
    pending_review = PendingReview.query.get(review_id)
    if not pending_review:
        return jsonify({'message': 'Bekleyen yorum bulunamadı'}), 404

    # Pending review'ı sil (reddedildi)
    db.session.delete(pending_review)
    db.session.commit()

    return jsonify({'message': 'Yorum reddedildi'}), 200

# Spam yorumları getir (Admin)
@app.route('/api/admin/reviews/spam', methods=['GET'])
def get_spam_reviews():
    admin_id = request.args.get('admin_id')
    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    # Sadece is_spam = True olan pendingleri getir
    spam_reviews = PendingReview.query.filter_by(is_spam=True).order_by(PendingReview.timestamp.desc()).all()

    reviews_data = []
    for review in spam_reviews:
        user = User.query.get(review.user_id)
        school = School.query.get(review.school_id)
        reviews_data.append({
            'id': review.id,
            'user_id': review.user_id,
            'username': user.username if user else 'Bilinmeyen',
            'school_id': review.school_id,
            'school_name': school.name if school else 'Bilinmeyen',
            'rating': review.rating,
            'comment': review.comment,
            'timestamp': review.timestamp.isoformat(),
            'physical_facilities_rating': review.physical_facilities_rating,
            'teacher_quality_rating': review.teacher_quality_rating,
            'transportation_rating': review.transportation_rating,
            'spam_score': review.spam_score,
            'is_spam': review.is_spam
        })

    return jsonify(reviews_data)

# Yorum yanıtı ekleme
@app.route('/api/reviews/<int:review_id>/reply', methods=['POST'])
def add_review_reply(review_id):
    data = request.json
    user_name = data.get('user_name')
    reply_text = data.get('reply_text')

    if not all([user_name, reply_text]):
        return jsonify({'message': 'Kullanıcı adı ve yanıt metni gerekli'}), 400

    # Review var mı kontrol et
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'message': 'Yorum bulunamadı'}), 404

    new_reply = ReviewReply(
        review_id=review_id,
        user_name=user_name,
        reply_text=reply_text,
        is_approved=False
    )

    db.session.add(new_reply)
    db.session.commit()

    return jsonify({'message': 'Yanıt admin onayına gönderildi'}), 201

# Bekleyen yanıtları getir (Admin)
@app.route('/api/admin/replies/pending', methods=['GET'])
def get_pending_replies():
    admin_id = request.args.get('admin_id')
    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    pending_replies = ReviewReply.query.filter_by(is_approved=False).order_by(ReviewReply.timestamp.desc()).all()

    replies_data = []
    for reply in pending_replies:
        review = Review.query.get(reply.review_id)
        school = School.query.get(review.school_id) if review else None
        replies_data.append({
            'id': reply.id,
            'review_id': reply.review_id,
            'user_name': reply.user_name,
            'reply_text': reply.reply_text,
            'timestamp': reply.timestamp.isoformat(),
            'original_comment': review.comment if review else 'Yorum bulunamadı',
            'school_name': school.name if school else 'Okul bulunamadı'
        })

    return jsonify(replies_data)

@app.route('/school-profile.html')
def school_profile():
    return render_template('school-profile.html')

# Yanıt onaylama (Admin)
@app.route('/api/admin/replies/<int:reply_id>/approve', methods=['POST'])
def approve_reply(reply_id):
    data = request.json
    admin_id = data.get('admin_id')

    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({'message': 'Yanıt bulunamadı'}), 404

    reply.is_approved = True
    reply.approved_by = admin_id
    reply.approval_date = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Yanıt onaylandı'}), 200

# Faydalı oy verme/geri alma
@app.route('/api/reviews/<int:review_id>/helpful', methods=['POST'])
def toggle_helpful_vote(review_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'message': 'Kullanıcı ID gerekli'}), 400

    # Review var mı kontrol et
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'message': 'Yorum bulunamadı'}), 404

    # Kullanıcının bu yoruma daha önce oy verip vermediğini kontrol et
    existing_vote = HelpfulVote.query.filter_by(user_id=user_id, review_id=review_id).first()

    if existing_vote:
        # Oy varsa kaldır
        db.session.delete(existing_vote)
        review.helpful_count = max(0, review.helpful_count - 1)
        action = 'removed'
    else:
        # Oy yoksa ekle
        new_vote = HelpfulVote(user_id=user_id, review_id=review_id)
        db.session.add(new_vote)
        review.helpful_count += 1
        action = 'added'

    db.session.commit()

    return jsonify({
        'action': action,
        'helpful_count': review.helpful_count,
        'user_voted': action == 'added'
    }), 200

# Kullanıcının oy verdiği yorumları getir
@app.route('/api/users/<int:user_id>/helpful-votes', methods=['GET'])
def get_user_helpful_votes(user_id):
    votes = HelpfulVote.query.filter_by(user_id=user_id).all()
    review_ids = [vote.review_id for vote in votes]
    return jsonify({'voted_reviews': review_ids}), 200

# Okul yorumlarını getir (gelişmiş sıralama algoritması ile)
@app.route('/api/reviews/school/<int:school_id>', methods=['GET'])
def get_school_reviews(school_id):
    sort_by = request.args.get('sort', 'rating')  # quality, newest, oldest, rating

    # Sadece onaylanmış yorumları getir
    reviews = Review.query.filter_by(school_id=school_id, is_moderated=True).all()

    reviews_data = []
    for review in reviews:
        user = User.query.get(review.user_id)

        # Yorum kalitesi skoru hesapla
        quality_score = calculate_review_quality_score(review)

        reviews_data.append({
            'id': review.id,
            'user_id': review.user_id,
            'username': user.username if user else 'Anonim',
            'rating': review.rating,
            'comment': review.comment,
            'timestamp': review.timestamp.isoformat(),
            'physical_facilities_rating': review.physical_facilities_rating,
            'teacher_quality_rating': review.teacher_quality_rating,
            'transportation_rating': review.transportation_rating,
            'helpful_count': review.helpful_count or 0,
            'quality_score': quality_score
        })

    # Sıralama algoritması
    if sort_by == 'quality':
        reviews_data.sort(key=lambda x: x['quality_score'], reverse=True)
    elif sort_by == 'newest':
        reviews_data.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == 'oldest':
        reviews_data.sort(key=lambda x: x['timestamp'])
    elif sort_by == 'rating':
        reviews_data.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'helpful':
        reviews_data.sort(key=lambda x: x['helpful_count'], reverse=True)

    return jsonify(reviews_data), 200

# Yorum bildirme
@app.route('/api/reviews/<int:review_id>/report', methods=['POST'])
def report_review(review_id):
    data = request.json
    user_id = data.get('user_id')
    reason = data.get('reason', 'Uygunsuz içerik')

    if not user_id:
        return jsonify({'message': 'Kullanıcı ID gerekli'}), 400

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'message': 'Yorum bulunamadı'}), 404

    # Yorumu spam olarak işaretle ve spam skorunu artır
    review.spam_score = min(review.spam_score + 0.3, 1.0)
    if review.spam_score >= 0.7:
        review.is_spam = True

    db.session.commit()

    return jsonify({
        'message': 'Yorum bildirildi, inceleme için teşekkür ederiz',
        'spam_score': review.spam_score,
        'is_spam': review.is_spam
    }), 200


# Yorum silme (Admin)
@app.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    data = request.get_json()
    admin_id = data.get('admin_id')

    # Admin yetkisi var mı kontrol et
    if not admin_id or not check_admin_permission(admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    # Önce spam veya pending tablosunda mı kontrol et
    review = PendingReview.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'message': 'Bekleyen yorum silindi'}), 200

    # Yoksa onaylanmış yorumlardan sil (isteğe bağlı)
    review = Review.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'message': 'Onaylanmış yorum silindi'}), 200

    return jsonify({'message': 'Yorum bulunamadı'}), 404




# Admin giriş
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'E-posta ve şifre gerekli'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    if not user.is_admin:
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    if not user.check_password(password):
        return jsonify({'message': 'Şifre hatalı'}), 401

    if not user.is_active:
        return jsonify({'message': 'Hesap deaktif'}), 403

    return jsonify({
        'message': 'Giriş başarılı',
        'admin_id': user.id,
        'admin_name': user.username,
        'admin_email': user.email
    }), 200

# Admin kullanıcı oluşturma
@app.route('/api/admin/create', methods=['POST'])
def create_admin():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    creator_admin_id = data.get('creator_admin_id')

    # Sadece mevcut adminler yeni admin oluşturabilir
    if creator_admin_id and not check_admin_permission(creator_admin_id):
        return jsonify({'message': 'Admin yetkisi gerekli'}), 403

    if not all([username, email, password]):
        return jsonify({'message': 'Kullanıcı adı, e-posta ve şifre gerekli'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Kullanıcı adı veya e-posta zaten kullanımda'}), 409

    new_admin = User(username=username, email=email, is_admin=True)
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Admin kullanıcı başarıyla oluşturuldu', 'user_id': new_admin.id}), 201

# Media Management Routes
@app.route('/api/schools/<int:school_id>/media', methods=['GET'])
def get_school_media(school_id):
    """Get all media for a school"""
    media = SchoolMedia.query.filter_by(school_id=school_id, is_active=True).order_by(SchoolMedia.order).all()
    return jsonify([{
        'id': m.id,
        'media_type': m.media_type,
        'title': m.title,
        'description': m.description,
        'url': m.url,
        'thumbnail_url': m.thumbnail_url,
        'order': m.order
    } for m in media])

@app.route('/api/schools/<int:school_id>/media', methods=['POST'])
@admin_required
def add_school_media(school_id):
    """Add new media to a school"""
    data = request.json
    
    # Validate required fields
    required_fields = ['media_type', 'url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Create new media
    new_media = SchoolMedia(
        school_id=school_id,
        media_type=data['media_type'],
        title=data.get('title'),
        description=data.get('description'),
        url=data['url'],
        thumbnail_url=data.get('thumbnail_url'),
        order=data.get('order', 0)
    )
    
    db.session.add(new_media)
    db.session.commit()
    
    return jsonify({
        'id': new_media.id,
        'message': 'Media added successfully'
    }), 201

@app.route('/api/schools/<int:school_id>/media/<int:media_id>', methods=['PUT'])
@admin_required
def update_school_media(school_id, media_id):
    """Update existing media"""
    media = SchoolMedia.query.get_or_404(media_id)
    if media.school_id != school_id:
        return jsonify({'error': 'Media not found for this school'}), 404
    
    data = request.json
    media.title = data.get('title', media.title)
    media.description = data.get('description', media.description)
    media.url = data.get('url', media.url)
    media.thumbnail_url = data.get('thumbnail_url', media.thumbnail_url)
    media.order = data.get('order', media.order)
    media.is_active = data.get('is_active', media.is_active)
    
    db.session.commit()
    return jsonify({'message': 'Media updated successfully'})

@app.route('/api/schools/<int:school_id>/media/<int:media_id>', methods=['DELETE'])
@admin_required
def delete_school_media(school_id, media_id):
    """Delete media (soft delete)"""
    media = SchoolMedia.query.get_or_404(media_id)
    if media.school_id != school_id:
        return jsonify({'error': 'Media not found for this school'}), 404
    
    media.is_active = False
    db.session.commit()
    return jsonify({'message': 'Media deleted successfully'})

# Teacher Profile Routes
@app.route('/api/schools/<int:school_id>/teachers', methods=['GET'])
def get_school_teachers(school_id):
    """Get all teachers for a school"""
    teachers = TeacherProfile.query.filter_by(school_id=school_id, is_active=True).order_by(TeacherProfile.order).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'title': t.title,
        'bio': t.bio,
        'photo_url': t.photo_url,
        'video_url': t.video_url,
        'specialties': t.specialties,
        'education': t.education,
        'experience_years': t.experience_years,
        'order': t.order
    } for t in teachers])

@app.route('/api/schools/<int:school_id>/teachers', methods=['POST'])
@admin_required
def add_teacher(school_id):
    """Add new teacher profile"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Create new teacher profile
    new_teacher = TeacherProfile(
        school_id=school_id,
        name=data['name'],
        title=data.get('title'),
        bio=data.get('bio'),
        photo_url=data.get('photo_url'),
        video_url=data.get('video_url'),
        specialties=data.get('specialties'),
        education=data.get('education'),
        experience_years=data.get('experience_years'),
        order=data.get('order', 0)
    )
    
    db.session.add(new_teacher)
    db.session.commit()
    
    return jsonify({
        'id': new_teacher.id,
        'message': 'Teacher profile added successfully'
    }), 201

@app.route('/api/schools/<int:school_id>/teachers/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(school_id, teacher_id):
    """Update existing teacher profile"""
    teacher = TeacherProfile.query.get_or_404(teacher_id)
    if teacher.school_id != school_id:
        return jsonify({'error': 'Teacher not found for this school'}), 404
    
    data = request.json
    teacher.name = data.get('name', teacher.name)
    teacher.title = data.get('title', teacher.title)
    teacher.bio = data.get('bio', teacher.bio)
    teacher.photo_url = data.get('photo_url', teacher.photo_url)
    teacher.video_url = data.get('video_url', teacher.video_url)
    teacher.specialties = data.get('specialties', teacher.specialties)
    teacher.education = data.get('education', teacher.education)
    teacher.experience_years = data.get('experience_years', teacher.experience_years)
    teacher.order = data.get('order', teacher.order)
    teacher.is_active = data.get('is_active', teacher.is_active)
    
    db.session.commit()
    return jsonify({'message': 'Teacher profile updated successfully'})

@app.route('/api/schools/<int:school_id>/teachers/<int:teacher_id>', methods=['DELETE'])
@admin_required
def delete_teacher(school_id, teacher_id):
    """Delete teacher profile (soft delete)"""
    teacher = TeacherProfile.query.get_or_404(teacher_id)
    if teacher.school_id != school_id:
        return jsonify({'error': 'Teacher not found for this school'}), 404
    
    teacher.is_active = False
    db.session.commit()
    return jsonify({'message': 'Teacher profile deleted successfully'})

# File upload route
@app.route('/api/upload', methods=['POST'])
@admin_required
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Process media file
        result = media_service.process_media(file)
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f'Error processing media: {str(e)}')
        return jsonify({'error': 'Error processing media'}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Media cleanup task
@app.cli.command('cleanup-media')
def cleanup_media():
    """Clean up old media files"""
    try:
        media_service.cleanup_old_media()
        print('Media cleanup completed successfully')
    except Exception as e:
        print(f'Error during media cleanup: {str(e)}')

if __name__ == '__main__':
    print("🚀 Flask uygulaması başlatılıyor...")
    print(f"📁 Frontend dizini: {FRONTEND_DIR}")
    print(f"🌐 Ana sayfa: http://127.0.0.1:5000")
    print(f"🛡️ Admin panel: http://127.0.0.1:5000/admin.html")
    app.run(debug=True, host='127.0.0.1', port=5000)
