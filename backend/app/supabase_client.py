
import os

from dotenv import load_dotenv
from supabase import Client, create_client


# Load environment variables
load_dotenv()


def get_required_env(variable_name: str) -> str:
    """Retrieve a required environment variable."""
    value = os.getenv(variable_name)

    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {variable_name}"
        )

    return value


# Supabase configuration
SUPABASE_URL = get_required_env("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = get_required_env("SUPABASE_SERVICE_ROLE_KEY")


# Initialize Supabase client
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)
