"""Durable queue metadata; Celery and browser execution are later stages."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.users.models import TenantMembership


class JobQuerySet(models.QuerySet):
    def for_owner(self, user):
        return self.filter(owner=user, tenant__memberships__user=user, tenant__memberships__is_active=True)


class Worker(models.Model):
    class Kind(models.TextChoices):
        CLI = "cli", "CLI"
        BROWSER = "browser", "Browser"
        ARTIFACT = "artifact", "Artifact"

    class Status(models.TextChoices):
        OFFLINE = "offline", "Offline"
        IDLE = "idle", "Idle"
        BUSY = "busy", "Busy"
        DRAINING = "draining", "Draining"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_id = models.CharField(max_length=120, unique=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OFFLINE)
    heartbeat_at = models.DateTimeField(null=True, blank=True)
    memory_mb = models.PositiveIntegerField(default=0)
    cpu_percent = models.FloatField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["kind", "status"], name="iam_worker_kind_status")]


class Job(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        CLAIMED = "claimed", "Claimed"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("users.Tenant", on_delete=models.CASCADE, related_name="jobs")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="jobs")
    provider = models.ForeignKey(
        "providers.Provider", on_delete=models.PROTECT, related_name="jobs"
    )
    account = models.ForeignKey(
        "accounts.ProviderAccount", on_delete=models.PROTECT, related_name="jobs"
    )
    chat = models.ForeignKey("chats.Chat", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.QUEUED)
    priority = models.SmallIntegerField(default=0)
    idempotency_key = models.CharField(max_length=160, null=True, blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "idempotency_key"],
                condition=Q(idempotency_key__isnull=False) & ~Q(idempotency_key=""),
                name="iam_job_owner_idempotent",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status", "created_at"], name="iam_job_tenant_status"),
            models.Index(fields=["owner", "-created_at"], name="iam_job_owner_created"),
            models.Index(fields=["account", "status"], name="iam_job_account_status"),
        ]

    def clean(self):
        super().clean()
        if self.owner_id and self.tenant_id and not TenantMembership.objects.filter(
            tenant_id=self.tenant_id, user_id=self.owner_id, is_active=True
        ).exists():
            raise ValidationError({"owner": "Job owner must be an active tenant member."})
        if self.account_id:
            if self.account.tenant_id != self.tenant_id or self.account.owner_id != self.owner_id:
                raise ValidationError({"account": "Job account must belong to its owner and tenant."})
            if self.account.provider_id != self.provider_id:
                raise ValidationError({"provider": "Job provider must match its account."})
        if self.chat_id and (
            self.chat.owner_id != self.owner_id or self.chat.tenant_id != self.tenant_id
        ):
            raise ValidationError({"chat": "Job chat must belong to its owner and tenant."})

    def save(self, *args, **kwargs):
        self.clean()  # Tenant/account/chat checks on ordinary job persistence.
        return super().save(*args, **kwargs)


class Attempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="attempts")
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    number = models.PositiveIntegerField()
    state = models.CharField(max_length=20, default="claimed")
    error_code = models.CharField(max_length=120, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "number"], name="iam_attempt_job_number"),
            models.CheckConstraint(condition=Q(number__gte=1), name="iam_attempt_number_positive"),
        ]


class ResourceLease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="leases")
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, related_name="leases")
    account = models.ForeignKey(
        "accounts.ProviderAccount", on_delete=models.PROTECT, related_name="leases"
    )
    acquired_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account"],
                condition=Q(released_at__isnull=True),
                name="iam_lease_one_active_account",
            )
        ]
        indexes = [models.Index(fields=["expires_at", "released_at"], name="iam_lease_expiry")]
