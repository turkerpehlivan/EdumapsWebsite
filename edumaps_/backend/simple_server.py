#!/usr/bin/env python3
"""
Basit HTTP sunucusu - test amaçlı
"""

from flask import Flask, send_from_directory, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Frontend klasörünün yolu
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

print(f"Frontend dizini: {FRONTEND_DIR}")

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'main.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'API çalışıyor!',
        'backend': 'Simple Flask Server'
    })

@app.route('/api/schools')
def get_schools():
    from flask import request

    # Test verisi - Her okul için detaylı ve farklı bilgiler
    all_schools = [
        {
            'id': 1,
            'name': 'Balıkesir Bilnet Anaokulu',
            'city': 'Balıkesir',
            'district': 'Merkez',
            'address': 'Paşaalanı Mahallesi, Atatürk Caddesi No:45, Altıeylül/Balıkesir',
            'phone': '+90 266 245 67 89',
            'price_range': 'Orta',
            'monthly_fee': '1.500-2.500 TL',
            'average_rating': 4.2,
            'review_count': 18,
            'capacity': '15-20 öğrenci/sınıf',
            'age_groups': '3-6 yaş',
            'description': 'Modern eğitim anlayışı ile hizmet veren anaokulu. Deneyimli öğretmen kadrosu ve kaliteli eğitim programları ile çocuklarınızın gelişimini destekliyoruz.',
            'features': {'library': True, 'meal_service': True, 'transportation': True, 'playground': True, 'security_camera': True},
            'teachers': [
                {'name': 'Ayşe Demir', 'title': 'Okul Öncesi Öğretmeni', 'experience': '8 yıl', 'specialty': 'Oyun Tabanlı Öğrenme', 'education': 'Gazi Üniversitesi Okul Öncesi Öğretmenliği', 'achievements': ['Yılın Öğretmeni 2023', 'Montessori Sertifikası']},
                {'name': 'Mehmet Kaya', 'title': 'Beden Eğitimi Öğretmeni', 'experience': '5 yıl', 'specialty': 'Hareket Eğitimi', 'education': 'Ege Üniversitesi Beden Eğitimi', 'achievements': ['Çocuk Jimnastiği Uzmanı', 'İlk Yardım Sertifikası']},
                {'name': 'Fatma Özkan', 'title': 'Müzik Öğretmeni', 'experience': '12 yıl', 'specialty': 'Çocuk Şarkıları ve Ritim', 'education': 'İstanbul Üniversitesi Müzik Öğretmenliği', 'achievements': ['Orff Müzik Eğitimi Uzmanı', 'Piyano Performans Sertifikası']},
                {'name': 'Zehra Yıldız', 'title': 'Rehber Öğretmeni', 'experience': '6 yıl', 'specialty': 'Çocuk Psikolojisi', 'education': 'Ankara Üniversitesi Psikolojik Danışmanlık', 'achievements': ['Oyun Terapisi Uzmanı', 'Aile Danışmanlığı Sertifikası']}
            ]
        },
        {
            'id': 2,
            'name': 'İstanbul Çocuk Akademisi',
            'city': 'İstanbul',
            'district': 'Kadıköy',
            'address': 'Fenerbahçe Mahallesi, Bağdat Caddesi No:128, Kadıköy/İstanbul',
            'phone': '+90 216 348 92 15',
            'price_range': 'Yüksek',
            'monthly_fee': '4.500-6.000 TL',
            'average_rating': 4.7,
            'review_count': 32,
            'capacity': '12-15 öğrenci/sınıf',
            'age_groups': '2-6 yaş',
            'description': 'Çocuklarınızın yaratıcılığını ve sosyal becerilerini geliştiren özel eğitim programları sunuyoruz. İngilizce eğitim ve sanat atölyeleri ile fark yaratıyoruz.',
            'features': {'library': True, 'meal_service': True, 'playground': True, 'art_studio': True, 'english_program': True, 'swimming_pool': True},
            'teachers': [
                {'name': 'Dr. Elif Yılmaz', 'title': 'Okul Müdürü ve Okul Öncesi Uzmanı', 'experience': '15 yıl', 'specialty': 'Çocuk Gelişimi', 'education': 'Boğaziçi Üniversitesi Çocuk Gelişimi Doktorası', 'achievements': ['Uluslararası Erken Çocukluk Eğitimi Ödülü', 'Cambridge İngilizce Öğretmenliği Sertifikası']},
                {'name': 'Sarah Johnson', 'title': 'İngilizce Öğretmeni', 'experience': '7 yıl', 'specialty': 'Erken Yaş İngilizce', 'education': 'Oxford University TESOL Certificate', 'achievements': ['CELTA Sertifikası', 'Young Learners Specialist']},
                {'name': 'Zeynep Arslan', 'title': 'Sanat Öğretmeni', 'experience': '10 yıl', 'specialty': 'Yaratıcı Sanatlar', 'education': 'Mimar Sinan Güzel Sanatlar Üniversitesi', 'achievements': ['Çocuk Sanat Terapisi Uzmanı', 'Seramik Atölyesi Sertifikası']},
                {'name': 'Can Öztürk', 'title': 'Yüzme Antrenörü', 'experience': '6 yıl', 'specialty': 'Su Güvenliği ve Yüzme', 'education': 'Spor Bilimleri Fakültesi Antrenörlük', 'achievements': ['Milli Yüzücü (Eski)', 'Su Güvenliği Eğitmeni']},
                {'name': 'Aylin Kaya', 'title': 'Drama Öğretmeni', 'experience': '8 yıl', 'specialty': 'Yaratıcı Drama', 'education': 'Ankara Üniversitesi Tiyatro Bölümü', 'achievements': ['Çocuk Tiyatrosu Yönetmeni', 'Eğitici Drama Uzmanı']}
            ]
        },
        {
            'id': 3,
            'name': 'Ankara Montessori Okulu',
            'city': 'Ankara',
            'district': 'Çankaya',
            'address': 'Kızılay Mahallesi, Ziya Gökalp Caddesi No:67, Çankaya/Ankara',
            'phone': '+90 312 467 83 21',
            'price_range': 'Yüksek',
            'monthly_fee': '5.000-7.500 TL',
            'average_rating': 4.8,
            'review_count': 25,
            'capacity': '10-12 öğrenci/sınıf',
            'age_groups': '3-6 yaş',
            'description': 'Montessori eğitim metoduyla çocuklarınızın doğal öğrenme süreçlerini destekliyoruz. Bireysel gelişim odaklı yaklaşımımızla her çocuğun potansiyelini ortaya çıkarıyoruz.',
            'features': {'library': True, 'meal_service': True, 'montessori_materials': True, 'garden': True, 'organic_meals': True, 'multilingual': True},
            'teachers': [
                {'name': 'Prof. Dr. Meral Aksu', 'title': 'Montessori Uzmanı ve Müdür', 'experience': '20 yıl', 'specialty': 'Montessori Pedagojisi', 'education': 'Harvard University Montessori Eğitimi Doktorası', 'achievements': ['Uluslararası Montessori Derneği Üyesi', 'AMI Montessori Diploma']},
                {'name': 'Deniz Çelik', 'title': 'Montessori Öğretmeni', 'experience': '9 yıl', 'specialty': 'Pratik Yaşam Becerileri', 'education': 'Montessori Enstitüsü Sertifikası', 'achievements': ['3-6 Yaş Montessori Uzmanı', 'Çocuk Evi Lideri']},
                {'name': 'Maria Rodriguez', 'title': 'İspanyolca Öğretmeni', 'experience': '5 yıl', 'specialty': 'Çok Dilli Eğitim', 'education': 'Universidad de Barcelona Filoloji', 'achievements': ['DELE Sınav Komisyonu Üyesi', 'Çocuk İspanyolcası Uzmanı']},
                {'name': 'Ahmet Şen', 'title': 'Doğa Eğitimi Uzmanı', 'experience': '11 yıl', 'specialty': 'Bahçıvanlık ve Doğa Bilimi', 'education': 'Ege Üniversitesi Peyzaj Mimarlığı', 'achievements': ['Permakültür Tasarım Sertifikası', 'Organik Tarım Uzmanı']},
                {'name': 'Dr. Leyla Öz', 'title': 'Çocuk Gelişimi Uzmanı', 'experience': '13 yıl', 'specialty': 'Bireysel Gelişim', 'education': 'Hacettepe Üniversitesi Çocuk Gelişimi Doktorası', 'achievements': ['Montessori Gözlemci Sertifikası', 'Aile Eğitimi Uzmanı']}
            ]
        },
        {
            'id': 4,
            'name': 'İzmir Deniz Anaokulu',
            'city': 'İzmir',
            'district': 'Konak',
            'address': 'Alsancak Mahallesi, Kordon Boyu No:89, Konak/İzmir',
            'phone': '+90 232 421 56 78',
            'price_range': 'Orta',
            'monthly_fee': '2.800-3.500 TL',
            'average_rating': 4.3,
            'review_count': 22,
            'capacity': '16-18 öğrenci/sınıf',
            'age_groups': '3-6 yaş',
            'description': 'Deniz kenarında doğayla iç içe eğitim veren anaokulu. Deniz sporları ve doğa etkinlikleri ile çocuklarınızın fiziksel ve zihinsel gelişimini destekliyoruz.',
            'features': {'library': True, 'meal_service': True, 'sea_view': True, 'nature_activities': True, 'beach_access': True, 'sailing_program': True},
            'teachers': [
                {'name': 'Kaptan Serkan Deniz', 'title': 'Denizcilik Eğitmeni', 'experience': '13 yıl', 'specialty': 'Deniz Sporları ve Güvenlik', 'education': 'İstanbul Teknik Üniversitesi Gemi Mühendisliği', 'achievements': ['Kaptan Lisansı', 'Yelken Eğitmeni Sertifikası']},
                {'name': 'Gül Mavi', 'title': 'Okul Öncesi Öğretmeni', 'experience': '7 yıl', 'specialty': 'Doğa Temelli Öğrenme', 'education': 'Ege Üniversitesi Okul Öncesi Öğretmenliği', 'achievements': ['Doğa Eğitimi Uzmanı', 'Orman Okulu Sertifikası']},
                {'name': 'Okan Balık', 'title': 'Yüzme Antrenörü', 'experience': '9 yıl', 'specialty': 'Su Güvenliği', 'education': 'Spor Bilimleri Fakültesi', 'achievements': ['Milli Takım Antrenörü (Eski)', 'Can Kurtarma Eğitmeni']},
                {'name': 'Deniz Kum', 'title': 'Çevre Eğitimi Uzmanı', 'experience': '6 yıl', 'specialty': 'Deniz Ekolojisi', 'education': 'İzmir Katip Çelebi Üniversitesi Deniz Bilimleri', 'achievements': ['Deniz Biyolojisi Uzmanı', 'Çevre Koruma Sertifikası']},
                {'name': 'Ege Dalga', 'title': 'Müzik Öğretmeni', 'experience': '8 yıl', 'specialty': 'Deniz Şarkıları', 'education': 'Dokuz Eylül Üniversitesi Müzik Öğretmenliği', 'achievements': ['Halk Müziği Uzmanı', 'Gitar Performans Sertifikası']}
            ]
        },
        {
            'id': 5,
            'name': 'Balıkesir Güneş Anaokulu',
            'city': 'Balıkesir',
            'district': 'Karesi',
            'address': 'Toygar Mahallesi, İnönü Caddesi No:23, Karesi/Balıkesir',
            'phone': '+90 266 234 12 45',
            'price_range': 'Düşük',
            'monthly_fee': '1.200-1.800 TL',
            'average_rating': 4.0,
            'review_count': 15,
            'capacity': '18-22 öğrenci/sınıf',
            'age_groups': '3-6 yaş',
            'description': 'Uygun fiyatlarla kaliteli eğitim sunan anaokulu. Aile dostu yaklaşımımız ve sıcak ortamımızla çocuklarınızın mutlu bir eğitim almasını sağlıyoruz.',
            'features': {'meal_service': True, 'playground': True, 'family_events': True, 'affordable_fees': True, 'local_community': True},
            'teachers': [
                {'name': 'Hatice Güneş', 'title': 'Okul Müdürü ve Öğretmen', 'experience': '18 yıl', 'specialty': 'Aile Katılımlı Eğitim', 'education': 'Balıkesir Üniversitesi Okul Öncesi Öğretmenliği', 'achievements': ['Aile Eğitimi Uzmanı', 'Toplum Gönüllüsü Ödülü']},
                {'name': 'Mustafa Işık', 'title': 'Okul Öncesi Öğretmeni', 'experience': '4 yıl', 'specialty': 'Oyun ve Drama', 'education': 'Çanakkale Onsekiz Mart Üniversitesi', 'achievements': ['Drama Eğitimi Sertifikası', 'Genç Öğretmen Ödülü']},
                {'name': 'Sevgi Yıldız', 'title': 'Yardımcı Öğretmen', 'experience': '8 yıl', 'specialty': 'Çocuk Bakımı', 'education': 'Açık Öğretim Çocuk Gelişimi', 'achievements': ['İlk Yardım Sertifikası', 'Çocuk Bakımı Uzmanı']},
                {'name': 'Nurcan Ay', 'title': 'Müzik Öğretmeni', 'experience': '6 yıl', 'specialty': 'Halk Oyunları', 'education': 'Balıkesir Üniversitesi Müzik Öğretmenliği', 'achievements': ['Halk Oyunları Eğitmeni', 'Bağlama Sertifikası']},
                {'name': 'Hasan Ay', 'title': 'Güvenlik Görevlisi', 'experience': '12 yıl', 'specialty': 'Okul Güvenliği', 'education': 'Güvenlik Görevlisi Sertifikası', 'achievements': ['Çocuk Güvenliği Uzmanı', 'İlk Yardım Eğitmeni']}
            ]
        }
    ]

    # Filtreleme parametreleri
    query = request.args.get('query', '').lower()
    city = request.args.get('city', '')
    district = request.args.get('district', '')

    filtered_schools = all_schools

    # Arama sorgusu filtresi
    if query:
        filtered_schools = [
            school for school in filtered_schools
            if query in school['name'].lower() or
               query in school['description'].lower() or
               query in school['city'].lower() or
               query in school['district'].lower()
        ]

    # Şehir filtresi
    if city:
        filtered_schools = [
            school for school in filtered_schools
            if school['city'] == city
        ]

    # İlçe filtresi
    if district:
        filtered_schools = [
            school for school in filtered_schools
            if school['district'] == district
        ]

    return jsonify(filtered_schools)

