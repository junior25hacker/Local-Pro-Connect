#!/usr/bin/env python
"""
Wrapper to run comprehensive test data creation
"""
import subprocess
import sys
import os

# Change to Django directory
os.chdir('/workspace/Django')

# Run the script
result = subprocess.run([
    sys.executable, 
    'scripts/create_comprehensive_test_data.py'
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
    
sys.exit(result.returncode)
