# BuildOpportunityMap

Use this workflow when you want to turn a single seed topic, product, service, or offer into a repeatable market-research and automation pipeline.

## Inputs

- Seed topic, product, or offer
- Target geography or market, if relevant
- Primary goal:
  - content planning
  - SEO opportunity discovery
  - offer positioning
  - client acquisition
  - niche validation

## Workflow

### 1. Define the seed and success criteria

Write down:
- the core topic or offer
- who the audience is
- what kind of edge you want:
  - more traffic
  - better content ideas
  - better qualification
  - faster automation

Output:
- a one-sentence research target

### 2. Pull keyword and competition data with Ubersuggest

Use Ubersuggest to extract:
- keyword ideas
- search volume
- SEO difficulty
- paid difficulty or CPC if relevant
- competitor domains or content gaps
- top pages or related phrases

Questions to answer:
- Which terms have demand but lower competition?
- Which terms map cleanly to the offer?
- Which competitors dominate the obvious queries?

Output:
- keyword shortlist
- competitor shortlist
- priority terms

### 3. Pull audience-language data with AnswerThePublic

Run the same seed through AnswerThePublic and capture:
- questions
- comparisons
- prepositions
- alphabeticals

This step is not for volume. It is for intent language.

Questions to answer:
- What are people confused about?
- What comparisons or alternatives keep coming up?
- Which phrases sound like pain, curiosity, or buying intent?

Output:
- question clusters
- pain-point phrases
- comparison phrases
- content-angle list

### 4. Merge the two views into an opportunity map

Create a combined table with:
- keyword
- search demand signal
- question or audience-language match
- likely intent:
  - informational
  - comparative
  - transactional
  - navigational
- recommended asset:
  - article
  - landing page
  - short-form post
  - email
  - lead magnet

Output:
- one ranked opportunity map

### 5. Capture browser data with Playwright MCP

Use Playwright MCP for the browser-only steps that coding agents cannot do reliably with plain HTTP:
- log in if required
- open the right report or search views
- export or capture the relevant research artifacts
- save browser outputs to local files the Python step can read

Expected capture outputs:
- `ubersuggest.json` or `ubersuggest.csv`
- `answer-the-public.json` or `answer-the-public.csv`
- `capture-status.json` following `Tools/CaptureStatusContract.md`
- optional screenshots for audit trail

Output:
- local capture artifacts ready for deterministic downstream processing
- a capture-status manifest that maps browser failures into the pipeline taxonomy

### 6. Orchestrate normalization and merging with Python

Run the Python pipeline to:
- validate required artifacts
- normalize schema differences
- merge keyword and question data
- score or rank the opportunity map
- emit machine-readable outputs for agents or humans

Tooling:
- `Tools/OpportunityPipeline.py`

Output:
- a non-interactive CLI-agent pipeline instead of a SaaS automation flow

### 7. Stuck-state checkpoint protocol

If the pipeline gets stuck, stop and classify the issue with `FailureTaxonomy.md`.

At that point, the agent must ask the user using this exact shape:

- taxonomy: `[issue-category]`
- recommended option 1: `[best next action]`
- recommended option 2: `[second-best action]`
- custom direction: `Provide a different direction to change the flow`

Do not silently improvise past a blocked browser or schema state.

### 8. Optional AI content layer

Once the opportunity map is stable, generate:
- content briefs
- article outlines
- landing-page variants
- ad angles
- lead-research notes

Only do this after validating the keyword and question map. Do not start with generation.

## Deliverables

- Research target statement
- Keyword shortlist
- Question cluster list
- Ranked opportunity map
- Playwright capture trace
- capture-status manifest
- Python pipeline output
- Optional content brief pack

## Failure Modes

- Using only Ubersuggest and missing audience phrasing
- Using only AnswerThePublic and missing demand validation
- Jumping straight to AI generation before validating search and question data
- Treating browser capture and downstream processing as the same layer
- Continuing past a blocked step without surfacing a taxonomy-based checkpoint
- Treating the promotional CTA from the reel as part of the workflow

## Source Trace

Derived from:
- `/Users/sheshnarayaniyer/Downloads/instagram/saved/2026-03-05_15-54-55_DVgi0rbAWXN.mp4`
- `ReelEvidence.md`
