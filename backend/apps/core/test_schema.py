"""Stage 06 integration tests for multi-tenant account and job metadata.

Uses the CI-only SQLite database; production must use independent PostgreSQL.
"""
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import ProviderAccount
from apps.artifacts.models import Artifact
from apps.chats.models import Chat, Message
from apps.jobs.models import Attempt, Job, ResourceLease, Worker
from apps.providers.models import Capability, Connector, Provider
from apps.tokens.models import ApiToken
from apps.users.models import Tenant, TenantMembership


class SchemaIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.alice = user_model.objects.create_user(username="alice", password=uuid.uuid4().hex)
        cls.bob = user_model.objects.create_user(username="bob", password=uuid.uuid4().hex)
        cls.alice_tenant = Tenant.objects.create(slug="alice-workspace", name="Alice", owner=cls.alice)
        cls.bob_tenant = Tenant.objects.create(slug="bob-workspace", name="Bob", owner=cls.bob)
        TenantMembership.objects.create(
            tenant=cls.alice_tenant, user=cls.alice, role=TenantMembership.Role.OWNER
        )
        TenantMembership.objects.create(
            tenant=cls.bob_tenant, user=cls.bob, role=TenantMembership.Role.OWNER
        )
        cls.provider = Provider.objects.create(slug="example-provider", name="Example")
        cls.other_provider = Provider.objects.create(slug="other-provider", name="Other")
        cls.connector = Connector.objects.create(
            provider=cls.provider, slug="approved-cli", transport=Connector.Transport.CLI
        )
        cls.alice_account = ProviderAccount.objects.create(
            owner=cls.alice, tenant=cls.alice_tenant, provider=cls.provider,
            connector=cls.connector, label="my-account", status=ProviderAccount.Status.CONNECTED
        )
        cls.bob_account = ProviderAccount.objects.create(
            owner=cls.bob, tenant=cls.bob_tenant, provider=cls.provider,
            label="my-account", status=ProviderAccount.Status.CONNECTED
        )

    def test_custom_user_and_tenant_are_separate(self):
        self.assertNotEqual(self.alice.pk, self.bob.pk)
        self.assertNotEqual(self.alice_tenant.pk, self.bob_tenant.pk)
        self.assertEqual(TenantMembership.objects.filter(user=self.alice).count(), 1)

    def test_account_query_only_returns_owner_records(self):
        self.assertEqual(
            list(ProviderAccount.objects.for_owner(self.alice)),
            [self.alice_account],
        )
        self.assertEqual(
            list(ProviderAccount.objects.for_owner(self.bob)),
            [self.bob_account],
        )

    def test_cross_tenant_account_and_connector_rejected(self):
        invalid = ProviderAccount(
            tenant=self.bob_tenant, owner=self.alice, provider=self.provider, label="wrong"
        )
        with self.assertRaises(ValidationError):
            invalid.full_clean()
        mismatched = ProviderAccount(
            tenant=self.alice_tenant, owner=self.alice,
            provider=self.other_provider, connector=self.connector, label="bad-connector"
        )
        with self.assertRaises(ValidationError):
            mismatched.full_clean()

    def test_capabilities_are_unique_per_connector(self):
        Capability.objects.create(
            connector=self.connector,
            direction=Capability.Direction.INPUT,
            modality=Capability.Modality.TEXT,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Capability.objects.create(
                connector=self.connector,
                direction=Capability.Direction.INPUT,
                modality=Capability.Modality.TEXT,
            )

    def test_token_is_hashed_scoped_and_revocable(self):
        token, raw = ApiToken.objects.issue(
            tenant=self.alice_tenant, owner=self.alice, label="personal-token"
        )
        self.assertTrue(raw.startswith("aim_"))
        self.assertNotEqual(raw, token.token_digest)
        self.assertNotIn(raw, str(token))
        self.assertIsNotNone(ApiToken.objects.authenticate(raw))
        self.assertIsNone(ApiToken.objects.authenticate("wrong"))
        token.allowed_accounts.add(self.alice_account)
        self.assertTrue(token.allows_account(self.alice_account))
        self.assertFalse(token.allows_account(self.bob_account))
        token.revoked_at = timezone.now()
        token.save(update_fields=["revoked_at"])
        self.assertIsNone(ApiToken.objects.authenticate(raw))
        self.assertFalse(token.allows_account(self.alice_account))

    def test_provider_wide_token_not_cross_owner(self):
        token, _ = ApiToken.objects.issue(
            tenant=self.alice_tenant, owner=self.alice, label="provider-wide"
        )
        token.access_mode = ApiToken.AccessMode.PROVIDER
        token.save(update_fields=["access_mode"])
        token.allowed_providers.add(self.provider)
        self.assertTrue(token.allows_account(self.alice_account))
        self.assertFalse(token.allows_account(self.bob_account))
        self.assertFalse(
            ApiToken.objects.for_owner(self.bob).filter(pk=token.pk).exists()
        )

    def test_expired_token_not_valid(self):
        token, raw = ApiToken.objects.issue(
            tenant=self.alice_tenant, owner=self.alice, label="expired",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertFalse(token.is_valid())
        self.assertIsNone(ApiToken.objects.authenticate(raw))

    def test_chats_and_messages_are_isolated(self):
        chat = Chat.objects.create(
            tenant=self.alice_tenant, owner=self.alice, provider=self.provider,
            account=self.alice_account
        )
        Message.objects.create(chat=chat, sequence=1, role=Message.Role.USER, content="سلام")
        self.assertEqual(Chat.objects.for_owner(self.alice).count(), 1)
        self.assertEqual(Chat.objects.for_owner(self.bob).count(), 0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Message.objects.create(chat=chat, sequence=1, role=Message.Role.USER)
        invalid = Chat(
            tenant=self.alice_tenant, owner=self.alice, account=self.bob_account
        )
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_idempotency_is_unique_per_owner(self):
        job = Job.objects.create(
            tenant=self.alice_tenant, owner=self.alice, provider=self.provider,
            account=self.alice_account, idempotency_key="request-001"
        )
        self.assertEqual(Job.objects.for_owner(self.alice).get().pk, job.pk)
        self.assertFalse(Job.objects.for_owner(self.bob).exists())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Job.objects.create(
                tenant=self.alice_tenant, owner=self.alice, provider=self.provider,
                account=self.alice_account, idempotency_key="request-001"
            )
        Job.objects.create(
            tenant=self.bob_tenant, owner=self.bob, provider=self.provider,
            account=self.bob_account, idempotency_key="request-001"
        )

    def test_cross_owner_job_artifact_rejected(self):
        job = Job.objects.create(
            tenant=self.alice_tenant, owner=self.alice, provider=self.provider,
            account=self.alice_account
        )
        invalid_job = Job(
            tenant=self.bob_tenant, owner=self.bob, provider=self.provider,
            account=self.alice_account
        )
        with self.assertRaises(ValidationError):
            invalid_job.full_clean()

        artifact = Artifact.objects.create(
            tenant=self.alice_tenant, owner=self.alice, job=job,
            direction=Artifact.Direction.OUTPUT,
            storage_key="private/alice/file-1",
            original_filename="report.pdf", mime_type="application/pdf",
            byte_size=120, sha256="a" * 64
        )
        self.assertEqual(Artifact.objects.for_owner(self.alice).get(), artifact)
        self.assertFalse(Artifact.objects.for_owner(self.bob).exists())
        wrong_artifact = Artifact(
            tenant=self.bob_tenant, owner=self.bob, job=job,
            direction=Artifact.Direction.OUTPUT,
            storage_key="private/bob/file-1",
            original_filename="other.pdf", mime_type="application/pdf",
            byte_size=120, sha256="a" * 64
        )
        with self.assertRaises(ValidationError):
            wrong_artifact.full_clean()

    def test_attempt_and_account_lease_uniqueness(self):
        job = Job.objects.create(
            tenant=self.alice_tenant, owner=self.alice, provider=self.provider,
            account=self.alice_account
        )
        worker = Worker.objects.create(node_id="test-worker", kind=Worker.Kind.CLI)
        Attempt.objects.create(job=job, worker=worker, number=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Attempt.objects.create(job=job, worker=worker, number=1)

        ResourceLease.objects.create(
            job=job, worker=worker, account=self.alice_account,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ResourceLease.objects.create(
                job=job, worker=worker, account=self.alice_account,
                expires_at=timezone.now() + timedelta(minutes=5)
            )


    def test_ordinary_save_rejects_cross_tenant_rows(self):
        with self.assertRaises(ValidationError):
            ProviderAccount.objects.create(
                tenant=self.bob_tenant, owner=self.alice, provider=self.provider,
                label="foreign-account",
            )
        with self.assertRaises(ValidationError):
            Chat.objects.create(
                tenant=self.alice_tenant, owner=self.alice, account=self.bob_account
            )
        with self.assertRaises(ValidationError):
            Job.objects.create(
                tenant=self.alice_tenant, owner=self.alice,
                provider=self.provider, account=self.bob_account
            )

    def test_seeded_provider_catalogue_is_disabled_by_default(self):
        records = Provider.objects.filter(slug__in=["chatgpt", "gemini", "deepseek", "qwen", "zai"])
        self.assertEqual(records.count(), 5)
        self.assertFalse(records.filter(is_enabled=True).exists())
