"""
Test runner for supplier app tests.
This module provides a comprehensive test runner that coordinates all supplier app tests.
"""

from django.conf import settings
from django.test.utils import get_runner


def run_all_supplier_tests():
    """
    Run all supplier app tests.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    test_runner_class = get_runner(settings)
    test_runner = test_runner_class()

    test_modules = [
        "src.supplier.tests.test_models",
        "src.supplier.tests.test_responsibility_matrix",
        "src.supplier.tests.test_attachments",
        "src.supplier.tests.test_serializers",
        "src.supplier.tests.test_views",
    ]

    failures = test_runner.run_tests(test_modules)

    if failures:
        print(f"Tests failed with {failures} failures")
        return 1
    else:
        print("All tests passed successfully!")
        return 0


def run_specific_test_module(module_name):
    """
    Run tests from a specific module.

    Args:
        module_name (str): Name of the test module to run

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    test_runner_class = get_runner(settings)
    test_runner = test_runner_class()

    valid_modules = {
        "models": "src.supplier.tests.test_models",
        "matrix": "src.supplier.tests.test_responsibility_matrix",
        "attachments": "src.supplier.tests.test_attachments",
        "serializers": "src.supplier.tests.test_serializers",
        "views": "src.supplier.tests.test_views",
    }

    if module_name not in valid_modules:
        print(f"Invalid module name. Valid options: {', '.join(valid_modules.keys())}")
        return 1

    test_module = valid_modules[module_name]
    failures = test_runner.run_tests([test_module])

    if failures:
        print(f"Tests in {module_name} failed with {failures} failures")
        return 1
    else:
        print(f"All tests in {module_name} passed successfully!")
        return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        exit_code = run_specific_test_module(module_name)
    else:
        exit_code = run_all_supplier_tests()

    sys.exit(exit_code)
