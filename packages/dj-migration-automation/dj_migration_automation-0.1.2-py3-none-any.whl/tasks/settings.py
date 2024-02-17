"""
This module holds all settings and default values required for task queue to work.
"""

import os
import settings

class TaskConstant(object):
    """
    Class holding all constants required for task queue
    """
    CELERY_RESULTS_DB_KEY = 'database_migration'
    DP_CELERY_BROKER = settings.CONST_CELERY_SERVER_URL
    CELERY_RESULT_EXPIRES = 3600


class TaskQueue(object):
    """
    Class to define all Queues that can be used by DosePack projects
    Notes:
        - Make sure all class attributes have different values
    """
    SINGLE_WORKER = os.environ.get('dpws_single_worker_tasks', 'dpws_temp_single_worker_tasks_payal')
    MULTI_WORKER = os.environ.get('dpws_multi_worker_tasks', 'dpws_temp_multi_worker_tasks_payal')