@app.route('/api/schools/<int:school_id>')
def get_school_detail(school_id):
    # Tüm okulları al
    all_schools_response = get_schools()
    all_schools = all_schools_response.get_json()

    # Belirtilen ID'ye sahip okulu bul
    school = next((s for s in all_schools if s['id'] == school_id), None)

    if not school:
        return jsonify({'message': 'Okul bulunamadı'}), 404

    # Her okul için farklı yorumlar
    school_reviews = {
        1: [  # Balıkesir Bilnet Anaokulu
            {
                'id': 1,
                'user_id': 1,
                'user_name': 'Ayşe Mutlu',
                'rating': 5,
                'comment': 'Çocuğum bu okula gitmeye başladığından beri çok mutlu. Öğretmenler gerçekten ilgili ve deneyimli. Özellikle Ayşe öğretmenin oyun tabanlı öğrenme yaklaşımı harika! Zehra öğretmenin psikolojik desteği de çok değerli.',
                'timestamp': '2024-01-15T10:30:00',
                'helpful_count': 12
            },
            {
                'id': 2,
                'user_id': 2,
                'user_name': 'Mehmet Kaya',
                'rating': 4,
                'comment': 'Fiyat performans açısından çok iyi. Yemekleri de kaliteli ve çeşitli. Mehmet öğretmenin beden eğitimi dersleri çocuğumun motor becerilerini çok geliştirdi. Sadece bahçe biraz daha büyük olabilirdi.',
                'timestamp': '2024-01-10T14:20:00',
                'helpful_count': 8
            },
            {
                'id': 3,
                'user_id': 3,
                'user_name': 'Zeynep Arslan',
                'rating': 4,
                'comment': 'Servis hizmeti çok düzenli ve güvenli. Şoförler çok dikkatli. Fatma öğretmenin müzik dersleri sayesinde çocuğum evde sürekli şarkı söylüyor. Çok memnunuz!',
                'timestamp': '2024-01-05T09:15:00',
                'helpful_count': 6
            },
            {
                'id': 4,
                'user_id': 4,
                'user_name': 'Emre Demir',
                'rating': 5,
                'comment': 'Balıkesir\'de bu kalitede bir anaokulu bulmak gerçekten zor. Öğretmenlerin deneyimi ve samimiyeti çok etkileyici. Çocuğumun sosyal becerileri çok gelişti.',
                'timestamp': '2024-01-02T16:45:00',
                'helpful_count': 9
            }
        ],
        2: [  # İstanbul Çocuk Akademisi
            {
                'id': 5,
                'user_id': 5,
                'user_name': 'Elif Yılmaz',
                'rating': 5,
                'comment': 'İngilizce programı gerçekten çok başarılı. 4 yaşındaki kızım artık basit İngilizce cümleler kurabiliyor. Sarah öğretmenin metodolojisi ve Dr. Elif hanımın liderliği mükemmel. Yüzme dersleri de çok profesyonel.',
                'timestamp': '2024-01-20T16:45:00',
                'helpful_count': 18
            },
            {
                'id': 6,
                'user_id': 6,
                'user_name': 'Can Öztürk',
                'rating': 5,
                'comment': 'Sanat atölyesi çok güzel düzenlenmiş. Zeynep öğretmenin yaratıcı sanatlar dersleri sayesinde çocuğumun hayal gücü inanılmaz gelişti. Yüzme havuzu ve güvenlik önlemleri de mükemmel.',
                'timestamp': '2024-01-18T11:20:00',
                'helpful_count': 15
            },
            {
                'id': 7,
                'user_id': 7,
                'user_name': 'Selin Demir',
                'rating': 4,
                'comment': 'Kaliteli eğitim veriyorlar ama fiyatı biraz yüksek. Aylin öğretmenin drama dersleri çocuğumun özgüvenini çok artırdı. Genel olarak çok memnunuz.',
                'timestamp': '2024-01-12T13:30:00',
                'helpful_count': 11
            },
            {
                'id': 8,
                'user_id': 8,
                'user_name': 'Murat Kaya',
                'rating': 5,
                'comment': 'İstanbul\'da bu seviyede bir okul bulmak çok zor. Özellikle çok dilli eğitim programı ve bireysel ilgi harika. Can antrenörün yüzme dersleri de çok güvenli.',
                'timestamp': '2024-01-08T09:20:00',
                'helpful_count': 13
            }
        ],
        3: [  # Ankara Montessori Okulu
            {
                'id': 7,
                'user_id': 7,
                'user_name': 'Dr. Ahmet S.',
                'rating': 5,
                'comment': 'Montessori metodunu gerçekten doğru uyguluyorlar. Çocuğumun bağımsızlığı ve öz güveni çok gelişti. Prof. Meral hanımın deneyimi çok değerli.',
                'timestamp': '2024-01-25T08:45:00',
                'helpful_count': 15
            },
            {
                'id': 8,
                'user_id': 8,
                'user_name': 'Pınar M.',
                'rating': 5,
                'comment': 'Organik yemekler ve çok dilli eğitim programı harika. Bahçede yaptıkları etkinlikler çocuğumu doğaya çok yakınlaştırdı.',
                'timestamp': '2024-01-22T15:10:00',
                'helpful_count': 11
            },
            {
                'id': 9,
                'user_id': 9,
                'user_name': 'Emre K.',
                'rating': 4,
                'comment': 'Eğitim kalitesi çok yüksek. Sadece fiyatı biraz pahalı ama kaliteye değer.',
                'timestamp': '2024-01-15T12:00:00',
                'helpful_count': 7
            }
        ],
        4: [  # İzmir Deniz Anaokulu
            {
                'id': 10,
                'user_id': 10,
                'user_name': 'Deniz B.',
                'rating': 5,
                'comment': 'Deniz kenarında olmak çocuğum için harika! Yelken programı çok eğlenceli. Kaptan Serkan çok deneyimli.',
                'timestamp': '2024-01-28T14:30:00',
                'helpful_count': 10
            },
            {
                'id': 11,
                'user_id': 11,
                'user_name': 'Gökhan M.',
                'rating': 4,
                'comment': 'Doğa etkinlikleri çok güzel. Çocuğum deniz canlıları hakkında çok şey öğrendi. Manzara da muhteşem!',
                'timestamp': '2024-01-24T10:15:00',
                'helpful_count': 8
            },
            {
                'id': 12,
                'user_id': 12,
                'user_name': 'Aylin K.',
                'rating': 4,
                'comment': 'Yüzme dersleri çok iyi organize edilmiş. Güvenlik önlemleri de yeterli.',
                'timestamp': '2024-01-20T16:45:00',
                'helpful_count': 6
            }
        ],
        5: [  # Balıkesir Güneş Anaokulu
            {
                'id': 13,
                'user_id': 13,
                'user_name': 'Fatma G.',
                'rating': 4,
                'comment': 'Uygun fiyatlı ve kaliteli. Hatice öğretmen çok deneyimli ve çocukları çok seviyor. Aile etkinlikleri de güzel.',
                'timestamp': '2024-01-30T09:20:00',
                'helpful_count': 7
            },
            {
                'id': 14,
                'user_id': 14,
                'user_name': 'Hasan Y.',
                'rating': 4,
                'comment': 'Mahalle okulu olmasına rağmen çok iyi hizmet veriyorlar. Çocuğum arkadaşlarıyla çok iyi anlaşıyor.',
                'timestamp': '2024-01-26T11:30:00',
                'helpful_count': 5
            },
            {
                'id': 15,
                'user_id': 15,
                'user_name': 'Sevim A.',
                'rating': 3,
                'comment': 'Genel olarak memnunuz ama biraz daha modern ekipman olabilir.',
                'timestamp': '2024-01-18T14:45:00',
                'helpful_count': 3
            }
        ]
    }

    # Detaylı bilgiler ekle
    detailed_school = school.copy()
    detailed_school.update({
        'video_url': f'https://example.com/video/{school_id}',
        'virtual_tour_url': f'https://example.com/tour/{school_id}',
        'reviews': school_reviews.get(school_id, [])
    })

    return jsonify(detailed_school)

