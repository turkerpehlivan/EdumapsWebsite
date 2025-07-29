// Admin Panel JavaScript

const API_BASE_URL = 'http://127.0.0.1:5000/api';

class AdminPanel {
    constructor() {
        this.currentAdminId = null;
        this.pendingReviews = [];
        this.spamReviews = [];
        this.currentTab = 'pending';
        this.init();
    }

    init() {
        console.log('🚀 Admin panel initializing...');
        this.checkAdminAuth();

        // Eğer admin ID varsa data yükle
        if (this.currentAdminId) {
            console.log('📊 Admin ID found, loading data...');
            this.loadData();
        } else {
            console.log('⏳ No admin ID yet, waiting for login...');
        }

        this.setupEventListeners();
    }

    checkAdminAuth() {
        console.log('🔍 Checking admin auth...');
        const adminId = localStorage.getItem('adminId');
        const adminName = localStorage.getItem('adminName');
        const adminEmail = localStorage.getItem('adminEmail');

        console.log('📋 LocalStorage values:', { adminId, adminName, adminEmail });

        if (!adminId || !adminEmail) {
            console.log('❌ No admin credentials, showing login modal');
            this.showLoginModal();
            return;
        }

        this.currentAdminId = parseInt(adminId);
        console.log('✅ Admin authenticated, ID:', this.currentAdminId);
        document.getElementById('adminName').textContent = adminName || 'Admin';
        this.hideLoginModal();
    }

    showLoginModal() {
        document.getElementById('loginModal').style.display = 'flex';
        this.setupLoginForm();
    }

    hideLoginModal() {
        document.getElementById('loginModal').style.display = 'none';
    }

    setupLoginForm() {
        const form = document.getElementById('adminLoginForm');
        const loginBtn = document.getElementById('loginBtn');
        const errorDiv = document.getElementById('loginError');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('adminEmail').value.trim();
            const password = document.getElementById('adminPassword').value;

            if (!email || !password) {
                this.showLoginError('E-posta ve şifre gerekli');
                return;
            }

            loginBtn.disabled = true;
            loginBtn.textContent = 'Giriş yapılıyor...';
            errorDiv.style.display = 'none';

            try {
                const response = await fetch(`${API_BASE_URL}/admin/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                const result = await response.json();

                if (response.ok) {
                    // Başarılı giriş
                    console.log('✅ Login successful, result:', result);
                    localStorage.setItem('adminId', result.admin_id);
                    localStorage.setItem('adminName', result.admin_name);
                    localStorage.setItem('adminEmail', result.admin_email);

                    this.currentAdminId = result.admin_id;
                    console.log('🔑 Admin ID set to:', this.currentAdminId);
                    document.getElementById('adminName').textContent = result.admin_name;

                    this.hideLoginModal();
                    console.log('📊 Calling loadData after login...');
                    this.loadData();
                } else {
                    this.showLoginError(result.message || 'Giriş başarısız');
                }
            } catch (error) {
                console.error('Login error:', error);
                this.showLoginError('Bağlantı hatası oluştu');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Giriş Yap';
            }
        });
    }

    showLoginError(message) {
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    setupEventListeners() {
        // Tab butonlarına event listener ekle
        setTimeout(() => {
            const pendingTab = document.getElementById('pendingTab');
            const spamTab = document.getElementById('spamTab');

            if (pendingTab) {
                pendingTab.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('🖱️ Pending tab clicked');
                    this.switchTab('pending');
                });
            }

            if (spamTab) {
                spamTab.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('🖱️ Spam tab clicked');
                    this.switchTab('spam');
                });
            }

            console.log('✅ Event listeners added to tabs');
        }, 100);
    }

    switchTab(tabName) {
        console.log('🔄 Switching to tab:', tabName);

        // Tüm tab butonlarından active class'ını kaldır
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Tüm tab panellerini gizle
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        // Seçilen tab'ı aktif yap
        if (tabName === 'pending') {
            document.getElementById('pendingTab').classList.add('active');
            document.getElementById('pendingPanel').classList.add('active');
        } else if (tabName === 'spam') {
            document.getElementById('spamTab').classList.add('active');
            document.getElementById('spamPanel').classList.add('active');
        }

        this.currentTab = tabName;
        console.log('✅ Tab switched to:', tabName);
    }

    async loadData() {
        console.log('🔄 loadData called, currentAdminId:', this.currentAdminId);
        if (!this.currentAdminId) {
            console.log('❌ No admin ID, skipping data load');
            return;
        }

        console.log('📊 Loading admin data...');
        await Promise.all([
            this.loadPendingReviews(),
            this.loadSpamReviews()
        ]);

        this.updateStats();
        console.log('✅ Data loading completed');
    }

    async loadPendingReviews() {
        try {
            console.log('🔍 Loading pending reviews for admin ID:', this.currentAdminId);
            const response = await fetch(`${API_BASE_URL}/admin/reviews/pending?admin_id=${this.currentAdminId}`);

            if (response.ok) {
                this.pendingReviews = await response.json();
                console.log('📋 Pending reviews loaded:', this.pendingReviews);
                this.renderPendingReviews();
            } else if (response.status === 403) {
                alert('Admin yetkisi gerekli!');
                this.logout();
            } else {
                console.error('Bekleyen yorumlar yüklenemedi, status:', response.status);
            }
        } catch (error) {
            console.error('Bekleyen yorumlar yüklenirken hata:', error);
            document.getElementById('pendingReviews').innerHTML = 
                '<div class="empty-state"><div class="empty-icon">⚠️</div><p>Yorumlar yüklenirken hata oluştu</p></div>';
        }
    }

    async loadSpamReviews() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/reviews/spam?admin_id=${this.currentAdminId}`);
            
            if (response.ok) {
                this.spamReviews = await response.json();
                this.renderSpamReviews();
            } else if (response.status === 403) {
                alert('Admin yetkisi gerekli!');
                this.logout();
            } else {
                console.error('Spam yorumlar yüklenemedi');
            }
        } catch (error) {
            console.error('Spam yorumlar yüklenirken hata:', error);
            document.getElementById('spamReviews').innerHTML = 
                '<div class="empty-state"><div class="empty-icon">⚠️</div><p>Yorumlar yüklenirken hata oluştu</p></div>';
        }
    }

