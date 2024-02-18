"""Custom Troj errors"""


class TrojJSONError(Exception):
    """Raise if error occurs when loading a dict from JSON stored on disk"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TrojConfigError(Exception):
    """Raise when the loaded config is not compliant with the requirements"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TrojDataLoaderError(Exception):
    """Raise when the there is an issue with creating a data loader"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TrojImageError(Exception):
    """Raise when an operation on an image fails"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TrojCorruptionError(Exception):
    """Raise when there is an issue within a corruption module"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TrojOptimizationError(Exception):
    """Raise when there is an issue within an optimizaiton algorithm"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
