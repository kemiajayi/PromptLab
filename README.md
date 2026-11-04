# PromptLab

**Your AI Prompt Engineering Platform**

---

## Project Overview and Purpose
PromptLab is a FastAPI backend designed for storing and organizing prompt text. It currently uses in-memory storage.

### Features

Implemented Features:

- Prompt Management: Create, retrieve, fully replace (PUT), partially update (PATCH), and delete prompts.
- Collection Management: Create, list, retrieve, and delete collections, with enforced restrictions on deletion when prompts reference the collection.
- Prompt Filtering: Filter prompts by collection ID.
- Search Functionality: Perform case-insensitive substring search in prompt titles and descriptions.
- Sorting: List prompts in descending order by creation time.
- Health Status Reporting: Check API health and retrieve application version.

Planned Features:

- Prompt version history.
- A tagging system for improved prompt organization.
- A frontend interface for enhanced user experience.

---

## Prerequisites

- Python 3.12 is recommended for the current backend dependencies
- Node.js 18+ is anticipated for future enhancements (not yet required).
- Git is required for version control and repository management.

## Installation

```bash
# Clone the repository
git clone https://github.com/kemiajayi/PromptLab.git
cd PromptLab

# Create a virtual environment
py -3.12 -m venv .venv

# Activate the virtual environment in Git Bash
source .venv/Scripts/activate

# Set up the backend
cd backend
python -m pip install -r requirements.txt

```
## Quick Start

```bash
# Start the API
python main.py

API will run at: http://localhost:8000

# Access the API documentation 
Navigate to http://localhost:8000/docs for interactive API documentation
```
## Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Project Structure

```
promptlab/
├── README.md                    # You are here
├── .continuerules               # Project rules for the Continue AI assistant
│
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Package marker and app version (__version__)
│   │   ├── api.py               # FastAPI routes
│   │   ├── models.py            # Pydantic models
│   │   ├── storage.py           # In-memory storage
│   │   └── utils.py             # Helper functions
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py          # API tests
│   │   └── conftest.py          # Test fixtures
│   ├── main.py                  # Entry point
│   └── requirements.txt
│
├── docs/
│   ├── API_REFERENCE.md         # Endpoint reference with curl examples and responses
│   ├── SYSTEM_MODEL.md          # Architecture and request flow
│   ├── agent-effect-note.md     # Before-and-after evidence for .continuerules
│   ├── ai-verification-note.md  # AI verification evidence
│   └── prompt-log.md            # Log of AI prompts used
│
├── specs/
│   ├── prompt-versions.md       # Feature spec: prompt version history
│   └── tagging-system.md        # Feature spec: prompt tags
│
├── frontend/                    # Will be created in Week 4
└── .github/                     # Not created yet. Will set up CI/CD in Week 3
```

---

## API Endpoint Summary

| Method | Endpoint               | Description                                                        | Request Body           | Query Parameters            | Response Model        |
|--------|------------------------|------------------------------------------------------------------|--------------------------|-----------------------------|-----------------------|
| GET    | `/health`              | Health check for the API                                         | None                     | None                        | HealthResponse        |
| GET    | `/prompts`             | List all prompts or filter by collection and search              | None                     | `collection_id`, `search`   | PromptList            |
| GET    | `/prompts/{id}`        | Retrieve a prompt by its unique identifier                       | None                     | None                        | Prompt                |
| POST   | `/prompts`             | Create a new prompt                                              | `PromptCreate`           | None                        | Prompt                |
| PUT    | `/prompts/{id}`        | Replace an existing prompt                                       | `PromptUpdate`           | None                        | Prompt                |
| PATCH  | `/prompts/{id}`        | Partially update an existing prompt                              | `PromptUpdatePartial`    | None                        | Prompt                |
| DELETE | `/prompts/{id}`        | Delete a prompt by its unique identifier                         | None                     | None                        | None                  |
| GET    | `/collections`         | List all collections                                             | None                     | None                        | CollectionList        |
| GET    | `/collections/{id}`    | Retrieve a collection by its unique identifier                   | None                     | None                        | Collection            |
| POST   | `/collections`         | Create a new collection                                          | `CollectionCreate`       | None                        | Collection            |
| DELETE | `/collections/{id}`    | Delete a collection if no prompts are associated with it         | None                     | None                        | None                  |

### Useful curl Examples

1. **Check API Health:**
   ```bash
   curl -X GET http://localhost:8000/health
   ```

2. **List All Prompts:**
   ```bash
   curl -X GET http://localhost:8000/prompts
   ```

3. **Filter Prompts by Collection:**
   ```bash
   curl -X GET "http://localhost:8000/prompts?collection_id=<collection_id>"
   ```

4. **Search Prompts:**
   ```bash
   curl -X GET "http://localhost:8000/prompts?search=<search_query>"
   ```

5. **Retrieve a Specific Prompt:**
   ```bash
   curl -X GET http://localhost:8000/prompts/<prompt_id>
   ```

6. **Create a new prompt:**
   ```bash
   curl -i -X POST "http://localhost:8000/prompts" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Example Prompt",
       "content": "This is an example of prompt content.",
       "description": "An example description."
     }'
   ```

7. **Partially update an existing prompt:**

   ```bash
   curl -i -X PATCH "http://localhost:8000/prompts/$PROMPT_ID" \
     -H "Content-Type: application/json" \
     -d '{"title":"Updated Example Prompt"}'
   ```

8. **Delete a Prompt:**
   ```bash
   curl -X DELETE http://localhost:8000/prompts/<prompt_id>
   ```

9. **Create a New Collection:**
   ```bash
   curl -X POST http://localhost:8000/collections \
   -H "Content-Type: application/json" \
   -d '{
       "name": "New Collection",
       "description": "Description of the new collection."
   }'
   ```

10. **Delete a Collection:**
   ```bash
   curl -X DELETE http://localhost:8000/collections/<collection_id>
   ```

---

## Development Setup

For the setup and initial installation, please refer to the **Installation** and **Quick Start** sections above to get the backend running.

To run tests after the setup:

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Execute the test suite using pytest:
   ```bash
   python -m pytest tests/ -v
   ```
   This will run the tests defined in `test_api.py`. The `conftest.py` file contains shared test fixtures that can be utilized across your tests, helping to set up necessary contexts and dependencies.

## Contributing Guidelines

Thank you for considering contributing to the PromptLab project! To ensure a smooth collaboration, please adhere to the following guidelines specific to this repository:

1. **Fork the Repository:** Create a fork of this repository to implement your changes.

2. **Create a Feature Branch:** Develop your changes in a separate branch. Use descriptive names for your branches that indicate the feature or bug addressed:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes:** Implement your changes in your branch, and ensure that your code is clean and follows the project's coding conventions.

4. **Run All Tests:** Before submitting a pull request, ensure that all tests are passing:
   ```bash
   python -m pytest tests/ -v
   ```

5. **Submit a Pull Request:** When ready, submit a pull request to the main repository with a clear explanation of the changes made and mention any relevant issues.

6. **Respect Project Guidelines:** Please maintain a respectful and collaborative environment in all discussions and contributions. Keep communication constructive and focused on the project’s goals. 

By following these guidelines, you can help maintain the project's quality and promote a positive developer experience. Thank you for your contributions!

