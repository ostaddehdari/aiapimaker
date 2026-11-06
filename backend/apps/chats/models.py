"""Private conversations and messages with stable sequence numbers."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.users.models import TenantMembership


class ChatQuerySet(models.QuerySet):
    def for_owner(self, user):
        return self.filter(owner=user, tenant__memberships__user=user, tenant__memberships__is_active=True)


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("users.Tenant", on_delete=models.CASCADE, related_name="chats")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="chats")
    provider = models.ForeignKey(
        "providers.Provider", on_delete=models.SET_NULL, null=True, blank=True
    )
    account = models.ForeignKey(
        "accounts.ProviderAccount", on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=255, default="گفتگوی جدید")
    is_archived = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ChatQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["owner", "-updated_at"], name="iam_chat_owner_updated"),
            models.Index(fields=["tenant", "is_archived"], name="iam_chat_tenant_archived"),
        ]

    def clean(self):
        super().clean()
        if self.owner_id and self.tenant_id and not TenantMembership.objects.filter(
            tenant_id=self.tenant_id, user_id=self.owner_id, is_active=True
        ).exists():
            raise ValidationError({"owner": "Chat owner must be an active tenant member."})
        if self.account_id:
            if self.account.owner_id != self.owner_id or self.account.tenant_id != self.tenant_id:
                raise ValidationError({"account": "Chat account must belong to its owner/tenant."})
            if self.provider_id and self.account.provider_id != self.provider_id:
                raise ValidationError({"provider": "Provider must match the selected account."})

    def save(self, *args, **kwargs):
        self.clean()  # Owner/account consistency before creating chat rows.
        return super().save(*args, **kwargs)


class Message(models.Model):
    class Role(models.TextChoices):
        SYSTEM = "system", "System"
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        TOOL = "tool", "Tool"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sequence = models.PositiveIntegerField()
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField(blank=True)
    structured_content = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(fields=["chat", "sequence"], name="iam_message_sequence_unique"),
            models.CheckConstraint(condition=Q(sequence__gte=1), name="iam_message_seq_positive"),
        ]
