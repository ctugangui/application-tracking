# Application Tracker — Project Context

A personal tool for tracking my job applications, built as a backend-engineering
warm-up after ~6 months away from coding. Two jobs: (1) be a real tool I use to
run my job search, (2) rebuild my Python + AWS reps and produce one interview
story I can discuss fluently.

**Repo:** `~/development/python/application-tracking` (private, GitHub: ctugangui/application-tracking)
**Source of truth:** the GitHub repo. This project is a workspace; the repo is canonical.
After each session: work → update docs → commit → push. If a file here disagrees with the repo, the repo wins.

---

## Stack

- **Python** + **FastAPI** (web framework)
- **SQLModel** (ORM — one class is both the API schema and the DB table)
- **SQLite** locally (one file, zero setup; chosen deliberately over Postgres for a single-user local tool)
- Later: **Docker** + **Terraform** + **AWS** (see Phase 2)

## Design principles

- **Local first, AWS later.** The app runs and works locally before any cloud deploy.
- **Smallest finished thing wins.** Ship a working milestone, then stop. No gold-plating.
- **Understand every line.** Anything I can't explain in an interview comes out.
- **Hand-write the core; generate the boilerplate.** Core logic (models, endpoints,
  the follow-up query) I write myself — that's the rep and the Surge-assessment prep.
  Boilerplate (Dockerfile, Terraform, test fixtures) is where Claude Code / generation
  earns its place, with every generated line reviewed.

---

## Phased plan

**Milestone 1 — DONE.** Record and retrieve one application.
`POST /applications` + `GET /applications`, SQLModel + SQLite. Working, committed, pushed.
First record logged: Populous, Cloud Engineer, applied.

**Milestone 2 — status lifecycle.** Status as a real enum
(`saved → applied → screen → technical → onsite → offer → rejected → ghosted`),
`PATCH /applications/{id}` to move status, `GET /applications?status=` filter.
A couple of pytest tests around status transitions.

**Milestone 3 — the useful query.** An `Event`/`FollowUp` table (application_id, date, kind, note),
`POST /applications/{id}/events`, and `GET /followups` — applications with no event in N days
("who's gone quiet"). This is the one query a spreadsheet can't easily do.

**Milestone 4 (optional) — one polish.** A `stats` endpoint (apps/week, response rate)
*or* a minimal HTML page. Pick one, then stop.

**Phase 2 — AWS deployment (separate build block, later).**
Containerize (Dockerfile), then Terraform a small real environment: ECS Fargate (or App Runner)
behind an ALB, RDS Postgres, secrets in Secrets Manager, one GitHub Actions CI step.
Flip SQLite → RDS via SQLModel (the "how I productionized it" interview beat).
**Cost guardrail:** stand it up, confirm it works, capture the Terraform + screenshots,
then `terraform destroy`. The artifact is the code, not a service left running on gig income.
**Secrets guardrail:** never commit AWS keys, `.tfstate`, or `.env` — they're in `.gitignore` from day one.

---

## Data model (current + planned)

- **Application:** id, company, role, status  *(M1: id/company/role/status)*
- **Company** *(planned):* name, careers URL, notes
- **Event / FollowUp** *(M3):* application_id, date, kind, note

## Guardrails on scope

- This is a **warm-up + personal tool**, not a product. It has been built ~50 times
  (Huntr, Teal, Simplify, etc.) — no plans to sell it. Open-sourcing the artifact is fine; that's the ceiling.
- Build-block work only. It does **not** borrow hours from the daily application block —
  applications are the thing that actually moves the job search.
