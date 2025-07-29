# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
import json  # JSON alanları için gerekebilir

db = SQLAlchemy()


class SchoolMedia(db.Model):
    __tablename__ = 'school_media'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)  # '360_tour', 'photo', 'video'
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    url = db.Column(db.String(1024), nullable=False)  # URL or file path
    thumbnail_url = db.Column(db.String(1024))  # For videos and 360° tours
    order = db.Column(db.Integer, default=0)  # For ordering in gallery
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    school = db.relationship('School', back_populates='media')


class TeacherProfile(db.Model):
    __tablename__ = 'teacher_profiles'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))  # e.g., "Mathematics Teacher", "Department Head"
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(1024))
    video_url = db.Column(db.String(1024))  # Introduction video URL
    specialties = db.Column(db.JSON)  # List of specialties/subjects
    education = db.Column(db.JSON)  # Educational background
    experience_years = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)  # For display order

    # Relationship
    school = db.relationship('School', back_populates='teachers')

# Update School model to include new relationships
class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    price_range = db.Column(db.String(50))  # 'Low', 'Medium', 'High' gibi
    success_rate = db.Column(db.Float)  # Okulun başarı oranı (örneğin %90.5)
    average_rating = db.Column(db.Float)  # Veli yorumlarından gelen ortalama puan
    description = db.Column(db.Text)
    features = db.Column(db.JSON)  # SQL Server'da JSON tipi desteği var
    virtual_tour_url = db.Column(db.String(1024))  # 360° tour embed URL
    cover_photo_url = db.Column(db.String(1024))  # School cover photo
    logo_url = db.Column(db.String(1024))  # School logo
    video_url = db.Column(db.String(1024))
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'district': self.district,
            'description': self.description,
            'features': self.features,
            'success_rate': self.success_rate,
            'average_rating': self.average_rating,
            'virtual_tour_url': self.virtual_tour_url,
            'cover_photo_url': self.cover_photo_url,
            'logo_url': self.logo_url,
            'video_url': self.video_url,
        }

    # İlişkiler
    reviews = db.relationship('Review', backref='school', lazy=True)
    user_activities = db.relationship('UserActivity', backref='school', lazy=True)
    media = db.relationship('SchoolMedia', back_populates='school', lazy=True)
    teachers = db.relationship('TeacherProfile', back_populates='school', lazy=True)

    def update_average_rating(self):
        """Okula ait ortalama puanı günceller."""
        valid_reviews = [r.rating for r in self.reviews if r.rating]
        if valid_reviews:
            self.average_rating = sum(valid_reviews) / len(valid_reviews)
        else:
            self.average_rating = 0
    



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Şifrelerin hash'lenmiş hali
    preferences = db.Column(db.JSON,
                            default=lambda: {})  # Kullanıcı tercihleri (örn: {'budget': 'medium', 'age_group': 'primary'})
    is_admin = db.Column(db.Boolean, default=False)  # Admin yetkisi
    is_active = db.Column(db.Boolean, default=True)  # Kullanıcı aktif mi

    # İlişkiler
    user_activities = db.relationship('UserActivity', backref='user', lazy=True)
    reviews = db.relationship('Review', foreign_keys='Review.user_id', backref='user', lazy=True)
    moderated_reviews = db.relationship('Review', foreign_keys='Review.moderated_by', backref='moderator', lazy=True)

    def set_password(self, password):
        # Gerçek uygulamada şifre hash'leme için werkzeug.security.generate_password_hash gibi bir kütüphane kullanılmalı
        # Şimdilik basitçe kaydediyoruz, ancak bu GÜVENLİ DEĞİLDİR!
        self.password_hash = password

    def check_password(self, password):
        # Gerçek uygulamada hash'lenmiş şifre karşılaştırması yapılmalı
        return self.password_hash == password


