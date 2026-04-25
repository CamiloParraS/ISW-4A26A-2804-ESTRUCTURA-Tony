class ValidationUtils:
    @staticmethod
    def is_digits_only(value: str) -> bool:
        return value == "" or value.isdigit()

    @staticmethod
    def safe_int(value: str) -> int:
        digits = "".join(character for character in value if character.isdigit())
        if not digits:
            return 0
        return int(digits)
