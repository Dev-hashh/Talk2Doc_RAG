# Run this as a quick one-off test (python test_supabase.py)
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
print(client.storage.list_buckets())