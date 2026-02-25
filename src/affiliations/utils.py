"""Utility functions"""

from uuid import UUID
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from affiliations.models import Affiliation, ClinicalDomainWorkingGroup


VCEP_BASE = 50000
GCEP_BASE = 40000
AFFIL_BASE = 10000


def generate_next_affiliation_id(cleaned_data: dict) -> None:
    """Generate the next sequential affiliation_id as an integer."""
    with transaction.atomic():

        if (
            cleaned_data.get("affiliation_id") is not None
            or cleaned_data.get("expert_panel_id") is not None
        ):
            raise ValidationError(
                "ID's cannot be manually assigned. Please remove from request."
            )
        existing_ids = (
            Affiliation.objects.select_for_update()
            .values_list("affiliation_id", flat=True)
            .order_by("affiliation_id")
        )

        if existing_ids:
            last_id = max(existing_ids)
            next_id = last_id + 1
        else:
            next_id = AFFIL_BASE

        if next_id < AFFIL_BASE or next_id >= 20000:
            raise ValidationError("Affiliation ID out of range. Contact administrator.")

        cleaned_data["affiliation_id"] = next_id


def set_expert_panel_id(cleaned_data: dict) -> None:
    """Assign expert_panel_id based on type and affiliation_id."""
    affil_id = cleaned_data.get("affiliation_id")
    type_ = cleaned_data.get("type")

    if affil_id is None:
        raise ValidationError("affiliation_id is required to create expert_panel_id.")

    ep_id = None

    if type_ == "VCEP":
        ep_id = (affil_id - AFFIL_BASE) + VCEP_BASE
        if not VCEP_BASE <= ep_id < 60000:
            raise ValidationError("VCEP ID out of range. Contact administrator.")

    elif type_ == "SC_VCEP":
        ep_id = (affil_id - AFFIL_BASE) + VCEP_BASE
        if not VCEP_BASE <= ep_id < 60000:
            raise ValidationError("SC-VCEP ID out of range. Contact administrator.")

    elif type_ == "GCEP":
        ep_id = (affil_id - AFFIL_BASE) + GCEP_BASE
        if not GCEP_BASE <= ep_id < VCEP_BASE:
            raise ValidationError("GCEP ID out of range. Contact administrator.")

    cleaned_data["expert_panel_id"] = ep_id


def validate_unique_cdwg_name(name: str, instance_id=None) -> None:
    """
    Raise ValidationError if another CDWG with the same name exists.
    Case-insensitive check. Allows the current instance to retain its name.
    """
    qs = ClinicalDomainWorkingGroup.objects.all()
    if instance_id:
        qs = qs.exclude(id=instance_id)
    if qs.filter(name__iexact=name).exists():
        raise ValidationError(
            "A Clinical Domain Working Group with this name already exists."
        )


def validate_cdwg_matches_type(cleaned_data: dict, instance=None) -> None:
    """Ensure the provided CDWG is valid for the given immutable type."""
    type_ = cleaned_data.get("type")
    cdwg = cleaned_data.get("clinical_domain_working_group")

    if not type_ and instance:
        type_ = getattr(instance, "type", None)
    if not cdwg:
        return

    if type_ == "SC_VCEP":
        expected = ClinicalDomainWorkingGroup.objects.get(name="Somatic Cancer")
        if cdwg != expected:
            raise ValidationError(
                "If type is 'Somatic Cancer Variant Curation Expert Panel', "
                + "then CDWG must be 'Somatic Cancer'."
            )

    elif (
        type_ == "INDEPENDENT_CURATION"
    ):  # If your type for independent groups is 'ICG'
        expected = ClinicalDomainWorkingGroup.objects.get(name="None")
        if cdwg != expected:
            raise ValidationError(
                "If type is 'Independent Curation Group', then CDWG must be 'None'."
            )


def check_duplicate_affiliation_uuid(uuid_val: UUID, instance=None) -> bool:
    """Check if an affiliation with the given UUID already exists."""
    if uuid_val is None:
        return False
    uuid_value = Affiliation.objects.filter(uuid=uuid_val)
    if instance:
        uuid_value = uuid_value.exclude(pk=instance.pk)
    return uuid_value.exists()


def check_duplicate_cdwg_uuid(uuid_val: UUID, instance=None) -> bool:
    """Check if a CDWG with the given UUID already exists."""
    if uuid_val is None:
        return False
    uuid_qs = ClinicalDomainWorkingGroup.objects.filter(uuid=uuid_val)
    if instance:
        uuid_qs = uuid_qs.exclude(pk=instance.pk)
    return uuid_qs.exists()


def validate_type_and_uuid(cleaned_data: dict) -> None:
    """Validate that Independent Groups do not have UUIDs."""
    uuid_val = cleaned_data.get("uuid")
    type_val = cleaned_data.get("type")

    if type_val == "INDEPENDENT_CURATION":
        if uuid_val:
            raise ValidationError("UUID must be empty for 'INDEPENDENT_CURATION' type.")


def validate_id_duplicates(cleaned_data: dict, instance=None) -> None:
    """Validate when an ID has been edited by superuser,
    the ID should not already exist in DB."""
    affil_id = cleaned_data.get("affiliation_id")
    ep_id = cleaned_data.get("expert_panel_id")

    # Skip if IDs are unchanged
    if (
        instance
        and affil_id == instance.affiliation_id
        and ep_id == instance.expert_panel_id
    ):
        return

    qs = Affiliation.objects.all()
    if instance:
        qs = qs.exclude(pk=instance.pk)

    duplicates = list(
        qs.filter(Q(affiliation_id=affil_id) | Q(expert_panel_id=ep_id)).values(
            "affiliation_id", "expert_panel_id"
        )
    )

    if duplicates:
        affil_exists = any(d["affiliation_id"] == affil_id for d in duplicates)
        ep_exists = any(d["expert_panel_id"] == ep_id for d in duplicates)

        if affil_exists and ep_exists:
            id_type = "Affiliation and Expert Panel"
        elif affil_exists:
            id_type = "Affiliation"
        else:
            id_type = "Expert Panel"

        raise ValidationError(f"An affiliation with this {id_type} ID already exists.")


def validate_id_suffix_match(
    cleaned_data: dict,
) -> None:
    """
    Ensure that the numeric suffix of affiliation_id and expert_panel_id match.
    Example: 10001 ↔ 40001, 10098 ↔ 50098.
    """
    affil_id = cleaned_data.get("affiliation_id")
    ep_id = cleaned_data.get("expert_panel_id")
    ep_type = cleaned_data.get("type")

    if affil_id is None or ep_id is None:
        return

    if not 10000 <= affil_id <= 19999:
        raise ValidationError("Affiliation ID must be between 10000 and 19999.")
    if ep_type == "GCEP":
        if not 40000 <= ep_id <= 49999:
            raise ValidationError(
                "GCEP Expert Panel ID must be between 40000 and 49999."
            )
    if ep_type in ("VCEP", "SC_VCEP"):
        if not 50000 <= ep_id <= 59999:
            raise ValidationError(
                "VCEP/SC-VCEP Expert Panel ID must be between 50000 and 59999."
            )

    # Compare suffixes (last 3 digits)
    affil_suffix = affil_id % 1000
    ep_suffix = ep_id % 1000

    if affil_suffix != ep_suffix:
        raise ValidationError(f"The ID suffix must match: got {affil_id} and {ep_id}.")
