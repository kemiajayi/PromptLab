# Feature Spec: Tagging System

Depends on: existing prompt endpoints in `backend/app/api.py`

## 1. Overview

Collections give each prompt one place to live, because a prompt has at most one `collection_id`. Users also need to label prompts across collections, for example marking prompts as `python`, `code-review`, and `draft` at the same time.

This feature will enable users to classify and organize their prompts using tags. It will let users attach short labels (tags) to prompts, add and remove them, filter the prompt list by tag, and see every tag in use with a count.

## 2. Goals

- G1. A prompt can have zero to 10 tags.
- G2. Tags are normalized, so `Python`, ` python `, and `python` are the same tag.
- G3. Users can add tags to and remove tags from an existing prompt without resending the prompt.
- G4. Users can filter `GET /prompts` by one tag.
- G5. Users can list all tags currently in use, with how many prompts use each.
- G6. Existing behavior remains unchanged for requests that do not use the new tagging fields or query parameter. Requests using them follow this spec's validation rules. The visible changes are a new `tags` field in prompt responses, an optional `tags` field on create, and a new `tag` query parameter on `GET /prompts`.

## 3. Definitions

- **Tag**: a string label attached to a prompt.
- **Normalization**: removing leading and trailing whitespace, then converting to lowercase.
- **Valid tag**: after normalization, 1 to 32 characters, made of lowercase letters `a-z`, digits `0-9`, and single hyphens between them. It cannot start or end with a hyphen or contain two hyphens in a row. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`.
  - Valid: `python`, `code-review`, `gpt4`, `2026`.
  - Invalid: `code review` (space), `c++` (symbol), `-draft` (leading hyphen), `a--b` (double hyphen), a 33-character string.
- **Tag in use**: a tag attached to at least one prompt.

## 4. Behavior rules

These rules apply across all user stories.

- R1. Every tag in a request is normalized before it is validated, compared, or stored.
- R2. A prompt's tags are stored and returned in alphabetical order, with no duplicates.
- R3. Duplicates in one request collapse into one tag. `["python", "Python"]` stores `["python"]`.
- R4. Adding a tag the prompt already has is not an error. It changes nothing.
- R5. A request may contain at most 10 tag entries before deduplication. More than 10 entries returns `422`, even if some repeat. A prompt may store at most 10 unique normalized tags. Adding tags that would exceed this stored limit returns `400`.
- R6. Tags have no storage of their own. A tag exists only while at least one prompt has it, so `GET /tags` is computed from prompts.
- R7. `PUT` and `PATCH /prompts/{prompt_id}` do not read or change tags. A `tags` field in their request body is ignored, and the prompt keeps its existing tags.
- R8. When an add or remove request changes a prompt's tag set, the prompt's `updated_at` is refreshed. When it changes nothing (R4), `updated_at` is not changed.
- R9. A request that fails (400, 404, or 422) changes nothing.

## 5. User stories and acceptance criteria

Each criterion has an ID so tests can reference it.

### US1. Tag a prompt when creating it

As a prompt author, I want to add tags when I create a prompt, so that it is organized from the start.

- AC1.1. When I `POST /prompts` with `"tags": ["Python", "code-review"]`, then the response is `201 Created` and includes `"tags": ["code-review", "python"]`.
- AC1.2. When I `POST /prompts` without a `tags` field, then the response includes `"tags": []`.
- AC1.3. When I `POST /prompts` with `"tags": ["python", " PYTHON "]`, then the response includes `"tags": ["python"]`.
- AC1.4. When I `POST /prompts` with a tag of 33 characters at index 0, then the response is `422 Unprocessable Entity`, the error's `loc` is `["body", "tags", 0]`, and no prompt is created.
- AC1.5. When I `POST /prompts` with `"tags": ["code review"]`, then the response is `422 Unprocessable Entity` with `loc` `["body", "tags", 0]`.
- AC1.6. When I `POST /prompts` with 11 tags, then the response is `422 Unprocessable Entity` with `loc` `["body", "tags"]`.
- AC1.7. When I `POST /prompts` with `"tags": [""]` or `"tags": ["   "]`, then the response is `422 Unprocessable Entity` with `loc` `["body", "tags", 0]`.

### US2. Add tags to an existing prompt

As a prompt author, I want to add tags to a prompt I already have, so that I do not have to resend the whole prompt.

- AC2.1. Given a prompt with `"tags": ["python"]`, when I `POST /prompts/{prompt_id}/tags` with `{"tags": ["draft"]}`, then the response is `200 OK` and the returned prompt has `"tags": ["draft", "python"]`.
- AC2.2. Given a prompt with `"tags": ["python"]`, when I `POST /prompts/{prompt_id}/tags` with `{"tags": ["Python"]}`, then the response is `200 OK`, `tags` is still `["python"]`, and `updated_at` is unchanged (R4, R8).
- AC2.3. Given a prompt with `"tags": ["python"]`, when I add `["draft"]`, then `updated_at` in the response is later than before, and `created_at` and `id` are unchanged.
- AC2.4. Given a prompt with 9 tags, when I add 2 new tags, then the response is `400 Bad Request` with `{"detail": "A prompt can have at most 10 tags"}` and the prompt still has 9 tags.
- AC2.5. Given a prompt with 10 tags, when I add one of the tags it already has, then the response is `200 OK`, because the final set is still 10 tags (R5).
- AC2.6. Given no prompt with id `missing-id`, when I `POST /prompts/missing-id/tags` with `{"tags": ["python"]}`, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`.
- AC2.7. When I `POST /prompts/{prompt_id}/tags` with `{"tags": []}` or `{}`, then the response is `422 Unprocessable Entity`.
- AC2.8. When I `POST /prompts/{prompt_id}/tags` with `{"tags": ["c++"]}`, then the response is `422 Unprocessable Entity` with `loc` `["body", "tags", 0]`, and the prompt's tags are unchanged.

