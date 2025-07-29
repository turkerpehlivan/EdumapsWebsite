class AdminMedia {
    constructor() {
        this.currentSchoolId = null;
        this.mediaData = null;
        this.dropzone = null;
        this.currentMediaId = null;
        
        this.init();
    }

    async init() {
        try {
            await this.loadSchools();
            this.setupEventListeners();
            this.initializeDropzone();
            
            console.log('✅ Admin media management initialized');
        } catch (error) {
            console.error('Error initializing admin media:', error);
            this.showError('Medya yönetimi başlatılırken bir hata oluştu.');
        }
    }

    async loadSchools() {
        try {
            const response = await fetch('/api/schools');
            if (!response.ok) throw new Error('Schools fetch failed');
            
            const schools = await response.json();
            this.populateSchoolSelect(schools);
        } catch (error) {
            console.error('Error loading schools:', error);
            throw error;
        }
    }

    populateSchoolSelect(schools) {
        const select = document.getElementById('schoolSelect');
        select.innerHTML = '<option value="">Okul seçin...</option>';
        
        schools.forEach(school => {
            const option = document.createElement('option');
            option.value = school.id;
            option.textContent = school.name;
            select.appendChild(option);
        });
    }

    async loadMediaData() {
        if (!this.currentSchoolId) return;

        try {
            const response = await fetch(`/api/schools/${this.currentSchoolId}/media`);
            if (!response.ok) throw new Error('Media fetch failed');
            
            this.mediaData = await response.json();
            this.renderMedia();
        } catch (error) {
            console.error('Error loading media:', error);
            this.showError('Medya yüklenirken bir hata oluştu.');
        }
    }

    renderMedia() {
        const photoGrid = document.getElementById('photoGrid');
        const videoGrid = document.getElementById('videoGrid');
        const tourPreview = document.getElementById('tourPreview');
        
        photoGrid.innerHTML = '';
        videoGrid.innerHTML = '';
        tourPreview.innerHTML = '';

        this.mediaData.forEach(media => {
            if (media.media_type === 'photo') {
                photoGrid.appendChild(this.createMediaItem(media));
            } else if (media.media_type === 'video') {
                videoGrid.appendChild(this.createMediaItem(media));
            } else if (media.media_type === '360_tour') {
                this.updateTourPreview(media.url);
            }
        });
    }

    createMediaItem(media) {
        const div = document.createElement('div');
        div.className = 'media-item';
        div.innerHTML = `
            <img src="${media.media_type === 'video' ? media.thumbnail_url : media.url}" 
                 alt="${media.title || ''}" 
                 loading="lazy">
            <div class="media-overlay">
                <div class="media-title">${media.title || 'Başlıksız'}</div>
                <div class="media-actions">
                    <button onclick="adminMedia.editMedia('${media.id}')">Düzenle</button>
                    <button onclick="adminMedia.deleteMedia('${media.id}')">Sil</button>
                </div>
            </div>`;
        return div;
    }

    updateTourPreview(url) {
        const preview = document.getElementById('tourPreview');
        const tourUrl = document.getElementById('tourUrl');
        
        tourUrl.value = url || '';
        
        if (url) {
            preview.innerHTML = `
                <iframe src="${url}" 
                        frameborder="0" 
                        allowfullscreen 
                        style="width: 100%; height: 400px;">
                </iframe>`;
        } else {
            preview.innerHTML = '<p>Önizleme yok</p>';
        }
    }

    initializeDropzone() {
        Dropzone.autoDiscover = false;
        
        this.dropzone = new Dropzone("#uploadForm", {
            url: "/api/upload",
            autoProcessQueue: false,
            addRemoveLinks: true,
            maxFiles: 10,
            acceptedFiles: "image/*,video/*",
            dictDefaultMessage: "Dosyaları buraya sürükleyin veya tıklayarak seçin",
            init: function() {
                this.on("addedfile", file => {
                    if (file.type.startsWith('video/')) {
                        // Generate video thumbnail
                        const video = document.createElement('video');
                        video.src = URL.createObjectURL(file);
                        video.addEventListener('loadeddata', () => {
                            video.currentTime = 1; // Seek to 1 second
                        });
                        video.addEventListener('seeked', () => {
                            const canvas = document.createElement('canvas');
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                            file.thumbnail = canvas.toDataURL();
                        });
                    }
                });
            }
        });
    }

    setupEventListeners() {
        // School selection
        document.getElementById('schoolSelect').addEventListener('change', (e) => {
            this.currentSchoolId = e.target.value;
            if (this.currentSchoolId) {
                this.loadMediaData();
            }
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        // Upload modal
        document.getElementById('uploadMediaBtn').addEventListener('click', () => this.showUploadModal());
        document.querySelectorAll('.modal .close').forEach(btn => {
            btn.addEventListener('click', () => this.hideModals());
        });

        // Save media button
        document.getElementById('saveMediaBtn').addEventListener('click', () => this.saveMedia());

        // Update media button
        document.getElementById('updateMediaBtn').addEventListener('click', () => this.updateMedia());

        // Delete media button
        document.getElementById('deleteMediaBtn').addEventListener('click', () => this.deleteMedia());

        // Save tour button
        document.getElementById('saveTourBtn').addEventListener('click', () => this.saveTour());

        // Tour URL preview
        document.getElementById('tourUrl').addEventListener('input', (e) => {
            this.updateTourPreview(e.target.value);
        });
    }

    switchTab(tabId) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabId}Tab`);
        });
    }

    showUploadModal() {
        if (!this.currentSchoolId) {
            this.showError('Lütfen önce bir okul seçin.');
            return;
        }
        
        document.getElementById('uploadModal').classList.add('show');
    }

    hideModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
        this.dropzone.removeAllFiles();
        this.currentMediaId = null;
    }

    async saveMedia() {
        if (!this.currentSchoolId) {
            this.showError('Lütfen önce bir okul seçin.');
            return;
        }

        const title = document.getElementById('mediaTitle').value;
        const description = document.getElementById('mediaDescription').value;
        const type = document.getElementById('mediaType').value;

        if (!title) {
            this.showError('Lütfen bir başlık girin.');
            return;
        }

        try {
            // Upload files first
            const uploadedFiles = await this.uploadFiles();
            
            // Create media entries
            for (const file of uploadedFiles) {
                const mediaData = {
                    school_id: this.currentSchoolId,
                    media_type: type,
                    title: title,
                    description: description,
                    url: file.url,
                    thumbnail_url: file.thumbnail || null
                };

                const response = await fetch(`/api/schools/${this.currentSchoolId}/media`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(mediaData)
                });

                if (!response.ok) throw new Error('Media save failed');
            }

            this.hideModals();
            this.loadMediaData();
            this.showSuccess('Medya başarıyla yüklendi.');
        } catch (error) {
            console.error('Error saving media:', error);
            this.showError('Medya kaydedilirken bir hata oluştu.');
        }
    }

    async uploadFiles() {
        return new Promise((resolve, reject) => {
            const files = this.dropzone.getQueuedFiles();
            const uploadedFiles = [];
            let completedUploads = 0;

            if (files.length === 0) {
                reject(new Error('No files to upload'));
                return;
            }

            files.forEach(file => {
                const formData = new FormData();
                formData.append('file', file);

                fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    uploadedFiles.push({
                        url: data.url,
                        thumbnail: file.thumbnail
                    });
                    completedUploads++;

                    if (completedUploads === files.length) {
                        resolve(uploadedFiles);
                    }
                })
                .catch(error => {
                    reject(error);
                });
            });
        });
    }

    async editMedia(mediaId) {
        const media = this.mediaData.find(m => m.id === mediaId);
        if (!media) return;

        this.currentMediaId = mediaId;
        
        document.getElementById('editTitle').value = media.title || '';
        document.getElementById('editDescription').value = media.description || '';
        document.getElementById('editOrder').value = media.order || 0;
        
        document.getElementById('editModal').classList.add('show');
    }

    async updateMedia() {
        if (!this.currentMediaId) return;

        const mediaData = {
            title: document.getElementById('editTitle').value,
            description: document.getElementById('editDescription').value,
            order: parseInt(document.getElementById('editOrder').value) || 0
        };

        try {
            const response = await fetch(`/api/schools/${this.currentSchoolId}/media/${this.currentMediaId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(mediaData)
            });

            if (!response.ok) throw new Error('Media update failed');

            this.hideModals();
            this.loadMediaData();
            this.showSuccess('Medya başarıyla güncellendi.');
        } catch (error) {
            console.error('Error updating media:', error);
            this.showError('Medya güncellenirken bir hata oluştu.');
        }
    }

    async deleteMedia(mediaId = this.currentMediaId) {
        if (!mediaId) return;

        if (!confirm('Bu medyayı silmek istediğinizden emin misiniz?')) {
            return;
        }

        try {
            const response = await fetch(`/api/schools/${this.currentSchoolId}/media/${mediaId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Media deletion failed');

            this.hideModals();
            this.loadMediaData();
            this.showSuccess('Medya başarıyla silindi.');
        } catch (error) {
            console.error('Error deleting media:', error);
            this.showError('Medya silinirken bir hata oluştu.');
        }
    }

    async saveTour() {
        if (!this.currentSchoolId) {
            this.showError('Lütfen önce bir okul seçin.');
            return;
        }

        const tourUrl = document.getElementById('tourUrl').value;
        if (!tourUrl) {
            this.showError('Lütfen sanal tur URL\'sini girin.');
            return;
        }

        try {
            const response = await fetch(`/api/schools/${this.currentSchoolId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    virtual_tour_url: tourUrl
                })
            });

            if (!response.ok) throw new Error('Tour save failed');

            this.showSuccess('Sanal tur başarıyla kaydedildi.');
        } catch (error) {
            console.error('Error saving tour:', error);
            this.showError('Sanal tur kaydedilirken bir hata oluştu.');
        }
    }

    showError(message) {
        // You can implement a more sophisticated error notification system
        alert(message);
    }

    showSuccess(message) {
        // You can implement a more sophisticated success notification system
        alert(message);
    }
}

// Initialize admin media management when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminMedia = new AdminMedia();
}); 