import redis
import torch


redis_client = redis.Redis(host= "192.168.50.32", port= 6379, decode_responses=True)
# redis_client = redis.Redis(host= "localhost", port= 6379, decode_responses=True)

redis_client.set('foo', 'bar')

print(redis_client.get('foo'))


