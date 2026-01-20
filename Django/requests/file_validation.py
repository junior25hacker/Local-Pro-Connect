"""
File upload validation utilities for secure photo storage.
Provides validation for file size, type, and content.
"""

import os
import mimetypes
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB for images

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/jpg', 
    'image/png',
    'image/gif',
    'image/webp'
}

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Image dimension limits
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100


def validate_file_size(file_obj, max_size=MAX_FILE_SIZE):
    """
    Validate file size doesn't exceed the maximum allowed.
    
    Args:
        file_obj: Django UploadedFile object
        max_size: Maximum file size in bytes
        
    Raises:
        ValidationError: If file is too large
    """
    if file_obj.size > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = file_obj.size / (1024 * 1024)
        raise ValidationError(
            _('File size (%(file_size).1f MB) exceeds maximum allowed size (%(max_size).1f MB)'),
            params={'file_size': file_mb, 'max_size': max_mb}
        )


def validate_image_type(file_obj):
    """
    Validate file is an allowed image type.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If file type is not allowed
    """
    # Check file extension
    file_extension = os.path.splitext(file_obj.name)[1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _('File extension "%(extension)s" is not allowed. Allowed types: %(allowed)s'),
            params={
                'extension': file_extension,
                'allowed': ', '.join(ALLOWED_IMAGE_EXTENSIONS)
            }
        )
    
    # Check MIME type
    mime_type = file_obj.content_type or mimetypes.guess_type(file_obj.name)[0]
    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            _('File type "%(mime_type)s" is not allowed. Allowed types: %(allowed)s'),
            params={
                'mime_type': mime_type,
                'allowed': ', '.join(ALLOWED_IMAGE_TYPES)
            }
        )


def validate_image_content(file_obj):
    """
    Validate image content and dimensions using PIL.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If image is corrupted or dimensions are invalid
    """
    try:
        # Reset file pointer
        file_obj.seek(0)
        
        # Open image with PIL to validate content
        with Image.open(file_obj) as img:
            width, height = img.size
            
            # Check dimensions
            if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
                raise ValidationError(
                    _('Image dimensions (%(width)dx%(height)d) exceed maximum allowed (%(max_width)dx%(max_height)d)'),
                    params={
                        'width': width,
                        'height': height,
                        'max_width': MAX_IMAGE_WIDTH,
                        'max_height': MAX_IMAGE_HEIGHT
                    }
                )
            
            if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                raise ValidationError(
                    _('Image dimensions (%(width)dx%(height)d) are below minimum required (%(min_width)dx%(min_height)d)'),
                    params={
                        'width': width,
                        'height': height,
                        'min_width': MIN_IMAGE_WIDTH,
                        'min_height': MIN_IMAGE_HEIGHT
                    }
                )
            
            # Verify image format
            if img.format.lower() not in ['jpeg', 'jpg', 'png', 'gif', 'webp']:
                raise ValidationError(
                    _('Invalid image format: %(format)s'),
                    params={'format': img.format}
                )
        
        # Reset file pointer for future use
        file_obj.seek(0)
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            _('Invalid or corrupted image file: %(error)s'),
            params={'error': str(e)}
        )


def validate_request_photo(file_obj):
    """
    Comprehensive validation for request photos.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate file size (smaller limit for request photos)
    validate_file_size(file_obj, MAX_IMAGE_SIZE)
    
    # Validate image type
    validate_image_type(file_obj)
    
    # Validate image content
    validate_image_content(file_obj)


def generate_secure_filename(original_filename, prefix="photo"):
    """
    Generate a secure filename to prevent path traversal attacks.
    
    Args:
        original_filename: Original uploaded filename
        prefix: Prefix for the new filename
        
    Returns:
        str: Secure filename
    """
    import uuid
    import time
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()
    
    # Generate unique filename
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    secure_filename = f"{prefix}_{timestamp}_{unique_id}{ext}"
    
    return secure_filename


class SecureImageField:
    """
    Custom validator class for secure image uploads.
    Can be used with Django forms or models.
    """
    
    def __init__(self, max_size=MAX_IMAGE_SIZE):
        self.max_size = max_size
    
    def __call__(self, file_obj):
        validate_file_size(file_obj, self.max_size)
        validate_image_type(file_obj)
        validate_image_content(file_obj)
        return file_obj