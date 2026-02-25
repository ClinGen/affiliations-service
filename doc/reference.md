# Reference Guides

Reference guides contain code conventions, technical reference for APIs,
and technical reference for other aspects of the HCI’s machinery.
Reference material is information-oriented.

## Affiliations Service API

The affiliations service provides an API for integration with other tools.
For a lesson on how to use the affiliations service API, check out the
[tutorial](tutorial.md#using-the-affiliations-service-api).

### Routes

- [`api/database_list/`](#apidatabase_list)
- [`api/database_list/<int:pk>/`](#apidatabase_listintpk)
- [`api/affiliations_list/`](#apiaffiliations_list)
- [`api/affiliation_detail/`](#apiaffiliation_detail)
- [`api/affiliation_detail/uuid/<str:uuid>/`](#apiaffiliation_detailuuidstruuid)
- [`api/affiliation/create/`](#apiaffiliationcreate)
- [`api/affiliation/update/affiliation_id/<int:affiliation_id>/`](#apiaffiliationupdateaffiliation_idintaffiliation_id)
- [`api/affiliation/update/expert_panel_id/<int:expert_panel_id>/`](#apiaffiliationupdateexpert_panel_idintexpert_panel_id)
- [`api/cdwg_list/`](#apicdwg_list)
- [`api/cdwg_detail/id/<int:id>/`](#apicdwg_detailidintid)
- [`api/cdwg_detail/name/<str:name>/`](#apicdwg_detailnamestrname)
- [`api/cdwg_detail/uuid/<str:uuid>/`](#apicdwg_detailuuidstruuid)
- [`api/cdwg/create/`](#apicdwgcreate)
- [`api/cdwg/id/<int:id>/update/`](#apicdwgidintidupdate)

#### `api/database_list/`

Shows detailed information for each affiliation in the database in a list.
Unauthenticated users can issue `GET` requests to this route.

#### `api/database_list/<int:pk>/`

Shows detailed information for a specific affiliation in the database. 
Requires the primary key for the affiliation. Unauthenticated users can issue `GET`
requests to this route.

#### `api/affiliations_list/`

Shows basic information for all affiliations in a list. To issue `GET` requests to this
route, you must have an API key.

#### `api/affiliation_detail/`

Shows basic information for a specific affiliation. Requires query parameter `affil_id`.
To issue `GET` requests to this route, you must have an API key.

#### `api/affiliation_detail/uuid/<str:uuid>/`

Shows detailed information for a specific affiliation given the GPM UUID.
Unauthenticated users can issue `GET` requests to this route.

#### `api/affiliation/create/`

Creates a new affiliation. Returns unique `affiliation_id` and corresponding
`expert_panel_id` if successful. Returns error message with missing or invalid fields
otherwise. To issue a `POST` request to this route, you must have an API key with write
access.

**Required Fields**:

- `full_name` (*string*): The full name of the affiliation.
- `clinical_domain_working_group` (*integer*): The ID of the clinical domain working
  group.
- `type` (*string*): The type of affiliation. Must be one of the following:
  - `VCEP`
  - `GCEP`
  - `SC_VCEP`
  - `INDEPENDENT_CURATION`
- `status` (*string*): The current status of the affiliation. Must be one of the 
  following:
  - `APPLYING`
  - `ACTIVE`
  - `INACTIVE`
  - `RETIRED`
  - `ARCHIVED`

#### `api/affiliation/update/affiliation_id/<int:affiliation_id>/`

Updates an affiliation by affiliation ID. To issue a `PATCH` request to this route, you
must have an API key with write access. The `affiliation_id` must be part of the URL.
Fields that need to be updated should be included in the request.

#### `api/affiliation/update/expert_panel_id/<int:expert_panel_id>/`

Updates an affiliation by expert panel ID. To issue a `PATCH` request to this route, you
must have an API key with write access. The `expert_panel_id` must be part of the URL.
Fields that need to be updated should be included in the request.

#### `api/cdwg_list/`

Shows all clinical domain working groups in a list. To issue `GET` requests to this
route, you must have an API key.

#### `api/cdwg_detail/id/<int:id>/`

Shows detailed information for a specific clinical domain working group given the ID.
To issue `GET` requests to this route, you must have an API key.

#### `api/cdwg_detail/name/<str:name>/`

Shows detailed information for a specific clinical domain working group given the name.
To issue `GET` requests to this route, you must have an API key.

#### `api/cdwg_detail/uuid/<str:uuid>/`

Shows detailed information for a specific clinical domain working group given the GPM UUID.
To issue `GET` requests to this route, you must have an API key.

#### `api/cdwg/create/`

Creates a new clinical domain working group. To issue a `POST` request to this route,
you must have an API key with write access. Returns the `name`, `id`, and `uuid` of the
created record if successful. If a CDWG with the given UUID already exists, returns the
existing record with HTTP 200 instead of creating a duplicate.

**Required Fields**:

- `name` (*string*): The name of the clinical domain working group.
- `uuid` (*string*): The GPM UUID for the clinical domain working group.

#### `api/cdwg/id/<int:id>/update/`

Updates a clinical domain working group by ID. To issue a `PATCH` request to this route,
you must have an API key with write access. The ID of the clinical domain working group
must be part of the URL. Fields that need to be updated should be included in the
request. Note that the `uuid` field is read-only and cannot be updated.

