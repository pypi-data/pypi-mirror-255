### Rulent

Rulent is a python in-memory latency events engine that uses a set of declarative rules and triggers actions (outcomes).

### Quick Start 

Here is a sample implementation using **rulent** with FastAPI:

```python
from fastapi import FastAPI
from .import models
import rulent

app = FastAPI()
rulent.load_rules()

@app.post("/validate")
async def validate(request: models.EventRequest):
    print(request)
    return rulent.validate_data(dict(request))

@app.get("/reload")
async def reload_engine():
    rulent.load_rules()
    return {
		"status":  "success",
		"message": "Conditions reloaded successfully",
	}
```

Make sure you have a folder called "events" with atleast one YAML file like the below example:

```Yaml
events:
  click:
    rules-operator: "and"
    rules:
      - rule: "Name Check"
        conditions:
          - "person.name": "James"
      - rule: "Age Check"
        conditions:
          - "person.age": "42"
```

- You can programatically create this folder and sample file using __rulent.init()__. This needs to be used only once.

### Key Components

The main components of the event engine are as below.

#### The Web API

This is for ingesting events. This acts as the entry point for new events to be received and validation against rules.

#### Events

Events are specific, explicitly sent, pieces of information sent with the payload. This sets the foundation for the rules engine to process rules based on the event.

#### Rules

These are the rules that need to be applied on the JSON payload. This has support for dot notation. The rules can be combined using `rules-operator: "or"`. 

A sample rules block:

```yaml
events:
  click:
    rules-operator: "and"
    rules:
      - rule: "Name Check"
        conditions:
          - "person.name": "James"
      - rule: "Age Check"
        conditions:
          - "person.age": "42"
```

#### Outcomes

Once the payloads have been processed against rules, matched payloads can initiate actions. **Actions** are bundled together as outcomes.

Note: Actions are executed asynchronously.


#### Actions 

Actions that are part of outcomes can be extended by navigating to the logic folder and actions.go file. Currently, this has access to outcomes and the payloads that were received.


