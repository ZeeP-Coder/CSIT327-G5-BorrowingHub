from supabase import create_client
from django.conf import settings
import uuid
from datetime import datetime

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_item_image(file, item_id):
    """Uploads a file to Supabase Storage using item_id to generate unique name"""
    file_ext = file.name.split('.')[-1]
    timestamp = int(datetime.now().timestamp())
    unique_id = uuid.uuid4().hex
    file_path = f"items/item_{item_id}_{timestamp}_{unique_id}.{file_ext}"

    # Upload file
    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        file_path,
        file.read(),
        {"content-type": file.content_type}
    )

    # Return public URL directly (it's already a string)
    return supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)