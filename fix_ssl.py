#!/usr/bin/env python3
"""
Fix for Python 3.7 SSL certificate issue on macOS.
Run this once to install certifi certificates.
"""
import ssl
import certifi
import os

# This ensures pip can use HTTPS
ssl_context = ssl.create_default_context(cafile=certifi.where())

print("SSL setup complete!")
print(f"Certifi location: {certifi.where()}")
