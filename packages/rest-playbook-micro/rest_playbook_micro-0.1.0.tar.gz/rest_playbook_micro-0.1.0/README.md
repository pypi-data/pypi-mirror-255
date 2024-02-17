# Python REST Playbook

Provides a framework for defining a series (playbook) of rest messages to perform automated testing or access of an endpoint.

# Features

-   Substitution of values in a templated REST message
    -   Content can be optional or mandatory for provided values
-   Run messages in a user defined order
-   Define pause times between messages
-   TODO: Run python statements against step responses

# Usage

Since playbook is driven from defined input files the code required to run a playbook is short. All of the development time as a goal should be spent in the input files

```python
from rest_playbook_micro.rest_playbook import RESTPlaybook as RP
pb = RP("test.playbook","test.scenario","test.vars")
results = pb.run_playbook()
print(results)
```

All files are flat text and we will discuss their format now. Examples are provided in ```./test```

## Vars file
All variables are defined in the format ```<variable_name>=<value>```
<variable_name> character set is best restricted to ```[A-Z_]``` and never ```=```. ```=``` symbols in ```<value>``` do not need to be escaped since the parser will only use the first occurance in each line as a separator.
```text
PAGE=1
ID=ORDER001
SERVICE_ID=SERVICEORDER001
TIMESTAMP=2023-01-02 12:25:01
```
## Scenario
Define a scenario for a specific message content. `SCENARIO=` block outlines meta information for the content, whereas `HEADER=`, `PARAMS=` and `BODY=` outline standard HTTP REST data. Close each block with the block name prepended with `=`

Variable substitutions are marked with `%ENV_<VARNAME>%`. You can define content that will not be copied with `%OPTIONAL:` and enforce variables being provided with `%MANDATORY:%`

```text
----
SCENARIO=
NAME=EASY NAME
DESCRIPTION=Scenario Example
TYPE=POST
ENDPOINT=http://localhost:3876/200
=SCENARIO
HEADER=
	Content-Type:application/json
	Accept:application/json
=HEADER
PARAMS=
	page=%ENV_PAGE%
=PARAMS
BODY=
{
    "timestamp":"%ENV_TIMESTAMP%"
    %OPTIONAL:ENV_ID%,"id":"%ENV_ID%"
    %MANDATORY:ENV_SERVICE_ID%,"service_id":"%ENV_SERVICE_ID%"
}
=BODY
----
```

## Playbook


# Build

```bash
python -m build
python -m twine upload dist/*
```
