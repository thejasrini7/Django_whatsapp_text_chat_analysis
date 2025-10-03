"""
WSGI config for myproject project (RENDER).

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings_render')

<<<<<<< HEAD
=======
# Ensure the application binds to the correct port
os.environ.setdefault('PORT', '10000')

>>>>>>> 49340df8744b6570747d6bd4d9b58a8af76954d8
application = get_wsgi_application()