from redis import Redis

from src.singleton.env import env

redis = Redis.from_url(env.REDIS_URL, decode_responses=True)
