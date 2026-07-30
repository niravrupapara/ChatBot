from fastapi import APIRouter, HTTPException
from src.api.schemas import HealthResponse, ChatRequest, ChatResponse

from src.graph.builder import build_graph
from src.services.session_service import generate_session_id
from src.utils.logger import get_logger
from src.utils.runtime_config import reset_tool_calls, get_tool_calls

logger = get_logger(__name__)


router = APIRouter()

graph = build_graph()

@router.get("/health", response_model=HealthResponse, summary="API Health check")
def health_check() -> HealthResponse:
    logger.info("Health check endpoint invoked")
    return HealthResponse()

@router.post("/api/v1/chat", response_model=ChatResponse, summary="Send chat prompt to agent")
def chat_endpoint(request: ChatRequest) -> ChatResponse:

    try:
        session_id = request.session_id or generate_session_id()
        logger.info(f"API chat request received | session_id={session_id}")

        thread_config = {"configurable": {"thread_id":session_id}}

        reset_tool_calls()
        result = graph.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=thread_config
        )
        tool_used = get_tool_calls()

        reply = result["messages"][-1].content if result and "messages" in result else ""

        logger.info(f"API char response generated for session: {session_id}")

        return ChatResponse(
                            session_id=session_id,
                            response=reply,
                            tools_used=tool_used
                            )

    except Exception as e:
        logger.error(f"Error in chat_endpoint for session {request.session_id} : {e} ", exc_info=True)

        raise HTTPException(status_code=500,
                            detail=f"Failed to process chat request: {str(e)}")
