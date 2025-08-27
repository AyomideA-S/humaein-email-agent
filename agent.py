#!/usr/bin/env python3
"""Email sending agent for Gmail and Outlook."""
import argparse
import logging
import re

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Import playwright patch
from undetected_playwright import Tarnished

logging.basicConfig(
    level=logging.INFO,
    filename="logs/agent.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def mock_llm_parse(instruction: str) -> dict:
    """Parse instruction into to, subject, body.

    Args:
        instruction (str): The instruction string to parse.

    Raises:
        ValueError: If no recipient is found.

    Returns:
        dict: A dictionary containing the parsed email components.
    """
    # Extract recipient email
    to_match = re.search(r"to\s+([\w\.-]+@[\w\.-]+)", instruction)
    to = to_match.group(1) if to_match else None
    # Extract body
    if "saying" in instruction:
        body_part = instruction.split("saying ")[-1]
        body = body_part.strip("'\"")
    else:
        body = ""
    subject = "Automated Email"  # Default
    if not to:
        raise ValueError("No recipient found.")
    # Log the parsed email components
    logging.info(f"Parsed: to={to}, subject={subject}, body={body}")
    return {"to": to, "subject": subject, "body": body}


class BaseEmailAgent:
    """Base class for email agents that automate sending emails via
    a web-based interface using Playwright."""

    def __init__(self, url: str):
        """Initializes the BaseEmailAgent with the specified URL for the
        email service.

        Args:
            url (str): The URL of the email service's web interface.
        """
        self.url = url

    def send(self, to: str, subject: str, body: str) -> None:
        """Sends an email by launching a browser, navigating to the URL,
        composing the email, and waiting for user confirmation.

        Args:
            to (str): The recipient's email address.
            subject (str): The subject line of the email.
            body (str): The body content of the email.
        """
        with sync_playwright() as p:
            args = ["--disable-blink-features=AutomationControlled"]
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=args
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 720}
            )
            Tarnished.apply_stealth(context)  # Evade detection with stealth
            page = context.new_page()

            # Navigate and handle login/passkey prompts
            logging.info(f"Navigating to {self.url}")
            page.goto(self.url)
            try:
                # Wait for Gmail inbox or handle passkey prompt
                page.wait_for_url(
                    "https://mail.google.com/*", timeout=150000
                )  # 150s for login
            except PlaywrightTimeoutError:
                logging.warning(
                    "Inbox not reached; checking for passkey prompt"
                )
                # Check for passkey/security prompt and dismiss if present
                try:
                    page.click(
                        'button:has-text("Not now")', timeout=5000
                    )  # Dismiss passkey
                    page.wait_for_url(
                        "https://mail.google.com/mail/*",
                        timeout=30000
                    )
                except PlaywrightTimeoutError:
                    logging.error(
                        "Failed to reach inbox after passkey handling"
                    )
                    input("Press Enter to close...")
                    browser.close()
                    return

            logging.info("Reached Gmail inbox")
            try:
                self.compose(page, to, subject, body)
                logging.info("Email sent successfully")
                context.storage_state(path="auth_state.json")  # Save session
            except PlaywrightTimeoutError as e:
                logging.error(f"Compose error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
            input("Press Enter to close...")
            browser.close()

    def compose(self, page: object, to: str, subject: str, body: str) -> None:
        """Abstract method to compose and send the email on the provided page.
        Must be implemented in subclasses.

        Args:
            page: The Playwright page object for interacting with the
                web interface.
            to (str): The recipient's email address.
            subject (str): The subject line of the email.
            body (str): The body content of the email.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Implement in subclass.")


class GmailAgent(BaseEmailAgent):
    """Email agent for sending emails via Gmail."""

    def __init__(self):
        """Initializes the GmailAgent for sending emails via Gmail."""
        # Call the parent constructor with the Gmail URL
        super().__init__("https://mail.google.com")

    def compose(self, page: object, to: str, subject: str, body: str) -> None:
        """
        Composes and sends an email via the Gmail web interface.

        Args:
            page: The Playwright page object for interacting with the
                web interface.
            to (str): The recipient's email address.
            subject (str): The subject line of the email.
            body (str): The body content of the email.
        """
        logging.info("Attempting to click Compose")
        try:
            page.click('div[role="button"][gh="cm"]', timeout=60000)
            logging.info("Clicked Compose")
            page.fill('textarea[name="to"]', to, timeout=10000)
            logging.info("Filled To")
            page.fill('input[name="subjectbox"]', subject, timeout=10000)
            logging.info("Filled Subject")
            page.fill('div[aria-label="Message Body"]', body, timeout=10000)
            logging.info("Filled Body")
            page.click(
                'div[role="button"][data-tooltip*="Send"]',
                timeout=10000
            )
            logging.info("Clicked Send")
        except PlaywrightTimeoutError as e:
            logging.error(f"Timeout during compose: {e}")
            raise e


class OutlookAgent(BaseEmailAgent):
    """Email agent for sending emails via Outlook."""

    def __init__(self):
        """Initializes the OutlookAgent for sending emails via Outlook."""
        # Call the parent constructor with the Outlook URL
        super().__init__("https://outlook.live.com")

    def compose(self, page: object, to: str, subject: str, body: str) -> None:
        """
        Composes and sends an email via the Outlook web interface.

        Args:
            page: The Playwright page object for interacting with the
                web interface.
            to (str): The recipient's email address.
            subject (str): The subject line of the email.
            body (str): The body content of the email.
        """
        logging.info("Attempting to click New Message")
        try:
            logging.info("Clicked New mail")
            page.click('button[aria-label="New mail"]', timeout=60000)
            logging.info("Filled To")
            page.fill('input[aria-label="To recipients"]', to, timeout=10000)
            logging.info("Filled Subject")
            page.fill(
                'input[aria-label="Add a subject"]',
                subject,
                timeout=10000
            )
            logging.info("Filled Body")
            page.fill('div[role="textbox"]', body, timeout=10000)
            logging.info("Clicked Send")
            page.click('button[aria-label="Send"]', timeout=10000)
        except PlaywrightTimeoutError as e:
            logging.error(f"Timeout during compose: {e}")
            raise e


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Send email via Gmail or Outlook."
    )
    parser.add_argument(
        "instruction",
        help="E.g., 'Send email to test@example.com saying Hi'"
    )
    parser.add_argument(
        "--provider",
        default="gmail",
        choices=["gmail", "outlook"]
    )
    # Parse the command-line arguments
    args = parser.parse_args()
    try:
        # Parse the instruction
        parsed = mock_llm_parse(args.instruction)
        # Determine the email agent to use
        agent = GmailAgent() if args.provider == "gmail" else OutlookAgent()
        # Send the email
        agent.send(**parsed)
    except Exception as e:
        logging.error(f"Failed: {e}")
