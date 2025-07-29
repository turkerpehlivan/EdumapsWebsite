#!/usr/bin/env python3
"""
Admin login API test scripti
"""

import requests
import json

API_BASE = 'http://127.0.0.1:5000/api'

def test_admin_login():
    """Admin login API'sini test et"""
    print("🔐 Admin Login API Test")
    print("="*30)
    
    # Test 1: Doğru bilgilerle giriş
    print("\n1️⃣ Doğru bilgilerle giriş testi")
    login_data = {
        'email': 'admin@edumaps.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/login', json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Admin girişi başarılı!")
            admin_id = result.get('admin_id')
            
            # Test admin API'lerini
            print(f"\n2️⃣ Admin API test (Admin ID: {admin_id})")
            pending_response = requests.get(f'{API_BASE}/admin/reviews/pending?admin_id={admin_id}')
            print(f"Bekleyen yorumlar - Status: {pending_response.status_code}")
            if pending_response.status_code == 200:
                pending_reviews = pending_response.json()
                print(f"Bekleyen yorum sayısı: {len(pending_reviews)}")
            
        else:
            print("❌ Admin girişi başarısız!")
            
    except Exception as e:
        print(f"Hata: {e}")
    
    # Test 2: Yanlış şifre
    print("\n3️⃣ Yanlış şifre testi")
    wrong_login = {
        'email': 'admin@edumaps.com',
        'password': 'wrongpassword'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/login', json=wrong_login)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Hata: {e}")
    
    # Test 3: Olmayan email
    print("\n4️⃣ Olmayan email testi")
    nonexistent_login = {
        'email': 'nonexistent@example.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/login', json=nonexistent_login)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Hata: {e}")
    
    # Test 4: Normal kullanıcı ile admin girişi
    print("\n5️⃣ Normal kullanıcı ile admin girişi testi")
    user_login = {
        'email': 'test@example.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/login', json=user_login)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Hata: {e}")
    
    print("\n" + "="*50)
    print("✅ Admin Login API testleri tamamlandı!")
    print("\n🌐 Admin Panel: http://127.0.0.1:5000/admin.html")
    print("📧 Admin Email: admin@edumaps.com")
    print("🔑 Admin Şifre: admin123")

if __name__ == '__main__':
    test_admin_login()
