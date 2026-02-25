"""Views for the affiliations service."""

# Third-party dependencies:
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import exception_handler

from django.shortcuts import get_object_or_404

# from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse, Http404

# In-house code:
from affiliations.models import Affiliation, Approver, ClinicalDomainWorkingGroup
from affiliations.serializers import (
    AffiliationSerializer,
    ClinicalDomainWorkingGroupSerializer,
)
from affiliations.permissions import HasWriteAccess, HasAffilsAPIKey


def custom_exception_handler(exc, context):
    """Add custom consistent error responses."""
    response = exception_handler(exc, context)
    if response is not None:
        return Response(
            {
                "error": "Request Failed",
                "details": response.data,
            },
            status=response.status_code,
        )
    logging.error("Unhandled exception", exc_info=exc)

    return Response(
        {
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class AffiliationsList(generics.ListCreateAPIView):
    """List all affiliations, or create a new affiliation."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer


class AffiliationsDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an affiliation."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer


class AffiliationDetailByUUID(generics.RetrieveAPIView):
    """Look up an affiliation by its UUID."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer

    def get_object(self):
        uuid = self.kwargs.get("uuid")
        return get_object_or_404(Affiliation, uuid=uuid)


class AffiliationUpdateView(generics.RetrieveUpdateAPIView):
    """Update editable affiliation data, return all affiliation information.
    This view supports lookup by either `affiliation_id` or `expert_panel_id`
    (only one should be provided in the URL).
    """

    permission_classes = [HasWriteAccess]
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer

    def get_object(self):
        """Retrieve Affiliation by either affiliation_id or expert_panel_id."""
        affiliation_id = self.kwargs.get("affiliation_id")
        expert_panel_id = self.kwargs.get("expert_panel_id")

        if affiliation_id is not None:
            try:
                return Affiliation.objects.get(affiliation_id=affiliation_id)
            except Affiliation.DoesNotExist as exc:
                raise Http404(
                    "Affiliation with the provided affiliation_id was not found."
                ) from exc

        if expert_panel_id is not None:
            try:
                return Affiliation.objects.get(expert_panel_id=expert_panel_id)
            except Affiliation.DoesNotExist as exc:
                raise Http404(
                    "Affiliation with the provided expert_panel_id was not found."
                ) from exc

        raise Http404("An affiliation_id or expert_panel_id must be provided.")


class CDWGCreateView(generics.CreateAPIView):
    """Create a new CDWG.

    If a CDWG with the given UUID already exists,
    it returns the existing record with HTTP 200 instead of creating a duplicate.
    """

    permission_classes = [HasWriteAccess]
    serializer_class = ClinicalDomainWorkingGroupSerializer
    queryset = ClinicalDomainWorkingGroup.objects.all()

    def create(self, request, *args, **kwargs):
        # Check for existing CDWG with same UUID
        uuid_val = request.data.get("uuid")
        if uuid_val:
            existing = ClinicalDomainWorkingGroup.objects.filter(uuid=uuid_val).first()
            if existing:
                return Response(
                    {
                        "name": existing.name,
                        "id": existing.id,
                        "uuid": str(existing.uuid),
                    },
                    status=status.HTTP_200_OK,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(
            {
                "name": instance.name,
                "id": instance.id,
                "uuid": str(instance.uuid),
            },
            status=status.HTTP_201_CREATED,
        )


class CDWGUpdateView(generics.RetrieveUpdateAPIView):
    """Update editable CDWG data, return all CDWG information."""

    permission_classes = [HasWriteAccess]
    queryset = ClinicalDomainWorkingGroup.objects.all()
    serializer_class = ClinicalDomainWorkingGroupSerializer
    lookup_field = "id"


class CDWGListView(generics.ListAPIView):
    """List all CDWGs."""

    permission_classes = [HasAffilsAPIKey]
    queryset = ClinicalDomainWorkingGroup.objects.all()
    serializer_class = ClinicalDomainWorkingGroupSerializer


class CDWGDetailView(generics.RetrieveAPIView):
    """List a single CDWG, lookup by either name or ID."""

    permission_classes = [HasAffilsAPIKey]
    queryset = ClinicalDomainWorkingGroup.objects.all()
    serializer_class = ClinicalDomainWorkingGroupSerializer

    def get_object(self):
        queryset = self.get_queryset()
        cdwg_id = self.kwargs.get("id")
        name = self.kwargs.get("name")
        if cdwg_id is not None:
            try:
                return queryset.get(id=cdwg_id)
            except ClinicalDomainWorkingGroup.DoesNotExist as exc:
                raise Http404("A CDWG with that ID does not exist.") from exc

        if name is not None:
            try:
                return queryset.get(name=name)
            except ClinicalDomainWorkingGroup.DoesNotExist as exc:
                raise Http404("A CDWG with that name does not exist.") from exc

        raise Http404("No CDWG ID or name provided.")


class CDWGDetailByUUID(generics.RetrieveAPIView):
    """Look up a CDWG by its UUID."""

    permission_classes = [HasAffilsAPIKey]
    queryset = ClinicalDomainWorkingGroup.objects.all()
    serializer_class = ClinicalDomainWorkingGroupSerializer

    def get_object(self):
        uuid = self.kwargs.get("uuid")
        return get_object_or_404(ClinicalDomainWorkingGroup, uuid=uuid)


@api_view(["GET"])
@permission_classes([HasAffilsAPIKey])
def affiliations_list_json_format(request):  # pylint: disable=unused-argument
    """List all affiliations in old JSON format."""
    affils_queryset = Affiliation.objects.filter(is_deleted=False).values()
    response_obj = {}
    for affil in affils_queryset:
        affil_type = affil["type"].lower()
        # In old JSON, SC-VCEPS are only considered VCEPS.
        if affil_type == "sc_vcep":
            affil_type = "vcep"
        # In old JSON, Affiliation IDs and EP Ids are in string format.
        affil_id = str(affil["affiliation_id"])
        ep_id = str(affil["expert_panel_id"])

        if affil_id not in response_obj:
            if affil_type in ["vcep", "gcep"]:
                old_json_format = {
                    "affiliation_id": affil_id,
                    "affiliation_fullname": affil["full_name"],
                    "subgroups": {
                        affil_type: {
                            "id": ep_id,
                            "fullname": affil["full_name"],
                        },
                    },
                }
            # Independent curation group format
            else:
                old_json_format = {
                    "affiliation_id": affil_id,
                    "affiliation_fullname": affil["full_name"],
                }
            response_obj[affil_id] = old_json_format
        elif affil_type not in response_obj[affil_id]["subgroups"]:
            # If VCEP or GCEP in full name, add other subgroup to end of name.
            if ("VCEP" in response_obj[affil_id]["affiliation_fullname"]) or (
                "GCEP" in response_obj[affil_id]["affiliation_fullname"]
            ):
                response_obj[affil_id]["affiliation_fullname"] = (
                    response_obj[affil_id]["affiliation_fullname"] + "/" + affil["type"]
                )
            # Else append affiliation subgroup name to full name
            else:
                response_obj[affil_id]["affiliation_fullname"] = (
                    response_obj[affil_id]["affiliation_fullname"]
                    + "/"
                    + affil["full_name"]
                )

            response_obj[affil_id]["subgroups"][affil_type] = {
                "id": ep_id,
                "fullname": affil["full_name"],
            }
        # If there are approvers, add them to the object.
        approvers_queryset = Approver.objects.filter(
            affiliation_id=affil["id"]
        ).values_list("approver_name", flat=True)
        if approvers_queryset and "approver" not in response_obj[affil_id]:
            response_obj[affil_id]["approver"] = []
        for name in approvers_queryset:
            if name not in response_obj[affil_id]["approver"]:
                response_obj[affil_id]["approver"].append(name)

    return JsonResponse(
        list(response_obj.values()),
        status=200,
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )


@api_view(["GET"])
@permission_classes([HasAffilsAPIKey])
def affiliation_detail_json_format(request):
    """List specific affiliation in old JSON format."""
    affil_id = request.GET.get("affil_id")
    affils_queryset = Affiliation.objects.filter(
        affiliation_id=affil_id, is_deleted=False
    ).values()
    response_obj = {}
    for affil in affils_queryset:
        affil_type = affil["type"].lower()
        # In old JSON, SC-VCEPS are only considered VCEPS.
        if affil_type == "sc_vcep":
            affil_type = "vcep"
        # In old JSON, Affiliation IDs and EP Ids are in string format.
        affil_id = str(affil["affiliation_id"])
        ep_id = str(affil["expert_panel_id"])

        if affil_id not in response_obj:
            if affil_type in ["vcep", "gcep"]:
                old_json_format = {
                    "affiliation_id": affil_id,
                    "affiliation_fullname": affil["full_name"],
                    "subgroups": {
                        affil_type: {
                            "id": ep_id,
                            "fullname": affil["full_name"],
                        },
                    },
                }
            # Independent curation group format
            else:
                old_json_format = {
                    "affiliation_id": affil_id,
                    "affiliation_fullname": affil["full_name"],
                }
            response_obj[affil_id] = old_json_format
        elif affil_type not in response_obj[affil_id]["subgroups"]:
            # If VCEP or GCEP in full name, add other subgroup to end of name.
            if ("VCEP" in response_obj[affil_id]["affiliation_fullname"]) or (
                "GCEP" in response_obj[affil_id]["affiliation_fullname"]
            ):
                response_obj[affil_id]["affiliation_fullname"] = (
                    response_obj[affil_id]["affiliation_fullname"] + "/" + affil["type"]
                )
            # Else append affiliation subgroup name to full name
            else:
                response_obj[affil_id]["affiliation_fullname"] = (
                    response_obj[affil_id]["affiliation_fullname"]
                    + "/"
                    + affil["full_name"]
                )

            response_obj[affil_id]["subgroups"][affil_type] = {
                "id": ep_id,
                "fullname": affil["full_name"],
            }
        # If there are approvers, add them to the object.
        approvers_queryset = Approver.objects.filter(
            affiliation_id=affil["id"]
        ).values_list("approver_name", flat=True)
        if approvers_queryset and "approver" not in response_obj[affil_id]:
            response_obj[affil_id]["approver"] = []
        for name in approvers_queryset:
            if name not in response_obj[affil_id]["approver"]:
                response_obj[affil_id]["approver"].append(name)
    return JsonResponse(
        list(response_obj.values()),
        status=200,
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )


@api_view(["POST"])
@permission_classes([HasWriteAccess])
def create_affiliation(request):
    """Handle POST request to create a new affiliation, return affiliation_id
    and expert_panel_id in response."""
    serializer = AffiliationSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        return Response(
            {
                "affiliation_id": instance.affiliation_id,
                "expert_panel_id": instance.expert_panel_id,
            },
            status=status.HTTP_201_CREATED,
        )
    logging.warning("Affiliation creation failed: %s", serializer.errors)
    return Response(
        {
            "error": "Validation Failed",
            "details": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
