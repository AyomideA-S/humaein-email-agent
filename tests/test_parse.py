#!/usr/bin/env python3
"""Test parsing function."""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_parse():
    from agent import mock_llm_parse
    result = mock_llm_parse("Send email to test@example.com saying Hi")
    assert result["to"] == "test@example.com"
    assert result["body"] == "Hi"
    assert result["subject"] == "Automated Email"
    print("Parse test passed!")


if __name__ == "__main__":
    test_parse()
