from drf_spectacular.utils import extend_schema
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api.api_view import ApiViewV3Mixin
from api.pagination import LimitOffsetPagination, get_paginated_response
from django_simple_media_manager.application.apis.serializers.image import ImageOutputSerializer, \
    ImageMultipleInputSerializer, BriefImageOutputSerializer
from django_simple_media_manager.application.dependency.registry import \
    django_compound_image_repository as DjangoCompoundImageRepository
from django_simple_media_manager.domain.command.image import BulkUploadImageCommand, GetImageByIDCommand, RetrieveImagesCommand, DeleteImageCommand


class UploadImageApi(ApiViewV3Mixin, APIView):

    def __init__(self, **kwargs):
        super(UploadImageApi, self).__init__(**kwargs)
        self.upload_image = BulkUploadImageCommand(repository=DjangoCompoundImageRepository)

    @extend_schema(
        request=ImageMultipleInputSerializer(many=True),
        responses=BriefImageOutputSerializer
    )
    def post(self, request):
        serializer = ImageMultipleInputSerializer(many=True, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.upload_image.handle(files=serializer.validated_data)
            result = BriefImageOutputSerializer(instance, many=True, context={'request': request}).data
            return Response(result)
        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class GetImagesApi(ApiViewV3Mixin, APIView):

    def __init__(self, **kwargs):
        super(GetImagesApi, self).__init__(**kwargs)
        self.retrieve_images = RetrieveImagesCommand(repository=DjangoCompoundImageRepository)

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        responses=BriefImageOutputSerializer
    )
    def get(self, request):
        try:
            query = self.retrieve_images.handle()
            return get_paginated_response(
                pagination_class=self.Pagination,
                serializer_class=BriefImageOutputSerializer,
                queryset=query,
                request=request,
                view=self,
            )

        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class GetImageByIdApi(ApiViewV3Mixin, APIView):

    def __init__(self, **kwargs):
        super(GetImageByIdApi, self).__init__(**kwargs)
        self.get_image_by_id = GetImageByIDCommand(repository=DjangoCompoundImageRepository)

    class IdParameterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True, allow_null=False)

    @extend_schema(
        parameters=[IdParameterSerializer],
        responses=ImageOutputSerializer
    )
    def get(self, request):
        """
        image_id -- This is the essential parameter for using this api
        """
        try:
            query = self.get_image_by_id.handle(image_id=request.GET.get('id'))
            result = ImageOutputSerializer(query, context={"request": request}).data
            return Response(result)

        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class DeleteImageByIdApi(ApiViewV3Mixin, APIView):

    def __init__(self, **kwargs):
        super(DeleteImageByIdApi, self).__init__(**kwargs)
        self.delete_image_by_id = DeleteImageCommand(repository=DjangoCompoundImageRepository)

    class IdParameterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True, allow_null=False)

    @extend_schema(
        parameters=[IdParameterSerializer]
    )
    def delete(self, request):

        param_serializer = self.IdParameterSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)
        try:
            self.delete_image_by_id.handle(id=param_serializer.validated_data.get('id'))
            return Response(f"Successfully deleted", status=status.HTTP_200_OK)

        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)
