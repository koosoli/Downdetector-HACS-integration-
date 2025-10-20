#!/usr/bin/env python3
"""Validation script for Downdetector integration."""
import json
import os
import sys
from pathlib import Path


def validate_integration():
    """Validate the integration structure and files."""
    errors = []
    warnings = []
    
    # Base path
    base_path = Path(__file__).parent / "custom_components" / "downdetector"
    
    # Check required files
    required_files = [
        "__init__.py",
        "manifest.json",
        "config_flow.py",
        "const.py",
        "sensor.py",
        "api.py",
        "strings.json",
    ]
    
    for file in required_files:
        file_path = base_path / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")
        else:
            print(f"✓ Found {file}")
    
    # Validate manifest.json
    try:
        manifest_path = base_path / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_manifest_keys = [
            "domain", "name", "config_flow", "documentation",
            "requirements", "version"
        ]
        
        for key in required_manifest_keys:
            if key not in manifest:
                errors.append(f"Missing manifest key: {key}")
            else:
                print(f"✓ Manifest has '{key}': {manifest[key]}")
        
        if manifest.get("domain") != "downdetector":
            errors.append("Domain must be 'downdetector'")
        
        if not manifest.get("config_flow"):
            errors.append("config_flow must be true")
            
    except json.JSONDecodeError as e:
        errors.append(f"Invalid manifest.json: {e}")
    except Exception as e:
        errors.append(f"Error reading manifest.json: {e}")
    
    # Validate strings.json
    try:
        strings_path = base_path / "strings.json"
        with open(strings_path) as f:
            strings = json.load(f)
        print("✓ Valid strings.json")
        
        if "config" not in strings:
            warnings.append("strings.json missing 'config' section")
            
    except json.JSONDecodeError as e:
        errors.append(f"Invalid strings.json: {e}")
    except Exception as e:
        errors.append(f"Error reading strings.json: {e}")
    
    # Check translations
    translations_path = base_path / "translations"
    if not translations_path.exists():
        errors.append("Missing translations directory")
    else:
        en_translation = translations_path / "en.json"
        if not en_translation.exists():
            errors.append("Missing en.json translation file")
        else:
            try:
                with open(en_translation) as f:
                    json.load(f)
                print("✓ Valid translations/en.json")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid translations/en.json: {e}")
    
    # Check hacs.json
    hacs_path = Path(__file__).parent / "hacs.json"
    if not hacs_path.exists():
        warnings.append("Missing hacs.json (recommended for HACS)")
    else:
        try:
            with open(hacs_path) as f:
                hacs = json.load(f)
            print("✓ Valid hacs.json")
            
            if "name" not in hacs:
                warnings.append("hacs.json missing 'name' field")
                
        except json.JSONDecodeError as e:
            errors.append(f"Invalid hacs.json: {e}")
    
    # Check Python syntax
    for py_file in base_path.glob("*.py"):
        try:
            with open(py_file) as f:
                compile(f.read(), py_file, "exec")
            print(f"✓ Valid Python syntax: {py_file.name}")
        except SyntaxError as e:
            errors.append(f"Syntax error in {py_file.name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if not errors and not warnings:
        print("✅ All checks passed! Integration is ready.")
        return 0
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print(f"\n❌ {len(errors)} Error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(validate_integration())
