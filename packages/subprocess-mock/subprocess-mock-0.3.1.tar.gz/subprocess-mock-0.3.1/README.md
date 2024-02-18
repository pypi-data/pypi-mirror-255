# Subprocess Mock

_Mock objects for the standard library’s subprocess module_

```
pip install subprocess-mock
```

Installation in a virtual environment is recommended.


## Example Usage

Use the functions defined in the **subprocess\_mock.functions** module
(and also exposed in the **subprocess_mock** namespace) to patch
subprocess module functions in unit tests.


```python
>>> import pathlib
>>> import subprocess
>>> import subprocess_mock
>>> from unittest.mock import patch
>>>
>>> new_file = pathlib.Path("testfile.txt")
>>> new_file.exists()
False
>>> # Test: call a process with a mock.patched subprocess.run
>>> # No Process is called,
>>> # but a subprocess.CompletedProcess instance is returned.
>>>
>>> with patch("subprocess.run", new=subprocess_mock.run):
...     run_result = subprocess.run(["touch", str(new_file)])
...
>>> run_result
CompletedProcess(args=['touch', 'testfile.txt'], returncode=0)
>>> new_file.exists()
False
>>>
>>> # Counter-test: call the process without patching subprocess.run
>>> # The process is called with normal effects.
>>>
>>> run_result = subprocess.run(["touch", str(new_file)])
>>> new_file.exists()
True
>>>
```


## Further reading

Please see the documentation at <https://blackstream-x.gitlab.io/subprocess-mock>
for detailed usage information.

If you found a bug or have a feature suggestion,
please open an issue [here](https://gitlab.com/blackstream-x/subprocess-mock/-/issues)

