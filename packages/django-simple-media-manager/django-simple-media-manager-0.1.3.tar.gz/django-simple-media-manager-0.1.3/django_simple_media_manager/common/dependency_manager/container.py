from abc import abstractmethod
from typing import Any

from ...utils.singletone import Singleton


class BaseDependencyContainer:
    def __init__(self):
        self.dependencies = {}

    @abstractmethod
    def register_dependency(self, dependency_name: str, dependency: Any):
        """
        Abstraction of register a new dependency into container
        Args:
            dependency_name (str): A unique name for the dependency.
            dependency (object): The dependency object to be registered.
        """

    @abstractmethod
    def resolve_dependency(self, dependency_name: str):
        """
        Abstraction of accessing an existed dependency from container
        Args:
            dependency_name (str): The name of the dependency to resolve.
        Returns:
            object: The resolved dependency object.
        """


class ApplicationDependencyContainer(Singleton, BaseDependencyContainer):

    def register_dependency(self, dependency_name: str, dependency: Any):
        self.dependencies[dependency_name.lower()] = dependency

    def resolve_dependency(self, dependency_name: str):
        if dependency_name in self.dependencies:
            return self.dependencies[dependency_name.lower()]
        else:
            raise Exception(f"Dependency '{dependency_name}' not found in the container.")
