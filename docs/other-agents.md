# Using ux-auditor With Other Agents (and in CI without an Agent)

`ux-auditor` is designed to be fully portable. `SKILL.md` is an open standard supported by Claude Code, Google Antigravity, Gemini CLI, OpenAI Codex, and Cursor. The underlying scanners and report pipeline are plain Python that can run anywhere without an AI agent, including in CI/CD pipelines.

---

## 1. Feature Support Matrix

| Capability | Claude Code | Antigravity / Gemini CLI | Codex / Cursor | Standalone / CI (No Agent) |
|---|---|---|---|---|
| Static UX code scanner (`ux_scan.py`) | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Dual-viewport runtime Playwright audit (`ux_runtime.py`) | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Report & Action Plan pipeline (`ux_report.py`) | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Skills (audits, remedies, standards) | ✅ Automatic | ✅ After 1-line install | ✅ After 1-line install | As markdown manuals |
| 7 Specialist Agents in parallel | ✅ Yes | ✅ Yes (Subagents) | Sequential fallback | N/A |
| Namespaced commands (`/ux audit`, `/ux scan`) | ✅ Yes | ✅ Yes (via Skill trigger) | ✅ Yes | CLI arguments |

---

## 2. Installing Skills Into Other Agents

Use the included `install_skills.py` script:

```bash
# Clone the repository if not already cloned:
git clone https://github.com/Capzel/ux-auditor.git
cd ux-auditor

# Google Antigravity / Gemini CLI: install to ~/.gemini/skills (user) or .gemini/skills (project)
python3 scripts/install_skills.py --agent antigravity --scope user

# OpenAI Codex: install to ~/.agents/skills (user) or .agents/skills (project)
python3 scripts/install_skills.py --agent codex --scope project

# Custom directory (Cursor, Claude, or any tool reading SKILL.md):
python3 scripts/install_skills.py --dir ~/.cursor/skills
```

> [!NOTE]
> The installer rewrites `${CLAUDE_PLUGIN_ROOT}` to the absolute path of your checkout so bundled scripts and data files resolve cleanly in all agents.

---

## 3. Running Without an Agent (Scripts Only in CI/CD)

You can run the scanners and report generator in your terminal or GitHub Actions without any LLM API calls:

```bash
# 1. Static codebase scan
python3 scripts/ux_scan.py . --output scan.json
python3 scripts/ux_scan.py . --format summary

# 2. Dual-viewport Playwright runtime check (if web server is running)
python3 scripts/ux_runtime.py --url http://localhost:3000 \
        --pages / /login /checkout \
        --output runtime.json \
        --screenshots ./screenshots

# 3. Merge & Render reports
python3 scripts/ux_report.py merge --audit-dir ./ux-audit/run
python3 scripts/ux_report.py render --data ./ux-audit/run/audit-data.json
```

### GitHub Actions CI Example:

```yaml
name: UX & Usability Audit
on: [push, pull_request]

jobs:
  ux-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run UX Static Scanner
        run: |
          python3 scripts/ux_scan.py . --output ux-scan.json
          python3 - <<'PY'
          import json, sys
          data = json.load(open("ux-scan.json"))
          critical = [s for s in data["signals"] if s["severity"] == "critical"]
          if critical:
              print(f"::error::{len(critical)} critical UX defects detected!")
              for c in critical:
                  print(f"  • {c['rule_id']}: {c['title']} at {c['file']}:{c.get('line')}")
              sys.exit(1)
          print("✅ No critical UX blockers found.")
          PY

      - name: Upload UX Scan Results
        uses: actions/upload-artifact@v4
        with:
          name: ux-scan-report
          path: ux-scan.json
```
