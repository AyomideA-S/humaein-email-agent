# Humaein Case Study #2: Cross-Platform Email Agent

## Overview

This project implements an AI-driven agent to send emails via Gmail and Outlook web interfaces, as part of Humaein's AI Full Stack Developer screening. It uses Playwright for browser automation, a mocked LLM for parsing natural language instructions, and modular classes for extensibility.

## Setup

1. Install Python 3.8+

2. Clone this repo:

   ```bash
   git clone https://github.com/AyomideA-S/humaein-email-agent.git
   ```

3. Create virtualenv

   ```bash
   python -m venv .venv
   ```

   (Unix)

   ```bash
   source .venv/bin/activate
   ```

   or (Windows)

   ```bash
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Install browsers:

   ```bash
   playwright install
   ```

## Usage

Run:

```bash
python agent.py "Send email to test@example.com saying Hello" --provider gmail
```

- Log in manually when browser opens.
- Logs saved to `logs/agent.log`.

## Structure

- `agent.py`: Main script with agent logic.
- `requirements.txt`: Dependencies.
- `logs/`: Runtime logs.
- `tests/`: Optional test scripts.

## Notes

- Non-headless mode for manual login due to security.
- Tested on Windows 11, Python 3.12.
- Uses `undetected-playwright` to bypass Gmail's "This browser may not be secure" error.
- Handles passkey prompts and URL variations with extended timeouts and selector checks.
- Manual login required; session saved to `auth_state.json` (excluded from repo).

Author: Ayomide Ayodele-Soyebo