### US3. Remove a tag from a prompt

As a prompt author, I want to remove a tag that no longer applies, so that my labels stay accurate.

- AC3.1. Given a prompt with `"tags": ["draft", "python"]`, when I `DELETE /prompts/{prompt_id}/tags/draft`, then the response is `204 No Content` with an empty body, and `GET /prompts/{prompt_id}` returns `"tags": ["python"]`.
- AC3.2. Given a prompt with `"tags": ["python"]`, when I `DELETE /prompts/{prompt_id}/tags/Python`, then the response is `204 No Content`, because the path value is normalized (R1).
- AC3.3. Given a prompt with `"tags": ["python"]`, when I `DELETE /prompts/{prompt_id}/tags/draft`, then the response is `404 Not Found` with `{"detail": "Tag not found on prompt"}`.
- AC3.4. Given no prompt with id `missing-id`, when I `DELETE /prompts/missing-id/tags/python`, then the response is `404 Not Found` with `{"detail": "Prompt not found"}`. The prompt check happens before the tag check.
- AC3.5. After AC3.1, the prompt's `updated_at` is later than before.

### US4. Filter prompts by tag

As a prompt author, I want to see only prompts with a given tag, so that I can find related prompts across collections.

- AC4.1. Given prompt A tagged `["python"]` and prompt B tagged `["sql"]`, when I `GET /prompts?tag=python`, then the response is `200 OK` with `"total": 1` and only prompt A.
- AC4.2. Given prompt A tagged `["python"]`, when I `GET /prompts?tag=PYTHON`, then prompt A is returned (R1).
- AC4.3. When I `GET /prompts?tag=unused`, then the response is `200 OK` with `{"prompts": [], "total": 0}`.
- AC4.4. Given prompt A tagged `["python"]` in collection C1 and prompt B tagged `["python"]` in collection C2, when I `GET /prompts?tag=python&collection_id=C1`, then only prompt A is returned. The `tag`, `collection_id`, and `search` filters combine with AND.
- AC4.5. When I `GET /prompts?tag=`, then the response is `422 Unprocessable Entity`.
- AC4.6. When I `GET /prompts` with a `tag` value of 33 characters, then the response is `422 Unprocessable Entity`.
- AC4.7. Results filtered by tag keep the existing order: newest `created_at` first.
- AC4.8. When I `GET /prompts?tag=code%20review`, then the response is `422 Unprocessable Entity` with `loc` `["query", "tag"]`.

