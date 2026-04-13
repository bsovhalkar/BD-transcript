#!/usr/bin/env python3
"""
generate_notes.py – Automated Lecture Notes Generator

Processes lecture transcript PDFs and generates high-quality structured
Markdown notes using the OpenAI API (GPT-4o).

Usage:
    python generate_notes.py
    python generate_notes.py --lectures 1-10
    python generate_notes.py --lectures 5
    python generate_notes.py --output-dir my_notes/
    python generate_notes.py --force          # re-generate already processed lectures

Requirements:
    pip install -r requirements.txt
    export OPENAI_API_KEY="sk-..."
"""

import argparse
import os
import sys
import time
import pdfplumber
from openai import OpenAI, RateLimitError, APIError
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOTAL_LECTURES = 60
DEFAULT_OUTPUT_DIR = "notes"
MODEL = "gpt-4o"
MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds

SYSTEM_PROMPT = (
    "You are an expert academic assistant with the teaching quality of an IIT professor. "
    "Your task is to transform raw lecture transcripts into well-structured, comprehensive "
    "study notes. Be precise, thorough, and pedagogically clear. Use Markdown formatting."
)

NOTE_TEMPLATE = """You have been given the raw transcript of Lecture {lecture_num} from a \
Business Development course (covering topics from basics to scaling).

Please generate high-quality structured notes in EXACTLY this format:

---

# Lecture {lecture_num} – [Derive a concise, descriptive topic title from the content]

## Overview
A 3-5 sentence summary of what this lecture covers and why it matters.

## Key Concepts
A bulleted list of the main concepts introduced or discussed, each with a one-line definition \
or explanation.

## Detailed Explanations
For each key concept, provide a deeper explanation (2-5 sentences). Use sub-headings \
(### Concept Name) for each concept. Include examples, analogies, or frameworks mentioned \
in the transcript.

## Important Insights & Takeaways
Bulleted list of the most important insights, lessons, or practical takeaways a student \
should remember from this lecture.

## Summary
A concise paragraph (4-6 sentences) summarising the entire lecture and its significance \
within the broader Business Development course.

---

RAW TRANSCRIPT:
{transcript}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_lecture_range(value: str) -> list[int]:
    """Parse a range string into a sorted, deduplicated list of lecture numbers.

    Supported formats:
      - Single number: '5'       → [5]
      - Range:         '1-10'    → [1, 2, ..., 10]
      - Mixed list:   '1,3,5-8' → [1, 3, 5, 6, 7, 8]

    Raises:
        ValueError: If any part of the string cannot be converted to an integer,
                    or if a range is malformed (e.g. non-numeric bounds).
    """
    lectures = []
    for part in value.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            lectures.extend(range(int(start), int(end) + 1))
        else:
            lectures.append(int(part))
    return sorted(set(lectures))


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using pdfplumber.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        A single string containing all page text joined by double newlines.
        Returns an empty string if no text could be extracted.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        pdfplumber.exceptions.PDFSyntaxError: If the file is not a valid PDF.
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)


def _backoff_wait(lecture_num: int, attempt: int, reason: str) -> None:
    """Log a retry message and sleep for an exponentially increasing duration."""
    wait = INITIAL_BACKOFF * (2 ** (attempt - 1))
    tqdm.write(
        f"  [Lecture {lecture_num}] {reason}. Retrying in {wait}s "
        f"(attempt {attempt}/{MAX_RETRIES})…"
    )
    time.sleep(wait)


def generate_notes_with_retry(
    client: OpenAI, lecture_num: int, transcript: str
) -> str:
    """Call OpenAI API with exponential backoff on rate-limit / transient errors.

    Args:
        client: An initialised OpenAI client.
        lecture_num: The lecture number, used only for log messages.
        transcript: The raw text extracted from the lecture PDF.

    Returns:
        The generated Markdown notes as a string.

    Raises:
        RateLimitError: If the rate limit is still exceeded after MAX_RETRIES attempts.
        APIError: If a transient API error persists after MAX_RETRIES attempts.
        RuntimeError: If the retry loop exhausts without returning (should not occur).
    """
    prompt = NOTE_TEMPLATE.format(lecture_num=lecture_num, transcript=transcript)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except RateLimitError as exc:
            if attempt == MAX_RETRIES:
                raise
            _backoff_wait(lecture_num, attempt, f"Rate limited ({exc})")
        except APIError as exc:
            if attempt == MAX_RETRIES:
                raise
            _backoff_wait(lecture_num, attempt, f"API error: {exc}")

    raise RuntimeError(f"Failed to generate notes for Lecture {lecture_num} after {MAX_RETRIES} attempts.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate structured Markdown notes from lecture transcript PDFs."
    )
    parser.add_argument(
        "--lectures",
        default=f"1-{TOTAL_LECTURES}",
        help=(
            "Lecture numbers to process. Accepts a single number (e.g. '5'), "
            "a range (e.g. '1-10'), or a comma-separated mix (e.g. '1,3,5-8'). "
            f"Default: 1-{TOTAL_LECTURES}"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write generated Markdown notes. Default: '{DEFAULT_OUTPUT_DIR}/'",
    )
    parser.add_argument(
        "--pdf-dir",
        default=".",
        help="Directory containing the LecXX.pdf transcript files. Default: current directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-generate notes even if the output file already exists.",
    )
    args = parser.parse_args()

    # Validate API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "Error: OPENAI_API_KEY environment variable is not set.\n"
            "Export it before running:\n"
            "    export OPENAI_API_KEY='sk-...'",
            file=sys.stderr,
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Resolve lecture list
    try:
        lecture_nums = parse_lecture_range(args.lectures)
    except ValueError as exc:
        print(f"Error parsing --lectures value '{args.lectures}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    pdf_dir = args.pdf_dir

    skipped = []
    failed = []

    for lecture_num in tqdm(lecture_nums, desc="Generating notes", unit="lecture"):
        pdf_filename = f"Lec{lecture_num:02d}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        output_path = os.path.join(output_dir, f"Lec{lecture_num:02d}.md")

        # Skip if already done (unless --force)
        if os.path.exists(output_path) and not args.force:
            tqdm.write(f"  [Lecture {lecture_num}] Skipping – output already exists: {output_path}")
            skipped.append(lecture_num)
            continue

        # Check PDF exists
        if not os.path.exists(pdf_path):
            tqdm.write(f"  [Lecture {lecture_num}] WARNING – PDF not found: {pdf_path}. Skipping.")
            failed.append(lecture_num)
            continue

        # Extract text
        tqdm.write(f"  [Lecture {lecture_num}] Extracting text from {pdf_filename}…")
        try:
            transcript = extract_text_from_pdf(pdf_path)
        except Exception as exc:
            tqdm.write(f"  [Lecture {lecture_num}] ERROR extracting PDF: {exc}. Skipping.")
            failed.append(lecture_num)
            continue

        if not transcript.strip():
            tqdm.write(f"  [Lecture {lecture_num}] WARNING – No text extracted from {pdf_filename}. Skipping.")
            failed.append(lecture_num)
            continue

        # Generate notes
        tqdm.write(f"  [Lecture {lecture_num}] Calling OpenAI ({MODEL})…")
        try:
            notes = generate_notes_with_retry(client, lecture_num, transcript)
        except Exception as exc:
            tqdm.write(f"  [Lecture {lecture_num}] ERROR generating notes: {exc}. Skipping.")
            failed.append(lecture_num)
            continue

        # Write output
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(notes)
        tqdm.write(f"  [Lecture {lecture_num}] Notes written to {output_path}")

    # Final summary
    processed = [n for n in lecture_nums if n not in skipped and n not in failed]
    print(
        f"\nDone. Processed: {len(processed)}, Skipped (already existed): {len(skipped)}, "
        f"Failed: {len(failed)}"
    )
    if failed:
        print(f"Failed lectures: {failed}")


if __name__ == "__main__":
    main()
