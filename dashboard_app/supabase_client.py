from supabase import create_client
from django.conf import settings
import uuid

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_item_image(file):
    """Uploads a file to Supabase Storage and returns public URL"""
    file_ext = file.name.split('.')[-1]
    file_path = f"items/{uuid.uuid4()}.{file_ext}"

    # Upload to Supabase
    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        file_path,
        file.read(),
        {"content-type": file.content_type}
    )

    # Return public URL
    return supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
