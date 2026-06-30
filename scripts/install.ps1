param(
    [string]$TargetRoot = (Get-Location).Path,
    [string[]]$Tool = @(),
    [ValidateSet("project", "user")]
    [string]$Scope = "user",
    [switch]$NoCheckers,
    [switch]$NoCrossInstall,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PromptSource = Join-Path $RepoRoot "prompts"
$CheckerSource = Join-Path $RepoRoot "checkers"
$SkillSource = Join-Path $RepoRoot "skills/agent-steered-sdlc"
$TargetRoot = (Resolve-Path -LiteralPath $TargetRoot).Path

function Test-SamePath {
    param([string]$Left, [string]$Right)
    $leftResolved = (Resolve-Path -LiteralPath $Left).Path.TrimEnd('\', '/')
    $rightResolved = (Resolve-Path -LiteralPath $Right).Path.TrimEnd('\', '/')
    return [string]::Equals($leftResolved, $rightResolved, [System.StringComparison]::OrdinalIgnoreCase)
}

if (-not (Test-Path -LiteralPath $PromptSource)) {
    throw "Prompt source folder not found: $PromptSource"
}
if (-not $NoCheckers -and -not (Test-Path -LiteralPath $CheckerSource)) {
    throw "Checker source folder not found: $CheckerSource"
}
if (-not (Test-Path -LiteralPath $SkillSource)) {
    throw "Skill source folder not found: $SkillSource"
}
if (Test-SamePath $TargetRoot $RepoRoot) {
    Write-Warning (
        "TargetRoot is the commands repository itself. This is okay for dogfooding, " +
        "but project-local artifacts such as GitHub Copilot prompts and checkers will be " +
        "installed into the source checkout. Use -TargetRoot <product-workspace> for a product."
    )
}
if ($DryRun) {
    Write-Host "Dry run: no files will be written and no companion install will be executed."
}

$InstallableTools = @("codex", "copilot", "claude-code", "gemini", "claude", "pi")
$AllowedTools = $InstallableTools + @("all")
$Tool = @(
    $Tool | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ }
)
$invalidTools = @($Tool | Where-Object { $AllowedTools -notcontains $_ })
if ($invalidTools.Count -gt 0) {
    throw "Unknown tool(s): $($invalidTools -join ', '). Allowed: $($InstallableTools -join ', ')"
}

function Get-CommandName {
    param([System.IO.FileInfo]$File)
    return $File.Name -replace '\.prompt\.md$', ''
}

function Get-PromptBody {
    param([string]$Path)
    $text = Get-Content -LiteralPath $Path -Raw
    return ($text -replace '(?s)^---\s*.*?\s*---\s*', '')
}

function Get-PromptDescription {
    param([string]$Path)
    $text = Get-Content -LiteralPath $Path -Raw
    if ($text -match '(?m)^description:\s*(.+)$') {
        return $Matches[1].Trim()
    }
    return "Command prompt installed from commands repository."
}

function Get-CopilotPromptText {
    param([string]$Path)
    $text = Get-Content -LiteralPath $Path -Raw
    return ($text -replace '(?m)^agent:\s*agent\s*$', 'mode: agent')
}

function Copy-CodexPromptFiles {
    param([string]$Destination)
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $name = Get-CommandName $_
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $Destination "$name.md") -Force
    }
}

function Get-CodexDestinations {
    if ($Scope -eq "user") {
        $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
        return @{
            Skill = Join-Path $codexHome "skills/agent-steered-sdlc"
            Prompts = Join-Path $codexHome "prompts"
        }
    }
    return @{
        Skill = Join-Path $TargetRoot ".codex/skills/agent-steered-sdlc"
        Prompts = Join-Path $TargetRoot ".codex/prompts"
    }
}

function Get-CopilotPromptDestination {
    if ($Scope -ne "user") {
        return Join-Path $TargetRoot ".github/prompts"
    }
    if ($env:AGENT_SDLC_COPILOT_PROMPTS_DIR) {
        return $env:AGENT_SDLC_COPILOT_PROMPTS_DIR
    }
    if ($env:APPDATA) {
        return Join-Path $env:APPDATA "Code/User/prompts"
    }
    if ((Get-Variable -Name IsMacOS -ErrorAction SilentlyContinue) -and $IsMacOS) {
        return Join-Path $HOME "Library/Application Support/Code/User/prompts"
    }
    return Join-Path $HOME ".config/Code/User/prompts"
}

