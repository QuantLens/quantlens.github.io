# QuantLens — Go-To-Market Playbook

This is a concise GTM plan you can execute in days. It includes positioning, channels, a 2-week launch sprint, and ready-to-use copy.

---

## Positioning

- Product: QuantLens — Multi‑Horizon Market Export Engine (TradingView → JSON → LLM TA)
- Core value: Alerts in, insights out. Compact, structured TA payloads ready for models.
- Target users (ICP):
  - Indie traders using TradingView who want AI summaries and ranking
  - Quant/automation tinkerers wiring webhooks → notebooks/LLMs
  - Creators/analysts who publish setups and need repeatable JSON
- Differentiators:
  - Multi‑horizon snapshot (short/med/long) with VP‑Lite, signals, and risk
  - Compact, short‑key JSON for low token cost
  - Production‑ready prompts + website templates

## Pricing thesis (starter)

- Free docs + samples
- Early‑access license (one-time or small subscription)
- Team/org plans later (webhook collector, dashboards, schema validator)

---

## 2-week launch sprint

Week 1

- Publish website to a free subdomain (Pages/Netlify)
- Share preview on X/LinkedIn with a GIF of payload → model output
- Seed 5–10 TradingView communities and a couple of Discords/Telegram (respect rules)
- Post a detailed walkthrough on LinkedIn article or Medium

Week 2

- Show HN (if you’re comfortable): “QuantLens — Turn TradingView alerts into AI‑ready JSON”
- Product Hunt (weekday morning): add screenshots, tagline, and a short video
- Cold outreach to 10 creators/analysts (DM/email) with a personal sample for their symbol/TF
- Start a small newsletter (Substack/Beehiiv) with weekly LLM TA recipes

---

## Channels & tactics

- TradingView: Publish indicator page (or invite‑only link) with JSON sample & prompts
- X/Twitter: short demos; threads explaining the JSON keys and prompts
- LinkedIn: thought‑leadership post + article; tag relevant folks
- Reddit: r/algotrading, r/algotrader, r/Daytrading (follow rules; share method & code snippets)
- Discord/Telegram: partner with 2–3 communities; offer private walkthroughs
- Dev communities: Show HN, GitHub README polish, dev.to/Medium write‑up

---

## Copy templates (steal these)

X / Twitter (short):

- Alerts in. Insights out. QuantLens turns TradingView alerts into compact, multi‑horizon JSON your LLM can read. Try the samples + prompts on the site. #tradingview #ai #quant

X / Twitter (thread bullets):

1) Add the QuantLens study to your chart
2) Alert → Once per bar close → Webhook/Log
3) JSON emits short‑keys: hdr/feat/levels/vp/sig/risk
4) Paste into the included prompts → instant TA
5) Works for stocks, crypto, FX

LinkedIn (post):

We built a small engine that turns TradingView alerts into AI‑ready JSON for fast, structured TA. Multi‑horizon context (short/med/long), VP‑Lite, signals, and risk — all designed for low token cost. Website has prompts, samples, and an automation flow. Looking for early users; DMs open.

Reddit (method-focused):

Title: Turn TradingView alerts into structured JSON for AI TA — open prompts + samples

Body (keep code-light):

- Problem: charts are visual, models need structure
- Approach: Pine v6 emits short‑key JSON on bar close; webhook or copy from alert log
- What’s in the JSON: multi‑horizon aggregates, features, VP‑Lite, signals, risk, bars
- Prompts included: TA + ranking + watchlist flow
- Link to site; feedback welcome

Hacker News (Show HN):

Show HN: QuantLens — Turn TradingView alerts into AI‑ready TA JSON

What it is: a Pine indicator that emits compact JSON + prompts & a simple website

Why: structured, cheap tokens; repeatable TA for LLMs

Looking for: feedback, use‑cases; roadmap includes collector & dashboards

Product Hunt tagline:

QuantLens — Alerts in. Insights out. Multi‑horizon TA JSON for your LLM.

Creator outreach (email/DM):

Subject: A ready‑to‑paste JSON + prompt for your [SYMBOL] setups

Hi [Name], I made a compact TradingView → JSON exporter with prompts that might fit your workflow. I ran it on [SYMBOL/TF] and got a clean summary out of GPT. If you want, I’ll tailor a sample to your pairs and send a plug‑and‑play prompt. Cheers — [You]

---

## TradingView publishing checklist

- Title and short description match the site branding
- Clear summary of what the JSON contains; link to website Templates page
- A single stand‑out screenshot/GIF of payload → model output
- Usage: add study → create alert once per bar close → webhook/copy
- Limits: payload sizes, bar caps, toggles

---

## Asset checklist

- OG/social image (1200×630)
- Favicon + logo variants (light/dark)
- 10–20s screen capture GIF: alert → JSON → LLM output
- A public sample payload JSON (redact secrets)

---

## Measurement

- Add analytics (GA4 or Plausible) to the site
- Use UTM parameters for campaign links
- Track contact/waitlist submissions

---

## Next steps

- Choose the first week’s channels, schedule the posts
- Prepare a short demo video and OG image
- Wire a contact/waitlist form and enable analytics
