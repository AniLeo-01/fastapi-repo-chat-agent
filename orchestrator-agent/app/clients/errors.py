class AgentCallError(Exception):
    def __init__(self, agent: str, message: str):
        self.agent = agent
        self.message = message
        super().__init__(f"[{agent}] {message}")
