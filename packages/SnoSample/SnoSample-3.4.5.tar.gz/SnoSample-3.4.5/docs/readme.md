# SnoSample

Simplified tools for Python projects.

## Installation

To install the SnoSample package either:

- run the command 'pip install snosample' in the command line.
- install the package via your IDE.

## Features

#### SnoSample module

1. The user is able to define extra arguments for the Python script,  
   when running it from the command line:
   1. these arguments can be required.
   2. these arguments can be optional.
   3. an error is raised when the required arguments are not given.
   4. an error is raised when an unknown argument is given.
   5. these arguments can be viewed from the command line.

#### SnoSample.testing module

1. The user is able to define test cases inside a test suite.
2. The user is able to run all test cases with a single command:
   1. this command shows if the test suite succeeded.
   2. this command can exit with code 1 when the test suite fails.
3. The user is able to see the test case results after each run:
   1. these results show if a test case failed.
   2. these results show why a test case failed.
   3. these results reset before each run.
   4. these results include the traceback if an error is raised.
4. The user is able to define a test suite setup:
   1. this setup is optional.
   2. this setup can be run independently of the test cases.
   3. this setup triggers automatically when the test suite is run.
   4. the test cases will not be run when this setup fails.
5. The user is able to define a test suite teardown:
   1. this teardown is optional.
   2. this teardown can be run independently of the test cases.
   3. this teardown triggers automatically when the test suite is run.
6. The user is able to define a test case setup:
   1. this setup is optional.
   2. this setup can be run independently of the test cases.
   3. this setup triggers automatically before each test case.
   4. this setup shows its results under the respective test case when not successful.
7. The user is able to define a test case teardown:
   1. this teardown is optional.
   2. this teardown can be run independently of the test cases.
   3. this teardown triggers automatically after each test case. 
   4. this teardown shows its results under the respective test case when not successful.
8. The user is able to assert if two variables are (un)equal:
   1. these variables can be booleans.
   2. these variables can be strings.
   3. these variables can be integers or floats.
   4. these variables can be lists or tuples.
   5. these variables can be dictionaries.
   6. these variables can be numpy arrays.
9. The user is able to assert if two variables are almost equal within a margin:
   1. the user can define this margin.
   2. this margin can be relative or absolute.
   3. these variables can be integers or floats.
   4. these variables can be lists or tuples with integers and/or floats.
   5. an error is raised when these variables have different/no sizes.
   6. an error is raised when these variables contain a non-numeric value.
   7. these variables can be numpy arrays.
10. The user is able to assert if an expression is True.
11. The user is able to assert if an expression is False.
12. The user is able to assert if executing a callable raises an error:
    1. the user can define the callable including its arguments.
    2. the user can define the expected type of error raised.
    3. an error is raised when the error is not as expected.
    4. an error is raised when no error is raised.
13. A test suite summary is printed to the console when running the test cases:
    1. this summary includes the result of the test suite setup.
    2. this summary includes the result of each test case.
    3. this summary includes the result of the test suite teardown.
    4. this summary can be optional.

#### SnoSample.logging module

1. The logger is able to show messages in the console:
   1. the user can define these messages.
2. The logger is able to write messages to a text file:
   1. the user can define these messages.
   2. the user can define this file path.
   3. the logger raises an error when the file path does not exist.
   4. this text file does not need to exist.
   5. this text file is overwritten by the messages.
3. The logger is able to show the time at which the message was generated.
4. The logger is able to show the level of the message:
   1. the user can define this level.
   2. the accepted message levels are: 'debug', 'info', 'warning', 'error'.
   3. an error is raised when an unacceptable message level is given.
   4. debug messages have a blue colour in the console.
   5. info messages have a white colour in the console.
   6. warning messages have a yellow colour in the console.
   7. error messages have a red colour in the console.
5. The user is able to define a message level threshold:
   1. the accepted thresholds are: 'debug', 'info', 'warning', 'error'.
   2. an error is raised when an unacceptable message level is given.
   3. all messages below this threshold will not be shown by the logger.
   4. this threshold can be different for the file and the console messages.
