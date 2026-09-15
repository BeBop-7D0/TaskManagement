from uuid import uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

class Comment(BaseModel):
    comment_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Идентификатор сообщения"
    )
    author_id: str = Field(..., description="Идентификатор автора сообщения")
    content: str = Field(..., description="Текст комментария")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="Дата создания комментария"
    )
    is_edited: bool = Field(default=False, description="Был ли изменен комментарий")
    edited_at: datetime | None = Field(default=None, description="Дата последнего редактирования")

    @model_validator(mode="after")
    def check_non_empty_fields(self):
        if not self.author_id or not self.author_id.strip():
            raise ValueError("Author id can't be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Content can't be empty")

        return self


    def edit_content(self, new_content: str) -> None:
        if not new_content.strip():
            raise ValueError("Content can't be empty")

        self.content = new_content
        self.is_edited = True
        self.edited_at = datetime.now(tz=timezone.utc)


    @property
    def was_ever_edited(self) -> bool:
        return self.is_edited


if __name__ == "__main__":
    com1 = Comment(
        comment_id="1",
        author_id="test_author_id",
        content= "test content"
    )

    com2 = Comment(
        comment_id="2",
        author_id="test_author_id",
        content= "test content"
    )

    com3 = Comment(
        comment_id="3",
        author_id="test_author_id",
        content= "test content"
    )


    coms = [com1, com2, com3]


    for elem in (i for i, c in enumerate(coms)):
        print(elem)
    print()


    comment_to_remove = next((i for i, c in enumerate(coms) if c.comment_id == "3"), None)

    print(comment_to_remove)