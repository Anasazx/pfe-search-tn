# pfe-search-tn

**Trouvez, classez et postulez aux stages PFE en Tunisie, depuis votre machine.**

Every year Tunisian companies publish hundreds of PFE subjects in their "PFE Books", each with its own rules: 2 subjects maximum, the reference in the email subject, a deadline, a cover letter or not. `pfe-search-tn` collects them, ranks them against your CV, reads each company's rules for you, and prepares the emails.

- **Free core, no AI needed:** scrape, rank, extract rules, draft `.eml` files with your CV attached, track applications and follow-ups.
- **Optional AI layer:** with [Claude Code](https://claude.com/claude-code), slash commands build your profile from your CV, write a tailored email per offer, and prepare you for interviews.
- **Private by design:** everything runs locally; your CV and applications never leave your machine (except the emails you choose to send).

## Quick start (free core)

```bash
git clone https://github.com/Anasazx/pfe-search-tn.git && cd pfe-search-tn
pip install -r requirements.txt

python -m pfe init                 # creates me/profile.yaml
# put your CV PDF in me/ and fill in me/profile.yaml (skills, level, highlights)

python -m pfe scrape               # ~1,900 offers on first run, only new ones afterwards
python -m pfe rank                 # top matches + output/pfe_offers.xlsx
python -m pfe show pb-10321        # full offer + its application rules
python -m pfe draft pb-10321       # .eml draft with your CV attached; double-click to open
python -m pfe track pb-10321 applied
python -m pfe followups            # who to follow up with (14 days without news)
```

## With Claude Code (AI layer)

Run `claude` in the repo, then:

| Command | What it does |
|---|---|
| `/setup` | Reads your CV and writes `me/profile.yaml` (skills, weights, proof points in French) |
| `/scan` | Scrapes, ranks, and briefs you: urgent deadlines, new offers, what to apply to next |
| `/apply <ids>` | Tailored email per company: follows its subject format and subject caps, ties its missions to your real experience, and names your gaps honestly. Produces the `.eml` |
| `/interview <id>` | Prep sheet: the subject explained, your 2-minute pitch, likely technical and HR questions with answers, questions to ask |
| `/followup` | Polite relances for applications with no answer after 14 days |

The AI never sends anything: you review every draft and send it yourself.

## How ranking works

| Part | Points | How |
|---|---|---|
| Skills | 65 | Your skills found in the offer. Counts more when listed in its required technologies. Weighted by how central each skill is to you |
| Level | 20 | Licence / Ingénieur / Master. Offers reserved for another level are hidden (`--all-levels` shows them) |
| Domain | 10 | Offer category within your `categories` |
| Location | 5 | Offer city within your `locations` (or remote) |

## What the rules engine reads from every offer
Application email or portal · max subjects per candidate · subject reference · required email-subject format · required documents (cover letter, photo, Europass) · deadline. `draft` warns before you exceed a company's cap, counting what you've already sent.

## Sources
- [pfebooks.com](https://pfebooks.com): aggregates company PFE Books (public API).

Adding a board means writing one module in `pfe/sources/` with a `fetch()` function (offer schema in `pfe/sources/__init__.py`). Contributions are welcome, e.g. Tanitjobs, Keejob, LinkedIn, or company career pages.

## Credits
Inspired by [ai-job-search](https://github.com/ai-job-search-dev/ai-job-search), the Claude Code job search framework. This project is an independent re-design for Tunisian PFE searches. It is not affiliated with pfebooks.com or Anthropic.

## License
MIT
