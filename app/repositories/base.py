from __future__ import annotations

from typing import Generic, TypeVar

from beanie import Document, PydanticObjectId

DocType = TypeVar("DocType", bound=Document)


class BaseRepository(Generic[DocType]):
    def __init__(self, model: type[DocType]) -> None:
        self.model = model

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[DocType]:
        return await self.model.find_all().skip(skip).limit(limit).to_list()

    async def count(self) -> int:
        return await self.model.count()

    async def get_by_id(self, doc_id: PydanticObjectId | str) -> DocType | None:
        if isinstance(doc_id, str):
            try:
                doc_id = PydanticObjectId(doc_id)
            except Exception:
                return None
        return await self.model.get(doc_id)

    async def create(self, doc: DocType) -> DocType:
        await doc.insert()
        return doc

    async def save(self, doc: DocType) -> DocType:
        await doc.save()
        return doc

    async def delete(self, doc: DocType) -> None:
        await doc.delete()
