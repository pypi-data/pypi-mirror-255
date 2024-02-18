def from_ini_file(file: str) -> dict | None:
    import configparser
    loader = configparser.ConfigParser()
    try:
        result = loader.read(file)
    except (FileNotFoundError, configparser.Error):
        result = None
    return result
