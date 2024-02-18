class KeyAlreadyExistsError(Exception):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Key '{key}' already exists in the collection.")