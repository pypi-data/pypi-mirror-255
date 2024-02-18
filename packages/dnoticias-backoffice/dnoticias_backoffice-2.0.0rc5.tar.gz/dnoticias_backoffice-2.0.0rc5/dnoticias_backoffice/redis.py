import logging
import redis

from django.conf import settings

logger = logging.getLogger(__name__)


def get_redis_connection() -> redis.Redis:
    if not hasattr(settings, "SESSION_REDIS"):
            logger.warning("[Redis] The SESSION_REDIS settings is not defined!")
            return None

    try:
        logger.info("[Redis] Connecting...")
        conn = redis.StrictRedis(
            host=settings.SESSION_REDIS.get("host"),
            port=settings.SESSION_REDIS.get("port"),
            socket_timeout=settings.SESSION_REDIS.get("socket_timeout"),
            retry_on_timeout=settings.SESSION_REDIS.get("retry_on_timeout"),
            db=settings.SESSION_REDIS.get("db"),
            password=settings.SESSION_REDIS.get("password"),
        )

        conn.ping()
    except Exception:
        logger.exception("[Redis] Failed to connect!")
        conn = None
    else:
        logger.info("[Redis] Connected.")

    return conn


class RedisContextManager(object):
    def __init__(self):
        self.conn: redis.Redis = get_redis_connection()

    def __enter__(self) -> redis.Redis:
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
