# BD-Transcript – Automated Lecture Notes Generator

This repository contains lecture transcripts for a **Business Development** course (from basics to scaling) and a script to automatically generate high-quality structured study notes from them.

---

## Repository Contents

| Path | Description |
|------|-------------|
| `Lec01.pdf` – `Lec60.pdf` | Raw lecture transcript PDFs |
| `generate_notes.py` | Main script to generate structured Markdown notes |
| `requirements.txt` | Python dependencies |
| `notes/` | Generated Markdown notes (created when you run the script) |

---

## Prerequisites

- Python 3.10 or higher
- An [OpenAI API key](https://platform.openai.com/account/api-keys)

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Setting Your OpenAI API Key

The script reads your key from the `OPENAI_API_KEY` environment variable. **Never hard-code secrets in source code.**

**macOS / Linux:**
```bash
export OPENAI_API_KEY="sk-..."
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

---

## Running the Script

### Process all 60 lectures (default)

```bash
python generate_notes.py
```

### Process a specific range of lectures

```bash
python generate_notes.py --lectures 1-10
```

### Process a single lecture

```bash
python generate_notes.py --lectures 5
```

### Process a custom selection

```bash
python generate_notes.py --lectures 1,3,5-8,12
```

### Re-generate notes (overwrite existing files)

By default the script **skips** lectures whose output file already exists. Use `--force` to overwrite:

```bash
python generate_notes.py --force
python generate_notes.py --lectures 1-5 --force
```

### Change the output directory

```bash
python generate_notes.py --output-dir my_notes/
```

### Change the PDF source directory

If you run the script from a different working directory, point it to where the PDFs are:

```bash
python generate_notes.py --pdf-dir /path/to/transcripts/
```

---

## Output Format

Each generated file (`notes/LecXX.md`) follows this structure:

```markdown
# Lecture N – [Topic Title]

## Overview
A concise summary of what the lecture covers and its significance.

## Key Concepts
- **Concept 1** – Brief definition
- **Concept 2** – Brief definition
...

## Detailed Explanations

### Concept 1
In-depth explanation with examples, analogies, and frameworks from the lecture.

### Concept 2
...

## Important Insights & Takeaways
- Key insight 1
- Key insight 2
...

## Summary
A closing paragraph summarising the lecture and its place in the course.
```

---

## Notes

- The script uses **GPT-4o** for high-quality, structured academic output.
- Rate limits are handled automatically with **exponential backoff** (up to 5 retries).
- The script is **idempotent** – already-processed lectures are skipped unless `--force` is passed.
- If the original grouped lecture notes PDFs (e.g. `CBR-BD-W1-L1.pdf`) are later added to the repository, the script can be extended to cross-reference both sources for richer notes.
