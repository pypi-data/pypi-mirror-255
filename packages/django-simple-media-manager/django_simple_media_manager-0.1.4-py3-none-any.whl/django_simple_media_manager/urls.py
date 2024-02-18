from django.urls import path

from django_simple_media_manager.application.apis.image import UploadImageApi, GetImagesApi, GetImageByIdApi, DeleteImageByIdApi

urlpatterns = [
    # Image
    path('upload-image', UploadImageApi.as_view(), name='upload_image'),
    path('get-images', GetImagesApi.as_view(), name='get_images'),
    path('get-image', GetImageByIdApi.as_view(), name='get_image_by_id'),
    path('delete-image', DeleteImageByIdApi.as_view(), name='delete_image_by_id')
]
