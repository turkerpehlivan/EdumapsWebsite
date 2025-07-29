class SchoolProfile {
    constructor() {
        this.schoolId = this.getSchoolIdFromUrl();
        this.mediaData = null;
        this.teacherData = null;
        this.swiper = null;
        this.currentUser = null;
        this.commentForm = document.getElementById('commentForm');
        this.commentText = document.getElementById('comment');
        this.commentRating = document.getElementById('rating');
        this.resultDiv = document.getElementById('result');
        this.selectedRatingSpan = document.getElementById('selectedRating');
        this.allComments = [];
        this.init();
    }

    async init() {
        try {
            this.currentUser = await this.getCurrentUser();
            await this.loadSchoolData();
            await this.loadMediaData();
            await this.loadTeacherData();
            await this.loadComments();

            this.initializeSwiper();
            this.setupEventListeners();
            this.setupCommentForm();
            this.highlightStars('generalRating', this.commentRating.value);
            this.setupStarsForGroup('generalRating', 'rating');

            this.setupStarsForGroup('facilitiesRating', 'physical_facilities_rating');
            this.setupStarsForGroup('teacherQualityRating', 'teacher_quality_rating');
            this.setupStarsForGroup('transportationRating', 'transportation_rating');



            console.log('✅ School profile initialized');
        } catch (error) {
            console.error('Error initializing school profile:', error);
            this.showError('Okul bilgileri yüklenirken bir hata oluştu.');
        }
    }

    setupCommentForm() {
    if (!this.commentForm) return;

    this.commentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const comment = this.commentText.value.trim();
        const rating = this.commentRating.value;

        if (!comment || rating === "0") {
            this.showError('Lütfen yorumunuzu ve puanınızı giriniz.');
            return;
        }

        // Kullanıcı oturum kontrolü
        if (!this.currentUser || !this.currentUser.user_id) {
            this.showError('Yorum yapmak için giriş yapmalısınız.');
            return;
        }

        try {
            const response = await fetch(`/api/reviews`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.currentUser.user_id, // Dinamik kullanıcı ID
                    school_id: this.schoolId,
                    rating: Number(rating),
                    comment: comment,
                    physical_facilities_rating: Number(document.getElementById('physical_facilities_rating').value),
                    teacher_quality_rating: Number(document.getElementById('teacher_quality_rating').value),
                    transportation_rating: Number(document.getElementById('transportation_rating').value)
                })
            });

            if (!response.ok) throw new Error('Yorum gönderilemedi.');

            // Formu sıfırla ve yorumları yenile
            this.commentText.value = '';
            this.commentRating.value = '0';
            await this.loadComments();
            this.showSuccess('✅ Yorum gönderme talebiniz başarıyla iletildi. Onay sürecinden sonra yayınlanacaktır.');

        } catch (error) {
            this.showError(error.message);
        }
    });
    }


    // Yorumları yüklemek için fonksiyon (örnek)
    async loadComments() {
        try {
            const response = await fetch(`/api/reviews/school/${this.schoolId}`);
            if (!response.ok) throw new Error('Yorumlar yüklenemedi.');

            const comments = await response.json();
            this.allComments = comments;
            this.renderComments(this.allComments);
        } catch (error) {
            console.error('Error loading comments:', error);
            this.showError('Yorumlar yüklenirken hata oluştu.');
        }
    }

    renderComments(comments) {
            const container = document.getElementById('reviewsContainer');
            container.innerHTML = '';
            const limited = comments.slice(0, 20);

            limited.forEach(c => {
                // Yıldızları doldur
                let starsHtml = '';
                for (let i = 1; i <= 5; i++) {
                    starsHtml += i <= c.rating
                        ? '<span class="star filled">★</span>'
                        : '<span class="star">★</span>';
                }

                // Tarihi biçimlendir (alan adı: timestamp / created_at hangisi varsa)
                const dateObj = new Date(c.timestamp); // <--- burayı senin alanına göre değiştir
                const formattedDate = dateObj.toLocaleDateString('tr-TR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });

                const div = document.createElement('div');
                div.className = 'comment-item';
                div.innerHTML = `
                    <div class="comment-header">
                        <div class="comment-left">
                            <span class="comment-user">${c.username || 'Anonim Kullanıcı'}</span>
                            <span class="comment-date">${formattedDate}</span>
                        </div>
                        <div class="comment-stars">${starsHtml}</div>
                    </div>
                    <div class="comment-body">
                        <p>${c.comment}</p>
                    </div>
                `;
                container.appendChild(div);
            });
        }

    sortCommentsByDate() {
    const sorted = [...this.allComments].sort((a,b) => {
        return new Date(b.timestamp) - new Date(a.timestamp); // yeniden > eskiye
    });
    this.renderComments(sorted);
    }

    sortCommentsByRating() {
        const sorted = [...this.allComments].sort((a,b) => b.rating - a.rating);
        this.renderComments(sorted);
    }




    setupStarsForGroup(containerId, inputId) {
        const stars = document.querySelectorAll(`#${containerId} span`);
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        if (!container || !input) return;

        stars.forEach(star => {
            star.addEventListener('click', () => {
                const value = star.dataset.value;
                input.value = value;
                this.highlightStars(containerId, value);
            });

            star.addEventListener('mouseenter', () => {
                const value = star.dataset.value;
                this.highlightStars(containerId, value);
            });
        });

        container.addEventListener('mouseleave', () => {
            this.highlightStars(containerId, input.value);
        });
    }



    updateResult(rating) {
        this.selectedRatingSpan.textContent = rating;
        this.resultDiv.style.display = 'block';
        }

        highlightStars(containerId, rating) {
            const stars = document.querySelectorAll(`#${containerId} span`);
            stars.forEach(star => {
                const starValue = parseInt(star.dataset.value);
                if (starValue <= rating) {
                    star.classList.add('selected');
                } else {
                    star.classList.remove('selected');
                }
            });
        }
    
    



    getSchoolIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        // önce school_id’ye, yoksa id’ye, yoksa default 1’e bak
        return params.get('school_id') || params.get('id') || '1';
    }

    async loadSchoolData() {
        try {
            const response = await fetch(`/api/schools/${this.schoolId}`);
            if (!response.ok) throw new Error('School data fetch failed');
            
            const schoolData = await response.json();
            this.updateSchoolInfo(schoolData);
        } catch (error) {
            console.error('Error loading school data:', error);
            throw error;
        }
    }

    async loadMediaData() {
        try {
            const response = await fetch(`/api/schools/${this.schoolId}/media`);
            if (!response.ok) throw new Error('Media data fetch failed');
            
            this.mediaData = await response.json();
            this.renderMediaGallery();
        } catch (error) {
            console.error('Error loading media data:', error);
            throw error;
        }
    }

    async loadTeacherData() {
        try {
            const response = await fetch(`/api/schools/${this.schoolId}/teachers`);
            if (!response.ok) throw new Error('Teacher data fetch failed');
            
            this.teacherData = await response.json();
            this.renderTeacherProfiles();
        } catch (error) {
            console.error('Error loading teacher data:', error);
            throw error;
        }
    }

    updateSchoolInfo(data) {
        // Update school header information
        document.getElementById('schoolName').textContent = data.name;
        document.getElementById('schoolLocation').textContent = `${data.city}, ${data.district}`;
        document.getElementById('schoolRating').textContent = `Puan: ${data.average_rating.toFixed(1)}`;
        
        // Update school cover and logo
        if (data.cover_photo_url) {
            document.getElementById('schoolCover').style.backgroundImage = `url(${data.cover_photo_url})`;
        }
        if (data.logo_url) {
            document.getElementById('schoolLogo').src = data.logo_url;
        }

        // Update virtual tour if available
        if (data.virtual_tour_url) {
            const tourContainer = document.getElementById('tourContainer');
            tourContainer.innerHTML = `
                <iframe 
                    src="${data.virtual_tour_url}" 
                    allowfullscreen 
                    loading="lazy">
                </iframe>`;
        }
        // Update tanıtım videosu (butonla açılacak olan)
        if (data.video_url) {
            const videoSection = document.getElementById('videoSection');
            if (videoSection) {
                videoSection.innerHTML = `
                    <iframe width="560" height="315"
                        src="${data.video_url}"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                `;
            }
        }


        // Update school description and features
        document.getElementById('schoolDescription').textContent = data.description;
        
        const featuresList = document.getElementById('schoolFeatures');
        featuresList.innerHTML = '';
        if (data.features) {
            Object.entries(data.features).forEach(([key, value]) => {
                if (value) {
                    const li = document.createElement('li');
                    li.textContent = this.formatFeatureName(key);
                    featuresList.appendChild(li);
                }
            });
        }
    }

    renderMediaGallery() {
        const photoGallery = document.getElementById('photoGallery');
        const videoGallery = document.getElementById('videoGallery');
        
        photoGallery.innerHTML = '';
        videoGallery.innerHTML = '';

        this.mediaData.forEach(media => {
            if (media.media_type === 'photo') {
                photoGallery.innerHTML += `
                    <a href="${media.url}" 
                       class="gallery-item" 
                       data-lightbox="school-photos" 
                       data-title="${media.title || ''}">
                        <img src="${media.url}" alt="${media.title || 'Okul fotoğrafı'}" loading="lazy">
                    </a>`;
            } else if (media.media_type === 'video') {
                videoGallery.innerHTML += `
                    <div class="gallery-item video-thumbnail" 
                         data-video-url="${media.url}"
                         onclick="schoolProfile.openVideoModal('${media.url}')">
                        <img src="${media.thumbnail_url}" alt="${media.title || 'Video önizleme'}" loading="lazy">
                    </div>`;
            }
        });
    }

    renderTeacherProfiles() {
        const teacherProfiles = document.getElementById('teacherProfiles');
        teacherProfiles.innerHTML = '';

        this.teacherData.forEach(teacher => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.innerHTML = `
                <div class="teacher-card">
                    <img src="${teacher.photo_url}" 
                         alt="${teacher.name}" 
                         class="teacher-photo"
                         loading="lazy">
                    <h3 class="teacher-name">${teacher.name}</h3>
                    <div class="teacher-title">${teacher.title}</div>
                    <p class="teacher-bio">${teacher.bio}</p>
                    ${teacher.video_url ? `
                        <a href="#" 
                           class="teacher-video"
                           onclick="schoolProfile.openVideoModal('${teacher.video_url}'); return false;">
                            Tanıtım Videosunu İzle
                        </a>
                    ` : ''}
                </div>`;
            teacherProfiles.appendChild(slide);
        });

        // Refresh Swiper after adding slides
        if (this.swiper) {
            this.swiper.update();
        }
    }

    initializeSwiper() {
        this.swiper = new Swiper('.teacherSwiper', {
            slidesPerView: 1,
            spaceBetween: 30,
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev'
            },
            breakpoints: {
                640: {
                    slidesPerView: 2
                },
                1024: {
                    slidesPerView: 3
                }
            }
        });
    }

    openVideoModal(videoUrl) {
        // Create modal element
        const modal = document.createElement('div');
        modal.className = 'video-modal';
        modal.innerHTML = `
            <div class="video-modal-content">
                <span class="close-modal">&times;</span>
                <div class="video-container">
                    <iframe 
                        src="${videoUrl}" 
                        frameborder="0" 
                        allowfullscreen>
                    </iframe>
                </div>
            </div>`;

        // Add modal to body
        document.body.appendChild(modal);

        // Close modal functionality
        const closeBtn = modal.querySelector('.close-modal');
        closeBtn.onclick = () => {
            document.body.removeChild(modal);
        };

        // Close on outside click
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
    }

    setupEventListeners() {
        // Add any additional event listeners here
        window.addEventListener('resize', () => {
            if (this.swiper) {
                this.swiper.update();
            }
        });
    }

    formatFeatureName(key) {
        // Convert camelCase to Title Case with spaces
        return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase());
    }

    showError(message) {
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        // Add to page
        document.querySelector('main').prepend(errorDiv);

        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;

        // messageContainer alanını bul ve içine ekle
        const container = document.getElementById('messageContainer');
        container.innerHTML = ''; // eski mesajı temizle
        container.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

async getCurrentUser() {
    try {
        const response = await fetch('/api/current_user', {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Giriş yapılmamış');
        return await response.json();
    } catch (error) {
        console.warn('Kullanıcı oturumu bulunamadı');
        return null;
    }
}



}



// Initialize school profile when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.schoolProfile = new SchoolProfile();

    // Video buton
    const toggleBtn = document.getElementById('toggleVideo');
    const videoSection = document.getElementById('videoSection');
    if (toggleBtn && videoSection) {
        videoSection.style.display = 'none';
        toggleBtn.addEventListener('click', () => {
            videoSection.style.display =
                window.getComputedStyle(videoSection).display === 'none' ? 'block' : 'none';
        });
    }

    // Filtreleme butonları
    const sortDateBtn = document.getElementById('sortDate');
    const sortRatingBtn = document.getElementById('sortRating');

    if (sortDateBtn) {
        sortDateBtn.addEventListener('click', () => {
            window.schoolProfile.sortCommentsByDate();
        });
    }

    if (sortRatingBtn) {
        sortRatingBtn.addEventListener('click', () => {
            window.schoolProfile.sortCommentsByRating();
        });
    }
});