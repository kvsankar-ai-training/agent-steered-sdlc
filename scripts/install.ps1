param(
    [string]$TargetRoot = (Get-Location).Path,
    [string[]]$Tool = @("all"),
    [ValidateSet("project", "user")]
    [string]$Scope = "project",
    [switch]$NoCheckers,
    [switch]$NoCrossInstall
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PromptSource = Join-Path $RepoRoot "prompts"
$CheckerSource = Join-Path $RepoRoot "checkers"
$SkillSource = Join-Path $RepoRoot "skills/agent-steered-sdlc"
$TargetRoot = (Resolve-Path -LiteralPath $TargetRoot).Path

if (-not (Test-Path -LiteralPath $PromptSource)) {
    throw "Prompt source folder not found: $PromptSource"
}
if (-not $NoCheckers -and -not (Test-Path -LiteralPath $CheckerSource)) {
    throw "Checker source folder not found: $CheckerSource"
}
if (-not (Test-Path -LiteralPath $SkillSource)) {
    throw "Skill source folder not found: $SkillSource"
}

$AllowedTools = @("all", "codex", "copilot", "claude-code", "gemini", "claude", "pi")
$Tool = @(
    $Tool | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ }
)
$invalidTools = @($Tool | Where-Object { $AllowedTools -notcontains $_ })
if ($invalidTools.Count -gt 0) {
    throw "Unknown tool(s): $($invalidTools -join ', '). Allowed: $($AllowedTools -join ', ')"
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

function Copy-Checkers {
    if ($NoCheckers) {
        return
    }
    $dest = Join-Path $TargetRoot "checkers"
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
    $dest = Join-Path $TargetRoot ".github/prompts"
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -LiteralPath $PromptSource -Filter "*.prompt.md" | Copy-Item -Destination $dest -Force
    Write-Host "Installed GitHub Copilot prompts -> $dest"
}

function Install-Codex {
    if ($Scope -eq "user") {
        $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
        $skillDest = Join-Path $codexHome "skills/agent-steered-sdlc"
    } else {
        $skillDest = Join-Path $TargetRoot ".codex/skills/agent-steered-sdlc"
    }
    Copy-SkillFolder $skillDest
    Write-Host "Installed Codex skill -> $skillDest"
}

function Install-ClaudeCode {
    if ($Scope -eq "user") {
        $dest = Join-Path $HOME ".claude/commands"
        $skillDest = Join-Path $HOME ".claude/skills/agent-steered-sdlc"
    } else {
        $dest = Join-Path $TargetRoot ".claude/commands"
        $skillDest = Join-Path $TargetRoot ".claude/skills/agent-steered-sdlc"
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

function Install-WslCompanion {
    if ($NoCrossInstall) {
        return
    }
    if (-not (Test-WslAvailable)) {
        Write-Host "WSL not available; skipping WSL companion install."
        return
    }

    $repoWsl = ConvertTo-WslPath $RepoRoot
    $targetWsl = ConvertTo-WslPath $TargetRoot
    $scriptWsl = "$repoWsl/scripts/install.sh"
    $toolList = $Tool -join ","
    $args = @($scriptWsl, "--target", $targetWsl, "--scope", $Scope, "--tools", $toolList, "--no-cross-install")
    if ($NoCheckers) {
        $args += "--no-checkers"
    }

    Write-Host "Installing WSL companion targets via $scriptWsl"
    & wsl.exe bash @args
    if ($LASTEXITCODE -ne 0) {
        throw "WSL companion install failed with exit code $LASTEXITCODE"
    }
}

$expandedTools = if ($Tool -contains "all") {
    @("codex", "copilot", "claude-code", "gemini", "claude", "pi")
} else {
    $Tool
}

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

Write-Host "Install complete for target: $TargetRoot"
