# Public API
Seeqc CLI has an intended public API composed of classes and methods.
These are listed here and their description can be found in the corresponding docstrings.


## Seeqc Client
This API is the highest level one and is used to establish a connection to our cloud API. Only the SeeqcCLI should be directly instantiated. The lower level classes should be instantiated via this class.
- in class `seeqc_client.SeeqcCLI`:
	- `initialise()'`
    - `get_experiment(uid: str) -> Experiment`
    - `create_experiment(upload: Union[Path, str]) -> Experiment`
- in class `seeqc_client.Experiment`:
	- `run()`
    - `results() -> str`
    - `get_register()`
    - `status()`

