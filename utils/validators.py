import string


def is_valid_password(password):
    """
    Prüft die Passwortregeln.

    Mindestens:
    - 8 Zeichen
    - ein Großbuchstabe
    - ein Kleinbuchstabe
    - eine Zahl
    - ein Sonderzeichen
    """

    if not password or len(password) < 8:
        return False

    return (
        any(character.isupper() for character in password)
        and any(character.islower() for character in password)
        and any(character.isdigit() for character in password)
        and any(
            character in string.punctuation
            for character in password
        )
    )
