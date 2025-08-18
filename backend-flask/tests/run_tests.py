"""
Test runner for all competitive feature tests
"""
import unittest
import sys
import os

# Add project directories to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'app'))
sys.path.insert(0, os.path.join(project_root, 'services'))
sys.path.insert(0, os.path.join(project_root, 'tests'))

def run_all_tests():
    """Run all competitive feature tests"""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load test modules
    test_modules = [
        'test_competitive_features',
        'test_api_endpoints'
    ]
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"Warning: Could not import {module}: {e}")
            continue
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
