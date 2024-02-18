from .meta import DbModelMeta
from pydantic import BaseModel


class DbModelCore(BaseModel, metaclass=DbModelMeta):
    ...
