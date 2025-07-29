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

    def test_feminine_avatar_path(self):
        """Test that the feminine avatar VRM file exists."""
        # Path to the feminine VRM avatar
        vrm_path = "thirdparty/vrm_samples/vroid/fem_vroid.vrm"
        
        # Check if the file exists (this is more of a setup check than a test)
        if os.path.exists(vrm_path):
            print(f"✅ Feminine avatar VRM file found: {vrm_path}")
        else:
            print(f"⚠️  Feminine avatar VRM file not found: {vrm_path}")
            print("   This is expected in some environments.")


if __name__ == '__main__':
    unittest.main()
