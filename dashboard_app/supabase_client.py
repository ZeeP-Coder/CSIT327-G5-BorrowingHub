# dashboard_app/supabase_client.py
from supabase import create_client
from django.conf import settings
import uuid
from datetime import datetime
from storage3._sync.file_api import StorageApiError

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_item_image(file, item_id, max_retries: int = 3) -> str:
    """
    Upload `file` to Supabase under a unique path that includes item_id, timestamp and uuid.
    Returns a public URL (string).
    Retries with a new filename if supabase returns Duplicate.
    """
    file_ext = file.name.split('.')[-1]
    for attempt in range(max_retries):
        timestamp = int(datetime.now().timestamp())
        unique_id = uuid.uuid4().hex
        file_path = f"items/item_{item_id}_{timestamp}_{unique_id}.{file_ext}"

        try:
            # upload expects (path, bytes) with your version of supabase-py
            supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                file_path,
                file.read(),
                {"content-type": getattr(file, "content_type", "application/octet-stream")}
            )

            # get_public_url usually returns a string in current supabase-py
            public_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
            return public_url

        except StorageApiError as e:
            # If duplicate, retry with a new uuid; otherwise re-raise
            err = getattr(e, "args", [None])[0]
            if isinstance(err, dict) and err.get("error") == "Duplicate":
                # try again (new filename)
                continue
            else:
                # re-raise unknown storage errors
                raise

    # if we hit max_retries, raise an error
    raise RuntimeError("Failed to upload file after multiple attempts.")