### US5. List tags in use

As a prompt author, I want to see every tag I have used and how often, so that I reuse existing tags instead of creating near-duplicates.

- AC5.1. Given no prompts, when I `GET /tags`, then the response is `200 OK` with `{"tags": [], "total": 0}`.
- AC5.2. Given prompt A tagged `["python", "sql"]` and prompt B tagged `["python"]`, when I `GET /tags`, then the response is `200 OK` with `"total": 2` and `tags` equal to `[{"name": "python", "prompt_count": 2}, {"name": "sql", "prompt_count": 1}]`, ordered by `name`.
- AC5.3. After the only prompt tagged `sql` is deleted, or has `sql` removed, `GET /tags` no longer includes `sql` (R6).

### US6. Existing edits leave tags alone

As a prompt author, I want my tags kept when I edit a prompt's text, so that editing does not silently remove them.

- AC6.1. Given a prompt tagged `["python"]`, when I `PUT /prompts/{prompt_id}` with only `title` and `content`, then the response is `200 OK` with `"tags": ["python"]`.
- AC6.2. Given a prompt tagged `["python"]`, when I `PATCH /prompts/{prompt_id}` with `{"tags": []}`, then the response is `200 OK` and `tags` is still `["python"]` (R7).

## 6. Data model changes

### 6.1 New type: `Tag` (in `backend/app/models.py`)

A string that is normalized (R1) and must be a valid tag (Section 4).

Implementation note: Pydantic's `StringConstraints(to_lower=True)` does not lowercase the value before the `pattern` check, so `"Python"` would be rejected. Normalize in a `BeforeValidator` and apply `StringConstraints(min_length=1, max_length=32, pattern=...)` after it. This keeps errors field-level, with `loc` pointing at the list index.

### 6.2 Changed model: `PromptCreate`

| Field | Type | Rules |
| --- | --- | --- |
| `tags` | `List[Tag]` | Added. Optional, default `[]`. At most 10 items in the request |

### 6.3 Changed model: `Prompt`

| Field | Type | Rules |
| --- | --- | --- |
| `tags` | `List[str]` | Added. Default `[]`. Sorted alphabetically, no duplicates, at most 10 |

`PromptBase`, `PromptUpdate`, and `PromptUpdatePartial` do not get a `tags` field. That is how R7 is enforced: `PUT` and `PATCH` bodies that include `tags` have it ignored, matching how FastAPI already treats undeclared fields. The `PUT` handler must copy the existing `tags` onto the rebuilt `Prompt`, because it currently builds a new `Prompt` field by field.

### 6.4 New request model: `TagAdd`

| Field | Type | Rules |
| --- | --- | --- |
| `tags` | `List[Tag]` | Required. 1 to 10 items |

### 6.5 New response models: `TagSummary` and `TagList`

`TagSummary`:

| Field | Type | Rules |
| --- | --- | --- |
| `name` | `str` | A tag in use |
| `prompt_count` | `int` | Number of prompts with this tag. Always 1 or more |

`TagList`:

| Field | Type | Rules |
| --- | --- | --- |
| `tags` | `List[TagSummary]` | Ordered by `name` ascending |
| `total` | `int` | Equals the length of `tags` |

This follows the existing `PromptList` and `CollectionList` pattern.

### 6.6 Storage and utilities