    renderPendingReviews() {
        console.log('🎨 renderPendingReviews called');
        console.log('📊 Pending reviews data:', this.pendingReviews);

        const container = document.getElementById('pendingReviews');
        console.log('📦 Container found:', !!container);

        if (!container) {
            console.error('❌ pendingReviews container not found!');
            return;
        }

        if (!this.pendingReviews || this.pendingReviews.length === 0) {
            console.log('📭 No pending reviews, showing empty state');
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✅</div>
                    <p>Bekleyen yorum bulunmuyor</p>
                </div>
            `;
            return;
        }

        console.log('📝 Creating HTML for', this.pendingReviews.length, 'reviews');
        const reviewsHTML = this.pendingReviews.map(review => this.createReviewHTML(review, 'pending')).join('');
        container.innerHTML = reviewsHTML;
        console.log('✅ Pending reviews rendered');
    }

    renderSpamReviews() {
        const container = document.getElementById('spamReviews');
        
        if (this.spamReviews.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🛡️</div>
                    <p>Spam yorum bulunmuyor</p>
                </div>
            `;
            return;
        }

        const reviewsHTML = this.spamReviews.map(review => this.createReviewHTML(review, 'spam')).join('');
        container.innerHTML = reviewsHTML;
    }

    createReviewHTML(review, type) {
        const date = new Date(review.timestamp).toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const spamScoreClass = review.spam_score > 0.7 ? 'spam-high' : 
                              review.spam_score > 0.3 ? 'spam-medium' : 'spam-low';

        const detailedRatings = [];
        if (review.physical_facilities_rating) {
            detailedRatings.push(`Fiziksel: ${this.generateStars(review.physical_facilities_rating)}`);
        }
        if (review.teacher_quality_rating) {
            detailedRatings.push(`Öğretmen: ${this.generateStars(review.teacher_quality_rating)}`);
        }
        if (review.transportation_rating) {
            detailedRatings.push(`Ulaşım: ${this.generateStars(review.transportation_rating)}`);
        }

        const actions = type === 'pending' ? `
            <div class="admin-actions">
                <button class="action-btn approve-btn" onclick="adminPanel.approveReview(${review.id})">
                    ✅ Onayla
                </button>
                <button class="action-btn reject-btn" onclick="adminPanel.rejectReview(${review.id})">
                    ❌ Reddet
                </button>
            </div>
        ` : `
            <div class="admin-actions">
                <button class="action-btn approve-btn" onclick="adminPanel.approveReview(${review.id})">
                    🔄 Geri Al
                </button>
                <button class="action-btn delete-btn" onclick="adminPanel.deleteReview(${review.id})">
                    🗑️ Sil
                </button>
            </div>
        `;

        return `
            <div class="admin-review-item" id="review-${review.id}">
                <div class="admin-review-header">
                    <div class="review-meta">
                        <div class="review-school">${review.school_name}</div>
                        <div class="review-user">👤 ${review.username}</div>
                        <div class="review-date">📅 ${date}</div>
                    </div>
                    <div class="spam-indicator">
                        <span>Spam Skoru:</span>
                        <span class="spam-score ${spamScoreClass}">
                            ${Math.round(review.spam_score * 100)}%
                        </span>
                    </div>
                </div>
                
                <div class="review-content">
                    <div class="review-rating">
                        <div class="rating-item">
                            <strong>Genel:</strong> ${this.generateStars(review.rating)} (${review.rating}/5)
                        </div>
                        ${detailedRatings.map(rating => `<div class="rating-item">${rating}</div>`).join('')}
                    </div>
                    
                    <div class="review-text">
                        ${this.escapeHtml(review.comment)}
                    </div>
                </div>
                
                ${actions}
            </div>
        `;
    }

