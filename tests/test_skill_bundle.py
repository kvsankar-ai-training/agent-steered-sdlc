from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "agent-steered-sdlc"


def source_files(folder: str, pattern: str) -> list[Path]:
    return sorted((ROOT / folder).glob(pattern), key=lambda path: path.name)


def assert_bundled_files_match(folder: str, pattern: str) -> None:
    sources = source_files(folder, pattern)
    bundled = sorted((SKILL / folder).glob(pattern), key=lambda path: path.name)

    assert [path.name for path in bundled] == [path.name for path in sources]
    for source in sources:
        copy = SKILL / folder / source.name
        assert copy.read_bytes() == source.read_bytes()


def test_agent_steered_sdlc_skill_bundles_all_prompts() -> None:
    assert_bundled_files_match("prompts", "*.prompt.md")


def test_agent_steered_sdlc_skill_bundles_all_checkers() -> None:
    assert_bundled_files_match("checkers", "*.py")
