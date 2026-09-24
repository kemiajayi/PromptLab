# PromptLab System Model

## System Overview

PromptLab is a FastAPI application for storing, organizing, and managing prompts.

The backend is divided into a small number of components:

- `backend/main.py` starts the application with Uvicorn.
- `backend/app/api.py` creates the FastAPI application and defines the HTTP routes.
- `backend/app/models.py` defines the Pydantic models used for requests and responses.
- `backend/app/storage.py` provides in-memory storage for prompts and collections.
- `backend/app/utils.py` contains helper functions used for filtering, searching, and sorting prompts.
- `backend/tests/` contains the API test suite.

At a high level, requests move through the system as follows:

HTTP request
→ FastAPI route in `api.py`
→ Pydantic request model and validation
→ storage and/or utility functions
→ Pydantic response model
→ HTTP response

## Application Entry Point

`backend/main.py` is the application entry point.

It imports the FastAPI application and uses Uvicorn to run it on port 8000.

The API application itself is created in `backend/app/api.py`.

## API Routes

The current application exposes the following routes.

| Method | Path | Handler | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | `health_check()` | Returns application health and version information |
| GET | `/prompts` | `list_prompts()` | Returns stored prompts, with optional collection filtering and search |
| GET | `/prompts/{prompt_id}` | `get_prompt()` | Retrieves one prompt by ID |
| POST | `/prompts` | `create_prompt()` | Creates a new prompt |
| PUT | `/prompts/{prompt_id}` | `update_prompt()` | Replaces an existing prompt |
| PATCH | `/prompts/{prompt_id}` | `update_prompt_partial()` | Partially updates only the prompt fields provided in the request |
| DELETE | `/prompts/{prompt_id}` | `delete_prompt()` | Deletes a prompt |
| GET | `/collections` | `list_collections()` | Returns all collections |
| GET | `/collections/{collection_id}` | `get_collection()` | Retrieves one collection by ID |
| POST | `/collections` | `create_collection()` | Creates a collection |
| DELETE | `/collections/{collection_id}` | `delete_collection()` | Deletes a collection |

These routes are defined directly in `backend/app/api.py`.

## Request and Data Flow

A request first reaches a FastAPI route in `api.py`.

FastAPI uses the type annotations and Pydantic models on the route to validate incoming data. The route then performs any required application logic and calls the storage layer when data must be retrieved or changed.

For example, creating a prompt follows this flow:

1. A client sends `POST /prompts`.
2. FastAPI passes the validated request body to `create_prompt()` as a `PromptCreate` object.
3. If the request includes a `collection_id`, the route calls `storage.get_collection()` to confirm that the collection exists.
4. The route converts the validated request data into a `Prompt` object.
5. The route calls `storage.create_prompt(prompt)`.
6. The storage layer saves the prompt in its `_prompts` dictionary.
7. `storage.create_prompt()` returns the stored `Prompt`.
8. FastAPI serializes the `Prompt` into the HTTP response.

The collection validation and creation logic are visible in `create_prompt()`.

The storage method places the prompt in `_prompts` using `prompt.id` as the dictionary key and returns the same object.

Other routes follow the same general pattern:

request
→ route handler
→ validation and application logic
→ storage or utility operation
→ response model
→ HTTP response

The prompt-listing route also uses functions from `utils.py` to filter by collection, search prompts, and sort results before returning a `PromptList`.

For partial prompt updates, `PATCH /prompts/{prompt_id}` uses `PromptUpdatePartial` to validate the request. The route retrieves the existing prompt, returns 404 if it does not exist, applies only the fields supplied in the request, validates a provided collection ID when necessary, updates
`updated_at`, and saves the resulting `Prompt` through `storage.update_prompt()`.

## Models and Relationships

PromptLab has two main domain objects:

- prompts
- collections

The prompt models inherit through `PromptBase`, which inherits from Pydantic's `BaseModel`.

`PromptCreate`, `PromptUpdate`, and `Prompt` inherit from `PromptBase`.
Collections use a similar model hierarchy through `CollectionBase`.
`PromptUpdatePartial` is a separate Pydantic request model used by `PATCH /prompts/{prompt_id}`. Its fields are optional so PATCH requests can update only the fields that were supplied without changing the full-update requirements used by PUT.

A prompt can contain an optional `collection_id`.

This creates the logical relationship between prompts and collections.

The relationship is:

Collection
→ zero or many Prompts

Prompt
→ zero or one Collection

A prompt can exist without belonging to a collection because `collection_id` is optional.

A prompt has only one `collection_id`, so it cannot reference multiple collections at the same time.

