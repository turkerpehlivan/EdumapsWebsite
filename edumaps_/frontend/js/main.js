// frontend/js/main.js

const API_BASE_URL = 'http://127.0.0.1:5000/api'; // Flask backend adresiniz

let currentUserId = null;
let currentUsername = null;

// Sayfa yüklendiğinde çalışacak kodlar
document.addEventListener('DOMContentLoaded', function() {
    checkUserSession(); // Kullanıcı oturumunu kontrol et
    showSection('school-list-section'); // Başlangıçta okul listesini göster
    fetchSchools(); // Okul listesini çek
    fetchRecommendations(); // Önerileri çek (eğer kullanıcı girişliyse)
});

// Bölümler arası geçiş
function showSection(sectionId) {
    document.querySelectorAll('main section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');

    // Tercihler veya Auth bölümüne geçişte özel işlemler
    if (sectionId === 'preferences-section') {
        if (!currentUserId) {
            alert('Tercihlerinizi görmek için giriş yapmalısınız!');
            showSection('auth-section');
            return;
        }
        loadPreferences(currentUserId);
    } else if (sectionId === 'auth-section') {
        // Oturum açma/kayıt formlarını temizle
        document.getElementById('register-message').textContent = '';
        document.getElementById('login-message').textContent = '';
        document.getElementById('register-username').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('register-password').value = '';
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
    }
}

// Kullanıcı oturumunu kontrol et (Basit bir kontrol, gerçekte JWT gibi yöntemler kullanılır)
function checkUserSession() {
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');
    if (userId && username) {
        currentUserId = parseInt(userId);
        currentUsername = username;
        document.getElementById('auth-link').style.display = 'none';
        document.getElementById('user-info').style.display = 'inline';
        document.getElementById('current-username').textContent = username;
        fetchRecommendations(currentUserId); // Kullanıcı girişliyse önerileri çek
    } else {
        document.getElementById('auth-link').style.display = 'inline';
        document.getElementById('user-info').style.display = 'none';
        document.getElementById('recommendations-section').classList.add('hidden'); // Öneri bölümünü gizle
    }
}

// Çıkış Yap
function logout() {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    currentUserId = null;
    currentUsername = null;
    checkUserSession();
    alert('Çıkış yapıldı.');
    showSection('school-list-section'); // Ana sayfaya dön
    document.getElementById('recommendation-list').innerHTML = '<p>Öneriler için giriş yapmalısınız.</p>';
}

// Kullanıcı Kaydı
async function registerUser() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const messageDiv = document.getElementById('register-message');

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        const result = await response.json();
        messageDiv.textContent = result.message;
        messageDiv.style.color = response.ok ? 'green' : 'red';
        if (response.ok) {
            // Başarılı kayıttan sonra giriş yapmayı tetikleyebiliriz
            document.getElementById('login-username').value = username;
            document.getElementById('login-password').value = password;
            messageDiv.textContent += ' Şimdi giriş yapabilirsiniz.';
        }
    } catch (error) {
        console.error('Kayıt hatası:', error);
        messageDiv.textContent = 'Bir hata oluştu, lütfen tekrar deneyin.';
        messageDiv.style.color = 'red';
    }
}

// Kullanıcı Girişi
async function loginUser() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const messageDiv = document.getElementById('login-message');

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        messageDiv.textContent = result.message;
        messageDiv.style.color = response.ok ? 'green' : 'red';

        if (response.ok) {
            localStorage.setItem('userId', result.user_id);
            localStorage.setItem('username', result.username);
            checkUserSession();
            showSection('school-list-section'); // Giriş sonrası ana sayfaya yönlendir
        }
    } catch (error) {
        console.error('Giriş hatası:', error);
        messageDiv.textContent = 'Bir hata oluştu, lütfen tekrar deneyin.';
        messageDiv.style.color = 'red';
    }
}


