"""
Cloudinary Service Module
==========================
Handles image uploads to Cloudinary.
"""

import os
import cloudinary.uploader


def upload_image(filename: str) -> str:
    """
    Upload image to Cloudinary and return public URL.
    
    Args:
        filename: Path to the image file
        
    Returns:
        HTTPS URL of uploaded image
    """
    try:
        upload_result = cloudinary.uploader.upload(
            filename,
            public_id=f"water_level_{os.path.basename(filename).split('.')[0]}"
        )
        
        url = upload_result["secure_url"]
        print(f"Uploaded to Cloudinary: {url}")
        return url
        
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")
