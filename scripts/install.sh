#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_SOURCE="$REPO_ROOT/prompts"
CHECKER_SOURCE="$REPO_ROOT/checkers"
SKILL_SOURCE="$REPO_ROOT/skills/agent-steered-sdlc"

TARGET_ROOT="$(pwd)"
SCOPE="project"
TOOLS="all"
NO_CHECKERS=0
NO_CROSS_INSTALL=0

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [options]

Options:
  --target <dir>        Target product workspace. Default: current directory.
  --scope <project|user>
                        Install project-local commands or user-global commands.
                        Default: project.
  --tools <list>        Comma-separated: all,codex,copilot,claude-code,gemini,claude,pi.
                        Default: all.
  --no-checkers         Do not copy checkers/ into the target workspace.
  --no-cross-install    Do not install companion targets across Windows/WSL.
  -h, --help            Show this help.

Notes:
  - GitHub Copilot prompts install to <target>/.github/prompts.
  - Codex skills install to <target>/.codex/skills or ~/.codex/skills.
  - Claude Code commands install to <target>/.claude/commands or ~/.claude/commands,
    and the skill installs to <target>/.claude/skills or ~/.claude/skills.
  - Gemini CLI commands install to <target>/.gemini/commands or ~/.gemini/commands.
  - Claude and Pi exports install to .ai-prompts/ because they do not expose a stable
    local slash-command folder.
  - When run in WSL, this script also installs Windows companion targets if
    powershell.exe is available. Use --no-cross-install to disable that.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_ROOT="$2"
      shift 2
      ;;
    --scope)
      SCOPE="$2"
      shift 2
      ;;
    --tools)
      TOOLS="$2"
      shift 2
      ;;
    --no-checkers)
      NO_CHECKERS=1
      shift
      ;;
    --no-cross-install)
      NO_CROSS_INSTALL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

TARGET_ROOT="$(cd "$TARGET_ROOT" && pwd)"

if [[ ! -d "$PROMPT_SOURCE" ]]; then
  echo "Prompt source folder not found: $PROMPT_SOURCE" >&2
  exit 1
fi
if [[ "$NO_CHECKERS" -eq 0 && ! -d "$CHECKER_SOURCE" ]]; then
  echo "Checker source folder not found: $CHECKER_SOURCE" >&2
  exit 1
fi
if [[ ! -d "$SKILL_SOURCE" ]]; then
  echo "Skill source folder not found: $SKILL_SOURCE" >&2
  exit 1
fi
if [[ "$SCOPE" != "project" && "$SCOPE" != "user" ]]; then
  echo "--scope must be project or user" >&2
  exit 2
fi

command_name() {
  local file="$1"
  basename "$file" .prompt.md
}

prompt_body() {
  awk '
    BEGIN { in_fm = 0; done = 0 }
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { in_fm = 0; done = 1; next }
    !in_fm { print }
  ' "$1"
}

prompt_description() {
  local line
  line="$(grep -m 1 '^description:' "$1" || true)"
  if [[ -n "$line" ]]; then
    printf '%s\n' "${line#description: }"
  else
    printf '%s\n' "Command prompt installed from commands repository."
  fi
}

toml_escape_basic() {
  sed 's/\\/\\\\/g; s/"/\\"/g'
}

copy_checkers() {
  if [[ "$NO_CHECKERS" -eq 1 ]]; then
    return
  fi
  local dest="$TARGET_ROOT/checkers"
  mkdir -p "$dest"
  cp "$CHECKER_SOURCE"/check_*.py "$dest"/
  echo "Installed checkers -> $dest"
}

copy_skill_folder() {
  local dest="$1"
  mkdir -p "$dest"
  cp -R "$SKILL_SOURCE"/. "$dest"/
}