// Okul Listesini Çekme
async function fetchSchools() {
    try {
        const response = await fetch(`${API_BASE_URL}/schools`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const schools = await response.json();
        renderSchools(schools, 'school-list'); // Tüm okulları render et
    } catch (error) {
        console.error('Okulları çekerken hata oluştu:', error);
        document.getElementById('school-list').innerHTML = '<p>Okullar yüklenemedi. Lütfen daha sonra tekrar deneyin.</p>';
    }
}

// Okul Arama ve Filtreleme
async function searchSchools() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const city = document.getElementById('city-filter').value;
    const district = document.getElementById('district-filter').value;

    try {
        // Statik okul verileri
        const allSchools = [
            {
                id: 1,
                name: "Atatürk İlkokulu",
                city: "İstanbul",
                district: "Kadıköy",
                description: "Modern eğitim anlayışı ile öğrencilerimizi geleceğe hazırlayan köklü bir eğitim kurumu.",
                price_range: "Devlet Okulu",
                success_rate: 92,
                average_rating: 4.5
            },
            {
                id: 2,
                name: "Cumhuriyet Ortaokulu",
                city: "İstanbul",
                district: "Beşiktaş",
                description: "Öğrenci merkezli eğitim yaklaşımı ile her öğrencinin potansiyelini keşfetmesine yardımcı olan dinamik bir ortaokul.",
                price_range: "Devlet Okulu",
                success_rate: 88,
                average_rating: 4.2
            },
            {
                id: 3,
                name: "Gazi Lisesi",
                city: "İstanbul",
                district: "Şişli",
                description: "Üniversite hazırlık sürecinde öğrencilerimize en iyi desteği sağlayan akademik başarı odaklı lise.",
                price_range: "Devlet Okulu",
                success_rate: 95,
                average_rating: 4.7
            },
            {
                id: 4,
                name: "Mesleki ve Teknik Anadolu Lisesi",
                city: "İstanbul",
                district: "Üsküdar",
                description: "Meslek hayatına yönelik pratik eğitim veren, sektör ihtiyaçlarına uygun donanımlı bireyler yetiştiren teknik lise.",
                price_range: "Devlet Okulu",
                success_rate: 85,
                average_rating: 4.1
            },
            {
                id: 5,
                name: "Özel Bilim Koleji",
                city: "İstanbul",
                district: "Etiler",
                description: "İnovatif eğitim metodları ve bireysel gelişim odaklı yaklaşımla öğrencilerimizin akademik ve sosyal becerilerini geliştiren özel kolej.",
                price_range: "15.000 - 25.000 TL",
                success_rate: 98,
                average_rating: 4.9
            }
        ];

        // Filtreleme
        let filteredSchools = allSchools.filter(school => {
            const matchesQuery = !query ||
                school.name.toLowerCase().includes(query) ||
                school.description.toLowerCase().includes(query);
            const matchesCity = !city || city === 'all' || school.city === city;
            const matchesDistrict = !district || district === 'all' || school.district === district;

            return matchesQuery && matchesCity && matchesDistrict;
        });

        renderSchools(filteredSchools, 'school-list');

        // Arama aktivitesini kaydet
        if (currentUserId) {
            recordUserActivity(currentUserId, null, 'search', 0, query || `${city} ${district}`);
        } else {
            console.log("Kullanıcı girişi yapılmadığı için arama aktivitesi kaydedilemedi.");
        }

    } catch (error) {
        console.error('Arama yaparken hata oluştu:', error);
        document.getElementById('school-list').innerHTML = '<p>Arama sonuçları yüklenemedi.</p>';
    }
}

// Okulları HTML'e render eden yardımcı fonksiyon
function renderSchools(schools, targetElementId) {
    const schoolListDiv = document.getElementById(targetElementId);
    schoolListDiv.innerHTML = ''; // İçeriği temizle

    if (schools.length === 0) {
        schoolListDiv.innerHTML = '<p>Gösterilecek okul bulunamadı.</p>';
        return;
    }

    schools.forEach(school => {
        const schoolCard = `
            <div class="school-card" data-school-id="${school.id}">
                <h3>${school.name}</h3>
                <p><strong>Şehir:</strong> ${school.city}, <strong>İlçe:</strong> ${school.district}</p>
                <p><strong>Fiyat Aralığı:</strong> ${school.price_range || 'Belirtilmemiş'}</p>
                <p><strong>Ortalama Puan:</strong> ${school.average_rating ? school.average_rating.toFixed(1) : 'Yok'}</p>
                <p>${school.description ? school.description.substring(0, 150) + '...' : 'Açıklama yok.'}</p>
                <button onclick="viewSchoolDetail(${school.id})">Detayları Gör</button>
            </div>
        `;
        schoolListDiv.innerHTML += schoolCard;
    });
}


