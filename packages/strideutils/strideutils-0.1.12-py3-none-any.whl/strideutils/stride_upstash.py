from typing import Dict, Optional

import redis

from strideutils.stride_config import config

redis_dbs = {}  # stores the redis dbs so we don't have to keep reconnecting


def get_redis_db(redis_db_name: str) -> redis.Redis:
    """
    Returns the redis db specified by redis_db_name.

    Currently supports 'public', 'frontend', and 'backend' dbs.
    """
    if redis_db_name not in redis_dbs:
        if redis_db_name == 'public':
            r = redis.Redis(
                host='usw1-certain-beagle-33773.upstash.io',
                port=33773,
                password=config.UPSTASH_PUBLIC_PASSWORD,
            )

        elif redis_db_name == 'frontend':
            r = redis.Redis(
                host='usw1-hot-bat-33320.upstash.io',
                port=33320,
                password=config.UPSTASH_STRIDE_FRONTEND_PASSWORD,
                ssl=True,
            )

        elif redis_db_name == 'backend':
            r = redis.Redis(
                host='usw1-mutual-mule-33971.upstash.io',
                port=33971,
                password=config.UPSTASH_STRIDE_BACKEND_PASSWORD,
                ssl=True,
            )

        else:
            raise ValueError(f'Invalid Redis DB: {redis_db_name}')

        redis_dbs[redis_db_name] = r

    return redis_dbs[redis_db_name]


def get(redis_key: str, db_name='frontend') -> Optional[str]:
    """
    This function will read the given Redis key and return the value.

    Pulls from the specified redis db.
    """
    db = get_redis_db(db_name)
    value = db.get(redis_key)

    return value.decode('utf-8') if value is not None else None


def set(redis_key: str, redis_val: str, db_name='frontend'):
    """
    This function will set the given key to value in the redis_db specified.
    """
    db = get_redis_db(db_name)
    db.set(redis_key, redis_val)


def set_keys(dict_to_upload: Dict[str, str], db_name='frontend', prefix=''):
    """
    Loops through all values in dict_to_upload and sets the keys+values in the redis db

    Will append "prefix" to all keys in the dict.
    """
    db = get_redis_db(db_name)
    for k, v in dict_to_upload.items():
        db.set(prefix + k, v)
