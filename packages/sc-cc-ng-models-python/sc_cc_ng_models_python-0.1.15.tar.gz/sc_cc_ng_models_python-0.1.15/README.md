# SC-CC-NG Python Data Models

Data models for the SC-CC-NG project.

## Installation

```bash
pip install sc-cc-ng-data-models
```

## Usage

```python
from sc_cc_ng_data_models import *

# BitVal's are holding values and a context
bv = BitVal(
    context=[
        "MODEL", 
        "ENGINE", 
        "HORSEPOWER",
    ],
    value=50.0,
)

# ContextType's enum are known context types for easier usage
ct = ContextType.MODEL

```
The context data type is a list of strings and not a list of `ContextType` because of 
they should be able to carry any context information.