// Okul Detaylarını Görüntüleme (Basit bir alert veya modal ile)
async function viewSchoolDetail(schoolId) {
    try {
        const response = await fetch(`${API_BASE_URL}/schools/${schoolId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const school = await response.json();

        // Basit bir detay gösterme (gerçekte modal veya yeni sayfa)
        let featuresHtml = '';
        if (school.features) {
            for (const [key, value] of Object.entries(school.features)) {
                if (value === true) {
                    featuresHtml += `<li>${key.replace(/_/g, ' ')}</li>`;
                }
            }
        }

        let reviewsHtml = '';
        if (school.reviews && school.reviews.length > 0) {
            reviewsHtml = '<h4>Yorumlar:</h4><ul>';
            school.reviews.forEach(review => {
                reviewsHtml += `<li>Puan: ${review.rating}/5 - "${review.comment || 'Yorum yok.'}" (Kullanıcı: ${review.user_id}, Tarih: ${new Date(review.timestamp).toLocaleDateString()})</li>`;
            });
            reviewsHtml += '</ul>';
        } else {
            reviewsHtml = '<p>Bu okul için henüz yorum yok.</p>';
        }


        const detailContent = `
            <h2>${school.name}</h2>
            <p><strong>Şehir:</strong> ${school.city}, ${school.district}</p>
            <p><strong>Açıklama:</strong> ${school.description || 'Yok'}</p>
            <p><strong>Fiyat Aralığı:</strong> ${school.price_range || 'Belirtilmemiş'}</p>
            <p><strong>Başarı Oranı:</strong> ${school.success_rate ? school.success_rate + '%' : 'Belirtilmemiş'}</p>
            <p><strong>Ortalama Veli Puanı:</strong> ${school.average_rating ? school.average_rating.toFixed(1) : 'Yok'}</p>
            ${featuresHtml ? `<h4>Özellikler:</h4><ul>${featuresHtml}</ul>` : ''}
            ${reviewsHtml}
            <button onclick="addReviewModal(${school.id})">Yorum Yap</button>
        `;
        // Bu içeriği bir modal (pop-up) içinde veya yeni bir sayfada gösterebilirsiniz.
        // Şimdilik basitçe alert ile gösterelim (tüm içeriği göstermeyebilir)
        alert(detailContent.replace(/<[^>]*>/g, '\n').replace(/\n\n+/g, '\n')); // HTML etiketlerini kaldırıp alertte göster

        // Kullanıcı aktivitesini kaydet (Okul Görüntüleme)
        if (currentUserId) {
            // Gerçek uygulamada, kullanıcının sayfada kaldığı süreyi de ölçüp göndermelisiniz.
            recordUserActivity(currentUserId, schoolId, 'view', 10); // Örneğin 10 saniye görüntüleme
        } else {
            console.log("Kullanıcı girişi yapılmadığı için görüntüleme aktivitesi kaydedilemedi.");
        }

    } catch (error) {
        console.error('Okul detaylarını çekerken hata oluştu:', error);
        alert('Okul detayları yüklenemedi.');
    }
}

// Yorum Yapma Modalı (Basit bir prompt veya daha gelişmiş bir modal kullanılabilir)
function addReviewModal(schoolId) {
    if (!currentUserId) {
        alert('Yorum yapmak için giriş yapmalısınız!');
        return;
    }
    const rating = prompt('Bu okula 1-5 arası kaç puan verirsiniz?');
    if (!rating || isNaN(rating) || rating < 1 || rating > 5) {
        alert('Geçersiz puan! Lütfen 1-5 arası bir sayı girin.');
        return;
    }
    const comment = prompt('Yorumunuz (isteğe bağlı):');

    // Detaylı puanlamaları da isteyebiliriz
    const physFacilities = prompt('Fiziksel İmkanlar (1-5):');
    const teacherQuality = prompt('Öğretmen Kalitesi (1-5):');
    const transportation = prompt('Ulaşım (1-5):');

    addReview(currentUserId, schoolId, parseInt(rating), comment, parseInt(physFacilities), parseInt(teacherQuality), parseInt(transportation));
}

// Yorum Ekleme API Çağrısı
async function addReview(userId, schoolId, rating, comment, physFacilities, teacherQuality, transportation) {
    try {
        const response = await fetch(`${API_BASE_URL}/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                school_id: schoolId,
                rating: rating,
                comment: comment,
                physical_facilities_rating: physFacilities,
                teacher_quality_rating: teacherQuality,
                transportation_rating: transportation
            })
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error('Yorum eklerken hata oluştu:', error);
        alert('Yorum eklenirken bir sorun oluştu.');
    }
}

