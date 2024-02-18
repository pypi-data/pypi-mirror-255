# morbin

Base class for creating bindings for command line tools.

## Installation

Install with:

<pre>
pip install morbin
</pre>

## Usage

The easiest way to start is to use the bundled template generator.  
The only argument it requires is the name of the program you want to create bindings for.

As an example we'll do `Pip`.

Running `morbin pip` in your terminal will produce a file named `pip.py` in your current directory.  
It should look like this:
<pre>
from morbin import Morbin, Output


class Pip(Morbin):
    @property
    def program(self) -> str:
    return "pip"
</pre>

Additional functions should be built on top of the `run` function and return its output.  

After adding functions for `install` and `upgrade` the class should look like this:
<pre>
from morbin import Morbin, Output


class Pip(Morbin):
    @property
    def program(self) -> str:
    return "pip"
    
    def install(self, package:str, *args:str)->Output:
        return self.run("install", package, *args)
    
    def upgrade(self, package:str)->Output:
        return self.install(package, "--upgrade")
    
    def install_requirements(self)->Output:
        return self.install("-r", "requirements.txt")
</pre>

It can be used like:
<pre>
pip = Pip()
output = pip.install_requirements()
</pre>


The `Output` object each function returns is a `dataclass` with three fields: `return_code`, `stdout`, and `stderr`.  
<pre>
@dataclass
class Output:
    """Dataclass representing the output of a terminal command.

    #### Fields:
    * `return_code: list[int]`
    * `stdout: str`
    * `stderr: str`"""

    return_code: list[int]
    stdout: str = ""
    stderr: str = ""

    def __add__(self, output: Self) -> Self:
        return Output(
            self.return_code + output.return_code,
            self.stdout + output.stdout,
            self.stderr + output.stderr,
        )
</pre>


By default `stdout` and `stderr` are not captured.  
They are sent to wherever they normally would be and the `stdout` and `stderr` fields of the `Output` object will be empty strings.  
`stdout` and `stderr` can be captured by either setting the `capture_output` property of a class instance to `True` 
or by using the `capturing_output` context manager.  
To get the output of `install_requirements`:
<pre>
pip = Pip(capture_output=True)
text = pip.install_requirements().stdout
</pre>
or
<pre>
pip = Pip()
with pip.capturing_output():
    text = pip.install_requirements().stdout
</pre>
