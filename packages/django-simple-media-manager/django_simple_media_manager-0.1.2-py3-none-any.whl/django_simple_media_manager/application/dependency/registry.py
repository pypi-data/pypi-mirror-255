from django_simple_media_manager.domain.repository.image import CompoundImageRepository
from django_simple_media_manager.infrastructure.adapters.image import DjangoImageReadRepository, DjangoImageWriteRepository

django_compound_image_repository = CompoundImageRepository(read_repository=DjangoImageReadRepository(),
                                                           write_repository=DjangoImageWriteRepository())
