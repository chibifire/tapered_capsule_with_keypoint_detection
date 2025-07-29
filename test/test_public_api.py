"""
Test the public API of the tapered capsule system.
"""

import sys
import os
import unittest

# Add the parent directory to the path so we can import the tapered_capsule module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tapered_capsule


class TestPublicAPI(unittest.TestCase):
    """Test the public API functions and classes."""

    def test_public_api_classes_exist(self):
        """Test that all public API classes exist and can be imported."""
        # Check that all expected classes are available
        self.assertTrue(hasattr(tapered_capsule, 'VRMMeshAnalyzer'))
        self.assertTrue(hasattr(tapered_capsule, 'VRMCapsulePipeline'))
        self.assertTrue(hasattr(tapered_capsule, 'SkinnedCapsulePipeline'))
        self.assertTrue(hasattr(tapered_capsule, 'CapsuleGenerator'))
        self.assertTrue(hasattr(tapered_capsule, 'GLTFCapsuleGenerator'))

    def test_public_api_functions_exist(self):
        """Test that all public API functions exist and can be imported."""
        # Check that all expected functions are available
        self.assertTrue(hasattr(tapered_capsule, 'analyze_vrm_mesh'))
        self.assertTrue(hasattr(tapered_capsule, 'generate_capsules_from_vrm'))
        self.assertTrue(hasattr(tapered_capsule, 'generate_skinned_capsules_from_vrm'))

    def test_version_info(self):
        """Test that version information is available."""
        self.assertTrue(hasattr(tapered_capsule, '__version__'))
        self.assertTrue(hasattr(tapered_capsule, '__author__'))


if __name__ == '__main__':
    unittest.main()
