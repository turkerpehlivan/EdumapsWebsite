#!/usr/bin/env python3
"""
SQL Server Express için veritabanı migration scripti - Yeni kolonları ekler
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from config import Config
from models import db, User, School, Review, UserActivity, ReviewReply, HelpfulVote, PendingReview
from flask import Flask

# Flask app'i manuel olarak oluştur
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def migrate_database():
    """Veritabanı şemasını güncelle"""
    with app.app_context():
        try:
            # Mevcut tabloları kontrol et
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("Mevcut tablolar:", tables)
            
            # Reviews tablosundaki kolonları kontrol et
            if 'reviews' in tables:
                columns = [col['name'] for col in inspector.get_columns('reviews')]
                print("Reviews tablosundaki kolonlar:", columns)

                # Eksik kolonları ekle
                missing_columns = []
                required_columns = {
                    'moderated_by': 'INT NULL',
                    'moderation_date': 'DATETIME2 NULL',
                    'is_spam': 'BIT NOT NULL DEFAULT 0',
                    'spam_score': 'FLOAT NOT NULL DEFAULT 0.0',
                    'helpful_count': 'INT NOT NULL DEFAULT 0'
                }
                
                for col_name, col_type in required_columns.items():
                    if col_name not in columns:
                        missing_columns.append((col_name, col_type))
                
                if missing_columns:
                    print(f"Eksik kolonlar bulundu: {[col[0] for col in missing_columns]}")
                    
                    # SQL Server için ALTER TABLE komutları
                    for col_name, col_type in missing_columns:
                        try:
                            sql = f"ALTER TABLE reviews ADD {col_name} {col_type}"
                            print(f"Çalıştırılıyor: {sql}")
                            with db.engine.connect() as conn:
                                conn.execute(text(sql))
                                conn.commit()
                            print(f"✓ {col_name} kolonu eklendi")
                        except Exception as e:
                            print(f"✗ {col_name} kolonu eklenirken hata: {e}")
                else:
                    print("✓ Tüm gerekli kolonlar mevcut")
            
            # Users tablosunu kontrol et
            if 'users' in tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                print("Users tablosundaki kolonlar:", columns)
                
                missing_user_columns = []
                required_user_columns = {
                    'is_admin': 'BIT NOT NULL DEFAULT 0',
                    'is_active': 'BIT NOT NULL DEFAULT 1'
                }
                
                for col_name, col_type in required_user_columns.items():
                    if col_name not in columns:
                        missing_user_columns.append((col_name, col_type))
                
                if missing_user_columns:
                    print(f"Users tablosunda eksik kolonlar: {[col[0] for col in missing_user_columns]}")
                    
                    for col_name, col_type in missing_user_columns:
                        try:
                            sql = f"ALTER TABLE users ADD {col_name} {col_type}"
                            print(f"Çalıştırılıyor: {sql}")
                            with db.engine.connect() as conn:
                                conn.execute(text(sql))
                                conn.commit()
                            print(f"✓ {col_name} kolonu eklendi")
                        except Exception as e:
                            print(f"✗ {col_name} kolonu eklenirken hata: {e}")
                else:
                    print("✓ Users tablosunda tüm gerekli kolonlar mevcut")
            
            if 'schools' in tables:
                columns = [col['name'] for col in inspector.get_columns('schools')]
                print("Schools tablosundaki kolonlar:", columns)
                if 'video_url' not in columns:
                    try:
                        sql = "ALTER TABLE schools ADD video_url VARCHAR(1024) NULL"
                        print(f"Çalıştırılıyor: {sql}")
                        with db.engine.connect() as conn:
                            conn.execute(text(sql))
                            conn.commit()
                        print("✓ video_url kolonu eklendi")
                    except Exception as e:
                        print(f"✗ video_url kolonu eklenirken hata: {e}")
                else:
                    print("✓ video_url kolonu zaten mevcut")


            print("\n✓ Veritabanı migration tamamlandı!")
            
            
        except Exception as e:
            print(f"Migration sırasında hata: {e}")
            print("Veritabanını tamamen yeniden oluşturmayı deneyin...")
            
            # Tabloları yeniden oluştur
            try:
                print("Tabloları yeniden oluşturuluyor...")
                db.drop_all()
                db.create_all()
                print("✓ Tablolar yeniden oluşturuldu!")
                
                # Test verilerini ekle
                create_test_data()
                
            except Exception as e2:
                print(f"Tablolar yeniden oluşturulurken hata: {e2}")

def create_test_data():
    """Test verilerini oluştur"""
    try:
        # Admin kullanıcısı
        admin_user = User(
            username='admin',
            email='admin@edumaps.com',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Test kullanıcısı
        test_user = User(
            username='testuser',
            email='test@example.com',
            is_admin=False,
            is_active=True
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        
        # Test okulu
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
                'music_room': True
            }
        )
        db.session.add(test_school)
        
        db.session.commit()
        
        # Test yorumları
        test_reviews = [
            {
                'user_id': test_user.id,
                'school_id': test_school.id,
                'rating': 5,
                'comment': 'Çok memnun kaldık. Öğretmenler çok ilgili ve okul temiz.',
                'physical_facilities_rating': 5,
                'teacher_quality_rating': 5,
                'transportation_rating': 4,
                'is_moderated': False
            },
            {
                'user_id': test_user.id,
                'school_id': test_school.id,
                'rating': 4,
                'comment': 'Genel olarak iyi bir okul. Sadece ulaşım biraz zor.',
                'physical_facilities_rating': 4,
                'teacher_quality_rating': 5,
                'transportation_rating': 3,
                'is_moderated': False
            }
        ]
        
        for review_data in test_reviews:
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
                is_spam=spam_score > 0.7
            )
            db.session.add(review)
        
        db.session.commit()
        
        print("✓ Test verileri oluşturuldu!")
        print("\nGiriş Bilgileri:")
        print("Admin: admin / admin123")
        print("Kullanıcı: testuser / test123")
        
    except Exception as e:
        print(f"Test verileri oluşturulurken hata: {e}")
        db.session.rollback()

if __name__ == '__main__':
    migrate_database()
