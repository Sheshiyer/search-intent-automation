# Reel Evidence

Source reel:
- `/Users/sheshnarayaniyer/Downloads/instagram/saved/2026-03-05_15-54-55_DVgi0rbAWXN.mp4`

Processed artifacts:
- `/Users/sheshnarayaniyer/Downloads/instagram/saved_processing/latest_20_videos_analysis/instagram_saved_latest_20_manifest.json`
- `/Users/sheshnarayaniyer/Downloads/instagram/saved_processing/latest_20_videos_analysis/ocr/01_DVgi0rbAWXN.json`

Direct caption evidence:

```text
Here’s how to be get edge over your ex or that irritating colleague.
Tools mentioned:
1) Ubersuggest by Neil Patel
2) Answerthepublic.com
3) Eu1.make.com
```

High-signal OCR evidence from the processed frames:

- `Ubersuggest by [NP] ... Dashboard ... Add Project ... Opportunities ... Keyword Research`
- `Questions ... Prepositions ... Comparisons ... Alphabeticals`
- `Organization ... Scenarios ... Credentials ... Webhooks ... Make AI Agents ... OpenAI ... Google Gemini`

Interpretation:

- The reel is recommending a three-stage workflow rather than isolated tools.
- `Ubersuggest` is the demand and SEO surface.
- `AnswerThePublic` is the audience-language and question-mining surface.
- In the source reel, `Make.com` is presented as the automation layer.
- The course CTA and registration screens are promotional noise and should not be treated as part of the core workflow.

Execution rewrite for coding agents:

- Keep the reel's research logic intact.
- Replace the `Make.com` implementation layer with:
  - `Playwright MCP` for browser capture and export collection
  - a Python CLI orchestrator for non-interactive downstream processing
- The Python layer should only continue partial runs when the user explicitly selects:
  - recommended option 2
  - or a custom direction
- This makes the workflow easier for CLI coding agents to run end to end with deterministic checkpoints, graceful fallbacks, resumable runs, and structured user-direction prompts.
