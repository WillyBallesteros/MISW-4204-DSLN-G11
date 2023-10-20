import re

def password_validation(passwd):
    # Regular expression to validate all conditions
    pattern = (r"^(?=.*[a-z])"        # Mimimal one loweer case letter
               r"(?=.*[A-Z])"         # Mimimal one upper case letter
               r"(?=.*\d)"            # Mimimal one number
               r"(?=.*[@$!%*?&#])"    # Mimimal one special char
               r".{8,}$")             # Mimimal 8 chars
    
    return bool(re.match(pattern, passwd))


def email_validation(email):
    pattern = (r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return bool(re.match(pattern, email))

def get_extension(filename):
    parts = filename.split('.')
    if len(parts) > 1:
        return parts[-1].lower()
    return None