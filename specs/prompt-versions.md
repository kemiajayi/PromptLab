# Feature Spec: Prompt Versions

Status: Draft for Module 3 implementation
Depends on: existing prompt endpoints in `backend/app/api.py`

## 1. Overview
 Today, `PUT` and `PATCH /prompts/{prompt_id}` overwrite a prompt in place. Once a prompt is edited, its earlier wording is gone. Prompt engineering is iterative, so users need to see how a prompt changed, compare earlier wording, and go back to a version that worked better.

This feature records an immutable snapshot of a prompt's text every time that text changes, lets users list and read those snapshots, and lets them revert to previous versions.

## 2. Goals

- G1. Every change to a prompt's `title`, `content`, or `description` is recorded as a new numbered version.
- G2. Users can list all versions of a prompt and read any single version.
- G3. Users can restore an earlier version without losing any history.
- G4. Existing prompt endpoints keep their current status codes, error messages, and behavior. The visible changes are a new `current_version` field in prompt responses and one bug fix: `PATCH` now rejects `null` for `title` and `content` (AC2.8).

## 3. Definitions

- **Versioned fields**: `title`, `content`, `description`.
- **Version**: an immutable snapshot of the versioned fields at one point in time, identified by `prompt_id` plus `version_number`.
- **Current version**: the highest `version_number` for a prompt. The prompt's versioned fields always equal this version's fields.

## 4. Behavior rules

These rules apply across all user stories.

- R1. Creating a prompt creates version 1.
- R2. `version_number` starts at 1 for each prompt and increases by exactly 1 for each new version. Numbers are never reused or skipped.
- R3. `PUT` or `PATCH` creates a new version only when at least one versioned field ends up different from the current version. Values are compared exactly, so `"Hello"` and `"hello"` are different, and `null` differs from `""`.
- R4. A `PUT` or `PATCH` that changes only `collection_id`, or changes nothing, creates no version and leaves `current_version` unchanged. The existing behavior of refreshing `updated_at` stays as it is.
- R5. A version's `created_at` equals the prompt's `updated_at` set by the same request. For version 1 it equals the prompt's `created_at`.
- R6. Versions are never modified or deleted individually.
- R7. Deleting a prompt deletes all of its versions.
- R8. A request that fails validation (400, 404, or 422) creates no version and changes nothing.

## 5. User stories and acceptance criteria

Each criterion has an ID so tests can reference it.

### US1. Automatic version on create

As a prompt author, I want my first draft saved as version 1, so that history starts from the beginning.

- AC1.1. Given no prompts, when I `POST /prompts` with a valid body, then the response is `201 Created` and includes `"current_version": 1`.
- AC1.2. Given that prompt, when I `GET /prompts/{prompt_id}/versions`, then the response is `200 OK` with `"total": 1`, and the single version has `version_number` 1 and the same `title`, `content`, and `description` as the created prompt.
- AC1.3. Given a `POST /prompts` that fails with `400 Bad Request` (`"Collection not found"`) or `422 Unprocessable Entity`, then no prompt and no version exist afterwards.

### US2. Automatic version on edit

As a prompt author, I want each edit to my prompt's text recorded, so that I can see how it evolved.

- AC2.1. Given a prompt at version 1, when I `PUT` it with a different `content`, then the response is `200 OK` with `"current_version": 2`, and version 2 contains the new content.
- AC2.2. Given a prompt at version 1, when I `PATCH` it with `{"title": "New title"}`, then the response has `"current_version": 2`, and version 2 has the new title plus the unchanged `content` and `description` from version 1.
- AC2.3. Given a prompt at version 2, when I `PATCH` it with a `title` equal to its current title, then `current_version` stays 2 and the version list `total` stays 2.
- AC2.4. Given a prompt in no collection at version 1, when I `PATCH` it with only a valid `collection_id`, then `current_version` stays 1.
- AC2.5. Given a prompt with a description at version 1, when I `PUT` it with only `title` and `content` equal to the current values, then a version 2 is created with `"description": null`, because PUT sets an omitted description to null (existing PUT behavior) and that changes a versioned field.
- AC2.6. Given a prompt at version 1, when I `PUT` it with a `collection_id` that does not exist, then the response is `400 Bad Request` with `{"detail": "Collection not found"}` and `current_version` stays 1.
- AC2.7. Given a version 1 created by `POST`, then that version's `created_at` equals the prompt's `created_at`. Given a version 2 created by `PATCH`, then its `created_at` equals the prompt's `updated_at` in the PATCH response.
- AC2.8. Given a prompt at version 1, when I `PATCH` it with `{"title": null}` or `{"content": null}`, then the response is `422 Unprocessable Entity`, the prompt is unchanged, and `current_version` stays 1. Omitting `title` or `content` is still allowed and keeps the existing value, as in AC2.2. Only an explicit `null` is rejected, because `title` and `content` are required on every prompt. (Current code returns `200 OK` and stores a null title, which a version could not hold.)
- AC2.9. Given a prompt at version 2, `GET /prompts/{prompt_id}` returns `"current_version": 2`, and `GET /prompts` includes that prompt with `"current_version": 2`.

