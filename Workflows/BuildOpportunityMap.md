# BuildOpportunityMap

Use this workflow when you want to turn a single seed topic, product, service, or offer into a repeatable market-research pipeline.

## Inputs

- Seed topic, product, or offer
- Optional geography or market
- Primary goal such as SEO discovery, offer positioning, or content planning

## Flow

1. Pull keyword and competition data with Ubersuggest.
2. Pull audience-language data with AnswerThePublic.
3. Use Playwright MCP for gated browser capture.
4. Write `capture-status.json` following `Tools/CaptureStatusContract.md`.
5. Run the installed CLI or `python Tools/OpportunityPipeline.py`.
6. If blocked, present the taxonomy and the three decision branches.

## Deliverables

- Keyword shortlist
- Question cluster map
- `capture-status.json`
- `opportunity-map.json` or `checkpoint.json`
