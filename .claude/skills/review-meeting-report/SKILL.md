---
name: review-meeting-report
description: Review a meeting report against the transcript and files discussed
argument-hint: "<lab-number> <iteration-number>"
---

Review the meeting report for lab N, iteration M by cross-checking it against the transcript and the files discussed during the meeting.

## Steps

1. Parse `$ARGUMENTS` to extract N (lab number) and M (iteration number). Both are required — if missing, ask the user.
2. Read [`contributing/conventions/meeting-report.md`](../../../contributing/conventions/meeting-report.md) for the report format rules and file locations. Substitute actual N and M into the paths defined in the File locations section.
3. Read the report at the path from step 2.
4. Read the transcript at the path from step 2.
5. If the report's **Metadata → Files discussed** section lists any files, read each of them.
6. Produce a review covering the five categories in [Section 5 (Review)](../../../contributing/conventions/meeting-report.md#5-review) of the conventions file. For each finding, cite the relevant transcript timestamp or report line so the author can locate it quickly.

## Output format

Write the review directly in the conversation. Use a heading for each category (A–E). Under each heading, list findings as numbered items. If a category has no findings, write "No issues found." At the end, add a **Summary** section with a short overall assessment.
