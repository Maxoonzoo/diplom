"""
WSGI config for repository project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')

application = get_wsgi_application()