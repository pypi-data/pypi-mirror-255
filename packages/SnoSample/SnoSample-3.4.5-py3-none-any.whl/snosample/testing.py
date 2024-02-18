# Default Python packages.
from sys import exit as sys_exit
from time import time
from traceback import format_exc
from typing import Callable, Type, Optional, Union

# Packages from requirements.
from numpy import ndarray, array_equal, allclose


SUPPORTED = Union[bool, str, int, float, list, tuple, dict, ndarray]


class TestSuite:
    """
    Parent class to define and run test cases with.
    """
    def __init__(self):
        self.results = {}

    def _get_test_cases(self) -> list:
        """
        Get all test cases defined in the child class.

        Returns
        -------
        list:
            All the test cases defined in the child class.
            Returns an empty list when the parent class is used directly.
        """
        # Get all child class attributes.
        child = self
        child_all = dir(self)
        child_attributes = list(self.__dict__.keys())

        # Get all parent class methods.
        parent = self.__class__.__base__
        parent_methods = dir(parent)

        # Get child methods which are not in parent class.
        tests = [test for test in child_all if test not in parent_methods]
        tests = [test for test in tests if test not in child_attributes]

        # Return empty list when parent class is used directly.
        if self.__class__.__base__ == object:
            tests = []

        return [getattr(child, test) for test in tests]

    def _run_test_suite_method(self, method: Callable) -> bool:
        """
        Run a test suite method.

        Parameters
        ----------
        method: Callable
            The test suite method to be run.

        Returns
        -------
        bool:
            True: the test suite method succeeded.
            False: the test suite method failed.
        """
        name = method.__name__
        success = False
        message = None
        trace = None

        try:
            method()
            success = True
        except Exception as error:
            message = f"{error.__class__.__name__}: {error}"
            trace = format_exc()

        self.results[name] = {"success": success, "message": message, "traceback": trace}
        return success

    def _run_test_case(self, test_case: Callable) -> bool:
        """
        Run a test case method including its setup and teardown.

        Parameters
        ----------
        test_case: Callable
            The test case method to be run.

        Returns
        -------
        bool:
            True: the test case, including its setup and teardown, succeeded.
            False: either the test case, its setup, or its teardown failed.
        """
        name_case = test_case.__name__
        name_setup = self.set_up_test_case.__name__
        name_teardown = self.tear_down_test_case.__name__

        # Return False when test case setup fails.
        if not self._run_test_suite_method(method=self.set_up_test_case):
            # Replace test case setup key with test case method key in results.
            self.results[name_case] = self.results.pop(name_setup)
            return False

        # Run test case.
        success = self._run_test_suite_method(method=test_case)

        # Return False when test case teardown fails.
        if not self._run_test_suite_method(method=self.tear_down_test_case):
            # Replace test case setup key with test case method key in results.
            self.results[name_case] = self.results.pop(name_teardown)
            return False

        return success

    def run_test_suite(self, do_exit: bool = True, do_summary: bool = True) -> Union[bool, int]:
        """
        Run the entire test suite including its setups and teardowns.

        Parameters
        ----------
        do_exit: bool
            Exit the interpreter once the test suite has run.
        do_summary: bool
            Print a summary of the test suite run in the console.

        Returns
        -------
        bool:
            True: all test suite methods succeeded.
            False: some test suite methods failed.
        int:
            0: all test suite methods succeeded.
            1: some test suite methods failed.
        """
        def _print_summary():
            front = f"Test summary '{self.__class__.__name__}'"
            back = f"{len(front) * '-'}"
            front = f"{front}\n{len(front) * '-'}\n"

            print(f"\n{front}{message}{back}\n")

        start = time()

        # Reset results.
        self.results = {}

        # Run test suite setup and exit/return if it fails.
        if not self._run_test_suite_method(method=self.set_up_test_suite):
            result = self.results["set_up_test_suite"]

            if do_summary:
                message = f"set_up_test_suite: {result['message']}"
                _print_summary()

            return sys_exit(result) if do_exit else False

        # Run all test cases.
        success = {"bool": True, "code": 0}
        tests = self._get_test_cases()

        for test in tests:
            if not self._run_test_case(test_case=test):
                success = {"bool": False, "code": 1}

        # Run test suite teardown.
        if not self._run_test_suite_method(method=self.tear_down_test_suite):
            success = {"bool": False, "code": 1}

        end = time()

        # Print test suite summary.
        if do_summary:
            length = len(tests)
            duration = round(end - start, 3)
            message = f"Ran {length} test cases in {duration} seconds.\n\n"

            if not success["bool"]:
                for result in self.results.keys():
                    if not self.results[result]["success"]:
                        message += f"{result}: {self.results[result]['message']}\n"
            else:
                message += "All tests passed!\n"

            _print_summary()

        # Return/exit success of test suite run.
        return sys_exit(success["code"]) if do_exit else success["bool"]

    def set_up_test_suite(self):
        """
        Editable placeholder for the test suite setup.
        """

    def tear_down_test_suite(self):
        """
        Editable placeholder for the test suite teardown.
        """

    def set_up_test_case(self):
        """
        Editable placeholder for the test case setup.
        """

    def tear_down_test_case(self):
        """
        Editable placeholder for the test case setup.
        """