### US3. List versions

As a prompt author, I want to see every version of a prompt, so that I can find the wording I want.

- AC3.1. Given a prompt with 3 versions, when I `GET /prompts/{prompt_id}/versions`, then the response is `200 OK`, `"total": 3`, and `versions` is ordered by `version_number` descending (3, 2, 1).
- AC3.2. Given no prompt with id `missing-id`, when I `GET /prompts/missing-id/versions`, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`.
- AC3.3. Given a prompt that has been deleted, when I `GET` its versions, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`.

### US4. Get one version

As a prompt author, I want to read a specific version, so that I can compare it to the current text.

- AC4.1. Given a prompt with 2 versions, when I `GET /prompts/{prompt_id}/versions/1`, then the response is `200 OK` and the body has `"version_number": 1` and the version 1 field values.
- AC4.2. Given a prompt with 2 versions, when I `GET /prompts/{prompt_id}/versions/3`, then the response is `404 Not Found` with `{"detail": "Version not found"}`.
- AC4.3. Given no prompt with id `missing-id`, when I `GET /prompts/missing-id/versions/1`, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`. The prompt check happens before the version check.
- AC4.4. When I `GET /prompts/{prompt_id}/versions/0`, `/versions/-1`, or `/versions/abc`, then the response is `422 Unprocessable Entity`, because `version_number` must be an integer of at least 1.

### US5. Restore a version

As a prompt author, I want to restore an earlier version, so that I can undo edits that made a prompt worse, without losing the edits I am undoing.

- AC5.1. Given a prompt with 3 versions, when I `POST /prompts/{prompt_id}/versions/1/restore`, then the response is `200 OK`, the returned prompt has the `title`, `content`, and `description` of version 1, and `"current_version": 4`.
- AC5.2. After AC5.1, `GET /prompts/{prompt_id}/versions` returns `"total": 4`. Version 4 has `"restored_from": 1`, and versions 1 to 3 are unchanged.
- AC5.3. Restore does not change the prompt's `id`, `created_at`, or `collection_id`, and it refreshes `updated_at`.
- AC5.4. Given a prompt whose current version is 3, when I `POST /prompts/{prompt_id}/versions/3/restore`, then the response is `400 Bad Request` with `{"detail": "Version is already current"}` and no version is created.
- AC5.5. Given a prompt with 2 versions, when I `POST /prompts/{prompt_id}/versions/5/restore`, then the response is `404 Not Found` with `{"detail": "Version not found"}`.
- AC5.6. Given no prompt with id `missing-id`, when I `POST /prompts/missing-id/versions/1/restore`, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`.
- AC5.7. When I `POST /prompts/{prompt_id}/versions/0/restore`, then the response is `422 Unprocessable Entity`.
- AC5.8. Given version 1 contains text A, version 2 contains text B, and version 3 was created by restoring version 1, when I `POST /prompts/{prompt_id}/versions/1/restore` again, then the response is `200 OK` and version 4 is created with `"restored_from": 1`, even though its text matches the current version. A restore is always recorded. Only restoring the current version number itself is rejected (AC5.4).

### US6. Versions are read-only

As a prompt author, I want versions to be a reliable record, so that history cannot be changed after the fact.

- AC6.1. When I send `PUT`, `PATCH`, or `DELETE` to `/prompts/{prompt_id}/versions/1`, then the response is `405 Method Not Allowed`.

### US7. Deleting a prompt removes its history

As a prompt author, I want a deleted prompt's history removed with it, so that no orphaned versions remain.

- AC7.1. Given a prompt with 2 versions, when I `DELETE /prompts/{prompt_id}`, then the response is `204 No Content`, and `GET /prompts/{prompt_id}/versions` returns `404 Not Found` with `{"detail": "Prompt not found"}`.

## 6. Data model changes

### 6.1 New model: `PromptVersion` (in `backend/app/models.py`)

