"""
Test script to demonstrate the Downdetector integration structure.

This script validates the integration structure without requiring Home Assistant.
"""
import ast
import json
import sys
from pathlib import Path


def test_file_structure():
    """Test that all required files exist."""
    print("Testing File Structure...")
    
    base_path = Path(__file__).parent / "custom_components" / "downdetector"
    
    required_files = {
        "__init__.py": "Main integration module",
        "manifest.json": "Integration manifest",
        "config_flow.py": "Configuration flow",
        "const.py": "Constants",
        "sensor.py": "Sensor platform",
        "api.py": "API client",
        "strings.json": "UI strings",
    }
    
    all_exist = True
    for filename, description in required_files.items():
        filepath = base_path / filename
        if filepath.exists():
            print(f"✓ {filename:20s} - {description}")
        else:
            print(f"❌ {filename:20s} - MISSING")
            all_exist = False
    
    # Check translations
    translations_path = base_path / "translations" / "en.json"
    if translations_path.exists():
        print(f"✓ {'translations/en.json':20s} - English translations")
    else:
        print(f"❌ {'translations/en.json':20s} - MISSING")
        all_exist = False
    
    return all_exist


def test_manifest():
    """Test the manifest.json structure."""
    print("\nTesting Manifest...")
    
    manifest_path = Path(__file__).parent / "custom_components" / "downdetector" / "manifest.json"
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_keys = ["domain", "name", "config_flow", "documentation", "requirements", "version"]
        
        for key in required_keys:
            if key in manifest:
                print(f"✓ {key:20s}: {manifest[key]}")
            else:
                print(f"❌ {key:20s}: MISSING")
                return False
        
        # Validate specific values
        if manifest["domain"] != "downdetector":
            print(f"❌ domain must be 'downdetector', got '{manifest['domain']}'")
            return False
        
        if not manifest["config_flow"]:
            print("❌ config_flow must be true")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False


def test_api_methods():
    """Test that API client has required methods."""
    print("\nTesting API Client Methods...")
    
    api_path = Path(__file__).parent / "custom_components" / "downdetector" / "api.py"
    
    try:
        with open(api_path) as f:
            tree = ast.parse(f.read())
        
        # Find the DowndetectorApiClient class
        client_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DowndetectorApiClient":
                client_class = node
                break
        
        if not client_class:
            print("❌ DowndetectorApiClient class not found")
            return False
        
        # Check for required methods
        required_methods = ["search_services", "get_service_status", "get_all_services"]
        found_methods = [n.name for n in client_class.body if isinstance(n, ast.AsyncFunctionDef)]
        
        for method in required_methods:
            if method in found_methods:
                print(f"✓ Method: {method}")
            else:
                print(f"❌ Missing method: {method}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing API client: {e}")
        return False


def test_config_flow_steps():
    """Test that config flow has required steps."""
    print("\nTesting Config Flow Steps...")
    
    config_flow_path = Path(__file__).parent / "custom_components" / "downdetector" / "config_flow.py"
    
    try:
        with open(config_flow_path) as f:
            tree = ast.parse(f.read())
        
        # Find the config flow class
        flow_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DowndetectorConfigFlow":
                flow_class = node
                break
        
        if not flow_class:
            print("❌ DowndetectorConfigFlow class not found")
            return False
        
        # Check for required methods
        required_steps = ["async_step_user", "async_step_select_service"]
        found_methods = [n.name for n in flow_class.body if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef))]
        
        for step in required_steps:
            if step in found_methods:
                print(f"✓ Step: {step}")
            else:
                print(f"❌ Missing step: {step}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing config flow: {e}")
        return False


def test_sensor_properties():
    """Test that sensor has required properties."""
    print("\nTesting Sensor Properties...")
    
    sensor_path = Path(__file__).parent / "custom_components" / "downdetector" / "sensor.py"
    
    try:
        with open(sensor_path) as f:
            tree = ast.parse(f.read())
        
        # Find the sensor class
        sensor_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DowndetectorSensor":
                sensor_class = node
                break
        
        if not sensor_class:
            print("❌ DowndetectorSensor class not found")
            return False
        
        print("✓ DowndetectorSensor class found")
        
        # Check for coordinator class
        coordinator_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DowndetectorDataUpdateCoordinator":
                coordinator_class = node
                break
        
        if coordinator_class:
            print("✓ DowndetectorDataUpdateCoordinator class found")
        else:
            print("❌ DowndetectorDataUpdateCoordinator class not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing sensor: {e}")
        return False


def test_constants():
    """Test that required constants are defined."""
    print("\nTesting Constants...")
    
    const_path = Path(__file__).parent / "custom_components" / "downdetector" / "const.py"
    
    try:
        with open(const_path) as f:
            content = f.read()
        
        required_constants = [
            "DOMAIN",
            "UPDATE_INTERVAL",
            "CONF_SERVICE_ID",
            "CONF_SERVICE_NAME",
            "ATTR_BASELINE",
            "ATTR_CURRENT_REPORTS",
            "ATTR_STATUS"
        ]
        
        for const in required_constants:
            if const in content:
                print(f"✓ Constant: {const}")
            else:
                print(f"❌ Missing constant: {const}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading constants: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("DOWNDETECTOR INTEGRATION STRUCTURE VALIDATION")
    print("=" * 70)
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Manifest", test_manifest),
        ("API Client", test_api_methods),
        ("Config Flow", test_config_flow_steps),
        ("Sensor", test_sensor_properties),
        ("Constants", test_constants),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
        print()
    
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30s}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if all(result for _, result in results):
        print("\n✅ All structure tests passed!")
        print("\n" + "=" * 70)
        print("INTEGRATION READY")
        print("=" * 70)
        print("\nThis integration provides:")
        print("  • Service search functionality via the Downdetector API")
        print("  • Real-time monitoring of service status")
        print("  • Automatic outage detection (minor/major)")
        print("  • Home Assistant config flow integration")
        print("  • HACS compatibility")
        print("\nTo use this integration:")
        print("  1. Copy 'custom_components/downdetector' to your Home Assistant config")
        print("  2. Restart Home Assistant")
        print("  3. Go to Settings → Devices & Services → Add Integration")
        print("  4. Search for 'Downdetector' and configure")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
