from typing import Dict, Any, List
from datetime import datetime

from app.memory.models import (
    ConversationTurn,
    AgentInvocation,
    RoutingDecision,
    UserContext,
)

class ConversationStore:
    """
    Central conversation memory store.
    Can be replaced by Redis / DB without touching orchestrator logic.
    """

    def __init__(self):
        self._history: Dict[str, List[ConversationTurn]] = {}
        self._agent_cache: Dict[str, Dict[str, AgentInvocation]] = {}
        self._routing: Dict[str, List[RoutingDecision]] = {}
        self._user_context: Dict[str, UserContext] = {}

    # 1) Conversation history
    def add_turn(self, session_id: str, query: str, response: Any):
        self._history.setdefault(session_id, []).append(
            ConversationTurn(
                timestamp=datetime.utcnow(),
                query=query,
                response=response,
            )
        )

    def get_history(self, session_id: str) -> List[ConversationTurn]:
        return self._history.get(session_id, [])

    # 2) Agent response cache
    def cache_agent_response(
        self,
        session_id: str,
        agent_name: str,
        agent_input: Dict[str, Any],
        agent_output: Dict[str, Any],
    ):
        self._agent_cache.setdefault(session_id, {})[agent_name] = AgentInvocation(
            agent_name=agent_name,
            input=agent_input,
            output=agent_output,
        )

    def get_cached_agent_response(
        self, session_id: str, agent_name: str
    ) -> AgentInvocation | None:
        return self._agent_cache.get(session_id, {}).get(agent_name)

    # 3) Routing decisions
    def add_routing_decision(self, session_id: str, decision: RoutingDecision):
        self._routing.setdefault(session_id, []).append(decision)

    def get_routing_history(self, session_id: str) -> List[RoutingDecision]:
        return self._routing.get(session_id, [])

    # 4) User context
    def set_user_context(self, session_id: str, context: UserContext):
        self._user_context[session_id] = context

    def get_user_context(self, session_id: str) -> UserContext:
        return self._user_context.get(session_id, UserContext())