| Field | Type | Rules |
| --- | --- | --- |
| `prompt_id` | `str` | Id of the prompt this version belongs to |
| `version_number` | `int` | 1 or more. Unique per prompt |
| `title` | `str` | Same constraints as `PromptBase.title` (1 to 200 characters) |
| `content` | `str` | Same constraints as `PromptBase.content` (at least 1 character) |
| `description` | `Optional[str]` | Same constraints as `PromptBase.description` (at most 500 characters) |
| `created_at` | `datetime` | Naive UTC, from `get_current_time()` (see R5) |
| `restored_from` | `Optional[int]` | Version number restored from. `null` unless created by a restore |

`PromptVersion` has no `id` of its own. It is identified by `prompt_id` plus `version_number`.

### 6.2 New model: `PromptVersionList`

| Field | Type | Rules |
| --- | --- | --- |
| `versions` | `List[PromptVersion]` | Ordered by `version_number` descending |
| `total` | `int` | Equals the length of `versions` |

This follows the existing `PromptList` and `CollectionList` pattern.

### 6.3 Changed model: `Prompt`

| Field | Type | Rules |
| --- | --- | --- |
| `current_version` | `int` | Added. Default 1. Equals the highest `version_number` for this prompt |

Request field names remain unchanged. `PromptUpdatePartial` must reject explicitly supplied `null` values for `title` and `content`, while continuing to allow those fields to be omitted (AC2.8). Clients cannot set `current_version`. If a request body includes it, it is ignored, because those request models do not declare it.

### 6.4 Storage changes (`backend/app/storage.py`)

- Add `self._versions: Dict[str, List[PromptVersion]]`, keyed by `prompt_id`.
- Add methods:
  - `add_version(version: PromptVersion) -> PromptVersion`
  - `get_versions(prompt_id: str) -> List[PromptVersion]`. Returns an empty list if none exist.
  - `get_version(prompt_id: str, version_number: int) -> Optional[PromptVersion]`. Returns `None` if not found.
  - `delete_versions(prompt_id: str) -> None`
- `delete_prompt()` also removes that prompt's versions (R7).
- `clear()` also clears `_versions`, so the `clear_storage` test fixture isolates version data.
- Storage methods do not raise for missing records. The API layer raises the HTTP errors, matching the current pattern.

No data migration is needed. Storage is in memory, so no prompts exist from before this feature when the app starts.

## 7. API endpoints

Documented `400`, `404`, and `405` errors contain a string under `detail`, for example `{"detail": "Prompt not found"}`. Request and path validation errors return `422 Unprocessable Entity` with an array of validation error objects under `detail`. No authentication is required.

### 7.1 `GET /prompts/{prompt_id}/versions`

Lists all versions of a prompt, newest first.

Path parameters: `prompt_id` (string).

Response `200 OK`:

```json
{
  "versions": [
    {
      "prompt_id": "PROMPT_ID",
      "version_number": 2,
      "title": "Code Review Prompt",
      "content": "Review this code for bugs and style issues:\n\n{{code}}",
      "description": "A prompt for AI code review",
      "created_at": "2026-10-24T12:05:00",
      "restored_from": null
    },
    {
      "prompt_id": "PROMPT_ID",
      "version_number": 1,
      "title": "Code Review Prompt",
      "content": "Review the following code and provide feedback:\n\n{{code}}",
      "description": "A prompt for AI code review",
      "created_at": "2026-10-24T12:00:00",
      "restored_from": null
    }
  ],
  "total": 2
}
```

Errors:

| Status | Detail | When |
| --- | --- | --- |
| `404 Not Found` | `"Prompt not found"` | No prompt has this id |

Tested by: AC3.1, AC3.2, AC3.3.

### 7.2 `GET /prompts/{prompt_id}/versions/{version_number}`

Returns one version.

Path parameters: `prompt_id` (string), `version_number` (integer, at least 1).

Response `200 OK`:

```json
{
  "prompt_id": "PROMPT_ID",
  "version_number": 1,
  "title": "Code Review Prompt",
  "content": "Review the following code and provide feedback:\n\n{{code}}",
  "description": "A prompt for AI code review",
  "created_at": "2026-10-24T12:00:00",
  "restored_from": null
}
```

Errors, checked in this order:

| Status | Detail | When |
| --- | --- | --- |
| `422 Unprocessable Entity` | Pydantic validation list | `version_number` is not an integer, or is less than 1 |
| `404 Not Found` | `"Prompt not found"` | No prompt has this id |
| `404 Not Found` | `"Version not found"` | The prompt exists but has no version with this number |

Tested by: AC4.1 to AC4.4.

### 7.3 `POST /prompts/{prompt_id}/versions/{version_number}/restore`

