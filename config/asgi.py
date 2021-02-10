import os
import sys
from pathlib import Path

import django
from channels.routing import get_default_application
from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# labrin_task directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "labrin_task"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()
application = get_default_application()
