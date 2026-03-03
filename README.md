# NovaOS

NovaOS is a local developer assistant that lets you run useful dev tasks in plain language from terminal.

---

## Why this project exists

As developers, we keep doing repetitive tasks:

- checking system status
- organizing files
- cleaning unused imports
- analyzing project quality
- undoing changes safely

Most of this is manual, error-prone, and time-consuming.

**NovaOS solves that** by giving one command interface where you type simple text like:

```powershell
nova "analyze project"
nova "fix import" --force
nova "undo import"
```

---

## What NovaOS can do

- ✅ Run natural-language commands from terminal
- ✅ Analyze your project and save a report
- ✅ Generate AI summary for analysis
- ✅ Remove unused imports
- ✅ Undo import cleanup using log file
- ✅ Organize Downloads folder by file type
- ✅ Undo Downloads organization
- ✅ Show command history
- ✅ Colorized output (green/yellow/red)

---

## Installation

### 1) Create virtual environment

```powershell
python -m venv os-env
```

### 2) Activate environment (PowerShell)

```powershell
.\os-env\Scripts\Activate.ps1
```

### 3) Install NovaOS

```powershell
python -m pip install -e .
```

### 4) Verify

```powershell
nova --help
```

---

## AI Setup (.env)

Create a `.env` file in project root.

### Recommended (Groq)

```env
AI_PROVIDER="groq"
GROQ_API_KEY="your_groq_api_key"
GROQ_MODEL="llama-3.3-70b-versatile"
AI_SUMMARY_MAX_CHARS="5000"
```

### Optional (Gemini)

```env
AI_PROVIDER="gemini"
GEMINI_API_KEY="your_gemini_api_key"
GEMINI_MODEL="gemini-2.0-flash"
AI_SUMMARY_MAX_CHARS="5000"
```

---

## How to use

You can use both styles:

```powershell
nova "hello"
nova command "hello"
```

### Common commands

```powershell
nova "hello"
nova "system"
nova "analyze project"
nova "fix import"
nova "fix import" --force
nova "undo import"
nova "organize downloads"
nova "organize downloads" --force
nova "undo"
nova history
```

---

## Safe workflow (recommended)

For import cleanup, always do this:

1. Dry run first:

```powershell
nova "fix import"
```

2. Apply changes:

```powershell
nova "fix import" --force
```

3. If needed, rollback:

```powershell
nova "undo import"
```

NovaOS stores removed imports in `import_log.json` and uses it for restore.

---

## Output files you will see

- `novaos_report_YYYYMMDD_HHMMSS.json` → analysis report
- `import_log.json` → temporary undo log for import fixes

---

## Troubleshooting

### `Unknown command`
Use supported phrases like:

- `analyze project`
- `fix import`
- `undo import`
- `organize downloads`

### `nova` command not found

```powershell
python -m pip install -e .
```

Also confirm virtual environment is active.

### AI summary not working

- Check API key in `.env`
- Check provider (`AI_PROVIDER`)
- Reduce `AI_SUMMARY_MAX_CHARS` if request is too large

---

## Final note

NovaOS is built to reduce repetitive terminal work and give you quick, reversible automation while coding.

---

Author: NIGAM
