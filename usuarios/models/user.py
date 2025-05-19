from django.contrib.auth import get_user_model

User = get_user_model()

class UserManager:
    @classmethod
    def get_all(cls):
        return User.objects.all()

    @classmethod
    def exclude_ids(cls, ids):
        return User.objects.exclude(id__in=ids).order_by('id')

    @classmethod
    def get_by_id(cls, user_id):
        return User.objects.filter(id=user_id).first()

    @classmethod
    def get_by_username(cls, username):
        return User.objects.filter(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        return User.objects.filter(email=email).first()

    @classmethod
    def exists_with_username(cls, username, exclude_pk=None):
        qs = User.objects.filter(username=username)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @classmethod
    def exists_with_email(cls, email):
        return User.objects.filter(email=email).exists()

    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        user = User.objects.create_user(username=username, email=email, password=password, **extra_fields)
        return user

    @classmethod
    def set_temporary_password(cls, user, temp_password):
        user.set_password(temp_password)
        user.save()
        return user