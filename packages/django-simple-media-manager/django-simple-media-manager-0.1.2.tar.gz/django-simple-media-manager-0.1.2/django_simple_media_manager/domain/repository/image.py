from abc import abstractmethod, ABC
from collections.abc import Iterator

from ...infrastructure.models.image import Image
from . import AbstractRepository


class ImageReadRepository(AbstractRepository):

    @abstractmethod
    def get(self, pk: int) -> Image:
        ...

    @abstractmethod
    def find(self, name: str) -> Iterator[Image]:
        ...

    @abstractmethod
    def all(self) -> Iterator[Image]:
        ...


class ImageWriteRepository(AbstractRepository):
    @abstractmethod
    def save(self, file: bytes, name: str) -> Image:
        ...

    @abstractmethod
    def bulk_save(self, files: list) -> Iterator[Image]:
        ...

    @abstractmethod
    def delete(self, id: int):
        ...


class ImageRepository(ImageReadRepository, ImageWriteRepository, ABC):
    ...


class CompoundImageRepository(ImageRepository):
    def __init__(self, read_repository: ImageReadRepository, write_repository: ImageWriteRepository):
        self.read_repository = read_repository
        self.write_repository = write_repository

    def get(self, pk: int) -> Image:
        return self.read_repository.get(pk=pk)

    def find(self, name: str) -> Iterator[Image]:
        return self.read_repository.find(name=name)

    def all(self) -> Iterator[Image]:
        return self.read_repository.all()

    def save(self, file: bytes, name: str) -> Image:
        return self.write_repository.save(file=file, name=name)

    def bulk_save(self, files: list) -> Iterator[Image]:
        return self.write_repository.bulk_save(files=files)

    def delete(self, id: int):
        self.write_repository.delete(id=id)
