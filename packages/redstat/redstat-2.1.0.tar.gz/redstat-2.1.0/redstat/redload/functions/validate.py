def validate(namespace):
    _validate_name(namespace.name)


def _validate_name(name: str) -> None:
    name_prefixes = ('r/', 'u/')
    if not name.startswith(name_prefixes):
        raise ValueError(f"Resource must start with: {', '.join(f'{prefix!r}' for prefix in name_prefixes)}")
