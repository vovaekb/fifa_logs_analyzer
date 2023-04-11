import json
import zmq
import time
import mongomock
from argparse import ArgumentParser


args_parser = ArgumentParser()
args_parser.add_argument('-f', '--file')


class DBManager:
    """
    Class for interaction with Database
    ...

    Attributes
    ----------
    db_client : MongoClient
        Database client for acees to DB
    collection : Collection
        Mongo Query Set
    
    Methods
    -------
    insert_record
    """
    def __init__(self):
        self.db_client = mongomock.MongoClient()
        self.collection = self.db_client.db.collection

    def insert_record(self, item):
        self.collection.insert_one(item)


class LogsReader:
    """
    Class for reading logs
    ...

    Attributes
    ----------
    db_manager : DBManager
        ..
    json_data : Any
        ..

    file_path : str
    
    Methods
    -------
    init_socket

    read_logs
    """
    def __init__(self, file_path):
        self.db_manager = DBManager()
        self.json_data = None
        self.file_path = file_path
        self.init_socket()

    def init_socket(self):
        print('Connecting to sender server…')
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")

    def read_logs(self):
        f = open(self.file_path)
        self.json_data = json.load(f)
        
    def save_logs_db(self):
        # Save to database
        for json_data_item in self.json_data:
            self.db_manager.insert_record(json_data_item)

    def send_logs(self):
        """
        Sends log messages to Analyzer
        
        Keyword arguments:
        ----
        Return: None
        """
        # send data to analyser service
        for json_data_item in self.json_data:
            del json_data_item['_id']
            message = {
                'status': 'data',
                'data': json_data_item 
            }
            self.socket.send_string(json.dumps(message))
            response = self.socket.recv()
        # send message that all the data are sent
        message = {
            'status': 'end',
            'data': {} 
        }
        self.socket.send_string(json.dumps(message))

    def process_logs(self):
        """
        Start processing logs
        
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        self.read_logs()
        self.save_logs_db()
        self.send_logs()


if __name__ == '__main__':
    file_path = '2252794827718791168-logs.json'
    logs_reader = LogsReader(file_path)
    logs_reader.process_logs()