import random
import secrets
import string


def generate_random_string(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def obfuscate_string(s):
    """
    Obfuscates a string by replacing 50% of its characters with asterisks
    Args:
        s (str): The string to obfuscate

    Returns:
        str: The obfuscated string
    """
    # Convert the string to a list of characters to facilitate replacements
    chars = list(s)
    # Determine the indices to replace with asterisks, selecting 50% of the characters at random
    indices_to_obfuscate = random.sample(range(len(chars)), k=len(chars) // 2)
    # Replace the selected characters with asterisks
    for index in indices_to_obfuscate:
        chars[index] = '*'
    # Convert the list of characters back to a string
    return ''.join(chars)


def obfuscate_sensitive_info(data: dict):
    """
    Obfuscate sensitive information in a dictionary, such as API keys and passwords.
    Args:
        data (dict): The dictionary to obfuscate

    Returns:
        dict: The obfuscated dictionary
    """
    copy_data = data.copy()

    sensitive_keywords = ["api_key", "password", "_key", "database_url"]
    obfuscated_data = {}
    for k, v in copy_data.items():
        if not "__" in k and "sys" not in k:
            # Check if the key, in lowercase, contains any of the sensitive keywords
            if any(keyword in k.lower() for keyword in sensitive_keywords) and isinstance(v, str):
                # Obfuscate the value if the key is considered sensitive
                obfuscated_data[k] = obfuscate_string(str(v))
            else:
                # Keep the original value if the key is not sensitive
                obfuscated_data[k] = v
    return obfuscated_data
