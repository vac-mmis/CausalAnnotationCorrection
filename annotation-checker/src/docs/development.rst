Clone and prepare for development
=================================

Clone the repository and navigate into the ``annotation-checker`` directory. Now you will need to install all packages that do not come with python.


* 
  If you want to use ``Pipenv``\ , make sure you are in the repository folder and run:

  .. code-block::

       $ pipenv shell
       $ pipenv install -e .

* 
  If you want to use your own virtual environment:

  .. code-block::

       $ python -m pip install -r requirements.txt
       $ python -m pip install -e .

This will install the module together with all other packages needed.

If you need some help with virtual environments, have a look at: 
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

Creating your own ``Check``
-------------------------------

This is a tutorial on how to create your own check using an example check that checks annotation for capital letters.


1. Go to ``src/acheck/checks`` and create a new module for your check. In this example we will call it: ``capital_letters.py``
2. Open ``capital_letters.py`` and create a new class that inherits
3. Import the abstract ``Check`` class from the ``acheck/checking/check_interface.py`` module and create a new class with the name of the check, which inherits from the ``Check`` interface.
4. Now you need to implement the abstract method ``run`` of the ``Check`` class and your code should look like this:

.. code-block:: python
        :linenos:

        from pathlib import Path
        from typing import List
        from acheck.checking.check_interface import Check
        from acheck.checking.error import Error

        class CapitalLettersCheck(Check):
            def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
               pass

5. Now we can create a function that checks the annotation for capital letters, and returns a list of ``Error`` objects. It should contain at least all parameters of the run method, plus a ``check_id`` and ``logs``:

.. code-block:: python
        :linenos:

        class CapitalLettersCheck(Check):

            @staticmethod
            def _check_capital_letters(self, annotation ,domain, problem, check_id, logs, line_limit):
                pass
            def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
                pass

6. We need to create a new ``ErrorType``. So navigate into the ``acheck/checking/error.py`` module and create the new ``ErrorType.IllegalUppercase`` type at the end of ``ErrorType(Enum)``\ :

.. code-block:: python
        :linenos:

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


7. Now implement your logic. You can use functions from ``acheck/utils/annotationhelper.py``\ , that help you iterate through the annotation file:

.. code-block:: python
        :linenos:

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

.. code-block:: python
        :linenos:

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



9. If you want to give some information to the user, you can just append message strings to the ``logs`` list, and they will be shown later in the tool.
10. As an important info, if there is any kind of ``Exception`` during the checking process, this check will be disabled automatically and the error message is shown in the tool. If you want to specify your own ``Exceptions`` just raise them with a custom message.
11. Now it is time to set up the ``run()`` method:

   .. code-block:: python
        :linenos:

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

12.
   Now we need to register the ``Check`` inside ``acheck/checkers.py``. Choose at which position you want the check to start and if you want it to be sequential or continuous:

   .. code-block:: python
        :linenos:

        .
        .
        .

        from acheck.checks.capital import CapitalLettersCheck

        def register_checks(tool_meta):

        .
        .
        .

        default_checks = [

          # For this example we just added the check at the beginning of the sequentially running checks
          CapitalLettersCheck(
              group=CheckGroup.Default,  # Pass the default group. For async_checks it would be CheckGroup.Async
              tool_meta=tool_meta  # Just pass the value. For more information have look in the API Listing under `ToolObjectsMeta`
          ),

          ReadFileCheck(
              group=CheckGroup.PreStart,
              tool_meta=tool_meta,
          ),
        .
        .
        .

13. Now that everything has been registered correctly, the application can be started and the new check appears in the tool.

