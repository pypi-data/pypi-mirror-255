def from_py_file(file: str, name: str) -> dict | None:
    import importlib.machinery
    try:
        loader = importlib.machinery.SourceFileLoader(name, file)
        loaded_module = loader.load_module()
        loaded_attr = getattr(loaded_module, name)
        if isinstance(loaded_attr, dict):
            result = loaded_attr
        else:
            result = None
    except (FileNotFoundError, ImportError, AttributeError, Exception):
        result = None
    return result
