import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from api.exceptions import AuthorizationError, ValidationError


class Tenant(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        if not owner:
            raise ValidationError("Tenant must be created with an owner.")
        is_new = self._state.adding

        super().save(*args, **kwargs)
        if owner and is_new:
            owner.tenant = self
            owner.role = "owner"
            owner.save()

    def __str__(self):
        return self.name


class TenantPolicyDependent(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Project(TenantPolicyDependent):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("owner", "Owner"),
    )
    role = models.CharField(
        max_length=50, blank=True, null=True, choices=ROLE_CHOICES, default="user"
    )
    tenant = models.ForeignKey(
        "Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
    )

    def change_role(self, new_role: str, changed_by=None):
        if changed_by is None:
            changed_by = self

        if self.tenant is None:
            raise ValidationError(
                "You are not part of any tenant. You cannot update other user role."
            )
        elif changed_by.pk == self.pk:
            raise ValidationError("Users cannot change their own role.")
        elif changed_by.tenant != self.tenant:
            raise AuthorizationError(
                "You are not allowed to update users from another tenant."
            )
        elif changed_by.role != "owner":
            raise AuthorizationError("You are not authorized to update users.")
        self.role = new_role
        super().save()

    def clean(self):
        super().clean()
        if (
            self.created_by
            and self.created_by.role != "owner"
            and self.role
            in [
                "admin",
                "owner",
            ]
        ):
            raise AuthorizationError(
                "Only users with 'owner' role can create users with 'admin' or 'owner' roles."
            )
        elif self.created_by and self.created_by.role == "user":
            raise AuthorizationError("You are not authorized to create other users.")
        elif self.created_by:
            user_exists = User.objects.get(pk=self.created_by.pk)
            if not user_exists:
                raise ValidationError("User creator doesn't exists.")

        if self.pk:
            existing_user = User.objects.get(pk=self.pk)
            if existing_user.tenant and existing_user.tenant != self.tenant:
                raise ValidationError(
                    f"{existing_user.username} already belongs to a tenant."
                )

            if self.created_by and self.created_by.pk == self.pk:
                raise ValidationError("Users cannot change their own role")

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.created_by and not self.tenant:
            self.role = "user"

        if self.created_by:
            self.tenant = self.created_by.tenant
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
