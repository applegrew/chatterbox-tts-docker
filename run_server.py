#!/usr/bin/env python
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from src.main import main

if __name__ == "__main__":
    main()
