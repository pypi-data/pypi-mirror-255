import re as _re


def rename_imports(module_content: str, mapping: dict[str, str]) -> str:
    """
    Rename imports in a module.

    Parameters
    ----------
    module_content : str
        The content of the Python module as a string.
    mapping : dict[str, str]
        A dictionary mapping the old import names to the new import names.

    Returns
    -------
    new_module_content : str
        The updated module content as a string with the old names replaced by the new names.
    """
    updated_module_content = module_content
    for old_name, new_name in mapping.items():
        # Regular expression patterns to match the old name in import statements
        patterns = [
            rf"^\s*from\s+{_re.escape(old_name)}(?:.[a-zA-Z0-9_]+)*\s+import",
            rf"^\s*import\s+{_re.escape(old_name)}(?:.[a-zA-Z0-9_]+)*",
        ]
        for pattern in patterns:
            # Compile the pattern into a regular expression object
            regex = _re.compile(pattern, flags=_re.MULTILINE)
            # Replace the old name with the new name wherever it matches
            updated_module_content = regex.sub(
                lambda match: match.group(0).replace(old_name, new_name, 1), updated_module_content
            )
    return updated_module_content
