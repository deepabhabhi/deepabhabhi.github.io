#!/usr/bin/env python3
"""
Simple program to decrypt the encrypted addition.py file and run it
Uses XOR cipher with base64 decoding (no external dependencies required)
"""

import os
import tempfile
import subprocess
import sys
import base64

def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("ERROR: .env file not found")
    return env_vars

def xor_encrypt_decrypt(data: bytes, key: str) -> bytes:
    """XOR encrypt/decrypt data with key"""
    key_bytes = key.encode()
    key_len = len(key_bytes)
    return bytes([data[i] ^ key_bytes[i % key_len] for i in range(len(data))])

def decrypt_file(encrypted_file_path: str, password: str) -> bytes:
    """Decrypt a file with given password using XOR cipher"""
    # Read the encrypted file
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encoded_data = encrypted_file.read()
    
    # Decode from base64
    encrypted_data = base64.b64decode(encoded_data)
    
    # Decrypt the data using XOR
    decrypted_data = xor_encrypt_decrypt(encrypted_data, password)
    
    return decrypted_data

def run_decrypted_program(decrypted_content: bytes):
    """Run the decrypted Python program"""
    # Create a temporary file to store decrypted content
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
        temp_file.write(decrypted_content)
        temp_file_path = temp_file.name
    
    try:
        # Execute the temporary Python file
        print("Running decrypted program:")
        print("-" * 40)
        result = subprocess.run([sys.executable, temp_file_path], 
                              capture_output=True, text=True)
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print("-" * 40)
        print(f"Program executed with return code: {result.returncode}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

def main():
    """Main function to decrypt and run the encrypted addition.py"""
    # Load environment variables
    env_vars = load_env_file()
    
    # Get decryption key from environment
    decrypt_key = env_vars.get('ENCRYPT_DECRYPT_KEY')
    if not decrypt_key:
        print("ERROR: ENCRYPT_DECRYPT_KEY not found in .env file")
        return
    
    # File path
    encrypted_file = 'addition.py.encrypted'
    
    # Check if encrypted file exists
    if not os.path.exists(encrypted_file):
        print(f"ERROR: Encrypted file '{encrypted_file}' not found")
        print("Please run encrypt_simple.py first to create the encrypted file.")
        return
    
    # Decrypt and run the file
    try:
        print(f"Decrypting '{encrypted_file}'...")
        decrypted_content = decrypt_file(encrypted_file, decrypt_key)
        print("Decryption successful!")
        
        # Run the decrypted program
        run_decrypted_program(decrypted_content)
        
    except Exception as e:
        print(f"ERROR: Failed to decrypt or run file: {e}")

if __name__ == "__main__":
    main()