import redis
import json

r0 = redis.Redis(
    host='localhost',
    port = 6379,
    db=0,
    decode_responses=True
)

r0.set('name',  'sunny', ex=600)

r0.delete('name')

print(r0.get('name')) 