from dependency_injector import containers, providers
import redis
from .services.redis_service import RedisService
from .services.note_service import NoteService
from .data.note_repository import NoteRepository
from .data.database import Database

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_client = providers.Singleton(
        redis.Redis,
        host=config.redis_host,
        port=config.redis_port,
        decode_responses=True
    )
    redis_service = providers.Factory(RedisService, redis_client=redis_client)

    database = providers.Singleton(Database, db_url=config.database_url)
    note_repository = providers.Factory(
        NoteRepository,
        session_factory=database.provided.session
    )

    note_service = providers.Factory(
        NoteService,
        note_repository=note_repository,
        redis_service=redis_service
    )