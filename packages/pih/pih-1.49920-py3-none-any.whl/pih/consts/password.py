from pih.collections import PasswordSettings

class RULES:
        SPECIAL_CHARACTER: str = "s"
        LOWERCASE_ALPHABET: str = "a"
        UPPERCASE_ALPHABET: str = "A"
        DIGIT: str = "d"
        DEFAULT_ORDER_LIST: list[str] = [
            SPECIAL_CHARACTER,
            LOWERCASE_ALPHABET,
            UPPERCASE_ALPHABET,
            DIGIT,
        ]

class PASSWORD:
    
    class SETTINGS:
        SIMPLE: PasswordSettings = PasswordSettings(
            3, "", RULES.DEFAULT_ORDER_LIST, 0, 3, 0, 0, False
        )
        NORMAL: PasswordSettings = PasswordSettings(
            8, "!@#", RULES.DEFAULT_ORDER_LIST, 3, 3, 1, 1, False
        )
        STRONG: PasswordSettings = PasswordSettings(
            10,
            "#%+\-!=@()_",
            RULES.DEFAULT_ORDER_LIST,
            3,
            3,
            2,
            2,
            True,
        )
        DEFAULT: PasswordSettings = NORMAL
        PC: PasswordSettings = NORMAL
        EMAIL: PasswordSettings = NORMAL

    def get(name: str) -> SETTINGS:
        return PASSWORD.__getattribute__(PASSWORD.SETTINGS, name)

