#!/usr/bin/env python3
"""
Hook: Auto-trigger code review when story status changes to "review"
Event: PostToolUse (fires after Write/Edit operations)

This hook detects when a story file is edited and the status is changed
to "review", then injects a message instructing Claude to run the
BMAD code-review workflow.
"""
import json
import sys
import re
from pathlib import Path


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    # Get file path from either Write or Edit tool
    file_path = tool_input.get('file_path', '')

    if not file_path:
        sys.exit(0)

    # Only trigger for story files in sprint artifacts or output folder
    # Patterns: stories/*.md, *-stories/*.md, story-*.md, **/X-Y-*.md (story key format)
    story_patterns = [
        r'stories?/.*\.md$',
        r'sprint.*artifacts?/.*\.md$',
        r'_bmad-output/.*story.*\.md$',
        r'_bmad-output/implementation-artifacts/.*\.md$',
        r'\d+-\d+-[a-z].*\.md$',  # Story key format like 1-2-user-auth.md
    ]

    is_story_file = any(re.search(pattern, file_path, re.IGNORECASE) for pattern in story_patterns)

    if not is_story_file:
        sys.exit(0)

    # Check if this edit involves setting status to "review"
    # For Edit tool: check new_string
    # For Write tool: check content
    content_to_check = tool_input.get('new_string', '') or tool_input.get('content', '')

    # Look for status change to review
    # Patterns: "status: review", "Status: review", "## Status\nreview"
    review_patterns = [
        r'status:\s*review',
        r'status:\s*"review"',
        r"status:\s*'review'",
    ]

    status_changed_to_review = any(
        re.search(pattern, content_to_check, re.IGNORECASE)
        for pattern in review_patterns
    )

    if status_changed_to_review:
        # Extract story filename for the message
        story_name = Path(file_path).name

        output = {
            "userMessage": (
                f"\n{'='*60}\n"
                f"CODE REVIEW TRIGGERED\n"
                f"{'='*60}\n"
                f"Story marked for review: {story_name}\n\n"
                f"Run the BMAD code-review workflow:\n"
                f"/bmad:bmm:workflows:code-review\n\n"
                f"Story path: {file_path}\n"
                f"{'='*60}\n"
            )
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
