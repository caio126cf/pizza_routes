# myapp/tokens.py
import jwt  # type: ignore
from datetime import timedelta
from allauth.headless.tokens.base import AbstractTokenStrategy
from django.conf import settings
from django.utils import timezone  # timezone-aware

class JWTTokenStrategy(AbstractTokenStrategy):
    """
    Estratégia de token JWT para Django Allauth Headless.
    """

    # Cria o token JWT
    def create_access_token(self, request):
        user = request.user
        now = timezone.now()  # datetime aware
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": now + timedelta(hours=1),  # expiração 1 hora
            "iat": now,                        # timestamp de criação
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    # Define o payload que será retornado no login/signup
    def create_access_token_payload(self, request):
        token = self.create_access_token(request)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }

    # Sessão baseada em cookie não será usada
    def create_session_token(self, request):
        return None

    def get_session_token(self, request):
        return None

    def lookup_session(self, session_token):
        return None

