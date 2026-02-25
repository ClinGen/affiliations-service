"""Models of the data in the affiliations service."""

# Third-party dependencies:
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_api_key.models import AbstractAPIKey


class CustomAPIKey(AbstractAPIKey):
    """Define custom API key model."""

    can_write: models.BooleanField = models.BooleanField(
        default=False, verbose_name="Allow to Create/Update Affiliations"
    )

    class Meta(AbstractAPIKey.Meta):
        """Meta class for custom API Key model."""

        verbose_name = "API Key"
        verbose_name_plural = "API Keys"


class AffiliationStatus(models.TextChoices):  # pylint: disable=too-many-ancestors
    """Creating choices for status."""

    APPLYING = "APPLYING", _("Applying")
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")
    RETIRED = "RETIRED", _("Retired")
    ARCHIVED = "ARCHIVED", _("Archived")


class AffiliationType(models.TextChoices):  # pylint: disable=too-many-ancestors
    """Creating choices for type."""

    VCEP = "VCEP", _("Variant Curation Expert Panel")
    GCEP = "GCEP", _("Gene Curation Expert Panel")
    INDEPENDENT_CURATION = "INDEPENDENT_CURATION", _("Independent Curation Group")
    SC_VCEP = "SC_VCEP", _("Somatic Cancer Variant Curation Expert Panel")


class ClinicalDomainWorkingGroup(models.Model):
    """Define the shape of an clinical domain working group(CDWG)."""

    name = models.CharField(
        max_length=255,
        help_text="""The full name of the clinical domain
        working group.""",
    )  # type: object
    uuid: models.UUIDField = models.UUIDField(
        unique=True, null=True, blank=True, verbose_name="GPM UUID"
    )

    class Meta:
        """Describe the fields on a CDWG."""

        verbose_name = "Clinical Domain Working Group"
        verbose_name_plural = "Clinical Domain Working Groups"

    def __str__(self):
        return str(self.name)


class Affiliation(models.Model):
    """Define the shape of an affiliation."""

    type: models.CharField = models.CharField(
        verbose_name="Type",
        choices=AffiliationType.choices,
    )
    """
    10000 ID. All affiliations will have this ID, however, some affiliations
    will share this ID. Affiliations that share this ID will have different
    expert_panel_ids.
    """
    affiliation_id: models.IntegerField = models.IntegerField(
        blank=True,
        verbose_name="Affiliation ID",
    )
    """
    40000 or 50000 ID. This ID can be null as independent groups will not have
    either of these IDs.
    """
    expert_panel_id: models.IntegerField = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Expert Panel ID",
    )
    full_name: models.CharField = models.CharField(verbose_name="Full Name")
    short_name: models.CharField = models.CharField(
        blank=True, null=True, verbose_name="Short Name"
    )
    status: models.CharField = models.CharField(
        verbose_name="Status",
        choices=AffiliationStatus.choices,
    )
    clinical_domain_working_group: models.ForeignKey = models.ForeignKey(
        ClinicalDomainWorkingGroup,
        on_delete=models.CASCADE,
        verbose_name="Clinical Domain Working Group",
        related_name="affiliations",
    )
    members: models.CharField = models.CharField(blank=True, null=True)
    is_deleted: models.BooleanField = models.BooleanField(default=False)
    """ID used and provided by UNC for the GPM."""
    uuid: models.UUIDField = models.UUIDField(
        unique=True, null=True, blank=True, verbose_name="GPM UUID"
    )

    def __str__(self):
        """Provide a string representation of an affiliation."""
        return f"Affiliation {self.affiliation_id} {self.full_name}"

    def delete(self, *args, **kwargs):
        """Override delete method to "soft-delete" affiliations."""
        self.is_deleted = True
        self.save(*args, **kwargs)


class Coordinator(models.Model):
    """Define the shape of an coordinator."""

    affiliation = models.ForeignKey(
        Affiliation, related_name="coordinators", on_delete=models.CASCADE
    )  # type: object
    coordinator_name: models.CharField = models.CharField(
        verbose_name="Coordinator Name"
    )
    coordinator_email: models.EmailField = models.EmailField(
        verbose_name="Coordinator Email"
    )


class Approver(models.Model):
    """Define the shape of an approver."""

    affiliation = models.ForeignKey(
        Affiliation, related_name="approvers", on_delete=models.CASCADE
    )  # type: object
    approver_name: models.CharField = models.CharField(verbose_name="Approver Name")


class Submitter(models.Model):
    """Define the shape of an submitter."""

    affiliation = models.ForeignKey(
        Affiliation, related_name="clinvar_submitter_ids", on_delete=models.CASCADE
    )  # type: object
    clinvar_submitter_id: models.CharField = models.CharField(
        verbose_name="ClinVar Submitter ID"
    )
