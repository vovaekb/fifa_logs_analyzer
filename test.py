import zmq
import unittest
import warnings
from analyser import MatchDispatcher, MATCH_SCORE_JSON, MATCH_STATUS_MAPPING, MATCH_STATE_JSON, MATCH_SCORE_JSON
from sender import LogsReader, DBManager


'''
class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        print("\nRunning setUp method...")
        warnings.simplefilter('ignore', category=Warning)
        self.match_dispatcher = MatchDispatcher()

    def tearDown(self):
        print("Running tearDown method...")

    def test_matchdispatcher_message_broker_initialized(self):
        self.assertIsInstance(self.match_dispatcher.message_broker.context, zmq.Context)

    def test_data_initialized(self):
        self.assertFalse(self.match_dispatcher.match_states)
        self.assertFalse(self.match_dispatcher.match_scores)
        self.assertFalse(self.match_dispatcher.period_scores)

    def test_event_initialized(self):
        self.assertIsNotNone(self.match_dispatcher.event)
'''
'''
class TestSender(unittest.TestCase):
    def setUp(self):
        print("\nRunning setUp method...")
        file_path = '2252794827718791168-logs.json'
        warnings.simplefilter('ignore', category=Warning)
        self.log_reader = LogsReader(file_path)
        # self.log_reader.process_logs()

    def tearDown(self):
        print("Running tearDown method...")

    def test_db_manager_initialized(self):
        self.assertIsInstance(self.log_reader.db_manager, DBManager)

    def test_socket_initialized(self):
        self.assertIsInstance(self.log_reader.socket, zmq.Socket)

    def test_read_logs(self):
        self.assertEqual(len(self.log_reader.json_data), 644)

    def test_save_logs_db(self):
        self.assertEqual(len(self.log_reader.db_manager.collection.find()), 644)

'''


class TestCommunication(unittest.TestCase):
    def setUp(self):
        print("\nRunning setUp method...")
        warnings.simplefilter('ignore', category=Warning)
        file_path = '2252794827718791168-logs.json'
        self.match_dispatcher = MatchDispatcher()
        self.log_reader = LogsReader(file_path)
        # self.log_reader.process_logs()

    def tearDown(self):
        print("Running tearDown method...")

    # Test cases for Analyzer
    def test_matchdispatcher_message_broker_initialized(self):
        self.assertIsInstance(self.match_dispatcher.message_broker.context, zmq.Context)

    def test_data_initialized(self):
        self.assertFalse(self.match_dispatcher.match_states)
        self.assertFalse(self.match_dispatcher.match_scores)
        self.assertFalse(self.match_dispatcher.period_scores)

    def test_event_initialized(self):
        self.assertIsNotNone(self.match_dispatcher.event)

    # Test cases for Sender
    def test_db_manager_initialized(self):
        self.assertIsInstance(self.log_reader.db_manager, DBManager)

    def test_socket_initialized(self):
        self.assertIsInstance(self.log_reader.socket, zmq.Socket)

    def test_read_logs(self):
        self.assertEqual(len(self.log_reader.json_data), 644)

    def test_save_logs_db(self):
        self.assertEqual(len(self.log_reader.db_manager.collection.find()), 644)


if __name__ == '__main__':
    unittest.main(verbosity=3)