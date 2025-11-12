from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# custom user manager 
class UserManager(BaseUserManager):
    def create_user(self, email, role, first_name, last_name="", password=None, password2=None):
        """
        Creates and saves a User with the given email,first_name,last_name, role and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            role = role,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name="", password=None):
        """
        Creates and saves a superuser with the given email, first_name,last_name, role and password.
        """
        user = self.create_user(
            email,
            password=password,
            role="admin",
            first_name=first_name,
            last_name=last_name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model 
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser