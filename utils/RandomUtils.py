import random
import string


class RandomUtils:

    @staticmethod
    def string(length):
        return ''.join(random.choices(string.ascii_lowercase +
                                      string.digits, k=length))

    @staticmethod
    def integer(n):
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        return random.randint(range_start, range_end)

    @staticmethod
    def password():
        length = 8
        while True:
            password = ''.join(
                random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))
            if (any(c.islower() for c in password) and
                    any(c.isupper() for c in password) and
                    any(c.isdigit() for c in password) and
                    any(c in string.punctuation for c in password)):
                return password

    @staticmethod
    def books_page_password():
        lowercase_chars = string.ascii_lowercase
        uppercase_chars = string.ascii_uppercase
        digit_chars = string.digits
        special_chars = "!@"

        password = (
                random.choice(lowercase_chars)
                + random.choice(uppercase_chars)
                + random.choice(digit_chars)
                + random.choice(special_chars)
                + random.choice(special_chars)
        )

        remaining_length = max(0, 8 - len(password))
        all_chars = lowercase_chars + uppercase_chars + digit_chars + special_chars
        password += ''.join(random.choice(all_chars) for _ in range(remaining_length))

        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)

        return password
