#!/usr/bin/env python3
"""
Hook: Check for pending code reviews before stopping
Event: Stop (fires when Claude is about to finish)

This hook scans sprint-status.yaml and story files to find any stories
with status "review" that haven't been code reviewed yet. If found,
it instructs Claude to run code reviews before completing.
"""
import json
import sys
import os
from pathlib import Path
import re


def find_project_root():
    """Find the project root directory."""
    # Try environment variable first
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        return Path(project_dir)

    # Fallback to current directory
    return Path.cwd()


def find_sprint_status(project_root: Path):
    """Find sprint-status.yaml file."""
    possible_paths = [
        project_root / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml",
        project_root / "_bmad-output" / "sprint-status.yaml",
        project_root / "sprint-status.yaml",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def find_stories_needing_review(project_root: Path):
    """Find story files with status 'review'."""
    stories_needing_review = []

    # Search directories for story files
    search_dirs = [
        project_root / "_bmad-output" / "implementation-artifacts",
        project_root / "_bmad-output" / "stories",
        project_root / "_bmad-output",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # Find markdown files that look like stories
        for md_file in search_dir.glob("*.md"):
            # Skip non-story files
            if md_file.name.startswith(('prd', 'architecture', 'epic', 'index', 'README')):
                continue

            try:
                content = md_file.read_text(encoding='utf-8')

                # Check if this is a story file with status: review
                if re.search(r'status:\s*["\']?review["\']?', content, re.IGNORECASE):
                    # Check if it has NOT been reviewed yet
                    # Look for absence of "Senior Developer Review" or "Code Review" sections
                    has_review = bool(re.search(
                        r'(Senior Developer Review|Code Review.*Findings|Review Complete)',
                        content,
                        re.IGNORECASE
                    ))

                    if not has_review:
                        stories_needing_review.append(str(md_file))

            except Exception:
                continue

    return stories_needing_review


def check_sprint_status_for_reviews(sprint_status_path: Path):
    """Check sprint-status.yaml for stories in review status."""
    stories_in_review = []

    try:
        content = sprint_status_path.read_text(encoding='utf-8')

        # Simple YAML parsing for development_status section
        # Look for patterns like "1-2-story-name: review"
        in_dev_status = False
        for line in content.split('\n'):
            if 'development_status:' in line:
                in_dev_status = True
                continue

            if in_dev_status:
                # Check if we've exited the section
                if line and not line.startswith(' ') and not line.startswith('#'):
                    in_dev_status = False
                    continue

                # Look for story: review pattern
                match = re.match(r'\s+([a-z0-9-]+):\s*["\']?review["\']?', line, re.IGNORECASE)
                if match:
                    stories_in_review.append(match.group(1))

    except Exception:
        pass

    return stories_in_review


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    project_root = find_project_root()

    # Collect stories needing review from multiple sources
    stories_needing_review = []

    # Check sprint-status.yaml
    sprint_status_path = find_sprint_status(project_root)
    if sprint_status_path:
        sprint_stories = check_sprint_status_for_reviews(sprint_status_path)
        stories_needing_review.extend(sprint_stories)

    # Check actual story files
    story_files = find_stories_needing_review(project_root)

    # Combine and deduplicate
    all_pending = list(set(stories_needing_review))

    if all_pending or story_files:
        message_parts = [
            "\n" + "=" * 60,
            "PENDING CODE REVIEWS DETECTED",
            "=" * 60,
        ]

        if all_pending:
            message_parts.append("\nStories in 'review' status (from sprint-status.yaml):")
            for story in all_pending:
                message_parts.append(f"  - {story}")

        if story_files:
            message_parts.append("\nStory files needing review:")
            for story_file in story_files:
                message_parts.append(f"  - {story_file}")

        message_parts.extend([
            "\nPlease run code review before completing:",
            "/bmad:bmm:workflows:code-review",
            "",
            "=" * 60,
        ])

        output = {
            "userMessage": "\n".join(message_parts)
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
