from google.cloud import secretmanager
import io
import os
import environ
import google.auth

from sky import Sky
from skydb.sheets import *

env = environ.Env(DEBUG=(bool, True))
_, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()

# Pull secrets from Secret Manager
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/db_secrets/versions/latest"
payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

env.read_env(io.StringIO(payload))

# Starting sky client
sky = Sky(
    api_key=os.getenv('BB_API_KEY'),
    token_path='/tmp/.sky-token',
    credentials={
        "client_id":os.getenv('CLIENT_ID'),
        "client_secret":os.getenv('CLIENT_SECRET'),
        "redirect_uri":'http://localhost:8080'
    })