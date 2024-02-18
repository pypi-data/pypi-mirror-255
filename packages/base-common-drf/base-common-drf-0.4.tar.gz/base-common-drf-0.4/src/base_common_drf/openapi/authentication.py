from drf_spectacular.authentication import SessionScheme as SpectacularSessionScheme


class SessionScheme(SpectacularSessionScheme):
    target_class = 'base_common_drf.authentication.SessionAuthentication'
