from collections.abc import Iterator

from django_simple_media_manager.domain.repository.image import ImageReadRepository, ImageWriteRepository
from django_simple_media_manager.infrastructure.models import Image


class DjangoImageWriteRepository(ImageWriteRepository):

    def save(self, file: bytes, name: str = '') -> Image:
        return Image.objects.create(file=file, name=name)

    def bulk_save(self, files: list) -> Iterator[Image]:
        bulk_list = [Image(image=file.get('image', None), name=file.get('name', None)) for file in files]
        return Image.objects.bulk_create(bulk_list)

    def delete(self, id: int):
        Image.objects.get(id=id).delete()


class DjangoImageReadRepository(ImageReadRepository):
    def all(self) -> Iterator[Image]:
        return Image.objects.all()

    def get(self, pk: int) -> Image:
        return Image.objects.get(pk=pk)

    def find(self, name: str) -> Iterator[Image]:
        return Image.objects.filter(name__icontains=name)
