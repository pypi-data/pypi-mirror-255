import clickhouse_connect
import uuid
from rova_client.utils import SessionTracker, TraceTracker, DateTracker, error_check, simplify_dict, reverse_simplify_dict, order_by
from typing import List, Dict
from functools import reduce
from itertools import chain


class Rova:

    def __init__(self, auth, timeout=1440):
        
        self.accounts = ['buster_dev']

        if(not self.check_auth(auth)):
            raise Exception("Invalid key!")
        else:
            self.client = clickhouse_connect.get_client(host='tbbhwu2ql2.us-east-2.aws.clickhouse.cloud', port=8443, username='default', password='V8fBb2R_ZmW4i')
            template = 'USE {}'.format(auth)
            self.client.command(template)
            self.auth = auth
            print("Key verified! You may begin using the client. ")

        self.product_cols = self.get_cols(auth, 'product')
        self.llm_cols = self.get_cols(auth, 'llm')

        # init clients
        self.session_client = SessionTracker(timeout)
        self.trace_client = TraceTracker()
        self.date_client = DateTracker()
    
    def get_cols(self, auth, table):
        sql = "DESCRIBE TABLE {}.{}".format(auth, table)
        cols = set([name[0] for name in self.client.query(sql).result_rows])
        return cols

    def check_auth(self, auth):
        return (auth in self.accounts)

    def error_check(self, values, columns):
        if(len(values) <= 0):
            raise ValueError("No data provided!")
        if('event_name' not in columns):
            raise ValueError("Missing required data: 'event_name'")
        return 0
    
    def format_to_rova(self, obj):
        args = simplify_dict(obj)
    
        if('timestamp' not in args):
            args['timestamp'] = self.date_client.get_timestamp()
        args['session_id'], new_session = self.session_client.get_session_id(args['user_id'], args['timestamp'])
        args['distinct_id'] = uuid.uuid4()

        if('llm_in_use' in args):
            args['trace_id'] = self.trace_client.get_trace_id(args['user_id'], new_session, 'llm')
            self.trace_client.set_prev_log(args['user_id'], 'llm')
            return (args, 1)
        else:   
            self.trace_client.set_prev_log(args['user_id'], 'product')
            return (args, 0)
    
    def capture_handler(self, events_list, flag):

        column_names_set = set(chain.from_iterable(map(dict.keys, events_list)))
        target_set = self.llm_cols if flag else self.product_cols
        column_names = list(filter(target_set.__contains__, column_names_set))

        values_list = list(map(lambda dct: list(map(dct.get, column_names)), events_list))
        error_code = self.error_check(values_list, column_names)

        try:
            if(not flag):
                db = "{}.product".format(self.auth)
                self.client.insert(db, values_list, column_names=column_names)
            else:
                db = "{}.llm".format(self.auth)
                self.client.insert(db, values_list, column_names=column_names)
            return 0
        except Exception as e:
            print(e)
            return -1

    def capture(self, args):

        sorted_data = order_by(args)
        data = [self.format_to_rova(obj) for obj in sorted_data]
        prod_events = [item[0] for item in data if item[1] == 0]
        llm_events = [item[0] for item in data if item[1] == 1]
        try:
            if(prod_events):
              self.capture_handler(prod_events, 0)
            if(llm_events):
              self.capture_handler(llm_events, 1)
            return 0
        except Exception as e:
            print(e)
            return -1