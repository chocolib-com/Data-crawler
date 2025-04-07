from prefect import flow, task, get_run_logger
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from model import Feed, FeedEntry
import feedparser
from datetime import datetime
import time
from prefect.blocks.system import Secret

secret_block = Secret.load("pg")


# Database config
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://chocolib:{secret_block.get()}@localhost/chocolib"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)


@task
def get_all_feeds() -> list[Feed]:
    logger = get_run_logger()
    logger.info("Fetching all feeds from database...")
    with Session(engine) as session:
        feeds = session.scalars(select(Feed)).all()
        logger.info(f"Retrieved {len(feeds)} feeds.")
        return feeds


@task
def parse_feed(feed: Feed) -> list[dict]:
    logger = get_run_logger()
    logger.info(f"Parsing feed from URL: {feed.url}")
    parsed = feedparser.parse(feed.url)
    entries = [
        entry
        for entry in parsed.entries
        if hasattr(entry, "title") and hasattr(entry, "guid")
    ]
    logger.info(f"Found {len(entries)} entries in feed: {feed.url}")
    return entries


@task
def store_feed_entries(feed_id: int, entries: list[dict]):
    logger = get_run_logger()
    logger.info(f"Storing {len(entries)} entries for feed ID {feed_id}...")
    with Session(engine) as session:
        for entry in entries:
            feed_entry_id_value = entry.get("guid")
            if feed_entry_id_value:
                existing_entry = (
                    session.query(FeedEntry)
                    .filter(FeedEntry.feed_entry_id == feed_entry_id_value)
                    .first()
                )
                if existing_entry:
                    continue

                feed_entry = FeedEntry(
                    feed_id=feed_id,
                    feed_entry_id=entry.guid,
                    title=entry.title,
                    publication_date=datetime.fromtimestamp(
                        time.mktime(entry.get("published_parsed"))
                    ),
                    raw=entry,
                )
                session.add(feed_entry)
        session.commit()
    logger.info(f"Stored entries for feed ID {feed_id}")


@flow
def rss_ingestion_flow():
    logger = get_run_logger()
    logger.info("Starting RSS ingestion flow.")
    feeds = get_all_feeds()
    for feed in feeds:
        entries = parse_feed(feed)
        store_feed_entries(feed.id, entries)
    logger.info("RSS ingestion flow completed.")


if __name__ == "__main__":
    rss_ingestion_flow()
