import redis

with redis.Redis() as client:
    # client.delete('tasks')
    # client.delete('answers')
    # client.lpush('tasks', 1,2,3,4)
    if client.lrange('tasks', 0, -1):
        print(client.lrange('tasks', 0, -1))
    if client.lrange('answers', 0, -1):
        print(client.lrange('answers', 0, -1))
    while True:
        client.brpoplpush('tasks', 'answers')#'tasks')[1].decode('utf-8')
        #print(task)
        #answer = task
        print(client.lrange('answers', 0, -1))
        #client.lpush('answers', answer)
