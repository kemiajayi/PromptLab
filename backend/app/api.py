"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate, PromptUpdatePartial,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None
):
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)
    
    # Sort by date (newest first)
    # Note: There might be an issue with the sorting...
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):

    """Retrieve a prompt by its unique identifier.

    Args:
        prompt_id: The unique identifier of the prompt to retrieve.

    Returns:
        The requested Prompt object.

    Raises:
        HTTPException: If the prompt does not exist.
    """

    prompt = storage.get_prompt(prompt_id)
    if prompt is None:  # Check for None before accessing attributes
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

    
@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):

    """Replace the editable fields of an existing prompt.

    Args:
        prompt_id: The unique identifier of the prompt to update.
        prompt_data: The new prompt data.

    Returns:
        The updated Prompt object.

    Raises:
        HTTPException: If the prompt does not exist.
        HTTPException: If a provided collection_id does not reference an
            existing collection.
    """
        
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()  # Set to the current time
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt_partial(prompt_id: str, prompt_data: PromptUpdatePartial):
    """Partially update an existing prompt. Only fields provided in the request are updated. If a field is not provided in the
    request, it will keep its existing value. The updated_at timestamp is set to the current time.
    
    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        prompt_data (PromptUpdatePartial): The fields to update in the prompt.

    Returns:
        The updated Prompt object.

    Raises:
        HTTPException: If the prompt does not exist.
        HTTPException: If a provided collection_id does not reference an existing collection.
    """
    existing_prompt = storage.get_prompt(prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Update fields based on what is provided
    updated_prompt_data = existing_prompt.model_copy(update=prompt_data.model_dump(exclude_unset=True))

    if prompt_data.collection_id is not None:
        # Validate collection if provided
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    updated_prompt_data.updated_at = get_current_time()  # Update the timestamp

    # Save the prompt using existing storage method
    storage.update_prompt(prompt_id, updated_prompt_data)

    return updated_prompt_data


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection if it has no associated prompts.

    Args:
        collection_id (str): The unique identifier of the collection to delete.

    Returns:
        None.

    Raises:
        HTTPException: If the collection does not exist.
        HTTPException: If prompts are still associated with the collection.
    """
    # Check if the collection exists
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check if there are associated prompts
    if storage.get_prompts_by_collection(collection_id):
        raise HTTPException(status_code=400, detail="Cannot delete collection with associated prompts")

    # Proceed to delete the collection
    storage.delete_collection(collection_id)
    return None

