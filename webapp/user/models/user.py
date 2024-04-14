from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **kwargs):
        # if not username:
        #     raise ValueError('username is required')
        # if not email:
        #     raise ValueError('email is required')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **kwargs,
        )
        user.set_password(password)
        user.save()

        return user

    def create_user(self, username, email, password, **kwargs):
        return self._create_user(username, email, password, **kwargs)

    def create_superuser(self, username, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        self._create_user(username, email, password, **kwargs)


class User(AbstractUser, PermissionsMixin):
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    username = models.CharField(
        verbose_name='유저 아이디',
        unique=True,
        max_length=40,
        null=False,
        blank=False,
    )

    googleId = models.CharField(
        verbose_name='구글 아이디',
        unique=True,
        max_length=225,
        null=True,
        blank=True,
    )

    kakaoId = models.CharField(
        verbose_name='카카오 아이디',
        unique=True,
        max_length=225,
        null=True,
        blank=True,
    )

    naverId = models.CharField(
        verbose_name='네이버 아이디',
        unique=True,
        max_length=225,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        max_length=100,
        unique=True
    )

    nickname = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name='생성 일시',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name='수정 일시',
        auto_now=True,
    )

    # is_admin = models.BooleanField(default=False)

    # is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        if self.kakaoId:
            return f"(카카오) {self.username}"
        elif self.naverId:
            return f"(네이버) {self.username}"
        elif self.googleId:
            return f"(구글) {self.username}"
        return f"(일반) {self.username}"

    # def has_perm(self, perm, obj=None):
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        return self.is_superuser
