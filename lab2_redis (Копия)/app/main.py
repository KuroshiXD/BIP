from fastapi import FastAPI
from dependency_injector.wiring import inject, Provide
from .containers import Container
from .controllers import note_controller, redis_controller

app = FastAPI()

container = Container()
container.config.redis_host.from_env("REDIS_HOST", "localhost")
container.config.redis_port.from_env("REDIS_PORT", 6379)
container.config.database_url.from_env("DATABASE_URL", "sqlite:///./notes.db")
container.wire(modules=[note_controller, redis_controller])

app.include_router(note_controller.router, prefix="/notes", tags=["notes"])
app.include_router(redis_controller.router, prefix="/redis", tags=["redis"])

@app.get("/")
def root():
    return {"message": "API is running"}