- No new storage dictionary. Tags live on each `Prompt`, the same way `collection_id` does (R6). Prompts are saved with the existing `storage.update_prompt()`.
- Add to `backend/app/utils.py`:
  - `normalize_tag(tag: str) -> str`
  - `filter_prompts_by_tag(prompts: List[Prompt], tag: str) -> List[Prompt]`
  - `count_tags(prompts: List[Prompt]) -> List[TagSummary]`, sorted by name.
- `storage.clear()` needs no change, because clearing prompts clears their tags. The `clear_storage` fixture keeps isolating tests.

No data migration is needed. Storage is in memory, so no prompts exist from before this feature when the app starts.

## 7. API endpoints

All errors use the existing formats: `{"detail": "..."}` for 400 and 404, and the Pydantic validation list for 422. No authentication is required.

### 7.1 `POST /prompts/{prompt_id}/tags`

Adds one or more tags to a prompt.

Request body:

```json
{
  "tags": ["Draft", "python"]
}
```

Response `200 OK` (the updated prompt):

```json
{
  "id": "PROMPT_ID",
  "title": "Code Review Prompt",
  "content": "Review the following code and provide feedback:\n\n{{code}}",
  "description": "A prompt for AI code review",
  "collection_id": null,
  "created_at": "2026-10-24T12:00:00",
  "updated_at": "2026-10-24T12:05:00",
  "tags": ["draft", "python"]
}
```

Errors, checked in this order:

| Status | Detail | When |
| --- | --- | --- |
| `422 Unprocessable Entity` | Validation list, `loc` points at the field or list index | Missing `tags`, empty list, more than 10 items, or an invalid tag |
| `404 Not Found` | `"Prompt not found"` | No prompt has this id |
| `400 Bad Request` | `"A prompt can have at most 10 tags"` | The final tag set would have more than 10 tags |

Tested by: AC2.1 to AC2.8.

### 7.2 `DELETE /prompts/{prompt_id}/tags/{tag}`

Removes one tag from a prompt. The `{tag}` path value is normalized before matching.

Response `204 No Content` with an empty body.

Errors, checked in this order:

| Status | Detail | When |
| --- | --- | --- |
| `404 Not Found` | `"Prompt not found"` | No prompt has this id |
| `404 Not Found` | `"Tag not found on prompt"` | The prompt exists but does not have this tag |

A `{tag}` value that could never be valid, such as `c++`, returns `404 "Tag not found on prompt"`, because no prompt can have it.

Tested by: AC3.1 to AC3.5.

### 7.3 `GET /tags`

Lists every tag in use with its prompt count.

Response `200 OK`:

```json
{
  "tags": [
    {"name": "python", "prompt_count": 2},
    {"name": "sql", "prompt_count": 1}
  ],
  "total": 2
}
```

Errors: none. With no tags in use, the response is `{"tags": [], "total": 0}`.

Tested by: AC5.1 to AC5.3.

### 7.4 Changes to existing endpoints

| Endpoint | Change |
| --- | --- |
| `POST /prompts` | Accepts optional `tags`. Response includes `tags` |
| `GET /prompts` | New optional query parameter `tag` (1 to 32 characters, normalized). Each prompt includes `tags` |
| `GET /prompts/{prompt_id}` | Response includes `tags` |
| `PUT /prompts/{prompt_id}` | Keeps existing tags. Response includes `tags` |
| `PATCH /prompts/{prompt_id}` | Keeps existing tags, ignores a `tags` field. Response includes `tags` |
| `DELETE /prompts/{prompt_id}` | No change. The prompt's tags disappear with it |

The `tag` query parameter uses the normalization and validity rules in Section 4. Invalid values return `422` with `loc` `["query", "tag"]`.

Existing behavior remains unchanged for requests that do not use the new tagging fields or query parameter. Requests using them follow this spec's validation rules.

Example: `GET /prompts?tag=python` returns `200 OK`:

