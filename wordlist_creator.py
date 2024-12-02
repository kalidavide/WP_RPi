"""
Name:           Wordlist Creator
Version:        1.0
Author:         Lucas G. 
Description:    Creates a random wordlist which can be used for Wifi Pentesting
Date:           2.12.2024
Usage:          python3 wordlist_creator.py
Dependencies:   python3
"""
import random, string, os


def setup_output(wordlist_dir="wordlist"):
    """Create output"""
    if not os.path.exists(wordlist_dir):
        os.makedirs(wordlist_dir)
        print(f"[INFO] Created folder: {wordlist_dir}")
    else:
        print(f"[INFO] Folder '{wordlist_dir}' already exists.")
    return wordlist_dir

def parameter_input():
    """Prompt user for wordlist parameters"""
    try:
        min_length = int(input("Enter minimum password length: "))
        max_length = int(input("Enter maximum password length: "))
        wordlist_size = int(input("Enter the number of passwords to generate: "))

        print("\nInclude special characters (symbols)?")
        print("1. Yes (letters, numbers, and symbols)")
        print("2. No (letters and numbers only)")
        char_choice = int(input("Enter your choice (1/2): "))

        if char_choice == 1:
            charset = string.ascii_letters + string.digits + string.punctuation
        elif char_choice == 2:
            charset = string.ascii_letters + string.digits
        else:
            print("[ERROR] Invalid choice. Defaulting to letters and numbers.")
            charset = string.ascii_letters + string.digits

        return min_length, max_length, wordlist_size, charset
    except ValueError as e:
        print(f"[ERROR] Invalid input: {e}")
        exit(1)

def generate_wordlist(wordlist_dir, min_length, max_length, wordlist_size, charset):
    """Generate a wordlist based on parameters"""
    file_path = os.path.join(wordlist_dir, "wordlist.txt")
    print(f"[INFO] Generating wordlist with {wordlist_size} passwords...")

    with open(file_path, "w") as f:
        for _ in range(wordlist_size):
            length = random.randint(min_length, max_length)
            password = ''.join(random.choices(charset, k=length))
            f.write(password + "\n")

    print(f"[SUCCESS] Wordlist saved to: {file_path}")
    return file_path

def main():
    """Main function to handle wordlist generation."""
    wordlist_dir = setup_output()
    min_length, max_length, wordlist_size, charset = parameter_input()
    generate_wordlist(wordlist_dir, min_length, max_length, wordlist_size, charset)

if __name__ == "__main__":
    main()