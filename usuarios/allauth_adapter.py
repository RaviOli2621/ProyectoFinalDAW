from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        print("DEBUG: pre_social_login ejecutado")
        # Si el usuario ya está autenticado, no hacer nada
        if request.user.is_authenticated:
            return

        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass