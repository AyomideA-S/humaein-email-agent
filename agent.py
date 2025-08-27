import re


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
        from playwright.sync_api import sync_playwright

        # Launch browser and navigate to email service
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            page.wait_for_timeout(15000)  # For login
            # Compose email
            self.compose(page, to, subject, body)
            input("Press Enter...")
            browser.close()

    def compose(self, page, to, subject, body):
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
