# Install / Update

This skill is a folder named `promptrefinelab`.

## Install the `prl` CLI (required to execute runs)

From the repo root:

```bash
uv pip install -e .
```

## Option A: User-level install (Codex)

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/PromptRefineLab/skills/promptrefinelab ~/.codex/skills/
```

## Option B: Project-level install

```bash
mkdir -p ./.codex/skills
cp -R /path/to/PromptRefineLab/skills/promptrefinelab ./.codex/skills/
```

## Claude skill locations (manual, verify in your environment)

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/PromptRefineLab/skills/promptrefinelab ~/.claude/skills/
```

```bash
mkdir -p ./.claude/skills
cp -R /path/to/PromptRefineLab/skills/promptrefinelab ./.claude/skills/
```

## Claude packaging (zip)

Create a zip where the skill folder is the root:

```
promptrefinelab.zip
└── promptrefinelab/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

## Option C: One-command install (script)

```bash
./scripts/install_skill.sh --user
./scripts/install_skill.sh --repo
```

## Package as .skill (zip)

```bash
./scripts/package_skill.sh
```

## Update

Re-run the same copy command to overwrite the existing folder.
