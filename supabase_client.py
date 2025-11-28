import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Muat variabel dari file .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_smtp_config():
    result = supabase.table("blaster_smtp_config").select("*").limit(1).execute()
    return result.data[0] if result.data else None

def log_email(to_email, subject, body, body_type, status, error_msg=None):
    supabase.table("blaster_email_logs").insert({
        "to_email": to_email,
        "subject": subject,
        "body": body,
        "body_type": body_type,
        "status": status,
        "error_msg": error_msg,
    }).execute()

def get_all_smtp_configs():
    res = supabase.table("blaster_smtp_config").select("*").execute()
    return res.data

def add_smtp_config(data):
    supabase.table("blaster_smtp_config").insert(data).execute()

def delete_smtp_config(config_id):
    supabase.table("blaster_smtp_config").delete().eq("id", config_id).execute()

def get_smtp_config_by_id(config_id):
    res = supabase.table("blaster_smtp_config").select("*").eq("id", config_id).limit(1).execute()
    return res.data[0] if res.data else None
