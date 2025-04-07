from prefect import flow

# Source for the code to deploy (here, a GitHub repo)
SOURCE_REPO = "https://github.com/chocolib-com/Data-crawler.git"

if __name__ == "__main__":
    flow.from_source(
        source=SOURCE_REPO,
        entrypoint="read_feed.py:rss_ingestion_flow",
    ).deploy(
        name="read-feed-deployment",
        work_pool_name="process-work-pool",
        cron="0/10 * * * *",  # Run every 10 minutes
    )