def assert_equal(calc: SUPPORTED, true: SUPPORTED) -> None:
    """
    Assert if two variables are equal.

    Parameters
    ----------
    calc: SUPPORTED
        Calculated or predicted variable value.
    true: SUPPORTED
        True or expected variable value.
    """
    # Raise error if numpy arrays are not equal.
    if isinstance(calc, ndarray) and isinstance(true, ndarray):
        if not array_equal(a1=calc, a2=true):
            raise AssertionError(f"calculated value {calc} is not equal to true value {true}")

    # Raise error if types are not equal.
    elif not isinstance(calc, type(true)):
        raise AssertionError(f"calculated {type(calc)} is not equal to true {type(true)}")

    # Raise error if variables with built-in types are not equal.
    elif calc != true:
        raise AssertionError(f"calculated value {calc} is not equal to true value {true}")


def assert_not_equal(calc: SUPPORTED, true: SUPPORTED) -> None:
    """
    Assert if two variables are not equal.

    Parameters
    ----------
    calc: SUPPORTED
        Calculated or predicted variable value.
    true: SUPPORTED
        True or expected variable value.
    """
    # Raise error if numpy arrays are equal.
    if isinstance(calc, ndarray) and isinstance(true, ndarray):
        if array_equal(a1=calc, a2=true):
            raise AssertionError(f"calculated value {calc} is equal to true value {true}")

    # Return if types are not equal.
    elif not isinstance(calc, type(true)):
        return

    # Raise error if variables with built-in types are equal.
    elif calc == true:
        raise AssertionError(f"calculated value {calc} is equal to true value {true}")


def assert_almost_equal(calc: Union[list, tuple, ndarray], true: Union[list, tuple, ndarray],
                        margin: float, relative: bool = True) -> None:
    """
    Assert if two variables are almost equal within a given margin.
    Supported accuracy: up to and including 10 ** -10.

    Parameters
    ----------
    calc: SUPPORTED
        Calculated or predicted variable value.
    true: SUPPORTED
        True or expected variable value.
    margin: float
        Allowed margin for the comparison.
        The true value is used as a reference.
    relative: bool
        The margin is a fraction of the reference value when True (relative),
        or the margin is used directly when False (absolute).
    """
    def check_elements(calc_ele, true_ele):
        # Check if elements are numeric.
        try:
            calc_ele, true_ele = float(calc_ele), float(true_ele)
        except ValueError:
            raise AssertionError("margin not supported for non-numeric variables")

        # Calculate allowed margin.
        allowed = true_ele * margin if relative else margin
        value = round(abs(calc_ele - true_ele), 10)

        # Iterables are not equal when element value lies outside allowed margin.
        if value >= allowed:
            raise AssertionError(f"calculated {calc} is not close to true {true}")

    # Raise error if numpy arrays are not almost equal.
    if isinstance(calc, ndarray) and isinstance(true, ndarray):
        margin_rel = margin if relative else 0
        margin_abs = margin if not relative else 0

        if not allclose(a=calc, b=true, rtol=margin_rel, atol=margin_abs):
            raise AssertionError(f"calculated {calc} is not close to true {true}")

    # Raise error if types are not equal.
    elif not isinstance(calc, type(true)):
        raise AssertionError(f"calculated {type(calc)} is not equal to true {type(true)}")

    # Check if variables are iterable.
    elif "__iter__" in dir(calc) and "__iter__" in dir(true):
        # Check if lengths match.
        if len(calc) != len(true):
            raise AssertionError(f"calculated {calc} is not the same size as true {true}")

        # Check each element if so.
        for i in range(len(calc)):
            check_elements(calc_ele=calc[i], true_ele=true[i])

    # Perform single comparison if not.
    else:
        check_elements(calc_ele=calc, true_ele=true)


def assert_true(expr: bool) -> None:
    """
    Assert if an expression is True.

    Parameters
    ----------
    expr: bool
        Any expression which can be reduced to a boolean (e.g. non-empty list, operator).
    """
    if not expr:
        raise AssertionError(f"calculated variable or statement {expr} is not True")


def assert_false(expr: bool) -> None:
    """
    Assert if an expression is False.

    Parameters
    ----------
    expr: bool
        Any expression which can be reduced to a boolean (e.g. empty list, operator).
    """
    if expr:
        raise AssertionError(f"calculated variable or statement {expr} is not False")


def assert_raises(action: Callable, expected: Type[Exception],
                  args: Optional[tuple] = None, kwargs: Optional[dict] = None) -> None:
    """
    Assert if executing a callable raises an error.

    Parameters
    ----------
    action: Callable
        Any callable object to be executed.
    expected: Type[Exception]
        Expected error to be raised.
    args: tuple
        Arguments for the callable, if any.
    kwargs: dict
        Keyword arguments for the callable, if any.
    """
    args = () if args is None else args
    kwargs = {} if kwargs is None else kwargs

    try:
        action(*args, **kwargs)
        message = "no error is raised"

    except Exception as error:
        if not isinstance(error, expected):
            message = f"raised error is not {expected}: {type(error)} {error}"
        else:
            return

    raise AssertionError(message)