Multiple prompts can contain the same `collection_id`, which allows a collection to contain multiple prompts.

The collection itself does not maintain a list of prompt IDs. Instead, the relationship is stored on each prompt.

## Storage Layer

PromptLab uses an in-memory `Storage` class defined in `backend/app/storage.py`.

The class maintains two dictionaries:

- `_prompts: Dict[str, Prompt]`
- `_collections: Dict[str, Collection]`

Each object is stored using its ID as the dictionary key.

### Prompt Operations

The storage layer supports:

- `create_prompt()` to store a prompt
- `get_prompt()` to retrieve one prompt
- `get_all_prompts()` to retrieve all prompts
- `update_prompt()` to replace an existing prompt
- `delete_prompt()` to remove a prompt

`update_prompt()` first checks whether the ID exists. If it does, the stored value is replaced with the supplied `Prompt`.

`delete_prompt()` removes the dictionary entry and returns whether deletion succeeded.

### Collection Operations

The storage layer supports:

- `create_collection()`
- `get_collection()`
- `get_all_collections()`
- `delete_collection()`
- `get_prompts_by_collection()`

There is no `update_collection()` method in the current storage implementation.

`get_prompts_by_collection()` does not use a separate relationship table or collection-owned list of prompts. The `delete_collection()` API route uses this method to detect associated prompts and prevents collection deletion when references still exist.

Instead, it searches the values in `_prompts` and returns prompts whose `collection_id` matches the requested collection ID.

### Storage Limitations

The storage layer is intentionally in-memory. The module itself states that a production environment would replace it with a database.

Important limitations include:

- Data is lost when the application process stops or restarts.
- There is no database-backed persistence.
- Referential integrity between prompts and collections is not automatically enforced by the storage layer.
- The storage layer does not automatically enforce referential integrity between prompts and collections. The API prevents deletion of a collection while prompts still reference it.
- Query behavior such as searching, filtering, and sorting is implemented in application code instead of a database query system.

The storage class also has a `clear()` method that removes all prompts and collections.

## External Dependencies

The backend dependencies are defined in `backend/requirements.txt`.

### FastAPI 0.109.0

FastAPI provides the web application framework.

PromptLab uses it to:

- create the API application
- define HTTP routes
- validate and serialize requests and responses with Pydantic models
- raise HTTP errors
- configure CORS middleware

The application and CORS middleware are configured in `api.py`.

### Uvicorn 0.27.0

Uvicorn is the ASGI server used to run the FastAPI application.

`backend/main.py` imports Uvicorn and runs the application on port 8000.

### Pydantic 2.5.3

Pydantic provides PromptLab's data-model and validation system.

Prompt and collection models ultimately inherit from Pydantic's `BaseModel`.

Methods such as `model_dump()` also come from Pydantic rather than being defined by PromptLab.

### pytest 7.4.4

pytest is used for the automated test suite.

It is used in `backend/tests/conftest.py` for fixtures and in `backend/tests/test_api.py` for API tests.

### pytest-cov 4.1.0

pytest-cov is installed as a pytest coverage plugin.

I did not find a documented `--cov` command in the repository areas I searched, so I cannot conclude that coverage reporting is currently part of the project's normal test command.

### HTTPX 0.26.0

HTTPX is installed as a dependency.

The repository does not directly import `httpx`. The tests use FastAPI's `TestClient`.

I found no evidence that the PromptLab application itself sends HTTP requests to external services, so HTTPX should not be described as an external-service integration based on the current source.

## AI Context Strategy

I began the exploration by providing the entire PromptLab repository to the AI.

Whole-repository context was appropriate initially because the codebase was unfamiliar and relatively small. I did not yet know which files controlled routing, models, storage, or request flow.

The first response gave me a high-level system overview but did not explain the implementation in enough detail. I then narrowed my prompts to specific questions, including:

- tracing the create-prompt request flow
- determining where `model_dump()` comes from
- understanding the relationship between prompts and collections
- identifying every API route
- understanding the storage layer
- identifying external dependencies

I used source-level verification after the AI responses rather than assuming they were correct. For example, when the AI stopped its create-prompt trace at `storage.create_prompt()`, I inspected `storage.py` to determine exactly how the prompt was stored.

When the AI described the model inheritance imprecisely, I inspected the class definitions in `models.py` and verified that `PromptCreate`, `PromptUpdate`, and `Prompt` inherit from `PromptBase`, while `PromptBase` inherits from Pydantic's `BaseModel`.

I also searched the repository to verify how dependencies such as Uvicorn, pytest, pytest-cov, and HTTPX were actually used.