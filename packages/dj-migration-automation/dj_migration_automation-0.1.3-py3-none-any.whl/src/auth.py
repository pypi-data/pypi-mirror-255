import logging.config
import jwt
import hashlib
import time
import random
import datetime

logger = logging.getLogger("root")


def generate_token(username):
    token = random.randint(1, 100000)
    return token


