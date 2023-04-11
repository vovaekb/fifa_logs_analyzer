import zmq
import time
import json
import copy
from datetime import datetime


# mapping for status field
STATUS_MAPPING = {
    'start_game': 0,
    'game_play': 1,
    'game_end': 2
}

# mapping for match status field
MATCH_STATUS_MAPPING = {
    'start_game': 0,
    'game_end': 3
}

MATCH_STATE_JSON = "match_state.json"
MATCH_SCORE_JSON = "match_score.json"


class MessageBroker:
    """
    Class for receiving data from sender script

    ...
    Attributes
    ----------
    context : zmq.Context
        context for ZMQ
    socket : Socket
        socket object
    
    Methods
    -------
    send_text(text):
        Sends text message to sender script.

    receive_object():
        Receives object from sender script
    """
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:5555")
    
    def send_text(self, text):
        self.socket.send(text)

    def receive_object(self):
        message = json.loads(self.socket.recv_string())
        return message


class MatchDispatcher:
    """
    Class for receiving data from queue and update match state and score

    ...
    Attributes
    ----------
    context : zmq.Context
        context for ZMQ
    socket : Socket
        socket object
    
    Methods
    -------
    init_event(text):
        Initializes event object.

    listen_requests():
        Listen for messages from sender script.

    is_log_valid(message):
        Checks if log message is valid.

    update(message):
        Updates match state and score based on log message from sender script

    write_results():
        Writes  match state and score results to JSON file.
    """
    def __init__(self):
        self.message_broker = MessageBroker()
        self.last_state = None
        self.match_score = None
        self.match_states = []
        self.match_scores = []
        self.period_scores = []
        self.init_event()
    
    def init_event(self):
        event_json_file = "2252794827718791168-event.json"
        f = open(event_json_file)
        self.event = json.load(f)

    def listen_requests(self):
        while True:
            # Wait for next request from client
            message = self.message_broker.receive_object()
            if message['status'] == 'end':
                print('data end')
                break
            self.update(message['data'])
            time.sleep(1)
            self.message_broker.send_text(b'Received')

    def is_log_valid(self, message):
        is_valid = True
        if self.last_state is not None:
            last_datetime = self.last_state['time']
            match_datetime = message['time']
            is_valid = ((message['home_score'] >= self.last_state['home_score']) and 
                (message['away_score'] >= self.last_state['away_score']) and 
                (match_datetime > last_datetime)
            )
        is_valid = is_valid and ((message['event_id'] == self.event['id']))
        return is_valid

    def update(self, message):
        # Check if new log message is valid
        is_valid = self.is_log_valid(message)
        
        # Perform update match state and score if some information has changed
        if self.last_state is not None:
            if self.last_state != message:
                # Form match_state
                if not is_valid:
                    status = 3
                else:
                    status = STATUS_MAPPING[message['status']]
                
                if message['status'] in MATCH_STATUS_MAPPING:
                    match_status = MATCH_STATUS_MAPPING[message['status']]
                else:
                    match_status = message['game_period'] + 1
                match_state = {
                    'status': status,
                    'match_status': match_status,
                    'match_time': message['match_time']
                }
                self.match_states.append(match_state)

                # If log message is invalid we dont update match score
                if not is_valid:
                    return
                
                # Form new match score
                self.match_score = {
                    'score': {
                        'home_score': message['home_score'],
                        'away_score': message['away_score']
                    },
                    'period_scores': []
                }
                game_period = message['game_period']
                    
                if game_period == 0:
                    if not self.period_scores:
                        period_score = {
                            'number': game_period,
                        }
                        self.period_scores.append(
                            period_score
                        )
                elif game_period == 1:
                    # if second period just started we add new period score
                    if len(self.period_scores) == 1:
                        period_score = {
                            'number': game_period
                        }
                        self.period_scores.append(
                            period_score
                        )
                if message['status'] != 'start_game':
                    self.period_scores[game_period]['home_score'] = message['home_score']
                    self.period_scores[game_period]['away_score'] = message['away_score']

                self.match_score['period_scores'] = copy.deepcopy(
                    self.period_scores
                )
                self.match_scores.append(self.match_score)
        self.last_state = message

    def write_results(self):
        print('saving results to file ...')
        # write match scores
        with open(MATCH_STATE_JSON, 'w') as f:
            f.write(json.dumps(self.match_states, indent=4))

        # write match states
        with open(MATCH_SCORE_JSON, 'w') as f:
            f.write(json.dumps(self.match_scores, indent=4))


if __name__ == '__main__':
    receiver = MatchDispatcher()
    receiver.listen_requests()
    receiver.write_results()