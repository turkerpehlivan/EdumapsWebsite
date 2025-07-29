#!/usr/bin/env python3
"""
SQL Server Express için test verilerini oluşturma scripti
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from config import Config
from models import db, User, School, Review, UserActivity
from flask import Flask

# Flask app'i manuel olarak oluştur
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_test_data():
    """SQL Server Express için test verilerini oluştur"""
    with app.app_context():
        try:
            print("Test verileri oluşturuluyor...")
            
            # Mevcut verileri kontrol et
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("Admin kullanıcısı zaten mevcut")
            else:
                # Admin kullanıcısı oluştur
                admin_user = User(
                    username='admin',
                    email='admin@edumaps.com',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                print("✓ Admin kullanıcısı oluşturuldu: admin / admin123")
            
            # Test kullanıcısı oluştur
            existing_user = User.query.filter_by(username='testuser').first()
            if existing_user:
                print("Test kullanıcısı zaten mevcut")
            else:
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    is_admin=False,
                    is_active=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                print("✓ Test kullanıcısı oluşturuldu: testuser / test123")
            
            # Veli kullanıcısı oluştur
            existing_parent = User.query.filter_by(username='veli1').first()
            if existing_parent:
                print("Veli kullanıcısı zaten mevcut")
            else:
                parent_user = User(
                    username='veli1',
                    email='veli1@example.com',
                    is_admin=False,
                    is_active=True
                )
                parent_user.set_password('veli123')
                db.session.add(parent_user)
                print("✓ Veli kullanıcısı oluşturuldu: veli1 / veli123")
            
            db.session.commit()
            
            # Test okulu oluştur
            existing_school = School.query.filter_by(name='Balıkesir Bilnet Anaokulu').first()
            if existing_school:
                print("Test okulu zaten mevcut")
                test_school = existing_school
            else:
                test_school = School(
                    name='Balıkesir Bilnet Anaokulu',
                    city='Balıkesir',
                    district='Merkez',
                    price_range='Medium',
                    success_rate=85.5,
                    average_rating=4.2,
                    description='Modern eğitim anlayışı ile hizmet veren anaokulu',
                    features={
                        'playground': True,
                        'library': True,
                        'sports_hall': True,
                        'music_room': True,
                        'security_camera': True,
                        'meal_service': True
                    }
                )
                db.session.add(test_school)
                db.session.commit()
                print("✓ Test okulu oluşturuldu")
            
            # İkinci test okulu
            existing_school2 = School.query.filter_by(name='Ankara Modern Anaokulu').first()
            if not existing_school2:
                test_school2 = School(
                    name='Ankara Modern Anaokulu',
                    city='Ankara',
                    district='Çankaya',
                    price_range='High',
                    success_rate=92.0,
                    average_rating=4.5,
                    description='Çankaya\'da modern eğitim veren prestijli anaokulu',
                    features={
                        'playground': True,
                        'library': True,
                        'sports_hall': True,
                        'music_room': True,
                        'art_room': True,
                        'swimming_pool': True
                    }
                )
                db.session.add(test_school2)
                db.session.commit()
                print("✓ İkinci test okulu oluşturuldu")
            
            # Kullanıcıları tekrar al (ID'leri almak için)
            admin_user = User.query.filter_by(username='admin').first()
            test_user = User.query.filter_by(username='testuser').first()
            parent_user = User.query.filter_by(username='veli1').first()
            
            # Test yorumları oluştur
            existing_reviews = Review.query.filter_by(school_id=test_school.id).count()
            if existing_reviews == 0:
                test_reviews = [
                    {
                        'user_id': test_user.id,
                        'school_id': test_school.id,
                        'rating': 5,
                        'comment': 'Çocuğum bu okulda çok mutlu. Öğretmenler gerçekten ilgili ve okul çok temiz. Kesinlikle tavsiye ederim.',
                        'physical_facilities_rating': 5,
                        'teacher_quality_rating': 5,
                        'transportation_rating': 4,
                        'is_moderated': True  # Onaylanmış yorum
                    },
                    {
                        'user_id': parent_user.id,
                        'school_id': test_school.id,
                        'rating': 4,
                        'comment': 'Genel olarak memnunuz. Sadece ulaşım biraz zor ama okul kalitesi bunu telafi ediyor.',
                        'physical_facilities_rating': 4,
                        'teacher_quality_rating': 5,
                        'transportation_rating': 3,
                        'is_moderated': False  # Onay bekleyen yorum
                    },
                    {
                        'user_id': test_user.id,
                        'school_id': test_school.id,
                        'rating': 3,
                        'comment': 'Ortalama bir okul. Bazı konularda gelişim göstermesi gerekiyor.',
                        'physical_facilities_rating': 3,
                        'teacher_quality_rating': 4,
                        'transportation_rating': 3,
                        'is_moderated': False  # Onay bekleyen yorum
                    },
                    {
                        'user_id': parent_user.id,
                        'school_id': test_school.id,
                        'rating': 1,
                        'comment': 'Çok kötü çok berbat hiç beğenmedim kesinlikle tavsiye etmem www.spam-site.com',
                        'physical_facilities_rating': 1,
                        'teacher_quality_rating': 1,
                        'transportation_rating': 1,
                        'is_moderated': False  # Spam olarak işaretlenecek
                    }
                ]
                
                for review_data in test_reviews:
                    # Spam skoru hesapla
                    spam_score = Review.calculate_spam_score(review_data['comment'])
                    
                    review = Review(
                        user_id=review_data['user_id'],
                        school_id=review_data['school_id'],
                        rating=review_data['rating'],
                        comment=Review.clean_comment(review_data['comment']),
                        physical_facilities_rating=review_data['physical_facilities_rating'],
                        teacher_quality_rating=review_data['teacher_quality_rating'],
                        transportation_rating=review_data['transportation_rating'],
                        is_moderated=review_data['is_moderated'],
                        spam_score=spam_score,
                        is_spam=spam_score > 0.7  # %70'den yüksek spam skoru varsa spam işaretle
                    )
                    
                    # Onaylanmış yorumlar için moderator bilgisi ekle
                    if review_data['is_moderated']:
                        review.moderated_by = admin_user.id
                        review.moderation_date = db.func.now()
                    
                    db.session.add(review)
                
                db.session.commit()
                print("✓ Test yorumları oluşturuldu")
            else:
                print("Test yorumları zaten mevcut")
            
            # Test aktiviteleri oluştur
            existing_activities = UserActivity.query.filter_by(user_id=test_user.id).count()
            if existing_activities == 0:
                activities = [
                    {
                        'user_id': test_user.id,
                        'school_id': test_school.id,
                        'activity_type': 'view',
                        'time_spent_seconds': 120
                    },
                    {
                        'user_id': parent_user.id,
                        'school_id': test_school.id,
                        'activity_type': 'view',
                        'time_spent_seconds': 180
                    }
                ]
                
                for activity_data in activities:
                    activity = UserActivity(
                        user_id=activity_data['user_id'],
                        school_id=activity_data['school_id'],
                        activity_type=activity_data['activity_type'],
                        time_spent_seconds=activity_data['time_spent_seconds']
                    )
                    db.session.add(activity)
                
                db.session.commit()
                print("✓ Test aktiviteleri oluşturuldu")
            
            print("\n" + "="*50)
            print("✅ TÜM TEST VERİLERİ BAŞARIYLA OLUŞTURULDU!")
            print("="*50)
            print("\n🌐 Uygulama URL'leri:")
            print("Ana Sayfa: http://127.0.0.1:5000")
            print("Admin Panel: http://127.0.0.1:5000/admin.html")
            print("\n👤 Giriş Bilgileri:")
            print("Admin: admin / admin123")
            print("Test Kullanıcı: testuser / test123")
            print("Veli: veli1 / veli123")
            print("\n📊 Oluşturulan Veriler:")
            print(f"- {User.query.count()} kullanıcı")
            print(f"- {School.query.count()} okul")
            print(f"- {Review.query.count()} yorum")
            print(f"- {UserActivity.query.count()} aktivite")
            print(f"- {Review.query.filter_by(is_moderated=False).count()} onay bekleyen yorum")
            print(f"- {Review.query.filter_by(is_spam=True).count()} spam yorum")
            
        except Exception as e:
            print(f"❌ Test verileri oluşturulurken hata: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_test_data()
