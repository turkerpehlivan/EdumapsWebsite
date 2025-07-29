#!/usr/bin/env python3
"""
Test admin kullanıcısı oluşturma scripti
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app, db
from backend.models import User, School, Review

def create_test_data():
    with app.app_context():
        # Veritabanını oluştur
        db.create_all()
        
        # Test admin kullanıcısı oluştur
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@edumaps.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("Admin kullanıcısı oluşturuldu: admin / admin123")
        
        # Test okulu oluştur
        test_school = School.query.filter_by(name='Balıkesir Bilnet Anaokulu').first()
        if not test_school:
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
            print("Test okulu oluşturuldu")
        
        # Test kullanıcısı oluştur
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            print("Test kullanıcısı oluşturuldu: testuser / test123")
        
        db.session.commit()
        
        # Test yorumları oluştur
        if Review.query.count() == 0:
            test_reviews = [
                {
                    'user_id': test_user.id,
                    'school_id': test_school.id,
                    'rating': 5,
                    'comment': 'Çok memnun kaldık. Öğretmenler çok ilgili ve okul temiz.',
                    'physical_facilities_rating': 5,
                    'teacher_quality_rating': 5,
                    'transportation_rating': 4
                },
                {
                    'user_id': test_user.id,
                    'school_id': test_school.id,
                    'rating': 4,
                    'comment': 'Genel olarak iyi bir okul. Sadece ulaşım biraz zor.',
                    'physical_facilities_rating': 4,
                    'teacher_quality_rating': 5,
                    'transportation_rating': 3
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
                    is_moderated=False,  # Admin onayı bekliyor
                    spam_score=spam_score,
                    is_spam=spam_score > 0.7
                )
                db.session.add(review)
            
            db.session.commit()
            print("Test yorumları oluşturuldu")
        
        print("\nTest verileri hazır!")
        print("Admin Panel: http://127.0.0.1:5000/admin.html")
        print("Ana Sayfa: http://127.0.0.1:5000")
        print("\nAdmin Giriş Bilgileri:")
        print("Admin ID: 1")
        print("Admin Adı: admin")

if __name__ == '__main__':
    create_test_data()
