"""Utils for io."""


def clean_file_extension(extension: str) -> str:
    """Clean an extension file.

    Removes all characters before the '.' and makes the extension lowercase.
    Example: '*.PY' -> '.py'

    It adds the '.' in case it's not present
    """
    dot_index = extension.find(".")

    clean_extension = "." + extension if dot_index == -1 else extension[dot_index:]

    return clean_extension.lower()
