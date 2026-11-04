"""In-memory storage for PromptLab

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection


class Storage:
    """Class to perform storage operations for prompts and collections.

    This class maintains an in-memory dictionary for prompts and collections.
    It allows for CRUD operations on prompts and support creation, retrieval, and deletion on collections.
    """

    def __init__(self):
        """Initialize the Storage class.

        This constructor initializes empty dictionaries for prompts and collections.
        """
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
    
    # ============== Prompt Operations ==============
    
    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Create a new prompt in storage. If the ID already exists, the stored object is replaced.

        Args:
            prompt (Prompt): The prompt object to be stored.

        Returns:
            Prompt: The stored prompt object.
        """
        self._prompts[prompt.id] = prompt
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieve a prompt by its ID.

        Args:
            prompt_id (str): The unique identifier of the prompt.

        Returns:
            Optional[Prompt]: The prompt object if found, otherwise None.
        """
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[Prompt]:
        """Retrieve all prompts in storage.

        Returns:
            List[Prompt]: A list of all stored prompt objects.
        """
        return list(self._prompts.values())
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Update an existing prompt in storage.

        Args:
            prompt_id (str): The unique identifier for the prompt to update.
            prompt (Prompt): The updated prompt object.

        Returns:
            Optional[Prompt]: The updated prompt object if found and updated, otherwise None.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt from storage by its ID.

        Args:
            prompt_id (str): The unique identifier of the prompt to delete.

        Returns:
            bool: True if the prompt was deleted, otherwise False.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False
    
    # ============== Collection Operations ==============
    
    def create_collection(self, collection: Collection) -> Collection:
        """Create a new collection in storage. If the ID already exists, the stored object is replaced.

        Args:
            collection (Collection): The collection object to be stored.

        Returns:
            Collection: The stored collection object.
        """
        self._collections[collection.id] = collection
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its ID.

        Args:
            collection_id (str): The unique identifier of the collection.

        Returns:
            Optional[Collection]: The collection object if found, otherwise None.
        """
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> List[Collection]:
        """Retrieve all collections in storage.

        Returns:
            List[Collection]: A list of all stored collection objects.
        """
        return list(self._collections.values())
    
    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection from storage by its ID. This method does not check for associated prompts. The API endpoint performs that check.

        Args:
            collection_id (str): The unique identifier of the collection to delete.

        Returns:
            bool: True if the collection was deleted, otherwise False.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False
    
    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Retrieve prompts belonging to a specific collection.

        Args:
            collection_id (str): The unique identifier of the collection.

        Returns:
            List[Prompt]: A list of prompts associated with the specified collection.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]
    
    # ============== Utility ==============
    
    def clear(self):
        """Clear all stored prompts and collections.

        This method empties the dictionaries for prompts and collections.

        Returns:
           None: All prompts and collections are removed from storage. 
        """
        self._prompts.clear()
        self._collections.clear()


# Global storage instance
storage = Storage()