// Kullanıcı Aktivitesi Kayıt API Çağrısı
async function recordUserActivity(userId, schoolId, activityType, timeSpentSeconds = 0, searchQuery = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/activity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                school_id: schoolId,
                activity_type: activityType,
                time_spent_seconds: timeSpentSeconds,
                search_query: searchQuery
            })
        });
        const result = await response.json();
        console.log('Aktivite kaydedildi:', result.message);
    } catch (error) {
        console.error('Aktivite kaydederken hata oluştu:', error);
    }
}

// Tercihleri Yükleme
async function loadPreferences(userId) {
    const messageDiv = document.getElementById('preferences-message');
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/preferences`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const preferences = data.preferences;

        document.getElementById('pref-budget').value = preferences.budget || '';
        document.getElementById('pref-age-group').value = preferences.age_group || '';

        document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(checkbox => {
            const feature = checkbox.dataset.feature;
            checkbox.checked = preferences.priority_features && preferences.priority_features.includes(feature);
        });
        messageDiv.textContent = 'Tercihler yüklendi.';
        messageDiv.style.color = 'green';
    } catch (error) {
        console.error('Tercihleri yüklerken hata oluştu:', error);
        messageDiv.textContent = 'Tercihler yüklenemedi. Varsayılanlar gösteriliyor.';
        messageDiv.style.color = 'red';
    }
}

// Tercihleri Kaydetme
async function savePreferences() {
    if (!currentUserId) {
        alert('Tercihlerinizi kaydetmek için giriş yapmalısınız!');
        return;
    }
    const budget = document.getElementById('pref-budget').value;
    const ageGroup = document.getElementById('pref-age-group').value;
    const priorityFeatures = [];
    document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked').forEach(checkbox => {
        priorityFeatures.push(checkbox.dataset.feature);
    });

    const preferences = {
        budget: budget,
        age_group: ageGroup,
        priority_features: priorityFeatures
    };
    const messageDiv = document.getElementById('preferences-message');

    try {
        const response = await fetch(`${API_BASE_URL}/user/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: currentUserId, preferences: preferences })
        });
        const result = await response.json();
        messageDiv.textContent = result.message;
        messageDiv.style.color = response.ok ? 'green' : 'red';
        if (response.ok) {
            fetchRecommendations(currentUserId); // Tercihler değiştiyse önerileri güncelle
        }
    } catch (error) {
        console.error('Tercihleri kaydederken hata oluştu:', error);
        messageDiv.textContent = 'Tercihler kaydedilirken hata oluştu.';
        messageDiv.style.color = 'red';
    }
}


// Yapay Zeka Destekli Öneri Çekme
async function fetchRecommendations(userId = currentUserId) {
    const recommendationListDiv = document.getElementById('recommendation-list');
    if (!userId) {
        recommendationListDiv.innerHTML = '<p>Size özel önerileri görmek için giriş yapın ve tercihlerinizi kaydedin.</p>';
        document.getElementById('recommendations-section').classList.remove('hidden'); // Bölümü göster
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/recommendations/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const schools = await response.json();
        document.getElementById('recommendations-section').classList.remove('hidden'); // Bölümü göster

        if (schools.length === 0) {
            recommendationListDiv.innerHTML = '<p>Size uygun öneri bulunamadı. Daha fazla okul inceleyin veya tercihlerinizi güncelleyin.</p>';
        } else {
            renderSchools(schools, 'recommendation-list');
        }
    } catch (error) {
        console.error('Önerileri çekerken hata oluştu:', error);
        recommendationListDiv.innerHTML = '<p>Öneriler yüklenirken bir hata oluştu.</p>';
    }
}