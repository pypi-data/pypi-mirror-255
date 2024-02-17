import os

SYSTEM_ORGANIZATION_ID = os.environ.get("ROBOTCLOUD_SYSTEM_ORGANIZATION_ID ", "org-0")
API_KEY = os.environ.get("ROBOTCLOUD_API_KEY")
ROOT_URL = os.environ.get("ROBOTCLOUD_ROOT_URL")
ROOT_URL = ROOT_URL[:-1] if ROOT_URL[-1] == '/' else ROOT_URL  # If last string is slash remove it

DEFAULT_TIMEOUT = os.environ.get("ROBOTCLOUD_DEFAULT_TIMEOUT", 5)
