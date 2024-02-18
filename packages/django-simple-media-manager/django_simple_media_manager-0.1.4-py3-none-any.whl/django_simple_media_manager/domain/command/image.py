from django_simple_media_manager.domain.command import Command
from django_simple_media_manager.domain.repository.image import ImageRepository


class BaseImageCommand(Command):
    def __init__(self, repository: ImageRepository):
        self.repository = repository


class GetImageByIDCommand(BaseImageCommand):
    def handle(self, image_id: int):
        return self.repository.get(pk=image_id)


class RetrieveImagesCommand(BaseImageCommand):
    def handle(self):
        return self.repository.all()


class BulkUploadImageCommand(BaseImageCommand):

    def handle(self, files: list[dict]):
        return self.repository.bulk_save(files=files)


class SaveImageCommand(BaseImageCommand):

    def handle(self, file: bytes, name: str):
        return self.repository.save(file=file, name=name)


class DeleteImageCommand(BaseImageCommand):
    def handle(self, id: int):
        self.repository.delete(id=id)