6. The user is able to define a layout for the messages:
   1. an error is raised when the message is not included in the layout.
   2. this layout can include extra substrings defined by the user.

#### SnoSample.multi module

1. The user is able to spawn subprocesses targeting a callable:
   1. this callable can be defined by the user.
   2. the list of parameter sets or this callable can be defined by the user.
   3. the number of these subprocesses can be defined by the user.
   4. these subprocesses terminate automatically when the callable has run.
   5. the callable is only run once per parameter set.
   6. the main process waits for these subprocesses to finish before continuing.
   7. a lock can be defined by the user.

2. The user is able to spawn threads targeting a callable:
   1. this callable can be defined by the user.
   2. the list of parameter sets or this callable can be defined by the user.
   3. the number of these threads can be defined by the user.
   4. these threads terminate automatically when the callable has run.
   5. the callable is only run once per parameter set.
   6. the main process waits for these threads to finish before continuing.
   7. a lock can be defined by the user.

## Usage

#### Arguments

1. To enable argument parsing for Python script import the 'parse_arguments' function.
2. Define the arguments according to the example given in the function description.      
   Run 'help(parse_arguments)' to view this example.
3. Call the function with the defined list.
4. It will return the arguments as a dictionary when running the script from the command line.

#### Testing

1. Define a child class from the 'TestSuite' parent class located in the 'testing' module.
2. In this class, define your test cases.
3. Optionally, define test suite or test case setups and teardowns.
4. Create an instance of the child class and run the 'run_test_suite' method.  
   By default, it exits with code 0 if successful or 1 if not.
   By default, it prints a summary after running the test suite.
   The results are also stored in the 'results' attribute of the instance.

#### Assertions

1. Import the desired types of assertions from the 'testing' module.
2. Assert away.

#### Logging

1. Create an instance of the 'Logger' class located in the 'logging' module.  
   By default, the messages will be printed in the console and will not be written to a file.  
   Optionally, to view all logging options, run 'help(Logger)'.
2. Create messages by running the instance method 'message'.  
   By default, the message level is 'info', this can be changed to: 'debug', 'warning', 'error'.

#### Multiprocessing

1. It is recommended to use multiprocessing with an 'if name equals main' statement.
2. It is recommended to use a lock from the 'multiprocessing' built-in module when writing to a single file.
3. For each repeated function call, create a set of parameters, and put these in a list.
4. Run the 'run_processes' function from the 'multi' module with the target function and its defined parameters.
   Optionally, define the number of subprocesses to create. 

#### Multithreading

1. It is recommended to use a lock from the 'multiprocessing' built-in module when writing to a single file.
2. For each repeated function call, create a set of parameters, and put these in a list.
3. Run the 'run_threads' function from the 'multi' module with the target function and its defined parameters.
   Optionally, define the number of threads to create. 

## Changelog

#### v3.4.5

- SnoSample.logging features 4.4 through 4.7 added.
- SnoSample.multi features 1.7 and 2.7 added.
- Revision of project structure.

#### v3.4.4

- SnoSample.testing feature 9 bugfix.

#### v3.4.3

- SnoSample.testing feature 13 bugfix.

#### v3.4.2

- SnoSample.testing feature 3.4 added.
- SnoSample.testing feature 13 bugfix.

#### v3.4.1

- SnoSample.testing feature 9 bugfix.

#### v3.4.0

- SnoSample.testing features 8.6 and 9.7 added.

#### v3.3.0

- SnoSample.testing features 2.2 and 13 added.

#### v3.2.0

- SnoSample.testing features 8 through 12 added.

#### v3.1.3

- SnoSample.multi features 1 and 2 added.

#### v2.1.3

- Revision of licence.

#### v2.1.2

- SnoSample feature 1 added.

#### v2.0.2

- Revision of project structure.

#### v2.0.1

- Revision of documentation.
- Revision of naming conventions.

#### v2.0.0

- SnoSample.logging features 1 through 6 added.

#### v1.0.0

- SnoSample.testing features 1 through 7 added.

#### v0.1.0

- Initial release.
