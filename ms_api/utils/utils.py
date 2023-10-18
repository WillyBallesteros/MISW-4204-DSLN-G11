import re

def password_validation(passwd):
    # Regular expression to validate all conditions
    pattern = (r"^(?=.*[a-z])"        # nimimal one loweer case letter
               r"(?=.*[A-Z])"         # nimimal one upper case letter
               r"(?=.*\d)"            # nimimal one number
               r"(?=.*[@$!%*?&#])"    # nimimal one special char
               r".{8,}$")             # nimimal 8 chars
    
    return bool(re.match(pattern, passwd))


def email_validation(email):
    pattern = (r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return bool(re.match(pattern, email))