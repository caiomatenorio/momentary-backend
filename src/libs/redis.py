from upstash_redis import Redis

from ..env import env

redis = Redis(
    url=env.REDIS_URL,
    token=env.REDIS_TOKEN,
)
