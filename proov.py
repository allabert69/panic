import logging
import os
import dotenv
dotenv.load_dotenv()
import watchtower
import boto3

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client(
    "logs",
    region_name='eu-north-1',
    aws_access_key_id=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
)

# Add Watchtower handler
handler = watchtower.CloudWatchLogHandler(
    log_group='panic',          # Your CloudWatch log group name
    stream_name='articles',       # Your log stream name
    create_log_group=False,
    boto3_client=s3,                   # Use the S3 client for authentication
)
logger.addHandler(handler)

# Log messages
logger.info("This is an info message")
logger.error("This is an error message")