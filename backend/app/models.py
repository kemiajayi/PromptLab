"""Pydantic models for PromptLab"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique identifier as a string.

    Returns:
        A UUID version 4 formatted as a string.

    Example:
        >>> unique_id = generate_id()
        >>> isinstance(unique_id, str)
        True
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Get the current UTC datetime without timezone information.

    Returns:
        datetime: The current UTC datetime.

    Example:
        >>> current_time = get_current_time()
        >>> current_time.tzinfo is None
        True
    """
    return datetime.utcnow()


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    """Base model for representing a prompt.

    Attributes:
        title (str): The title of the prompt, must be between 1 and 200 characters.
        content (str): The content of the prompt, must have at least one character.
        description (Optional[str]): A description of the prompt, default is None and must not exceed 500 characters.
        collection_id (Optional[str]): The ID of the collection to which the prompt belongs, default is None.

    Example:
        >>> prompt = PromptBase(title="Sample Prompt", content="This is a prompt content.")
        >>> prompt.title
        'Sample Prompt'
    """
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class PromptCreate(PromptBase):
    """Model for creating a new prompt, inheriting from PromptBase.

    Example:
        >>> new_prompt = PromptCreate(title="New Prompt", content="This is a new prompt.")
        >>> new_prompt.title
        'New Prompt'
    """
    pass


class PromptUpdate(PromptBase):
    """Model for updating an existing prompt, inheriting from PromptBase.

    Example:
        >>> update_prompt = PromptUpdate(title="Updated Prompt", content="Updated content")
        >>> update_prompt.title
        'Updated Prompt'
    """
    pass


class PromptUpdatePartial(BaseModel):
    """Fields that may be provided when partially updating a prompt. All fields default to None. Length constraints apply only to non-null strings.
    
    Attributes:
        title (Optional[str]): The title of the prompt, optional and must be between 1 and 200 characters when non-null.
        content (Optional[str]): The content of the prompt, optional and must have at least one character when non-null.
        description (Optional[str]): A description of the prompt, optional and must not exceed 500 characters when non-null.
        collection_id (Optional[str]): The ID of the collection to which the prompt belongs, default is None.

    Example:
        >>> prompt_update = PromptUpdatePartial(title="Updated Title", content="Updated content")
        >>> prompt_update.title
        'Updated Title'
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class Prompt(PromptBase):
    """Model for representing a prompt with additional attributes.

    Attributes:
        id (str): The unique identifier for the prompt, auto-generated if omitted.
        created_at (datetime): The timestamp when the prompt was created, auto-generated if omitted.
        updated_at (datetime): The timestamp when the prompt was last updated, auto-generated if omitted.

    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Configure validation from object attributes.

        Attributes:
            from_attributes (bool): Allow model validation using
                attributes from an object.
        """
        from_attributes = True


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """Base model for representing a collection.

    Attributes:
        name (str): The name of the collection, must be between 1 and 100 characters.
        description (Optional[str]): A description of the collection, default is None and must not exceed 500 characters.

    Example:
        >>> collection = CollectionBase(name="My Collection", description="A brief overview")
        >>> collection.name
        'My Collection'
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Model for creating a new collection, inheriting from CollectionBase.

    Example:
        >>> new_collection = CollectionCreate(name="New Collection")
        >>> new_collection.name
        'New Collection'
    """
    pass


class Collection(CollectionBase):
    """Complete model for a collection with additional attributes.

    Attributes:
        id (str): The unique identifier for the collection, auto-generated if omitted.
        created_at (datetime): The timestamp when the collection was created, auto-generated if omitted.

    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Configure validation from object attributes.

        Attributes:
            from_attributes (bool): Allow model validation using
                attributes from an object.
        """
        from_attributes = True


# ============== Response Models ==============

class PromptList(BaseModel):
    """Model for representing a list of prompts.

    Attributes:
        prompts (List[Prompt]): A list of prompt objects.
        total (int): Number of items returned in this response, supplied by the API.

    """
    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Model for representing a list of collections.

    Attributes:
        collections (List[Collection]): A list of collection objects.
        total (int): Number of items returned in this response, supplied by the API.

    """
    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Model for representing health check response.

    Attributes:
        status (str): The status of the service (e.g., "healthy", "unhealthy").
        version (str): The version of the service.

    Example:
        >>> health_response = HealthResponse(status="healthy", version="0.1.0")
        >>> health_response.status
        'healthy'
        >>> health_response.version
        '0.1.0'
    """
    status: str
    version: str

