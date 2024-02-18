from drf_spectacular.utils import OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import exceptions, serializers

ERROR_RESPONSES = {
    status_code: OpenApiResponse(
        description=description,
        response=inline_serializer(
            name='Error',
            fields={
                'detail': serializers.CharField(
                    help_text='A message describing the error'
                ),
            },
        ),
        examples=[
            OpenApiExample(
                name='Error',
                value={'detail': detail},
                status_codes=(status_code,),
            ),
        ],
    )
    for status_code, description, detail in (
        # 400
        (
            exceptions.ParseError.status_code,
            'Bad Request',
            exceptions.ParseError.default_detail,
        ),
        # 401
        (
            exceptions.NotAuthenticated.status_code,
            'Not Authenticated',
            exceptions.NotAuthenticated.default_detail,
        ),
        # 403
        (
            exceptions.PermissionDenied.status_code,
            'Forbidden',
            exceptions.PermissionDenied.default_detail,
        ),
        # 404
        (
            exceptions.NotFound.status_code,
            'Not Found',
            exceptions.NotFound.default_detail,
        ),
    )
}
