"""
main.py — CLI Entrypoint for Cryptex - Secure File Encryption
Author: Ojas Purohit (https://github.com/OjasPurohit)
"""

from encrypt import encrypt_file
from decrypt import decrypt_file

print("Cryptex - Secure File Encryption Tool")

choice = input("1 Encrypt File\n2 Decrypt File\n")

file = input("Enter file path: ")
password = input("Enter password: ")

if choice == "1":
    encrypt_file(file, password)

elif choice == "2":
    decrypt_file(file, password)

else:
    print("Invalid choice")