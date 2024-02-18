import unittest
from rulent import load_rules, validate_data, show_rules

class TestEngine(unittest.TestCase):

    def test_rules_data(self):
        """
        Test for validity of rules.
        """
        load_rules()
        expected_rules = {
            "events": {
                "purchase": {
                "rules-operator": "or",
                "rules": [
                    {
                    "rule": "Name Check",
                    "conditions": [
                        {
                        "person.name": "James"
                        },
                        {
                        "person.lname": "Wright"
                        }
                    ]
                    },
                    {
                    "rule": "Age Check",
                    "conditions": [
                        {
                        "person.age": ">40"
                        }
                    ]
                    }
                ],
                "outcomes": [
                    {
                    "name": "outcome1",
                    "action": "email",
                    "mode": "async",
                    "parameters": {
                        "recipients": [
                        "user@example.com"
                        ],
                        "subject": "Event 1 Triggered"
                    }
                    },
                    {
                    "name": "outcome2",
                    "action": "log",
                    "mode": "sync",
                    "parameters": {
                        "message": "Event 1 was triggered",
                        "level": "info"
                    }
                    }
                ]
                },
                "click": {
                "rules-operator": "and",
                "rules": [
                    {
                    "rule": "Name Check",
                    "conditions": [
                        {
                        "person.name": "James"
                        }
                    ]
                    },
                    {
                    "rule": "Age Check",
                    "conditions": [
                        {
                        "person.age": ">42"
                        },
                        {
                        "person.age": "!43"
                        }
                    ]
                    }
                ],
                "outcomes": [
                    {
                    "name": "outcome1",
                    "action": "email",
                    "mode": "sync",
                    "parameters": {
                        "recipients": [
                        "user@example.com"
                        ],
                        "subject": "Click Event Triggered"
                    }
                    },
                    {
                    "name": "outcome2",
                    "action": "log",
                    "mode": "sync",
                    "parameters": {
                        "message": "Event 1 was triggered",
                        "level": "info"
                    }
                    }
                ]
                }
            }
        }
        self.assertDictEqual(expected_rules, show_rules())

    def test_validate_data(self):
        """
        Test for correctness of rules.
        """
        load_rules()
        sample_request = {
            "events" : ["purchase"],
            "person": {
                "name": "James",
                "lname": "Wright",
                "age": "40"
            }
        }
        expected_response = {
            "outcomes": [
                {
                    "name": "outcome1",
                    "action": "email",
                    "mode": "async",
                    "parameters": {
                        "recipients": [
                            "user@example.com"
                        ],
                        "subject": "Event 1 Triggered"
                    }
                },
                {
                    "name": "outcome2",
                    "action": "log",
                    "mode": "sync",
                    "parameters": {
                        "message": "Event 1 was triggered",
                        "level": "info"
                    }
                }
            ]
        }
        
        self.assertEqual(
            validate_data(
                sample_request
            ), 
            expected_response
        )



if __name__ == '__main__':
    unittest.main()
