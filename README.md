This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/). 

![img.png](https://camo.githubusercontent.com/f05d4039b67688cfdf339d2a445ad686a60551f9891734c418f7096184de5fac/68747470733a2f2f692e6372656174697665636f6d6d6f6e732e6f72672f6c2f62792d6e632d73612f342e302f38387833312e706e67)

For details view the [Licence file](https://github.com/vac-mmis/CausalAnnotationCorrection/blob/main/LICENSE)!

---
# Causal Annotation Correction Tool
A tool support tool for inspection, validation and correction of behavioral annotations.

## Installation with Docker;

Fast start the example:
1. Install docker ([https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/))
2. Run the image from docker hub:
    ```
    $ docker run -p 9000:9000 -it fgratzkowski/cac
    ```
3. Navigate to: `Examples/Checking_Annotation` or `Examples/Creating_Domain`
4. Simply invoke: `make run`

Use your own files:
1. On your system, navigate to `your directory` that contains the files you want to use (domain.pddl, problem.pddl, annotation.csv).
2. Run the image from docker hub, you will need to replace `$(your_absolute_directory)` with the absolute path of `your directory`:
    ```
    $ docker run -p 9000:9000 --mount type=bind,source="$(your_absolute_directory)",target="/home/cac/CausalAnnotationCorrection/OUTSIDE" -it fgratzkowski/cac
    ```
3. You will find your files in the `OUTSIDE` directory:
    ```
    $ cd OUTSIDE
    ```
4. Simply run the tool by invoking:
    ```
    $ acheck check $domain.pddl $problem.pddl $annotation.csv
    ```
   For more information check out the `Usage` section below.


---
## Installation via PIP
If you just want to use the tool independently of docker,
you can install the package via `pip`:
```
$ pip install acheck
```
The tool requires **Python 3.8** or higher. 
  - If you experience any issues, you may want to have a look at: https://docs.python-guide.

### Spell Checking
The tool uses `pyenchant` for spell checking. It is a spellchecking library for Python, based on the [Enchant](https://abiword.github.io/enchant/) library. In order to work properly you will need to install the Enchant C library manually:

**MacOS:** 
  ```
  $ brew update
  $ brew install enchant
  ```
To avoid problems, restart your system after installation.

**Linux:**\
The quickest way is to install `libenchant` using the package manager of your current distribution.\
To detect the libenchant binaries, PyEnchant uses `ctypes.util.find_library()`, which requires `ldconfig`, `gcc`, `objdump` or `ld` to be installed. This is the case on most major distributions, however statically linked distributions (like Alpine Linux) might not bring along `binutils` by default.\
To avoid problems, restart your system after installation.
   ```
   $ pacman -S enchant
   
   $ sudo apt-get install enchant-2
   ````

If you experience any issues, you may want to have a look at: 
> https://pyenchant.github.io/pyenchant/install.html

It can happen that with the Enchant installation, no providers are installed that enable the spell check. 
For this you can install the desired provider yourself:
```
$ pacman -S aspell

$ sudo apt-get install aspell
```
Also, the desired languages can be installed in this way:
```
$ pacman -S aspell-en
$ pacman -S aspell-de

$ sudo apt-get install aspell-en
$ sudo apt-get install aspell-de
```
If you experience any issues, you may want to have look at:
>https://pyenchant.github.io/pyenchant/install.html#installing-a-dictionary

The standard language for the spell checker is English (en_US). You need to configure the language with the following command:
```
$ acheck config -l $language
```
Supported languages (at the moment): `en_US` `en_GB` `de_DE`


### Plan Validation
If you want to enable plan validation, you need to download the [KCL Validator](https://github.com/KCL-Planning/VAL). Just follow the instructions on the GitHub page and download the binaries for you operating system. 
To get to the download, just click on the `Azure Pipelines` button at the beginning of the [README.md](https://github.com/KCL-Planning/VAL/blob/master/README.md). Save the binaries in a location that suits you.
After downloading, you need to configure the path to the validator executable file. `bin/Validate` or `bin/Validate.exe`

In order to use the plan validator correctly, stop the tool and set the path like:
```
$ acheck config -v $path-to-validate-executable
```
Examples:
```
$ acheck config -v /Users/macos64/Val-20211204.1-Darwin/bin/Validate
$ acheck config -v /Users/linux/Val-20211204.1-Linux/bin/Validate
$ acheck config -v /Users/windows/Val-20211204.1-Windows/bin/Validate.exe
```
---

# Usage
After the package has been installed, just use:

```
$ acheck check $domain.pddl $problem.pddl $annotation.csv
```

By default, it will automatically start a local server on [127.0.0.1:9000](http://127.0.0.1:9000/).

#### Options:  
- `-l $file_1 $file_2 $file_n` : Enter one or multiple annotation files or the domain or problem file to lock them in editor
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -l domain.pddl anno_1.csv
    ```

- `-o $directory`: Enter a custom directory for all output files. 
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -o project/output
    ```
- `-p port`: Specify the `port` on which the server is running. 
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -p 8000
    ```
- `-v`: Enable verbose output. 

- `-m directory`: Enter a custom `directory` to load multiple annotations

- `--nogui`: For command line only use. 

- `--inplace`: Work with the original files. For command line only use without backup. 
   

---
# Structure

### Navbar

![navbar.png](res/navbar.png)

Click on `Check` to check the annotation. `Save` will save all changes that were made.\
`Show All`displays all errors found for the given annotation and model inside the output window.\
Click on `Dictionary` to open the dictionary.

### Dictionary
![dict.png](res/dict.png)
With the `Dictionary` you can tell the spell check to include or exclude words. 
Inside the dictionary, enter a word and click add to add it to the dictionary. Click on words that has been added to select them and click 'Remove' to delete them from the dictionary.

### Annotation Editor

![anno_editor.png](res/anno_editor.png)

Here you can see all open annotations. You can click on the tabs to switch between multiple loaded annotations.
The errors that were found during the check are highlighted. Click on them for further information. 
You will also get advices for fixing the errors if possible. 
You can select the line limit to have only a certain number 
of lines checked by clicking on the desired number of lines 

### Model Editor

![model_editor.png](res/model_editor.png)

Inside the model window you can view and edit the domain and problem file. 

### Check Options

![checks.png](res/checks.png)

The `Checks` panel contains information for each check applied to the annotation.
The checks are divided into two groups:  \
`Continuous Checks` are running everytime you press check. \
`Sequential Checks` are executed one after another. If a check throws an error, the checking process will stop. 
    It will move on if all error thrown by the actual checker are fixed.

You can toggle them off to deactivate them during the checking process. 
The gear button opens the menu for configuring the check.
The second button shows the log that is potentially generated during the execution. 
Click on the colored badge that shows the number of errors found by this check to automatically scroll to the first error found. 
Green means no errors. Yellow means there are only warnings, but they do not disturb the general process. 
Red means errors have been found that need to be taken care of.

### Output

![output.png](res/output.png)

The Output window displays all errors found in the clicked section of the annotation. If you click on one, you will get a selection of correction suggestions and information about the error. These are:
- ReplaceSequence: \
Replaces the section with a suggestion
- RemoveSequence: \
Removes the sequence
- WhitelistSignature: \
Saves the signature of an action as the active signature. Same actions with more or less parameters, are now marked as errors.
- Alert: \
Outputs more information about the error.
- AdaptModel: \
If you want to adapt the model, for example by adding actions or objects, AdaptModel copies a template to the clipboard, which you can directly take over and adapt afterwards.


### Resetting the tool
If you want to reload the original files just delete the output folder and restart the tool, otherwise the tool will always refer to the 
saved backup that was created on the first start.
---
# Clone and prepare for development
Clone the repository and navigate into the `annotation-checker` directory. Now you will need to install all packages that do not come with python.

- If you want to use `Pipenv`, make sure you are in the repository folder and run:
	```
	$ pipenv shell
	$ pipenv install -e .
	```

- If you want to use your own virtual environment:
	```
	$ python -m pip install -r requirements.txt
	$ python -m pip install -e .
	```

This will install the module together with all other packages needed.

If you need some help with virtual environments, have a look at: 
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

## Creating your own `Check`

This is a tutorial on how to create your own check using an example check that checks annotation for capital letters.

1. Go to `src/acheck/checks` and create a new module for your check. In this example we will call it: `capital_letters.py`
2. Open `capital_letters.py` and create a new class that inherits
3. Import the abstract `Check` class from the `acheck/checking/check_interface.py` module and create a new class with the name of the check, which inherits from the `Check` interface.
4. Now you need to implement the abstract method `run` of the `Check` class and your code should look like this:
   ````python
    from pathlib import Path
    from typing import List
    
    from acheck.checking.check_interface import Check
    from acheck.checking.error import Error
    
    
    class CapitalLettersCheck(Check):
    def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        pass
    ````
5. Now we can create a function that checks the annotation for capital letters, and returns a list of `Error` objects. It should contain at least all parameters of the run method, plus a check_id and logs:
    ````python
     class CapitalLettersCheck(Check):
    
     @staticmethod
     def _check_capital_letters(self, annotation ,domain, problem, check_id, logs, line_limit):
        pass
        
     def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        pass
    ````
6. We need to create a new `ErrorType`. So navigate into the `acheck/checking/error.py` module and create the new `ErrorType.IllegalUppercase` type at the end of `ErrorType(Enum)`:
    ````python
   class ErrorType(Enum):
    """All different error types that a check can display"""

    IllegalFile = auto()
    """There is an error when opening or reading the file"""
    IllegalCSVFile = auto()
    """There is an error when opening or reading a csv file"""
    WrongSpelling = auto()
    """There a spelling mistake"""
    IllegalCharacter = auto()
    """There are symbols in the annotation that are not allowed"""
    IllegalTimestampNoNumber = auto()
    """The time slice of an annotation is not a number"""
    IllegalTimestampNotAscending = auto()
    """The time stamps of the actions are equal and or not ascending"""
    IllegalExpressionStructure = auto()
    """The structure of the expressions does not correspond to the predefined structure of an annotation expression"""
    UnknownAction = auto()
    """An action is not defined in the domain"""
    UnknownObject = auto()
    """Another object is not known in the domain"""
    IllegalSignature = auto()
    """The signature of an action is not correct or marked as correct"""
    PlanValidationError = auto()
    """An error occurred when validating the plan resulting from the annotation."""
    IllegalDomainDescription = auto()
    """The PDDL description is not correct"""
    IllegalProblemDescription = auto()
   
    """There are uppercase letters in the annotation"""
    IllegalUppercase = auto()
    ````
7. Now implement your logic. You can use functions from `acheck/utils/annotationhelper.py`, that help you iterate through the annotation file:
    ````python
    """Helper functions parse_annotation and read_annotation"""
    times, divs, expressions = ah.parse_annotation(annotation,line_limit)
    lines = ah.read_annotation(annotation, line_limit) 
      
    """For an example.csv that looks like:
       0,putsock-left_sock-left_foot
       20,putsock-right_sock-right_foot
               
       The returning values of parse_annotation() will look like this:
        times = ["0","20"]
        divs = ["-","-"]
        expressions = ["left_sock-left_foot","right_sock-right_foot"]
               
        The returning values of read_annotation() will look like this:
         lines = [" 0,putsock-left_sock-left_foot"," 20,putsock-right_sock-right_foot"]
    """
8. Now we can implement the logic, that checks for capital letters: 
    ````python
    from pathlib import Path
    from typing import List
    from acheck.checking.check_interface import Check
    from acheck.checking.error import Error, ErrorType, Sequence, Fix, FixCode, ErrorLevel
    import acheck.utils.annotationhelper as ah
    
    
    class CapitalLettersCheck(Check):

    @staticmethod
    def _check_capital_letters(self, annotation, domain, problem, check_id, logs, line_limit):
        # Create an empty list, that will be returned at the end, containing all errors that were found.
        errors = []

        # Use helper function to get a list of all annotation lines
        lines = ah.read_annotation(annotation, line_limit)

        # Iterate through all lines
        for index, line in enumerate(lines):
            # Checking if there are any uppercase letters
            if line != line.lower():
                # We create an Error object and append it to the list
                errors.append(
                    Error(file_name = annotation,  # Simply pass the value
                          error_type = ErrorType.IllegalUppercase,  # Newly created ErrorType.IllegalUppercase
                          check_id = check_id,  # Simply pass the value
                          line_number = index + 1,  # Specify the line number
                          incorrect_sequence = Sequence(start_index=0, char_sequence=line),  # Specify the incorrect char Sequence. In this case we want to mark the whole line. So we can replace it with the correct one later.
                          fixes=[Fix(correct_string=line.lower(), fix_code=FixCode.ReplaceSequence)],  # Specify the auto fix behavior. In this case it will replace the incorrect sequence with the correct string.
                          error_level=ErrorLevel.Error,  # Specify the error level
                          )
                )
        # Return the list at the end
        return errors

    def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        pass
    ````
9. If you want to give some information to the user, you can just append message strings to the `logs` list, and they will be shown later in the tool.
10. As an important info, if there is any kind of `Exception` during the checking process, this check will be disabled automatically and the error message is shown in the tool. If you want to specify your own `Exceptions` just raise them with a custom message.
11. Now it is time to set up the `run()` method:
    ````python
    def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        
        #Always empty the logs at the start
        self.logs.clear()
        
        # Returning the list of errors, that was created by the `_check_capital_letters` method.
        return CapitalLettersCheck._check_capital_letters(
            annotation = annotation,  # Just pass the value
            domain = domain,  # Just pass the value
            problem = problem,  # Just pass the value
            check_id = self.id,  # Just pass the value. The id is generated automatically.
            logs = self.logs, # Just pass the value
            line_limit = line_limit  # Just pass the value. The id is generated automatically.
        )
    ````
12. Now we need to register the `Check` inside `acheck/checkers.py`. Choose at which position you want the check to start and if you want it to be sequential or continuous:
    ````python
    .
    .
    .
    
    from acheck.checks.capital import CapitalLettersCheck
    
    def register_checks(tool_meta):
    
    .
    .
    .
    
    default_checks = [

        # For this example we just added the check at the beginning of the sequentially running checks.
        CapitalLettersCheck(
            group=CheckGroup.Default,  # Pass the default group. For async_checks it would be CheckGroup.Async
            tool_meta=tool_meta  #  Just pass the value. For more information have look in the API Listing under `ToolObjectsMeta`
        ),
        
        ReadFileCheck(
            group=CheckGroup.PreStart,
            tool_meta=tool_meta,
        ),
    .
    .
    .
    ````
13. Now that everything has been registered correctly, the application can be started and the new check appears in the tool. 


---
Get further information and documentation at the [documentation](https://fgratzkowski.github.io/) page.
If you still have questions, feel free to create an [issue](https://github.com/vac-mmis/CausalAnnotationCorrection/issues/new) or contact me at [felix.gratzkowski@uni-rostock.de](felix.gratzkowski@uni-rostock.de).