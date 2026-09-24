AI Verification Note
====================

While investigating the missing PATCH `/prompts/{id}` endpoint, I asked Continue whether the existing `PromptUpdate` model supported partial updates.

Continue said that `PromptUpdate` already supported partial updates and suggested using it for PATCH with `exclude_unset=True`.

I verified this against `models.py` and found that the answer was incorrect. `PromptUpdate` inherits from `PromptBase`, where `title` and `content` are defined with `Field(...)`. Both fields are therefore required. `PromptUpdate` does not override them. A PATCH request containing only one field would fail request validation because `content` would still be required.

I found the mistake by checking the actual model definitions instead of relying on the AI's description of them.

I then changed my next prompt to explicitly state that `PromptUpdate` had required fields and added constraints that PUT must remain a full update while PATCH must support genuinely partial input. The AI revised its recommendation and proposed a separate partial-update request model with optional fields.

This mistake is traceable to the PATCH endpoint entries in `docs/prompt-log.md`, particularly Iterations 2 through 5.