Copies the versioned fields of an earlier version onto the prompt and records the result as a new version.

Path parameters: `prompt_id` (string), `version_number` (integer, at least 1).

Request body: none. Any body sent is ignored.

Response `200 OK` (the updated prompt):

```json
{
  "id": "PROMPT_ID",
  "title": "Code Review Prompt",
  "content": "Review the following code and provide feedback:\n\n{{code}}",
  "description": "A prompt for AI code review",
  "collection_id": null,
  "created_at": "2026-10-24T12:00:00",
  "updated_at": "2026-10-24T12:10:00",
  "current_version": 3
}
```

Errors, checked in this order:

| Status | Detail | When |
| --- | --- | --- |
| `422 Unprocessable Entity` | Pydantic validation list | `version_number` is not an integer, or is less than 1 |
| `404 Not Found` | `"Prompt not found"` | No prompt has this id |
| `404 Not Found` | `"Version not found"` | The prompt exists but has no version with this number |
| `400 Bad Request` | `"Version is already current"` | `version_number` equals the prompt's `current_version` |

The response is `200 OK`, not `201 Created`, because the main resource returned is the existing prompt.

Tested by: AC5.1 to AC5.8.

### 7.4 Changes to existing endpoints

| Endpoint | Change |
| --- | --- |
| `POST /prompts` | Creates version 1. Response includes `"current_version": 1` |
| `GET /prompts`, `GET /prompts/{prompt_id}` | Each prompt in the response includes `current_version` |
| `PUT /prompts/{prompt_id}` | Creates a new version when a versioned field changes (R3, R4) |
| `PATCH /prompts/{prompt_id}` | Creates a new version when a versioned field changes (R3, R4) |
| `DELETE /prompts/{prompt_id}` | Also deletes the prompt's versions |

Existing status codes and error messages remain unchanged except for the explicit-null `PATCH` validation change defined in AC2.8.

## 8. Error conditions and edge cases

| # | Case | Expected result | Criterion |
| --- | --- | --- | --- |
| E1 | Prompt id does not exist (list, get, restore) | `404`, `"Prompt not found"` | AC3.2, AC4.3, AC5.6 |
| E2 | Version number does not exist for an existing prompt | `404`, `"Version not found"` | AC4.2, AC5.5 |
| E3 | Version number is `0`, negative, or not an integer | `422` | AC4.4, AC5.7 |
| E4 | Restore the current version | `400`, `"Version is already current"`, no new version | AC5.4 |
| E5 | Restore an older version whose text equals the current text | New version created with `restored_from` set | AC5.8 |
| E6 | PATCH or PUT with identical versioned fields | No new version, `updated_at` still refreshed | AC2.3 |
| E7 | PATCH only `collection_id` | No new version | AC2.4 |
| E8 | PUT omits `description` on a prompt that had one | New version with `description: null` | AC2.5 |
| E9 | PUT or PATCH fails with 400, 404, or 422 | No version created | AC2.6, R8 |
| E10 | Prompt deleted | All versions removed, list returns `404` | AC7.1 |
| E11 | Write method sent to a version URL | `405 Method Not Allowed` | AC6.1 |
| E12 | Restore after the restored-from version's collection was deleted | Not applicable. Versions do not store `collection_id`, and restore leaves `collection_id` unchanged | AC5.3 |
| E13 | Request body includes `current_version` on POST, PUT, or PATCH | Ignored. Server sets the value | Section 7.3 |
| E14 | Two quick edits in a row | Each gets the next version number, no gaps or repeats | R2 |
| E15 | PATCH sets `title` or `content` to `null` | `422`, prompt unchanged, no version. `description: null` stays allowed | AC2.8 |

## 9. Test plan

Tests go in `backend/tests/test_api.py` in a new `TestPromptVersions` class, using the existing `client` and `sample_prompt_data` fixtures. `clear_storage` runs automatically. Each test asserts the status code. For `400` and `404` errors, tests also assert the exact `detail` message. For `422` errors, tests assert that `detail` is a list and that an error's `loc` names the affected field, for example `["path", "version_number"]` or `["body", "title"]`. They do not assert Pydantic's exact `msg` text, because that wording changes between Pydantic versions.

Minimum tests: one per acceptance criterion above.

## 10. Documentation updates required when implemented

- `docs/API_REFERENCE.md`: add the three new endpoints, and add `current_version` to every prompt response example.
- `README.md`: add the endpoints to the API summary.
- Docstrings for all new models, storage methods, and route functions.
- `docs/SYSTEM_MODEL.md`: add the version storage and its relationship to prompts.
