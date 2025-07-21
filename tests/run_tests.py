"""
Test runner for axr_options module.
Run with: python run_tests.py [test_name]
"""

import sys
import unittest
from . import test_axr_options

def run_all_tests():
    """Run all test cases"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_axr_options)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_specific_test(test_name: str):
    """Run a specific test case"""
    suite = unittest.TestSuite()
    
    # Try to find the test method
    try:
        test_class = test_axr_options.TestAxrOptions
        suite.addTest(test_class(test_name))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except AttributeError:
        print(f"Test '{test_name}' not found!")
        return False

def list_available_tests():
    """List all available test methods"""
    test_class = test_axr_options.TestAxrOptions
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    print("Available tests:")
    for method in test_methods:
        print(f"  - {method}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Run all tests
        print("Running all tests...")
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == '--list':
        # List available tests
        list_available_tests()
    
    elif sys.argv[1].startswith('test_'):
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running test: {test_name}")
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    
    else:
        print("Usage:")
        print("  python run_tests.py                  # Run all tests")
        print("  python run_tests.py --list           # List available tests")
        print("  python run_tests.py test_name        # Run specific test")
        sys.exit(1)
