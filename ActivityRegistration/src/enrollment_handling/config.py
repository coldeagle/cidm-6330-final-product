import os
from distutils.util import strtobool

from dotenv import load_dotenv
load_dotenv()


def get_sqlite_memory_uri():
    pass


def get_sqlite_file_url():
    return f"sqlite:///../activity_registration.db"


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", 5432)#54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user = os.environ.get('DB_USER', 'activity_registration')
    db_name = os.environ.get('DB_NAME', 'activity_registration')
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = os.environ.get('API_PORT', 80)#5005 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = os.environ.get('REDIS_PORT', 6379)

    #port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)


def get_email_host_and_port():
    host = os.environ.get("EMAIL_HOST", "localhost")
    port = 11025 if host == "localhost" else 1025
    http_port = 18025 if host == "localhost" else 8025
    sender_email = os.environ.get('SENDER_EMAIL', 'noone@noone.com')
    return dict(host=host, port=port, http_port=http_port, sender_email=sender_email)


def get_mj_credentials():
    use_mailjet = strtobool(os.environ.get('USE_MAILJET', 'False'))
    api_key = os.environ.get('MAILJET_API_KEY', 'abc123')
    private_key = os.environ.get('MAILJET_SECRET_KEY', 'abc12345')
    sender_email = os.environ.get('SENDER_EMAIL', 'noone@noone.com')
    return dict(use_mailjet=use_mailjet, api_key=api_key, private_key=private_key, sender_email=sender_email)