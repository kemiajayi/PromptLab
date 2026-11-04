# Agent Instructions Effect Note

## Setup

- Files attached with @: `backend/app/api.py`, `backend/app/models.py`
- Rules file: `.continuerules` (repo root)
- Each run used this identical prompt:

> Write the docs/API_REFERENCE.md entries for GET /health, PUT /prompts/{prompt_id}, and GET /prompts. For each endpoint include curl or fetch request examples, a sample success response, and the error responses.

## Rules under test

From the section "API Curl Examples":

> Include the `-i` flag for HTTP response headers.

From the section "API Reference Conventions":

> Every JSON example must be valid JSON. Never use `...` or `[...]` as a placeholder. Use a real example or an empty array with `"total": 0`.

## Before (rules off)

The curl command for `GET /health` had no `-i` flag:

```bash
curl -X GET "http://localhost:8000/health"
```

The JSON samples contained `//` comments, which are not valid JSON:

```json
{
    "status": "healthy",
    "version": "0.1.0"  // Example version number
}
```

```json
        // ... more prompts ...
    ],
    "total": 2
```

## After (rules on)

The same prompt produced:

```bash
curl -i "http://localhost:8000/health"
```

and JSON samples with no comments or placeholders:

```json
{
    "status": "healthy",
    "version": "0.1.0"
}
```

All three curl commands in this run included `-i`. None of the three in the rules-off run did. No JSON sample in the rules-on run contained a `//` comment.

## Effect

The `-i` flag appeared in every curl example only when the rules were loaded. This matters for PromptLab because several endpoints return an empty body (`204 No Content` on deletes) and others return `400` or `404` with a short `{"detail": "..."}` body. Without response headers, a reader running the examples cannot see the status code the reference is documenting.

The rules-off draft also embedded `//` comments inside JSON samples, which breaks copy and paste into a JSON parser. With the rules on, every sample was valid JSON.

## Limitations

- The rules did not fix everything. The rules-on draft used literal ids such as `abc123` instead of the `PROMPT_ID` and `COLLECTION_ID` placeholders the rules ask for. It also omitted the `422` validation response and the fact that `title` and `content` are required for PUT.
- I reviewed the generated drafts against the implementation and corrected `docs/API_REFERENCE.md` by hand. Those corrections are separate from this comparison.
