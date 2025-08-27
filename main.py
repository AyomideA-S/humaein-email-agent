#!/usr/bin/env python3
"""Script to test either email agent."""
import logging
from agent import GmailAgent  # noqa: F401
from agent import OutlookAgent

logging.basicConfig(
    level=logging.INFO,
    filename="logs/test.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

try:
    agent = OutlookAgent()
    logging.info("Starting Outlook email send test")
    agent.send("test@example.com", "Test", "Hello World")
    logging.info("Test completed successfully")
except Exception as e:
    logging.error(f"Test failed: {e}")
