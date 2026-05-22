import json

from app.core.redis import redis_client

from app.utils.logger import logger


CACHE_TTL = 300


class CacheService:


    @staticmethod
    def get(key: str):

        try:

            data = redis_client.get(key)

            if data:

                logger.info(
                    f"Cache HIT key={key}"
                )

                return json.loads(data)

            logger.info(
                f"Cache MISS key={key}"
            )

            return None

        except Exception as e:

            logger.error(
                f"Redis GET failed: {str(e)}"
            )

            return None


    @staticmethod
    def set(
        key: str,
        value
    ):

        try:

            redis_client.setex(
                key,
                CACHE_TTL,
                json.dumps(value)
            )

            logger.info(
                f"Cache SET key={key}"
            )

        except Exception as e:

            logger.error(
                f"Redis SET failed: {str(e)}"
            )


    @staticmethod
    def delete(key: str):

        try:

            redis_client.delete(key)

            logger.info(
                f"Cache DELETE key={key}"
            )

        except Exception as e:

            logger.error(
                f"Redis DELETE failed: {str(e)}"
            )