function Get-CopilotSkillDestinations {
    if ($Scope -eq "user") {
        return @(
            Join-Path $HOME ".copilot/skills/agent-steered-sdlc"
            Join-Path $HOME ".agents/skills/agent-steered-sdlc"
        )
    }
    return @(
        Join-Path $TargetRoot ".github/skills/agent-steered-sdlc"
        Join-Path $TargetRoot ".agents/skills/agent-steered-sdlc"
    )
}

function Write-DestinationSummary {
    param([string[]]$Entries)
    Write-Host "Destination folders:"
    if (-not $NoCheckers) {
        Write-Host "  Checkers -> $(Join-Path $TargetRoot 'checkers')"
    }
    foreach ($entry in $Entries) {
        switch ($entry) {
            "codex" {
                $dest = Get-CodexDestinations
                Write-Host "  Codex skill -> $($dest.Skill)"
                Write-Host "  Codex direct prompts -> $($dest.Prompts)"
                Write-Host "    Invoke as /prompts:spec-create, /prompts:design-create, etc. after restarting Codex."
            }
            "copilot" {
                Write-Host "  GitHub Copilot prompts -> $(Get-CopilotPromptDestination)"
                foreach ($skillDest in Get-CopilotSkillDestinations) {
                    Write-Host "  GitHub Copilot skill -> $skillDest"
                }
                if ($Scope -eq "user") {
                    Write-Host "    User-scoped VS Code prompt files plus Copilot CLI/agent skill locations."
                }
                Write-Host "    Reload Copilot CLI skills with /skills reload, then check /skills info agent-steered-sdlc."
            }
            "claude-code" {
                if ($Scope -eq "user") {
                    $cmdDest = Join-Path $HOME ".claude/commands"
                    $skillDest = Join-Path $HOME ".claude/skills/agent-steered-sdlc"
                } else {
                    $cmdDest = Join-Path $TargetRoot ".claude/commands"
                    $skillDest = Join-Path $TargetRoot ".claude/skills/agent-steered-sdlc"
                }
                Write-Host "  Claude Code commands -> $cmdDest"
                Write-Host "  Claude Code skill -> $skillDest"
            }
            "gemini" {
                $dest = if ($Scope -eq "user") {
                    Join-Path $HOME ".gemini/commands"
                } else {
                    Join-Path $TargetRoot ".gemini/commands"
                }
                Write-Host "  Gemini CLI commands -> $dest"
            }
            "claude" {
                $dest = if ($Scope -eq "user") {
                    Join-Path $HOME ".ai-prompts/claude"
                } else {
                    Join-Path $TargetRoot ".ai-prompts/claude"
                }
                Write-Host "  Claude prompt export -> $dest"
                Write-Host "  Claude skill export -> $(Join-Path $dest 'skills/agent-steered-sdlc')"
            }
            "pi" {
                $dest = if ($Scope -eq "user") {
                    Join-Path $HOME ".ai-prompts/pi"
                } else {
                    Join-Path $TargetRoot ".ai-prompts/pi"
                }
                Write-Host "  Pi prompt export -> $dest"
                Write-Host "  Pi skill export -> $(Join-Path $dest 'skills/agent-steered-sdlc')"
            }
        }
    }
}

