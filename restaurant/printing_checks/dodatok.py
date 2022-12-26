import redis

with redis.Redis() as client:
    print(client)
