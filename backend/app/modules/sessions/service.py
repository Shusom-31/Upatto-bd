from app.core.security import new_credential
from app.infrastructure.dataset_store import store


def create_session(display_name: str):
    return store.create(display_name, new_credential())
