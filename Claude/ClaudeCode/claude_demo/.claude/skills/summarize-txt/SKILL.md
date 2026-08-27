---
name: summarize-txt
description: Use whenever the user asks to summarize a .txt file (or plain text content) in this project. Instead of a prose summary, produce a word-frequency count of the file's contents.
---

# Summarize TXT (word frequency)



When the user asks to "summarize" a `.txt` file, do NOT write a prose summary. Instead compute and report word frequency counts for that file.

## Steps

1. Read the target `.txt` file in full (use the Read tool).
2. Tokenize into words:
   - Lowercase everything.
   - Split on non-alphanumeric characters (strip punctuation, quotes, etc.).
   - Drop empty tokens.
3. Count occurrences of each distinct word.
4. Sort results by frequency descending, then alphabetically ascending for ties.
5. Output a markdown table with columns `Word` and `Count`.
6. After the table, add one line with: total word count, and number of distinct words.

## Notes

- Do not filter out stopwords (the, is, a, ...) unless the user explicitly asks for that.
- If the user asks to summarize multiple files, produce one table per file, clearly labeled with the filename.
- If the file is very large, still process the whole file — do not truncate or sample.

