import redis
import pickle
import os


class Redis_File():
    '''
    A class to store the contents of a file in a redis instance
    
    '''

    def __init__(self, content, dest_file_path, source_machine, name = None):
        self.content : bytes = content # Pickled data
        self.name = name
        self.dest_file_path = dest_file_path
        self.source_machine = source_machine

    # Pickling attributes
    def __getstate__(self):
        
        return self.__dict__
    
    def __setstate__(self, state: dict):
        for attr in state:
            self.__dict__[attr] = state[attr]


    def to_file(self, dest = None) -> int:
        '''
        Writes file content to destination, alternative destination can be provided to overide\n
        data is loaded/unpickled before being written to file
        
        '''

        # Get destination
        if not dest:
            dest = self.dest_file_path
        
        try:
            # Write content to file
            with open(dest, 'w') as file:
                # Unpickle
                rev_file_dump = pickle.loads(self.content)

                # Write
                exit_code = file.write(rev_file_dump)
            
            

        except Exception as e:
            print(e)
        
        return exit_code
        

    def enqueue(self, redis_client: redis.Redis, queue_name, status):
        '''
        Adds self to queue for later download
        '''
        try:
            response = redis_client.lpush(queue_name, f"{self.source_machine} : {status}")

        except Exception as e:
            print(e)
            raise e
        
        return response
        

    def report(self, redis_client: redis.Redis, message):
        '''
        Adds message to to a redis stream, for reporting status to a stream\n
        messages
        
        '''

        try:
            response = redis_client.xadd(f"Worker: {self.source_machine}", message)
        except Exception as e:
            print(e)

        return response
    
        # return 0
        pass
    

    

def get_redis(redis_host: str, redis_port: int = 6379) ->redis.Redis:
    '''
    returns a redis client for 
    Params:\n
    redis_host := where redis instance is\n
    redis_port := port of vm/machine where redis is; default is 6379\n

    '''
    try:

        return redis.Redis(host= redis_host, port= redis_host, decode_responses=False)
    except Exception as e:
        print(e)
        raise e

def upload_file_to_redis(source_file_path, dest_file_path, redis_client: redis.Redis, source_machine):
    '''
    Used to upload files to redis instance\n
    Params:
    '''
    # try:
    #     redis_client = redis.Redis(host= f"{redis_host}", port= 6379, decode_responses=False)

    # except redis.
    # pickle_file = 
    with open(source_file_path, "r") as file:
        file_content = file.read()


    file_dump = pickle.dumps(file_content)
    to_be_redis_file = Redis_File(file_dump, dest_file_path, source_machine)
    
    

    pass

def upload_object_to_redis(redis_client: redis.Redis, obj):
    '''
    Used to upload objects to blob
    '''
    # redis_client = redis.Redis(host= f"{redis_host}", port= 6379, decode_responses=False)
    pass


def pull_from_redis(redis_client: redis.Redis, key):
    '''
    
    '''
    pass
    