"""
This module should have all business level functions which can be exposed as web service.
This module exists so that we don't mix functions
which may persist data and affect actual functionality.
This will prevent unexpected bug in actual functionality.
"""

import settings

logger = settings.logger