function Copy-Checkers {
    if ($NoCheckers) {
        return
    }
    $dest = Join-Path $TargetRoot "checkers"
    if ($Scope -eq "user") {
        Write-Warning (
            "Checkers are project-local; installing them to " +
            "$TargetRoot\checkers even though Scope is user. Use -NoCheckers to skip them."
        )
    }
    if ($DryRun) {
        Write-Host "Would install checkers -> $dest"
        return
    }
    $sourceResolved = (Resolve-Path -LiteralPath $CheckerSource).Path.TrimEnd("\", "/")
    if (Test-Path -LiteralPath $dest) {
        $destResolved = (Resolve-Path -LiteralPath $dest).Path.TrimEnd("\", "/")
        if ($sourceResolved -ieq $destResolved) {
            Write-Host "Checker destination is source folder; skipping checker copy."
            return
        }
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $CheckerSource -Filter "check_*.py" | Copy-Item -Destination $dest -Force
    Write-Host "Installed checkers -> $dest"
}

function Copy-SkillFolder {
    param([string]$Destination)
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -Force -LiteralPath $SkillSource | Copy-Item -Destination $Destination -Recurse -Force
}

function Install-Copilot {
    $dest = Get-CopilotPromptDestination
    $skillDests = Get-CopilotSkillDestinations
    if ($DryRun) {
        Write-Host "Would install GitHub Copilot prompts -> $dest"
        foreach ($skillDest in $skillDests) {
            Write-Host "Would install GitHub Copilot skill -> $skillDest"
        }
        return
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $body = Get-CopilotPromptText $_.FullName
        Set-Content -LiteralPath (Join-Path $dest $_.Name) -Value $body -NoNewline
    }
    Write-Host "Installed GitHub Copilot prompts -> $dest"
    foreach ($skillDest in $skillDests) {
        Copy-SkillFolder $skillDest
        Write-Host "Installed GitHub Copilot skill -> $skillDest"
    }
    Write-Host "Copilot prompts are written in agent mode without a tools allowlist; restart VS Code to reload them."
    Write-Host "Copilot CLI can load the skill after a new session or /skills reload; check with /skills info agent-steered-sdlc."
}

function Install-Codex {
    $dest = Get-CodexDestinations
    if ($DryRun) {
        Write-Host "Would install Codex skill -> $($dest.Skill)"
        Write-Host "Would install Codex direct prompts -> $($dest.Prompts)"
        return
    }
    Copy-SkillFolder $dest.Skill
    Write-Host "Installed Codex skill -> $($dest.Skill)"
    Copy-CodexPromptFiles $dest.Prompts
    Write-Host "Installed Codex direct prompts -> $($dest.Prompts)"
    Write-Host "Codex direct prompts are available as /prompts:spec-create, /prompts:design-create, etc. after restart."
}

function Install-ClaudeCode {
    if ($Scope -eq "user") {
        $dest = Join-Path $HOME ".claude/commands"
        $skillDest = Join-Path $HOME ".claude/skills/agent-steered-sdlc"
    } else {
        $dest = Join-Path $TargetRoot ".claude/commands"
        $skillDest = Join-Path $TargetRoot ".claude/skills/agent-steered-sdlc"
    }
    if ($DryRun) {
        Write-Host "Would install Claude Code slash commands -> $dest"
        Write-Host "Would install Claude Code skill -> $skillDest"
        return
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $name = Get-CommandName $_
        $body = Get-PromptBody $_.FullName
        Set-Content -LiteralPath (Join-Path $dest "$name.md") -Value $body -NoNewline
    }
    Write-Host "Installed Claude Code slash commands -> $dest"
    Copy-SkillFolder $skillDest
    Write-Host "Installed Claude Code skill -> $skillDest"
}

function Install-Gemini {
    if ($Scope -eq "user") {
        $dest = Join-Path $HOME ".gemini/commands"
    } else {
        $dest = Join-Path $TargetRoot ".gemini/commands"
    }
    if ($DryRun) {
        Write-Host "Would install Gemini CLI commands -> $dest"
        return
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $name = Get-CommandName $_
        $description = Get-PromptDescription $_.FullName
        $body = Get-PromptBody $_.FullName
        if ($body.Contains("'''")) {
            throw "Cannot write Gemini TOML for $($_.Name): prompt contains triple single quotes."
        }
        $toml = @"
description = "$($description.Replace('"', '\"'))"
prompt = '''
$body
'''
"@
        Set-Content -LiteralPath (Join-Path $dest "$name.toml") -Value $toml -NoNewline
    }
    Write-Host "Installed Gemini CLI commands -> $dest"
}

function Install-ClaudeExport {
    if ($Scope -eq "user") {
        $dest = Join-Path $HOME ".ai-prompts/claude"
    } else {
        $dest = Join-Path $TargetRoot ".ai-prompts/claude"
    }
    if ($DryRun) {
        Write-Host "Would export Claude prompt pack -> $dest"
        Write-Host "Would include skill bundle -> $(Join-Path $dest 'skills/agent-steered-sdlc')"
        return
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $name = Get-CommandName $_
        $body = Get-PromptBody $_.FullName
        Set-Content -LiteralPath (Join-Path $dest "$name.md") -Value $body -NoNewline
    }
    Copy-SkillFolder (Join-Path $dest "skills/agent-steered-sdlc")
    Write-Host "Exported Claude prompt pack -> $dest"
    Write-Host "Note: Claude web/desktop has no stable local slash-command folder; import/copy these prompts manually."
}

function Install-PiExport {
    if ($Scope -eq "user") {
        $dest = Join-Path $HOME ".ai-prompts/pi"
    } else {
        $dest = Join-Path $TargetRoot ".ai-prompts/pi"
    }
    if ($DryRun) {
        Write-Host "Would export Pi prompt pack -> $dest"
        Write-Host "Would include skill bundle -> $(Join-Path $dest 'skills/agent-steered-sdlc')"
        return
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | ForEach-Object {
        $name = Get-CommandName $_
        $body = Get-PromptBody $_.FullName
        Set-Content -LiteralPath (Join-Path $dest "$name.md") -Value $body -NoNewline
    }
    Copy-SkillFolder (Join-Path $dest "skills/agent-steered-sdlc")
    Write-Host "Exported Pi prompt pack -> $dest"
    Write-Host "Note: Pi has no stable local slash-command folder; import/copy these prompts manually."
}

function Test-WslAvailable {
    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        return $false
    }
    $probe = & wsl.exe -e sh -lc "printf ready" 2>$null
    return ($LASTEXITCODE -eq 0 -and $probe -eq "ready")
}

function ConvertTo-WslPath {
    param([string]$WindowsPath)
    if ($WindowsPath -match "^([A-Za-z]):\\(.*)$") {
        $drive = $Matches[1].ToLowerInvariant()
        $rest = $Matches[2] -replace "\\", "/"
        return "/mnt/$drive/$rest"
    }

    $converted = & wsl.exe wslpath -a -u $WindowsPath 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $converted) {
        throw "Could not convert Windows path to WSL path: $WindowsPath"
    }
    return $converted.Trim()
}

function Invoke-WslInstallScript {
    param(
        [string]$ScriptPath,
        [string]$TargetPath,
        [string]$ScopeValue,
        [string]$ToolsValue,
        [bool]$SkipCheckers
    )

    $skipCheckersFlag = if ($SkipCheckers) { "1" } else { "0" }
    $runner = @'
script_path=$1
target_path=$2
scope_value=$3
tools_value=$4
skip_checkers=$5
repo_root=$(cd "$(dirname "$script_path")/.." && pwd -P)

tmp_script=$(mktemp)
trap 'rm -f "$tmp_script"' EXIT
tr -d '\r' < "$script_path" > "$tmp_script"
chmod +x "$tmp_script"

args=(--target "$target_path" --scope "$scope_value" --tools "$tools_value" --no-cross-install)
if [ "$skip_checkers" = "1" ]; then
  args=("${args[@]}" --no-checkers)
fi

AGENT_SDLC_REPO_ROOT="$repo_root" bash "$tmp_script" "${args[@]}"
'@

    & wsl.exe -e bash -lc $runner "agent-sdlc-install" $ScriptPath $TargetPath $ScopeValue $ToolsValue $skipCheckersFlag
}

function Install-WslCompanion {
    if ($NoCrossInstall) {
        return
    }
    if ($DryRun) {
        Write-Host "Would install WSL companion targets if WSL is available."
        return
    }
    if (-not (Test-WslAvailable)) {
        Write-Host "WSL not available; skipping WSL companion install."
        return
    }

    $repoWsl = ConvertTo-WslPath $RepoRoot
    $targetWsl = ConvertTo-WslPath $TargetRoot
    $scriptWsl = "$repoWsl/scripts/install.sh"
    $toolList = $expandedTools -join ","

    Write-Host "Installing WSL companion targets via $scriptWsl"
    Invoke-WslInstallScript `
        -ScriptPath $scriptWsl `
        -TargetPath $targetWsl `
        -ScopeValue $Scope `
        -ToolsValue $toolList `
        -SkipCheckers $NoCheckers
    if ($LASTEXITCODE -ne 0) {
        throw "WSL companion install failed with exit code $LASTEXITCODE"
    }
}

$expandedTools = if ($Tool.Count -eq 0 -or $Tool -contains "all") {
    $InstallableTools
} else {
    $Tool
}

Write-DestinationSummary $expandedTools

Copy-Checkers
foreach ($entry in $expandedTools) {
    switch ($entry) {
        "codex" { Install-Codex }
        "copilot" { Install-Copilot }
        "claude-code" { Install-ClaudeCode }
        "gemini" { Install-Gemini }
        "claude" { Install-ClaudeExport }
        "pi" { Install-PiExport }
    }
}

Install-WslCompanion

if ($DryRun) {
    Write-Host "Dry run complete for target: $TargetRoot"
} else {
    Write-Host "Install complete for target: $TargetRoot"
}