    async approveReview(reviewId) {
        if (!confirm('Bu yorumu onaylamak istediğinizden emin misiniz?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/admin/reviews/${reviewId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    admin_id: this.currentAdminId
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('Yorum başarıyla onaylandı!', 'success');
                document.getElementById(`review-${reviewId}`).remove();
                let approvedCountEl = document.getElementById('approvedCount');
                let currentApproved = parseInt(approvedCountEl.textContent) || 0;
                approvedCountEl.textContent = currentApproved + 1;
                this.loadData(); // Verileri yenile
            } else {
                this.showAlert(result.message || 'Yorum onaylanırken hata oluştu', 'error');
            }
        } catch (error) {
            console.error('Yorum onaylama hatası:', error);
            this.showAlert('Bir hata oluştu, lütfen tekrar deneyin', 'error');
        }
    }

    async rejectReview(reviewId) {
        if (!confirm('Bu yorumu reddetmek istediğinizden emin misiniz?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/admin/reviews/${reviewId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    admin_id: this.currentAdminId
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('Yorum reddedildi!', 'success');
                document.getElementById(`review-${reviewId}`).remove();
                this.loadData(); // Verileri yenile
            } else {
                this.showAlert(result.message || 'Yorum reddedilirken hata oluştu', 'error');
            }
        } catch (error) {
            console.error('Yorum reddetme hatası:', error);
            this.showAlert('Bir hata oluştu, lütfen tekrar deneyin', 'error');
        }
    }
    async deleteReview(reviewId) {
        if (!confirm('Bu yorumu silmek istediğinize emin misiniz?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/admin/reviews/${reviewId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    admin_id: this.currentAdminId
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('Yorum başarıyla silindi!', 'success');
                document.getElementById(`review-${reviewId}`).remove();
                this.loadData(); // sayıyı güncelle
            } else {
                this.showAlert(result.message || 'Yorum silinirken hata oluştu', 'error');
            }
        } catch (error) {
            console.error('Yorum silme hatası:', error);
            this.showAlert('Bir hata oluştu, lütfen tekrar deneyin', 'error');
        }
    }


    updateStats() {
        document.getElementById('pendingCount').textContent = this.pendingReviews.length;
        document.getElementById('spamCount').textContent = this.spamReviews.length;
        document.getElementById('totalCount').textContent = this.pendingReviews.length + this.spamReviews.length;
        
        // Badge'leri güncelle
        document.getElementById('pendingBadge').textContent = this.pendingReviews.length;
        document.getElementById('spamBadge').textContent = this.spamReviews.length;
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '★';
        }
        
        for (let i = fullStars; i < 5; i++) {
            stars += '☆';
        }
        
        return stars;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showAlert(message, type) {
        // Basit alert sistemi
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass}`;
        alert.textContent = message;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.padding = '12px 16px';
        alert.style.borderRadius = '8px';
        alert.style.fontWeight = '500';

        document.body.appendChild(alert);

        setTimeout(() => {
            alert.remove();
        }, 3000);
    }

    logout() {
        localStorage.removeItem('adminId');
        localStorage.removeItem('adminName');
        localStorage.removeItem('adminEmail');

        // Ana sayfaya yönlendir
        window.location.href = '/';
    }
}

// Global functions
function switchTab(tabName) {
    // Tab butonlarını güncelle
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Panel'leri güncelle
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    document.getElementById(tabName + 'Panel').classList.add('active');
    
    adminPanel.currentTab = tabName;
}

function logout() {
    adminPanel.logout();
}

// Global instance
let adminPanel;

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    adminPanel = new AdminPanel();
});
