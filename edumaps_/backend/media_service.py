import os
import magic
import boto3
import redis
from PIL import Image
from io import BytesIO
import ffmpeg_streaming
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import hashlib

class MediaService:
    def __init__(self, app):
        self.app = app
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=app.config['AWS_SECRET_KEY']
        )
        self.bucket = app.config['AWS_BUCKET_NAME']
        self.redis = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB']
        )
        self.allowed_image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        self.allowed_video_types = {'video/mp4', 'video/webm', 'video/ogg'}

    def process_media(self, file):
        """Process uploaded media file"""
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Detect file type
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type in self.allowed_image_types:
            return self.process_image(file)
        elif mime_type in self.allowed_video_types:
            return self.process_video(file)
        else:
            raise ValueError(f'Unsupported file type: {mime_type}')

    def process_image(self, image_file):
        """Process and optimize image file"""
        image = Image.open(image_file)
        
        # Generate different sizes
        sizes = {
            'thumbnail': (150, 150),
            'medium': (800, 800),
            'large': (1600, 1600)
        }
        
        results = {}
        for size_name, dimensions in sizes.items():
            # Create a copy of the image
            img_copy = image.copy()
            
            # Convert to RGB if necessary
            if img_copy.mode in ('RGBA', 'P'):
                img_copy = img_copy.convert('RGB')
            
            # Resize image
            img_copy.thumbnail(dimensions, Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            output = BytesIO()
            img_copy.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_filename = secure_filename(image_file.filename)
            filename = f"{os.path.splitext(original_filename)[0]}_{size_name}_{timestamp}.jpg"
            
            # Upload to S3
            self.s3.upload_fileobj(
                output,
                self.bucket,
                f"images/{filename}",
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            
            # Get URL
            url = f"https://{self.bucket}.s3.amazonaws.com/images/{filename}"
            results[size_name] = url
            
            # Cache URL
            cache_key = f"image:{filename}"
            self.redis.setex(cache_key, timedelta(days=7), url)
        
        return results

    def process_video(self, video_file):
        """Process and optimize video file"""
        # Save uploaded file temporarily
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f"/tmp/video_{timestamp}.mp4"
        video_file.save(temp_path)
        
        try:
            # Create video object
            video = ffmpeg_streaming.input(temp_path)
            
            # Generate HLS stream with multiple qualities
            hls = video.hls(ffmpeg_streaming.Formats.h264())
            hls.auto_generate_representations()
            
            # Generate unique path for the HLS stream
            original_filename = secure_filename(video_file.filename)
            stream_path = f"videos/{os.path.splitext(original_filename)[0]}_{timestamp}"
            local_stream_path = f"/tmp/{stream_path}"
            
            # Save HLS stream locally first
            os.makedirs(local_stream_path, exist_ok=True)
            hls.output(f"{local_stream_path}/stream.m3u8")
            
            # Upload all generated files to S3
            for root, _, files in os.walk(local_stream_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    s3_key = f"{stream_path}/{file}"
                    
                    with open(local_file_path, 'rb') as f:
                        self.s3.upload_fileobj(
                            f,
                            self.bucket,
                            s3_key,
                            ExtraArgs={'ContentType': 'application/x-mpegURL' if file.endswith('.m3u8') else 'video/MP2T'}
                        )
            
            # Generate thumbnail
            thumbnail = video.thumbnail(
                filename=f"{local_stream_path}/thumbnail.jpg",
                time_in_seconds=1
            )
            
            # Upload thumbnail to S3
            thumbnail_key = f"{stream_path}/thumbnail.jpg"
            with open(f"{local_stream_path}/thumbnail.jpg", 'rb') as f:
                self.s3.upload_fileobj(
                    f,
                    self.bucket,
                    thumbnail_key,
                    ExtraArgs={'ContentType': 'image/jpeg'}
                )
            
            # Get URLs
            base_url = f"https://{self.bucket}.s3.amazonaws.com"
            stream_url = f"{base_url}/{stream_path}/stream.m3u8"
            thumbnail_url = f"{base_url}/{thumbnail_key}"
            
            # Cache URLs
            cache_key = f"video:{stream_path}"
            cache_data = {
                'stream_url': stream_url,
                'thumbnail_url': thumbnail_url
            }
            self.redis.setex(cache_key, timedelta(days=7), str(cache_data))
            
            return {
                'stream_url': stream_url,
                'thumbnail_url': thumbnail_url
            }
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(local_stream_path):
                for root, _, files in os.walk(local_stream_path):
                    for file in files:
                        os.remove(os.path.join(root, file))
                os.rmdir(local_stream_path)

    def get_cached_url(self, key):
        """Get cached media URL"""
        return self.redis.get(key)

    def invalidate_cache(self, key):
        """Invalidate cached media URL"""
        self.redis.delete(key)

    def generate_cache_key(self, identifier):
        """Generate a cache key for media"""
        return hashlib.md5(identifier.encode()).hexdigest()

    def cleanup_old_media(self, days=30):
        """Clean up media files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # List objects in S3 bucket
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket):
            for obj in page.get('Contents', []):
                # Check if object is older than cutoff date
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    # Delete object
                    self.s3.delete_object(
                        Bucket=self.bucket,
                        Key=obj['Key']
                    )
                    
                    # Invalidate cache
                    cache_key = self.generate_cache_key(obj['Key'])
                    self.invalidate_cache(cache_key) 