import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()


# Local development defaults
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'http://localhost:54321')
SUPABASE_KEY = os.environ.get(
	'SUPABASE_KEY',
	'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.localdevsecretkey1234567890abcdef.localdevsignature'
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
