class LayoutError(Exception):
    """Layout related error."""

    def __init__(self, message="Invalid storage layout data scheme."):
        self.message = message
        super().__init__(self.message)


class StorageLayoutError(LayoutError):
    """Storage layout related error."""

    def __init__(self, message="Invalid storage data scheme."):
        self.message = message
        super().__init__(self.message)


# todo: unused
class TypesLayoutError(LayoutError):
    """Types layout related error."""

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)