install_copilot() {
  local dest="$TARGET_ROOT/.github/prompts"
  mkdir -p "$dest"
  cp "$PROMPT_SOURCE"/*.prompt.md "$dest"/
  echo "Installed GitHub Copilot prompts -> $dest"
}

install_codex() {
  local skill_dest codex_home
  if [[ "$SCOPE" == "user" ]]; then
    codex_home="${CODEX_HOME:-$HOME/.codex}"
    skill_dest="$codex_home/skills/agent-steered-sdlc"
  else
    skill_dest="$TARGET_ROOT/.codex/skills/agent-steered-sdlc"
  fi
  copy_skill_folder "$skill_dest"
  echo "Installed Codex skill -> $skill_dest"
}

install_claude_code() {
  local dest skill_dest
  if [[ "$SCOPE" == "user" ]]; then
    dest="$HOME/.claude/commands"
    skill_dest="$HOME/.claude/skills/agent-steered-sdlc"
  else
    dest="$TARGET_ROOT/.claude/commands"
    skill_dest="$TARGET_ROOT/.claude/skills/agent-steered-sdlc"
  fi
  mkdir -p "$dest"
  for file in "$PROMPT_SOURCE"/*.prompt.md; do
    prompt_body "$file" > "$dest/$(command_name "$file").md"
  done
  echo "Installed Claude Code slash commands -> $dest"
  copy_skill_folder "$skill_dest"
  echo "Installed Claude Code skill -> $skill_dest"
}

install_gemini() {
  local dest
  if [[ "$SCOPE" == "user" ]]; then
    dest="$HOME/.gemini/commands"
  else
    dest="$TARGET_ROOT/.gemini/commands"
  fi
  mkdir -p "$dest"
  for file in "$PROMPT_SOURCE"/*.prompt.md; do
    if grep -q "'''" "$file"; then
      echo "Cannot write Gemini TOML for $(basename "$file"): prompt contains triple single quotes." >&2
      exit 1
    fi
    local name description
    name="$(command_name "$file")"
    description="$(prompt_description "$file" | toml_escape_basic)"
    {
      printf 'description = "%s"\n' "$description"
      printf "prompt = '''\n"
      prompt_body "$file"
      printf "\n'''\n"
    } > "$dest/$name.toml"
  done
  echo "Installed Gemini CLI commands -> $dest"
}

install_claude_export() {
  local dest
  if [[ "$SCOPE" == "user" ]]; then
    dest="$HOME/.ai-prompts/claude"
  else
    dest="$TARGET_ROOT/.ai-prompts/claude"
  fi
  mkdir -p "$dest"
  for file in "$PROMPT_SOURCE"/*.prompt.md; do
    prompt_body "$file" > "$dest/$(command_name "$file").md"
  done
  copy_skill_folder "$dest/skills/agent-steered-sdlc"
  echo "Exported Claude prompt pack -> $dest"
  echo "Note: Claude web/desktop has no stable local slash-command folder; import/copy these prompts manually."
}

install_pi_export() {
  local dest
  if [[ "$SCOPE" == "user" ]]; then
    dest="$HOME/.ai-prompts/pi"
  else
    dest="$TARGET_ROOT/.ai-prompts/pi"
  fi
  mkdir -p "$dest"
  for file in "$PROMPT_SOURCE"/*.prompt.md; do
    prompt_body "$file" > "$dest/$(command_name "$file").md"
  done
  copy_skill_folder "$dest/skills/agent-steered-sdlc"
  echo "Exported Pi prompt pack -> $dest"
  echo "Note: Pi has no stable local slash-command folder; import/copy these prompts manually."
}

copy_checkers

is_wsl() {
  [[ -n "${WSL_DISTRO_NAME:-}" ]] || grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null
}

install_windows_companion() {
  if [[ "$NO_CROSS_INSTALL" -eq 1 ]]; then
    return
  fi
  if ! is_wsl; then
    return
  fi
  if ! command -v powershell.exe >/dev/null 2>&1; then
    echo "powershell.exe not available; skipping Windows companion install."
    return
  fi
  if ! command -v wslpath >/dev/null 2>&1; then
    echo "wslpath not available; skipping Windows companion install."
    return
  fi

  local repo_win target_win script_win
  repo_win="$(wslpath -w "$REPO_ROOT")"
  target_win="$(wslpath -w "$TARGET_ROOT")"
  script_win="$repo_win\\scripts\\install.ps1"

  local args=(
    -NoProfile
    -ExecutionPolicy Bypass
    -File "$script_win"
    -TargetRoot "$target_win"
    -Tool "$TOOLS"
    -Scope "$SCOPE"
    -NoCrossInstall
  )
  if [[ "$NO_CHECKERS" -eq 1 ]]; then
    args+=(-NoCheckers)
  fi

  echo "Installing Windows companion targets via $script_win"
  powershell.exe "${args[@]}"
}

if [[ "$TOOLS" == "all" ]]; then
  TOOL_LIST=("codex" "copilot" "claude-code" "gemini" "claude" "pi")
else
  IFS=',' read -r -a TOOL_LIST <<< "$TOOLS"
fi

for tool in "${TOOL_LIST[@]}"; do
  case "$tool" in
    codex) install_codex ;;
    copilot) install_copilot ;;
    claude-code) install_claude_code ;;
    gemini) install_gemini ;;
    claude) install_claude_export ;;
    pi) install_pi_export ;;
    *) echo "Unknown tool: $tool" >&2; exit 2 ;;
  esac
done

install_windows_companion

echo "Install complete for target: $TARGET_ROOT"
