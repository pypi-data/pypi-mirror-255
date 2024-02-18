import os
import yaml
from .import logic

config = {}

def init():
    folder_path = 'events'
    file_path = os.path.join(folder_path, 'sample.yaml')

    # Sample YAML content
    data = {
        'events': {
            'purchase': {
                'rules-operator': 'or',
                'rules': [
                    {
                        'rule': 'Name Check',
                        'conditions': [
                            {'person.name': 'James'},
                            {'person.lname': 'Wright'}
                        ]
                    },
                    {
                        'rule': 'Age Check',
                        'conditions': [{'person.age': '>40'}]
                    }
                ],
                'outcomes': [
                    {
                        'name': 'outcome1',
                        'action': 'email',
                        'mode': 'async',
                        'parameters': {
                            'recipients': ['user@example.com'],
                            'subject': 'Event 1 Triggered'
                        }
                    },
                    {
                        'name': 'outcome2',
                        'action': 'log',
                        'mode': 'sync',
                        'parameters': {
                            'message': 'Event 1 was triggered',
                            'level': 'info'
                        }
                    }
                ]
            },
            'click': {
                'rules-operator': 'and',
                'rules': [
                    {
                        'rule': 'Name Check',
                        'conditions': [{'person.name': 'James'}]
                    },
                    {
                        'rule': 'Age Check',
                        'conditions': [
                            {'person.age': '>42'},
                            {'person.age': '!43'}
                        ]
                    }
                ],
                'outcomes': [
                    {
                        'name': 'outcome1',
                        'action': 'email',
                        'mode': 'sync',
                        'parameters': {
                            'recipients': ['user@example.com'],
                            'subject': 'Click Event Triggered'
                        }
                    },
                    {
                        'name': 'outcome2',
                        'action': 'log',
                        'mode': 'sync',
                        'parameters': {
                            'message': 'Event 1 was triggered',
                            'level': 'info'
                        }
                    }
                ]
            }
        }
    }

    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
        print(f"Events folder created with sample file.")
    else:
        print(f"Rulent already initialized.")

def show_rules():
    global config
    return config

def load_rules():
    global config
    config = {}
    events_dir = 'events'
    
    # Check if the directory exists
    if not os.path.exists(events_dir):
        print(f"The directory {events_dir} does not exist.")
        print(f"If you wish to programatically")
        print(f"create an 'events' folder,")
        print(f"you can call pyrulent.init()")
        return
    
    # List all files in the directory
    for filename in os.listdir(events_dir):
        if filename.endswith('.yaml'):
            file_path = os.path.join(events_dir, filename)
            # Load the YAML file
            with open(file_path, 'r') as stream:
                try:
                    # Load the current file's data
                    file_data = yaml.safe_load(stream)
                    config.update(file_data)
                except yaml.YAMLError as exc:
                    print(f"Error loading {file_path}: {exc}")

def validate_data(data):
    global config
    results = []
    rule_result = False
    for event in data['events']:
        if event in config['events']:
            event_config = config['events'][event]
            if event_config['rules-operator'] == 'or':
                rule_result = logic.check_or_rules(data, event_config['rules'])
            if event_config['rules-operator'] == 'and':
                rule_result = logic.check_and_rules(data, event_config['rules'])
            if rule_result == True:
                results.extend(event_config['outcomes'])  
    return {"outcomes":results}