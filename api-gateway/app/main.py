from fastapi import FastAPI
from app.routers import chat, index, agents, graph

app = FastAPI(title="FastAPI Repo Chat Gateway")

app.include_router(chat.router)
app.include_router(index.router)
app.include_router(agents.router)
app.include_router(graph.router)
