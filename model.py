from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


class Base(DeclarativeBase):
    pass


class Feed(Base):
    __tablename__ = "feed"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True)
    domain_name = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    last_crawled_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    _created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class FeedEntry(Base):
    __tablename__ = "feed_entry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    feed_id: Mapped[int] = Column(Integer, ForeignKey("feed.id"))
    feed_entry_id = Column(Text, unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publication_date = Column(TIMESTAMP(timezone=True))
    raw = Column(JSON, nullable=False)
    _created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "feed_entry_id": self.feed_entry_id,
            "title": self.title,
            "author": self.author,
            "publication_date": self.publication_date.isoformat()
            if self.publication_date
            else None,
        }
