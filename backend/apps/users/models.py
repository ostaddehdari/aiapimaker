"""Users, organizations and explicit tenant memberships.

Stage 06 creates the schema; actual login and object-level authorization are
delivered in later stages. Never infer access from a foreign key alone.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    class PlatformRole(models.TextChoices):
        ADMIN = "admin", "Platform administrator"
        USER = "user", "User"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform_role = models.CharField(
        max_length=10, choices=PlatformRole.choices, default=PlatformRole.USER
    )

    class Meta:
        indexes = [models.Index(fields=["platform_role", "is_active"], name="iam_user_role_active")]


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=80)
    name = models.CharField(max_length=160)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_tenants")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TenantMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Administrator"
        MEMBER = "member", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "user"], name="iam_tenant_member_unique"),
            models.CheckConstraint(
                condition=Q(role__in=["owner", "admin", "member"]),
                name="iam_tenant_member_role_valid",
            ),
        ]
        indexes = [models.Index(fields=["user", "is_active"], name="iam_member_user_active")]

# Import the Stage 07 auth tables so Django registers them during app loading.
from .security_models import AuthDeviceSession, AuthEvent, LoginThrottle  # noqa: E402, F401
