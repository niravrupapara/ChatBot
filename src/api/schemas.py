from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", example="ok")
    app_name: str = Field(default="LangGraph Chatbot API", example="LangGraph Chatbot API")


class ChatRequest(BaseModel):
    message: str = Field(..., example="Hello! What can you help me with?", description="User input prompt")
    session_id: str | None = Field(
        default=None,
        example="78cebe3e-2335-42d2-ab3a-06492dd0a3f6",
        description="Session UUID. If omitted, a new session ID will be generated.",
    )


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="Active session UUID")
    response: str = Field(..., description="Assistant response content")
    tools_used: list[str] = Field(default_factory=list, description="List of tools invoked during response generation")