# Basit favoriler sistemi (memory'de)
user_favorites = {}

@app.route('/api/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = user_favorites.get(user_id, [])
    # Favori okul ID'lerini okul bilgileriyle birleştir
    with app.test_request_context():
        schools = get_schools().get_json()
    favorite_schools = [school for school in schools if school['id'] in favorites]
    return jsonify(favorite_schools)

@app.route('/api/users/<int:user_id>/favorites/<int:school_id>', methods=['POST'])
def add_to_favorites(user_id, school_id):
    if user_id not in user_favorites:
        user_favorites[user_id] = []

    if school_id not in user_favorites[user_id]:
        user_favorites[user_id].append(school_id)
        return jsonify({'message': 'Okul favorilere eklendi'}), 201
    else:
        return jsonify({'message': 'Bu okul zaten favorilerinizde'}), 400

@app.route('/api/users/<int:user_id>/favorites/<int:school_id>', methods=['DELETE'])
def remove_from_favorites(user_id, school_id):
    if user_id in user_favorites and school_id in user_favorites[user_id]:
        user_favorites[user_id].remove(school_id)
        return jsonify({'message': 'Okul favorilerden çıkarıldı'}), 200
    else:
        return jsonify({'message': 'Bu okul favorilerinizde değil'}), 404

@app.route('/api/users/<int:user_id>/favorites/<int:school_id>/check', methods=['GET'])
def check_favorite_status(user_id, school_id):
    is_favorite = user_id in user_favorites and school_id in user_favorites[user_id]
    return jsonify({'is_favorite': is_favorite}), 200

# Basit kullanıcı veritabanı (memory'de)
users_db = {
    'testuser': {'id': 1, 'password': 'test123', 'email': 'test@example.com'},
    'admin': {'id': 2, 'password': 'admin123', 'email': 'admin@example.com'}
}
next_user_id = 3

# Onay bekleyen yorumlar veritabanı
pending_reviews = [
    {
        'id': 1,
        'school_id': 1,
        'user_id': 1,
        'user_name': 'testuser',
        'rating': 5,
        'comment': 'Çok güzel bir okul, öğretmenleri çok ilgili ve başarılı.',
        'timestamp': '2024-01-15T10:30:00',
        'status': 'pending',
        'helpful_count': 0
    },
    {
        'id': 2,
        'school_id': 2,
        'user_id': 1,
        'user_name': 'testuser',
        'rating': 4,
        'comment': 'Genel olarak memnunum, sadece ulaşım biraz zor.',
        'timestamp': '2024-01-15T14:20:00',
        'status': 'pending',
        'helpful_count': 0
    }
]
approved_reviews = []
next_review_id = 3

# Basit login sistemi
@app.route('/api/login', methods=['POST'])
def login():
    from flask import request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Username veya email ile giriş yapılabilir
    user_found = None
    user_key = None

    # Önce username ile kontrol et
    if username in users_db and users_db[username]['password'] == password:
        user_found = users_db[username]
        user_key = username
    else:
        # Email ile kontrol et
        for key, user in users_db.items():
            if user['email'] == username and user['password'] == password:
                user_found = user
                user_key = key
                break

    if user_found:
        return jsonify({
            'message': 'Giriş başarılı',
            'user_id': user_found['id'],
            'username': user_key,
            'email': user_found['email']
        }), 200
    else:
        return jsonify({'message': 'Geçersiz kullanıcı adı/email veya şifre'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    from flask import request
    global next_user_id

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Kullanıcı adı, e-posta ve şifre gerekli'}), 400

    if username in users_db:
        return jsonify({'message': 'Bu kullanıcı adı zaten kullanımda'}), 409

    # Check if email already exists
    for user_data in users_db.values():
        if user_data['email'] == email:
            return jsonify({'message': 'Bu e-posta adresi zaten kullanımda'}), 409

    # Add new user
    users_db[username] = {
        'id': next_user_id,
        'password': password,
        'email': email
    }
    next_user_id += 1

    return jsonify({
        'message': 'Kayıt başarılı! Şimdi giriş yapabilirsiniz.',
        'user_id': users_db[username]['id']
    }), 201

# Yorum gönderme endpoint'i
@app.route('/api/schools/<int:school_id>/reviews', methods=['POST'])
def submit_review(school_id):
    from flask import request
    global next_review_id

    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([user_id, username, rating, comment]):
        return jsonify({'message': 'Tüm alanlar gerekli'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'message': 'Puan 1-5 arasında olmalı'}), 400

    # Yeni yorumu onay bekleyen listesine ekle
    new_review = {
        'id': next_review_id,
        'school_id': school_id,
        'user_id': user_id,
        'user_name': username,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending',
        'helpful_count': 0
    }

    pending_reviews.append(new_review)
    next_review_id += 1

    return jsonify({
        'message': 'Yorumunuz başarıyla gönderildi! Admin onayından sonra yayınlanacaktır.',
        'review_id': new_review['id']
    }), 201

# Admin - onay bekleyen yorumları getir
@app.route('/api/admin/pending-reviews', methods=['GET'])
def get_pending_reviews():
    return jsonify(pending_reviews), 200

# Admin - spam yorumları getir (şimdilik boş liste)
@app.route('/api/admin/reviews/spam', methods=['GET'])
def get_spam_reviews():
    # Şimdilik boş liste döndür, ileride spam detection eklenebilir
    return jsonify([]), 200

# Admin - yorumu onayla
@app.route('/api/admin/reviews/<int:review_id>/approve', methods=['POST'])
def approve_review(review_id):
    global pending_reviews, approved_reviews

    # Onay bekleyen yorumlar arasında bul
    review_to_approve = None
    for i, review in enumerate(pending_reviews):
        if review['id'] == review_id:
            review_to_approve = pending_reviews.pop(i)
            break

    if not review_to_approve:
        return jsonify({'message': 'Yorum bulunamadı'}), 404

    # Onaylanmış yorumlara ekle
    review_to_approve['status'] = 'approved'
    approved_reviews.append(review_to_approve)

    # İlgili okul verilerine de ekle
    school_id = review_to_approve['school_id']
    if 1 <= school_id <= len(schools):
        if 'reviews' not in schools[school_id - 1]:
            schools[school_id - 1]['reviews'] = []
        schools[school_id - 1]['reviews'].append(review_to_approve)

    return jsonify({'message': 'Yorum onaylandı'}), 200

# Admin - yorumu reddet
@app.route('/api/admin/reviews/<int:review_id>/reject', methods=['POST'])
def reject_review(review_id):
    global pending_reviews

    # Onay bekleyen yorumlar arasında bul ve sil
    for i, review in enumerate(pending_reviews):
        if review['id'] == review_id:
            pending_reviews.pop(i)
            return jsonify({'message': 'Yorum reddedildi'}), 200

    return jsonify({'message': 'Yorum bulunamadı'}), 404

if __name__ == '__main__':
    print("🚀 Basit HTTP sunucusu başlatılıyor...")
    print(f"📁 Frontend dizini: {FRONTEND_DIR}")
    print(f"🌐 Ana sayfa: http://127.0.0.1:3000")
    print(f"🔧 API test: http://127.0.0.1:3000/api/test")
    
    app.run(debug=True, host='127.0.0.1', port=3000)