```json
{
  "prompts": [
    {
      "id": "PROMPT_ID",
      "title": "Code Review Prompt",
      "content": "Review the following code and provide feedback:\n\n{{code}}",
      "description": "A prompt for AI code review",
      "collection_id": null,
      "created_at": "2026-10-24T12:00:00",
      "updated_at": "2026-10-24T12:05:00",
      "tags": ["draft", "python"]
    }
  ],
  "total": 1
}
```

## 8. Error conditions and edge cases

| # | Case | Expected result | Criterion |
| --- | --- | --- | --- |
| E1 | Tag longer than 32 characters after trimming | `422`, `loc` points at the list index | AC1.4 |
| E2 | Tag with a space, symbol, leading or trailing hyphen, or double hyphen | `422`, `loc` points at the list index | AC1.5, AC2.8 |
| E3 | Empty or whitespace-only tag | `422` | AC1.7 |
| E4 | More than 10 tags in one request | `422`, `loc` `["body", "tags"]` | AC1.6 |
| E5 | Adding tags would exceed 10 in total | `400`, `"A prompt can have at most 10 tags"`, no change | AC2.4 |
| E6 | Adding only tags the prompt already has, including when the prompt already has 10 tags | `200`, no change, `updated_at` unchanged | AC2.2, AC2.5 |
| E7 | Same tag twice in one request, in different case | Stored once | AC1.3 |
| E8 | Add tags with an empty list or no body | `422` | AC2.7 |
| E9 | Prompt id does not exist (add or remove tag) | `404`, `"Prompt not found"` | AC2.6, AC3.4 |
| E10 | Removing a tag the prompt does not have | `404`, `"Tag not found on prompt"` | AC3.3 |
| E11 | Mixed-case tag in the delete path or `tag` query | Normalized, then matched | AC3.2, AC4.2 |
| E12 | Filter by a tag no prompt has | `200`, empty list | AC4.3 |
| E13 | `?tag=` empty, longer than 32 characters, or containing invalid characters | `422`, `loc` `["query", "tag"]` | AC4.5, AC4.6, AC4.8 |
| E14 | `tags` sent in a `PUT` or `PATCH` body | Ignored, existing tags kept | AC6.2 |
| E15 | Last prompt with a tag is deleted or untagged | Tag disappears from `GET /tags` | AC5.3 |
| E16 | Non-string tag such as `5` | `422`, `loc` points at the list index | Section 7.1 |

Tests for 422 responses assert the status code and the `loc`. They do not assert Pydantic's exact `msg` text, because that wording changes between Pydantic versions.

## 9. Interaction with prompt versions

The versions spec (`specs/prompt-versions.md`) may be implemented before or after this one.

- Tags are not a versioned field. Adding or removing tags never creates a version.
- Restoring a version leaves the prompt's current tags unchanged.
- Whichever feature is implemented second must keep the other feature's acceptance criteria passing. When `PUT` rebuilds a prompt, it preserves the existing tags and determines `current_version` according to the prompt versions spec.

## 10. Test plan

Tests go in `backend/tests/test_api.py` in a new `TestTags` class, using the existing `client` and `sample_prompt_data` fixtures. `clear_storage` runs automatically. Each test asserts the status code. Error tests also assert the exact `detail` text for 400 and 404, or the `loc` for 422.

Add unit tests for `normalize_tag`, `filter_prompts_by_tag`, and `count_tags` in a new `backend/tests/test_utils.py`.

Minimum tests: one per acceptance criterion above.

## 11. Documentation updates required when implemented

- `docs/API_REFERENCE.md`: add the three new endpoints and the `tag` query parameter, and add `tags` to every prompt response example.
- `README.md`: add the endpoints to the API summary and tagging to the features list.
- Docstrings for all new models, utility functions, and route functions.
- `docs/SYSTEM_MODEL.md`: add tags to the prompt model and the relationships section.
