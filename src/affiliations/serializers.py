"""Serializers and deserializers for the affiliations service."""

# Third-party dependencies:
from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError

# In-house code:
from affiliations.models import (
    Affiliation,
    Coordinator,
    Approver,
    Submitter,
    ClinicalDomainWorkingGroup,
)

from affiliations.utils import (
    generate_next_affiliation_id,
    set_expert_panel_id,
    validate_unique_cdwg_name,
    validate_cdwg_matches_type,
    check_duplicate_affiliation_uuid,
    check_duplicate_cdwg_uuid,
    validate_type_and_uuid,
)


class CoordinatorSerializer(serializers.ModelSerializer):
    """Serialize Coordinator objects."""

    class Meta:
        """Describe the fields on an Coordinator object."""

        model = Coordinator
        fields = [
            "coordinator_name",
            "coordinator_email",
        ]


class ApproverSerializer(serializers.ModelSerializer):
    """Serialize Approver objects."""

    class Meta:
        """Describe the fields on an Approver object."""

        model = Approver
        fields = [
            "approver_name",
        ]


class SubmitterSerializer(serializers.ModelSerializer):
    """Serialize Clinvar Submitter ID objects."""

    class Meta:
        """Describe the fields on an Submitter ID object."""

        model = Submitter
        fields = [
            "clinvar_submitter_id",
        ]


class ClinicalDomainWorkingGroupSerializer(serializers.ModelSerializer):
    """Serialize Clinical Domain Working Group objects."""

    uuid = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        """Describe the fields on a CDWG object."""

        model = ClinicalDomainWorkingGroup
        fields = ["id", "name", "uuid"]

    def validate(self, attrs):
        instance_id = self.instance.pk if self.instance else None
        try:
            validate_unique_cdwg_name(attrs["name"], instance_id)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        # Validate UUID on creation.
        if self.instance is None:
            uuid_val = attrs.get("uuid")
            if not uuid_val:
                raise serializers.ValidationError({"uuid": "This field is required."})
            if check_duplicate_cdwg_uuid(uuid_val):
                raise serializers.ValidationError({"uuid": "This UUID already exists."})
        else:
            # Prevent UUID changes on update.
            uuid_val = attrs.get("uuid")
            if uuid_val is not None and self.instance.uuid != uuid_val:
                raise serializers.ValidationError(
                    {"uuid": "uuid is a read-only field and cannot be updated."}
                )

        return attrs


class AffiliationSerializer(serializers.ModelSerializer):
    """Serialize Affiliation objects."""

    uuid = serializers.UUIDField(required=False, allow_null=True)
    coordinators = CoordinatorSerializer(many=True, required=False)
    approvers = ApproverSerializer(many=True, required=False)
    clinvar_submitter_ids = SubmitterSerializer(many=True, required=False)

    clinical_domain_working_group = serializers.PrimaryKeyRelatedField(
        queryset=ClinicalDomainWorkingGroup.objects.all(),
    )

    class Meta:
        """Describe the fields on an Affiliation object."""

        model = Affiliation
        fields = [
            "affiliation_id",
            "expert_panel_id",
            "full_name",
            "short_name",
            "status",
            "type",
            "clinical_domain_working_group",
            "members",
            "approvers",
            "coordinators",
            "clinvar_submitter_ids",
            "is_deleted",
            "uuid",
        ]

    def validate(self, attrs):
        # Validate UUID is present on creation
        if self.instance is None:
            uuid_val = attrs.get("uuid")
            type_ = attrs.get("type")
            if not uuid_val and type_ != "INDEPENDENT_CURATION":
                raise serializers.ValidationError({"uuid": "This field is required."})
            if check_duplicate_affiliation_uuid(uuid_val):
                raise serializers.ValidationError({"uuid": "This UUID already exists."})
            try:
                validate_type_and_uuid(attrs)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        """Create an Affiliation instance along with
        nested Coordinators, Approvers, and Submitter IDs."""
        try:
            generate_next_affiliation_id(validated_data)
            set_expert_panel_id(validated_data)
            validate_cdwg_matches_type(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        coordinators_data = validated_data.pop("coordinators", [])
        approvers_data = validated_data.pop("approvers", [])
        submitter_ids_data = validated_data.pop("clinvar_submitter_ids", [])

        affil = Affiliation.objects.create(
            **validated_data
        )  # pylint: disable=no-member
        for coordinator_data in coordinators_data:
            Coordinator.objects.create(affiliation=affil, **coordinator_data)
        for approver_data in approvers_data:
            Approver.objects.create(affiliation=affil, **approver_data)
        for submitter_id_data in submitter_ids_data:
            Submitter.objects.create(affiliation=affil, **submitter_id_data)
        return affil

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update and return an existing Affiliation instance,
        while preventing changes to immutable fields."""
        try:
            validate_cdwg_matches_type(validated_data, instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        # Prevent updates to immutable fields
        immutable_fields = ["affiliation_id", "expert_panel_id", "type", "uuid"]
        for field in immutable_fields:
            if (
                field in validated_data
                and getattr(instance, field) != validated_data[field]
            ):
                raise serializers.ValidationError(
                    {field: f"{field} is a read-only field and cannot be updated."}
                )

        coordinators_data = validated_data.pop("coordinators", [])
        approvers_data = validated_data.pop("approvers", [])
        submitter_ids_data = validated_data.pop("clinvar_submitter_ids", [])

        # Update the main fields on the instance
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
        instance.save()

        # Update nested objects by delete all existing and re-create.
        instance.coordinators.all().delete()
        for data in coordinators_data:
            Coordinator.objects.create(affiliation=instance, **data)

        instance.approvers.all().delete()
        for data in approvers_data:
            Approver.objects.create(affiliation=instance, **data)

        instance.clinvar_submitter_ids.all().delete()
        for data in submitter_ids_data:
            Submitter.objects.create(affiliation=instance, **data)

        return instance
