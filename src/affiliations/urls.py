"""URLs for the affiliations service."""

# Third-party dependencies:
from django.urls import path
from django.urls import URLResolver, URLPattern
from rest_framework.urlpatterns import format_suffix_patterns

# In-house code:
from affiliations import views

urlpatterns: list[URLResolver | URLPattern] = [
    path("database_list/", views.AffiliationsList.as_view()),
    path("database_list/<int:pk>/", views.AffiliationsDetail.as_view()),
    path(
        "affiliations_list/",
        views.affiliations_list_json_format,
    ),
    path(
        "affiliation_detail/",
        views.affiliation_detail_json_format,
    ),
    path(
        "affiliation_detail/uuid/<str:uuid>/", views.AffiliationDetailByUUID.as_view()
    ),
    path(
        "affiliation/create/",
        views.create_affiliation,
    ),
    path(
        "affiliation/update/affiliation_id/<int:affiliation_id>/",
        views.AffiliationUpdateView.as_view(),
    ),
    path(
        "affiliation/update/expert_panel_id/<int:expert_panel_id>/",
        views.AffiliationUpdateView.as_view(),
    ),
    path(
        "cdwg_list/",
        views.CDWGListView.as_view(),
    ),
    path(
        "cdwg_detail/id/<int:id>/",
        views.CDWGDetailView.as_view(),
    ),
    path(
        "cdwg_detail/name/<str:name>/",
        views.CDWGDetailView.as_view(),
    ),
    path(
        "cdwg_detail/uuid/<str:uuid>/",
        views.CDWGDetailByUUID.as_view(),
    ),
    path(
        "cdwg/create/",
        views.CDWGCreateView.as_view(),
    ),
    path(
        "cdwg/id/<int:id>/update/",
        views.CDWGUpdateView.as_view(),
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
