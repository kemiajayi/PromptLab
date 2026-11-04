# PromptLab API Reference

## Overview
The PromptLab API provides endpoints for managing prompts and collections in an AI prompt engineering platform. This document outlines each endpoint along with sample curl commands, responses, and additional notes.

### Base URL
```plaintext
http://localhost:8000
```
Example response IDs and timestamps are illustrative. In requests, replace `PROMPT_ID` and `COLLECTION_ID` with the actual `id` values returned by your own POST requests.

### Authentication
No authentication methods are implemented for the current version of the API.

### Request Validation Errors

Requests that fail request-model validation return `422 Unprocessable Entity`.

For example, sending `{}` to `POST /prompts` omits the required `title`
and `content` fields.

Response status: `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {},
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    },
    {
      "type": "missing",
      "loc": ["body", "content"],
      "msg": "Field required",
      "input": {},
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
```
POST /prompts, PUT /prompts/{prompt_id}, PATCH /prompts/{prompt_id},
and POST /collections use request-model validation. The specific errors
depend on the request body and the endpoint's model.

## Endpoints

### Health Check

- **GET** `/health`
  - Checks the health of the service.
  
  **Curl Example:**
  ```bash
  curl -i "http://localhost:8000/health"
  ```

  **Success Response (200 OK):**
  ```json
  {
      "status": "healthy",
      "version": "0.1.0"
  }
  ```

---

### Prompt Endpoints

#### List Prompts

- **GET** `/prompts`
  - Retrieves a list of prompts, optionally filtering by collection and searching.
  
  **Curl Example:**
  ```bash
  curl -i "http://localhost:8000/prompts?collection_id=COLLECTION_ID&search=example"
  ```

  **Success Response (200 OK):**
  ```json
  {
      "prompts": [],
      "total": 0
  }
  ```

---

#### Get Prompt

- **GET** `/prompts/{prompt_id}`
  - Retrieves a prompt by its unique identifier.
  
  **Curl Example:**
  ```bash
  curl -i "http://localhost:8000/prompts/PROMPT_ID"
  ```

  **Success Response (200 OK):**
  ```json
  {
      "id": "PROMPT_ID",
      "title": "Sample Prompt",
      "content": "This is prompt content.",
      "description": "A brief description.",
      "collection_id": null,
      "created_at": "2023-10-01T12:00:00",
      "updated_at": "2023-10-01T12:00:00"
  }
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Prompt not found"
  }
  ```

---

#### Create Prompt

- **POST** `/prompts`
  - Create a new prompt.

  **Curl Example:**
  ```bash
  curl -i -X POST "http://localhost:8000/prompts" -H "Content-Type: application/json" -d '{"title": "New Prompt", "content": "Prompt content", "description": "Some description", "collection_id": null}'
  ```

  **Success Response (201 Created):**
  ```json
  {
      "id": "NEW_PROMPT_ID",
      "title": "New Prompt",
      "content": "Prompt content",
      "description": "Some description",
      "collection_id": null,
      "created_at": "2023-10-01T12:00:00",
      "updated_at": "2023-10-01T12:00:00"
  }
  ```

  **Error Response (400 Bad Request):**
  ```json
  {
      "detail": "Collection not found"
  }
  ```

---

#### Update Prompt

- **PUT** `/prompts/{prompt_id}`
  - Replaces the editable fields. The `title` and `content` fields are required.
  - Omitted `description` and `collection_id` fields become `null`.
  - The `id` and `created_at` values are preserved, and `updated_at` is refreshed.
  
  **Curl Example:**
  ```bash
  curl -i -X PUT "http://localhost:8000/prompts/PROMPT_ID" -H "Content-Type: application/json" -d '{"title": "Updated Title", "content": "Updated content"}'
  ```

  **Success Response (200 OK):**
  ```json
  {
      "id": "PROMPT_ID",
      "title": "Updated Title",
      "content": "Updated content",
      "description": null,
      "collection_id": null,
      "created_at": "2023-10-01T12:00:00",
      "updated_at": "2023-10-01T12:05:00"
  }
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Prompt not found"
  }
  ```

  **Error Response (400 Bad Request):**
  ```json
  {
      "detail": "Collection not found"
  }
  ```

---

#### Partially Update Prompt

- **PATCH** `/prompts/{prompt_id}`
  - Partially update an existing prompt.
  - Updates only the supplied fields. Omitted fields keep their existing values.
  - The `id` and `created_at` values are preserved, and `updated_at` is refreshed.

  **Curl Example:**
  ```bash
  curl -i -X PATCH "http://localhost:8000/prompts/PROMPT_ID" -H "Content-Type: application/json" -d '{"title": "Partially Updated Title"}'
  ```

  **Success Response (200 OK):**
  ```json
  {
      "id": "PROMPT_ID",
      "title": "Partially Updated Title",
      "content": "Original content",
      "description": "A brief description.",
      "collection_id": null,
      "created_at": "2023-10-01T12:00:00",
      "updated_at": "2023-10-01T12:10:00"
  }
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Prompt not found"
  }
  ```

  **Error Response (400 Bad Request):**
  ```json
  {
      "detail": "Collection not found"
  }
  ```

---

#### Delete Prompt

- **DELETE** `/prompts/{prompt_id}`
  - Delete a prompt by its ID.

  **Curl Example:**
  ```bash
  curl -i -X DELETE "http://localhost:8000/prompts/PROMPT_ID"
  ```

  **Success Response (204 No Content):**
  ```plaintext
  HTTP/1.1 204 No Content
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Prompt not found"
  }
  ```

---

### Collection Endpoints

#### List Collections

- **GET** `/collections`
  - Retrieves all collections.
  
  **Curl Example:**
  ```bash
  curl -i "http://localhost:8000/collections"
  ```

  **Success Response (200 OK):**
  ```json
  {
      "collections": [],
      "total": 0
  }
  ```

---

#### Get Collection

- **GET** `/collections/{collection_id}`
  - Retrieves a collection by its ID.
  
  **Curl Example:**
  ```bash
  curl -i "http://localhost:8000/collections/COLLECTION_ID"
  ```

  **Success Response (200 OK):**
  ```json
  {
      "id": "COLLECTION_ID",
      "name": "My Collection",
      "description": "Description of the collection.",
      "created_at": "2023-10-01T12:00:00"
  }
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Collection not found"
  }
  ```

---

#### Create Collection

- **POST** `/collections`
  - Create a new collection.

  **Curl Example:**
  ```bash
  curl -i -X POST "http://localhost:8000/collections" -H "Content-Type: application/json" -d '{"name": "New Collection", "description": "Description"}'
  ```

  **Success Response (201 Created):**
  ```json
  {
      "id": "NEW_COLLECTION_ID",
      "name": "New Collection",
      "description": "Description",
      "created_at": "2023-10-01T12:00:00"
  }
  ```

---

#### Delete Collection

- **DELETE** `/collections/{collection_id}`
  - Delete a collection if it has no associated prompts.

  **Curl Example:**
  ```bash
  curl -i -X DELETE "http://localhost:8000/collections/COLLECTION_ID"
  ```

  **Success Response (204 No Content):**
  ```plaintext
  HTTP/1.1 204 No Content
  ```

  **Error Response (404 Not Found):**
  ```json
  {
      "detail": "Collection not found"
  }
  ```

  **Error Response (400 Bad Request):**
  ```json
  {
      "detail": "Cannot delete collection with associated prompts"
  }
  ```