class InvalidCollectionIdException(ValueError):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid collection id")


class InvalidAssetIdException(ValueError):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid asset id")


class InvalidWalletException(ValueError):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid wallet")
