"""
This module contains a set of mock classes that mimic the behavior of certain classes from the Databricks Utilities (dbutils) library.
These mock classes are intended for testing and development purposes, allowing developers to simulate the behavior of the actual dbutils classes without relying on a Databricks environment.

Classes:
- MockOptional: A mock class for the Optional class from the typing module.
- MockFileSystem: A mock class for the FileSystem class from the dbutils module.
- MockEntryPointContext: A mock class for the EntryPointContext class from the dbutils module.
- MockEntryPointNotebook: A mock class for the EntryPointNotebook class from the dbutils module.
- MockEntryPointDBUtils: A mock class for the EntryPointDBUtils class from the dbutils module.
- MockEntryPoint: A mock class for the EntryPoint class from the dbutils module.
- MockWidgets: A mock class for the Widgets class from the dbutils module.
- MockNotebook: A mock class for the Notebook class from the dbutils module.
- MockSecrets: A mock class for the Secrets class from the dbutils module.
- MockDBUtils: A mock class that combines the functionality of the above mock classes to simulate the behavior of the dbutils module.

Note: The methods and attributes of these mock classes may not fully match the actual dbutils classes, but they provide a basic implementation for testing purposes.
"""

__all__ = [
    "MockNotebook",
    "MockOptional",
    "MockSecrets",
    "MockWidgets",
    "MockDBUtils",
    "MockEntryPointNotebook",
    "MockEntryPoint",
    "MockEntryPointDBUtils",
    "MockEntryPointContext",
    "MockFileSystem",
]

from typing import Dict, Any


class MockOptional:
    """
    A mock implementation of the Optional class.

    Args:
        value (str): The value to be stored in the Optional object.

    Attributes:
        value (str): The stored value.

    Methods:
        getOrElse(default_value: str): Returns the stored value if it exists, otherwise returns the default value.

    """

    def __init__(self, value: str):
        self.value = value

    # noinspection PyPep8Naming
    def getOrElse(self, default_value: str):
        return self.value or default_value


class MockFileSystem:
    def __init__(self):
        pass


class MockEntryPointContext:

    @staticmethod
    def tags():
        return {
            "orgId": "mock-00",
            "clusterId": "mock-0",
        }

    # noinspection PyPep8Naming
    @staticmethod
    def notebookPath() -> MockOptional:
        # dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().getOrElse(None)
        path = "/Repos/Examples/example-course-source/Source/Version Info"
        return MockOptional(path)


class MockEntryPointNotebook:
    # noinspection PyPep8Naming
    @staticmethod
    def getContext():
        return MockEntryPointContext()


class MockEntryPointDBUtils:
    @staticmethod
    def notebook():
        return MockEntryPointNotebook()


class MockEntryPoint:
    # noinspection PyPep8Naming
    @staticmethod
    def getDbutils() -> "MockEntryPointDBUtils":
        # tags = dbutils.entry_point.getDbutils().notebook().getContext().tags()
        return MockEntryPointDBUtils()


class MockWidgets:
    def __init__(self):
        pass


class MockNotebook:
    @staticmethod
    def run(path: str, timeout_seconds: int, arguments: Dict[str, Any]):
        pass


class MockSecrets:

    SECRETS = dict()

    def __init__(self):
        pass

    @classmethod
    def get(cls, scope: str, key: str) -> str:
        return cls.SECRETS.get(f"{scope}-{key}")


class MockDBUtils:
    def __init__(self):
        self.fs = MockFileSystem()
        self.widgets = MockWidgets()
        self.secrets = MockSecrets()
        self.entry_point = MockEntryPoint()

        # Supports dbutils.notebook
        self.notebook = MockNotebook()

    # noinspection PyPep8Naming
    def displayHTML(self, **kwargs):
        pass

    def display(self, **kwargs):
        pass
