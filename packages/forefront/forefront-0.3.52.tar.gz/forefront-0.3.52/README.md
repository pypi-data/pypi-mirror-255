# forefront-sdk-python

## Getting started

In a virtual environment from the root of this folder (i.e. /path/to/forefront-python-sdk/) run:

```
python setup.py install
```

#### Confirm installation

Go to a python terminal:

```
python
```

Run

```
import forefront

```

## Usage

### Chat

```
will copy open ai
```

### Workflows

```
from forefront import Workflow
from forefront.workflows.utils import Chat

wf = Workflow(
    name="My workflow",
    inputs=['topic'],
    steps=[
        Chat('hello'),
        Chat('world')
        ]
    )

run = wf.run()
```

### Pipelines

```
from forefront import Pipeline
pipe = Pipeline("my-blog-pipeline")

pipe.add([run['messages']])

pipe.get_length()
```

... datasets, fine-tunes, etc.
