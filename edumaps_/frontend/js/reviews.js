// Yorum Sistemi JavaScript

class ReviewSystem {
    constructor() {
        this.currentSchoolId = null;
        this.currentUserId = null;
        this.ratings = {
            overall: 0,
            physical_facilities: 0,
            teacher_quality: 0,
            transportation: 0
        };
        this.init();
    }

    init() {
        console.log('💬 ReviewSystem initializing...');
        this.setupEventListeners();
        this.loadReviews();
        console.log('✅ ReviewSystem initialized');
    }

    setupEventListeners() {
        // Yorum ekleme butonu
        const addReviewBtn = document.getElementById('addReviewBtn');
        if (addReviewBtn) {
            addReviewBtn.addEventListener('click', () => this.showReviewForm());
        }

        // Form gönderme
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', (e) => this.submitReview(e));
        }

        // Form iptal
        const cancelBtn = document.getElementById('cancelReviewBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideReviewForm());
        }

        // Yıldız puanlama
        this.setupStarRatings();
    }

    setupStarRatings() {
        const ratingGroups = document.querySelectorAll('.star-rating');
        
        ratingGroups.forEach(group => {
            const stars = group.querySelectorAll('.star');
            const ratingType = group.dataset.rating;
            
            stars.forEach((star, index) => {
                star.addEventListener('click', () => {
                    this.setRating(ratingType, index + 1);
                    this.updateStarDisplay(group, index + 1);
                });
                
                star.addEventListener('mouseenter', () => {
                    this.highlightStars(group, index + 1);
                });
            });
            
            group.addEventListener('mouseleave', () => {
                this.updateStarDisplay(group, this.ratings[ratingType]);
            });
        });
    }

    setRating(type, value) {
        this.ratings[type] = value;
    }

    updateStarDisplay(group, rating) {
        const stars = group.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.classList.toggle('active', index < rating);
            star.classList.remove('hover');
        });
    }

    highlightStars(group, rating) {
        const stars = group.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.classList.toggle('hover', index < rating);
        });
    }

    showReviewForm() {
        // Kullanıcı girişi kontrolü
        if (!this.currentUserId) {
            this.showAlert('Yorum yapmak için giriş yapmalısınız.', 'warning');
            return;
        }

        const formContainer = document.getElementById('reviewFormContainer');
        if (formContainer) {
            formContainer.style.display = 'block';
            formContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    hideReviewForm() {
        const formContainer = document.getElementById('reviewFormContainer');
        if (formContainer) {
            formContainer.style.display = 'none';
        }
        this.resetForm();
    }

    resetForm() {
        // Formu sıfırla
        const form = document.getElementById('reviewForm');
        if (form) {
            form.reset();
        }

        // Puanları sıfırla
        this.ratings = {
            overall: 0,
            physical_facilities: 0,
            teacher_quality: 0,
            transportation: 0
        };

        // Yıldızları sıfırla
        document.querySelectorAll('.star-rating').forEach(group => {
            this.updateStarDisplay(group, 0);
        });
    }

    async submitReview(event) {
        event.preventDefault();

        const comment = document.getElementById('reviewComment').value.trim();

        // Validasyon
        if (this.ratings.overall === 0) {
            this.showAlert('Lütfen genel puan verin.', 'error');
            return;
        }

        // Yorum uzunluk kontrolü
        if (comment.length < 10) {
            this.showAlert('Yorum en az 10 karakter olmalıdır.', 'error');
            return;
        }

        if (comment.length > 1000) {
            this.showAlert('Yorum en fazla 1000 karakter olabilir.', 'error');
            return;
        }

        // Güvenlik kontrolü
        if (!this.validateComment(comment)) {
            this.showAlert('Yorumunuz uygunsuz içerik barındırıyor.', 'error');
            return;
        }

        const reviewData = {
            user_id: this.currentUserId,
            school_id: this.currentSchoolId,
            rating: this.ratings.overall,
            comment: comment,
            physical_facilities_rating: this.ratings.physical_facilities || null,
            teacher_quality_rating: this.ratings.teacher_quality || null,
            transportation_rating: this.ratings.transportation || null
        };

        try {
            const response = await fetch(`${API_BASE_URL}/reviews`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reviewData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('Yorumunuz başarıyla gönderildi. Moderasyon sonrası yayınlanacaktır.', 'success');
                this.hideReviewForm();
                this.loadReviews(); // Yorumları yenile
            } else {
                this.showAlert(result.message || 'Yorum gönderilirken hata oluştu.', 'error');
            }
        } catch (error) {
            console.error('Yorum gönderme hatası:', error);
            this.showAlert('Bir hata oluştu, lütfen tekrar deneyin.', 'error');
        }
    }

    async loadReviews() {
        console.log('💬 loadReviews called, currentSchoolId:', this.currentSchoolId);

        if (!this.currentSchoolId) {
            console.log('💬 No school ID, setting default school ID to 1');
            this.currentSchoolId = 1; // Default school ID
        }

        const reviewsList = document.getElementById('reviewsList');
        console.log('💬 reviewsList element:', reviewsList);

        if (!reviewsList) {
            console.error('❌ reviewsList element not found!');
            return;
        }

        // Show sample reviews directly for demo
        console.log('💬 Showing sample reviews for demo');
        this.showSampleReviews();
    }

    showSampleReviews() {
        const sampleReviews = [
            {
                id: 1,
                user_name: 'Ayşe Kaya',
                rating: 5,
                comment: 'Çocuğum bu okulda çok mutlu. Öğretmenler gerçekten ilgili ve eğitim kalitesi yüksek.',
                created_at: '2025-01-10',
                ratings: { overall: 5, physical_facilities: 4, teacher_quality: 5, transportation: 4 }
            },
            {
                id: 2,
                user_name: 'Mehmet Demir',
                rating: 4,
                comment: 'Okul binası modern ve temiz. Spor salonu ve kütüphane çok güzel.',
                created_at: '2025-01-08',
                ratings: { overall: 4, physical_facilities: 5, teacher_quality: 4, transportation: 3 }
            },
            {
                id: 3,
                user_name: 'Fatma Özkan',
                rating: 5,
                comment: 'Öğretmenler çok deneyimli. Çocuğumun gelişimini yakından takip ediyorlar.',
                created_at: '2025-01-05',
                ratings: { overall: 5, physical_facilities: 4, teacher_quality: 5, transportation: 4 }
            }
        ];

        this.renderReviews(sampleReviews);
        this.updateReviewStats(sampleReviews);
        console.log('✅ Sample reviews displayed');
    }

    renderReviews(reviews) {
        const reviewsList = document.getElementById('reviewsList');
        if (!reviewsList) return;

        if (reviews.length === 0) {
            reviewsList.innerHTML = '<p class="no-reviews">Henüz yorum yapılmamış. İlk yorumu siz yapın!</p>';
            return;
        }

        const reviewsHTML = reviews.map(review => this.createReviewHTML(review)).join('');
        reviewsList.innerHTML = reviewsHTML;
    }

    createReviewHTML(review) {
        const date = new Date(review.timestamp).toLocaleDateString('tr-TR');
        const userInitial = review.user_id ? review.user_id.toString().charAt(0).toUpperCase() : 'U';
        
        const detailedRatings = [];
        if (review.physical_facilities_rating) {
            detailedRatings.push({
                label: 'Fiziksel Olanaklar',
                value: review.physical_facilities_rating
            });
        }
        if (review.teacher_quality_rating) {
            detailedRatings.push({
                label: 'Öğretmen Kalitesi',
                value: review.teacher_quality_rating
            });
        }
        if (review.transportation_rating) {
            detailedRatings.push({
                label: 'Ulaşım',
                value: review.transportation_rating
            });
        }

        const detailedRatingsHTML = detailedRatings.map(rating => `
            <div class="detailed-rating">
                <span class="rating-label">${rating.label}</span>
                <div class="rating-value">
                    <span class="rating-stars">${this.generateStars(rating.value)}</span>
                    <span class="rating-number">${rating.value}/5</span>
                </div>
            </div>
        `).join('');

        return `
            <div class="review-item">
                <div class="review-header">
                    <div class="review-user">
                        <div class="user-avatar">${userInitial}</div>
                        <div class="user-info">
                            <h4>Kullanıcı ${review.user_id}</h4>
                            <div class="review-date">${date}</div>
                        </div>
                    </div>
                    <div class="review-rating">
                        <span class="rating-stars">${this.generateStars(review.rating)}</span>
                        <span class="rating-number">${review.rating}/5</span>
                    </div>
                </div>
                <div class="review-content">
                    <p class="review-text">${this.escapeHtml(review.comment)}</p>
                    ${detailedRatingsHTML ? `<div class="detailed-ratings">${detailedRatingsHTML}</div>` : ''}
                </div>
            </div>
        `;
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '★';
        }
        
        if (hasHalfStar) {
            stars += '☆';
        }
        
        for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) {
            stars += '☆';
        }
        
        return stars;
    }

    updateReviewStats(reviews) {
        const reviewCount = document.getElementById('reviewCount');
        const averageRating = document.getElementById('averageRating');
        const schoolStars = document.getElementById('schoolStars');

        if (reviews.length > 0) {
            const avgRating = reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length;
            
            if (reviewCount) reviewCount.textContent = `(${reviews.length} değerlendirme)`;
            if (averageRating) averageRating.textContent = avgRating.toFixed(1);
            if (schoolStars) schoolStars.textContent = this.generateStars(avgRating);
        }
    }

    showAlert(message, type) {
        // Mevcut alert'leri kaldır
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        const container = document.getElementById('reviewFormContainer') || document.querySelector('.reviews-section');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            
            // 5 saniye sonra kaldır
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    validateComment(comment) {
        // XSS ve zararlı içerik kontrolü
        const dangerousPatterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi,
            /<iframe/gi,
            /<object/gi,
            /<embed/gi,
            /<link/gi,
            /<meta/gi,
            /data:text\/html/gi,
            /vbscript:/gi
        ];

        // Zararlı pattern kontrolü
        for (const pattern of dangerousPatterns) {
            if (pattern.test(comment)) {
                return false;
            }
        }

        // URL spam kontrolü
        const urlCount = (comment.match(/https?:\/\/|www\./gi) || []).length;
        if (urlCount > 2) {
            return false;
        }

        // Aşırı tekrar kontrolü
        const words = comment.toLowerCase().split(/\s+/);
        const wordCounts = {};
        for (const word of words) {
            if (word.length > 2) {
                wordCounts[word] = (wordCounts[word] || 0) + 1;
                if (wordCounts[word] > 5) {
                    return false;
                }
            }
        }

        // Büyük harf oranı kontrolü
        const upperRatio = (comment.match(/[A-Z]/g) || []).length / comment.length;
        if (upperRatio > 0.7) {
            return false;
        }

        return true;
    }

    setSchoolId(schoolId) {
        this.currentSchoolId = schoolId;
        this.loadReviews();
    }

    setUserId(userId) {
        this.currentUserId = userId;
    }
}

// Global instance
let reviewSystem;

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    reviewSystem = new ReviewSystem();

    // Mevcut kullanıcı bilgilerini al
    const userId = localStorage.getItem('userId');
    if (userId) {
        reviewSystem.setUserId(parseInt(userId));
    }

    // Okul ID'sini al (bu örnekte sabit, gerçekte dinamik olacak)
    reviewSystem.setSchoolId(1);
});

// API Base URL'i global olarak tanımla
const API_BASE_URL = 'http://127.0.0.1:5000/api';
