from drf_spectacular.openapi import AutoSchema as SpectacularAutoSchema


class AutoSchema(SpectacularAutoSchema):
    def get_override_parameters(self):
        from django.conf import settings

        params = super().get_override_parameters()
        return params + settings.SPECTACULAR_SETTINGS.get('GLOBAL_PARAMS', [])
