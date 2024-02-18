# Decorator factory that accepts custom fields as arguments
import time
import functools
from rova_client.Rova import Rova

# decorator for llm call tracing and logging to client_db
def capture(*decorator_args):
    auth, event_name, user_id, datasoure_id = decorator_args
    rova_client = Rova(auth)
    def record_api_call(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                record = {
                    'input_content': args[0][-1]['content'] if args else kwargs.get('messages', [])[-1]['content'],
                    'event_name': event_name,
                    'output_content': None,
                    'latency': None,
                    'input_token_count': None,
                    'output_token_count': None,
                    'error_status': "none",
                    'time_to_first_token':0,
                    'user_id': user_id,
                    'data_source_id': datasoure_id,
                    'llm_in_use':True
                    # Initialize custom fields with None or a default value
                }
                for field in decorator_args:
                    record[field] = None

                record['input_token_count'] = len(record['input_content'].split())

                start_time = time.time()
                try:
                    response = func(*args, **kwargs)
                    end_time = time.time()

                    record['latency'] = end_time - start_time
                    record['output_content'] = response.choices[0].message.content if response.choices else ''
                    record['output_token_count'] = len(record['output_content'].split())
                    record['cost'] = (record['input_token_count'] + record['output_token_count'])*0.0004

                except Exception as e:
                    record['error_status'] = str(e)
                    end_time = time.time()
                    record['latency'] = end_time - start_time
                finally:
                    # log to client db
                    rova_client.capture_event_llm(record)

                if 'error_status' in record and record['error_status']:
                    return None

                return response

            return wrapper
                
    return record_api_call