class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'view', 'search', 'apply' gibi
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_seconds = db.Column(db.Integer, default=0)  # Görüntüleme süresi
    search_query = db.Column(db.Text)  # Eğer aktivite arama ise, arama sorgusu


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 arası puan
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_moderated = db.Column(db.Boolean, default=False)  # Yorumların yönetici onayı beklediği
    moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Hangi admin onayladı
    moderation_date = db.Column(db.DateTime, nullable=True)  # Onay tarihi
    is_spam = db.Column(db.Boolean, default=False)  # Spam olarak işaretlendi mi
    spam_score = db.Column(db.Float, default=0.0)  # Spam skoru (0-1 arası)

    physical_facilities_rating = db.Column(db.Integer)
    teacher_quality_rating = db.Column(db.Integer)
    transportation_rating = db.Column(db.Integer)
    helpful_count = db.Column(db.Integer, default=0)

    @staticmethod
    def clean_comment(comment):
        """XSS saldırılarına karşı yorum temizleme"""
        if not comment:
            return comment

        if BLEACH_AVAILABLE:
            # Bleach ile güvenli temizleme
            allowed_tags = []  # Hiç HTML tag'ine izin verme
            allowed_attributes = {}
            comment = bleach.clean(comment, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        else:
            # Fallback: Manuel temizleme
            # HTML etiketlerini kaldır
            comment = re.sub(r'<[^>]+>', '', comment)

            # Zararlı karakterleri temizle
            dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'onload=', 'onerror=']
            for char in dangerous_chars:
                comment = comment.replace(char, '')

        return comment.strip()

    @staticmethod
    def calculate_spam_score(comment):
        """Gelişmiş spam skoru hesaplama"""
        if not comment:
            return 0.0

        spam_score = 0.0
        comment_lower = comment.lower()

        # 1. URL ve link kontrolü
        url_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.tr']
        url_count = sum(1 for pattern in url_patterns if pattern in comment_lower)
        if url_count > 0:
            spam_score += 0.3

        # 2. Aşırı pozitif/negatif kelimeler
        positive_spam = ['mükemmel', 'harika', 'süper', 'en iyi', 'çok iyi', 'kesinlikle tavsiye']
        negative_spam = ['berbat', 'hiç beğenmedim', 'kesinlikle tavsiye etmem', 'çok kötü']

        positive_count = sum(1 for word in positive_spam if word in comment_lower)
        negative_count = sum(1 for word in negative_spam if word in comment_lower)

        if positive_count > 2 or negative_count > 2:
            spam_score += 0.2

        # 3. Uzunluk kontrolü
        if len(comment) < 10:
            spam_score += 0.4  # Çok kısa yorumlar şüpheli
        elif len(comment) > 1000:
            spam_score += 0.2  # Çok uzun yorumlar da şüpheli

        # 4. Tekrarlayan karakterler
        char_repetition = max(comment.count(char) for char in set(comment) if char.isalpha())
        if char_repetition > 5:
            spam_score += 0.2

        # 5. Büyük harf kullanımı
        upper_ratio = sum(1 for c in comment if c.isupper()) / len(comment)
        if upper_ratio > 0.5:  # %50'den fazla büyük harf
            spam_score += 0.2

        # 6. Sayı yoğunluğu
        digit_ratio = sum(1 for c in comment if c.isdigit()) / len(comment)
        if digit_ratio > 0.3:  # %30'dan fazla sayı
            spam_score += 0.1

        # 7. Özel karakter yoğunluğu
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        special_ratio = sum(1 for c in comment if c in special_chars) / len(comment)
        if special_ratio > 0.2:  # %20'den fazla özel karakter
            spam_score += 0.1

        # 8. Tekrarlayan kelimeler
        words = comment_lower.split()
        if len(words) > 0:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

            max_word_count = max(word_counts.values()) if word_counts else 0
            if max_word_count > 3:  # Aynı kelime 3'ten fazla tekrar
                spam_score += 0.1

        return min(spam_score, 1.0)  # 0-1 arası sınırla


    @classmethod
    def create_review(cls, user_id, school_id, rating, comment):
        """Yeni yorum oluşturup temizleme ve spam skorunu hesaplar."""
        clean_comment = cls.clean_comment(comment)
        spam_score = cls.calculate_spam_score(clean_comment)
        is_spam = spam_score > 0.5

        review = cls(
                user_id=user_id,
                school_id=school_id,
                rating=rating,
                comment=clean_comment,
                spam_score=spam_score,
                is_spam=is_spam
            )
        db.session.add(review)
        return review

class ReviewReply(db.Model):
    __tablename__ = 'review_replies'
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)

    # Relationship
    review = db.relationship('Review', backref='replies')


class HelpfulVote(db.Model):
    __tablename__ = 'helpful_votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint - bir kullanıcı bir yoruma sadece bir kez faydalı diyebilir
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='unique_user_review_vote'),)


class PendingReview(db.Model):
    __tablename__ = 'pending_reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 arası puan
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Detaylı puanlar
    physical_facilities_rating = db.Column(db.Integer)
    teacher_quality_rating = db.Column(db.Integer)
    transportation_rating = db.Column(db.Integer)

    # Spam detection
    is_spam = db.Column(db.Boolean, default=False)
    spam_score = db.Column(db.Float, default=0.0)

    # Relationships
    user = db.relationship('User', backref='pending_reviews')
    school = db.relationship('School', backref='pending_reviews')

    @staticmethod
    def clean_comment(comment):
        """Yorumu temizle ve XSS koruması uygula"""
        if not comment:
            return comment

        import re
        import html

        # HTML encode et
        comment = html.escape(comment)

        # Zararlı script taglerini temizle
        comment = re.sub(r'<script[^>]*>.*?</script>', '', comment, flags=re.IGNORECASE | re.DOTALL)
        comment = re.sub(r'<iframe[^>]*>.*?</iframe>', '', comment, flags=re.IGNORECASE | re.DOTALL)
        comment = re.sub(r'javascript:', '', comment, flags=re.IGNORECASE)
        comment = re.sub(r'on\w+\s*=', '', comment, flags=re.IGNORECASE)

        # Fazla boşlukları temizle
        comment = re.sub(r'\s+', ' ', comment)
        comment = comment.strip()

        # Maksimum uzunluk kontrolü
        if len(comment) > 1000:
            comment = comment[:1000] + '...'

        return comment

    @staticmethod
    def calculate_spam_score(comment):
        """Spam skorunu hesapla"""
        if not comment:
            return 0.0

        spam_indicators = [
            'spam', 'reklam', 'link', 'http', 'www', 'click', 'free', 'win', 'money',
            'çok ucuz', 'bedava', 'tıkla', 'kazanç', 'para kazan'
        ]

        comment_lower = comment.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in comment_lower)

        # Spam skoru hesapla (0-1 arası)
        spam_score = min(spam_count * 0.2, 1.0)

        # Çok kısa yorumlar şüpheli
        if len(comment.strip()) < 10:
            spam_score += 0.3

        # Çok uzun yorumlar da şüpheli
        if len(comment) > 1000:
            spam_score += 0.2

        return min(spam_score, 1.0)  # 0-1 arası sınırla