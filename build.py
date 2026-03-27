#!/usr/bin/env python3
"""
Build script for flux-tech.de.

Reads content.yaml, processes markdown-style formatting, and injects
the result into template.html to produce index.html.

Usage:
    python build.py            # Build index.html
    python build.py --check    # Dry run: validate YAML keys match template placeholders
"""

import re
import sys
import yaml


def load_content(path="content.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_template(path="template.html"):
    with open(path, "r") as f:
        return f.read()


def markdown_to_html(text):
    """Convert markdown-style inline formatting to HTML."""
    # Bold: **text** → <strong>text</strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Highlight: ==text== → <mark>text</mark>
    text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
    # Links: [text](url) → <a href="url">text</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def escape_html_entities(text):
    """Escape bare & characters that aren't already part of HTML entities or tags."""
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', text)
    return text


def process_value(value):
    """Process a YAML value into HTML content for injection into the template."""
    value = str(value).strip()

    # Escape HTML entities before markdown conversion
    value = escape_html_entities(value)

    # Apply markdown conversion
    value = markdown_to_html(value)

    # Split into paragraphs on double newlines
    paragraphs = re.split(r'\n\n', value)

    if len(paragraphs) == 1:
        # Single paragraph — return as-is (no span wrapper needed;
        # the template element may or may not use spans)
        return paragraphs[0]

    # Multiple paragraphs — wrap each in <span class="p">
    spans = []
    for p in paragraphs:
        p = p.strip()
        if p:
            spans.append(f'<span class="p">{p}</span>')
    return ''.join(spans)


def find_template_placeholders(template):
    """Return all {{key}} placeholders found in template."""
    return set(re.findall(r'\{\{([^}]+)\}\}', template))


def build(check_only=False):
    content = load_content()
    template = load_template()

    placeholders = find_template_placeholders(template)
    yaml_keys = set(content.keys())

    # Validate
    missing_in_template = yaml_keys - placeholders
    orphaned_in_template = placeholders - yaml_keys

    errors = False

    if missing_in_template:
        print(f"WARNING: YAML keys with no matching placeholder in template: {sorted(missing_in_template)}")
        errors = True

    if orphaned_in_template:
        print(f"ERROR: Template placeholders with no matching YAML key: {sorted(orphaned_in_template)}")
        print("Build blocked — these would appear as literal {{key}} text on the site.")
        sys.exit(1)

    if not missing_in_template:
        print(f"OK: {len(yaml_keys)} YAML keys match {len(placeholders)} template placeholders.")

    if check_only:
        sys.exit(0)

    # Build
    output = template
    for key, value in content.items():
        processed = process_value(value)
        placeholder = '{{' + key + '}}'
        if placeholder in output:
            output = output.replace(placeholder, processed)

    with open("index.html", "w") as f:
        f.write(output)

    print("Built index.html successfully.")


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    build(check_only=check_only)
