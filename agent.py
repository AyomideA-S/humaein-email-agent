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
