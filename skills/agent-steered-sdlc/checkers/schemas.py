"""Shared structural schemas for agent-steered SDLC checker scripts."""

SPEC_SECTIONS = [
    "Mission Statement",
    "User Needs",
    "Non-Goals",
    "Features",
    "Use Cases",
    "Functional Requirements",
    "Non-Functional Requirements",
    "Acceptance Tests",
    "Traceability Matrix",
    "Assumptions & Open Questions",
]

DESIGN_SECTIONS = [
    "Overview",
    "Tech Stack",
    "Drivers & Constraints",
    "Layers",
    "Components",
    "Interfaces",
    ("Core vs. Shell", "Core vs. Shell / Equivalent Separation"),
    "Key Flows",
    "Data Model",
    "Design Decisions",
    "Test Strategy",
    "Risks & Trade-offs",
    "Traceability Matrix",
]

PLAN_SECTIONS = [
    "Overview",
    "Strategy",
    "Milestones",
    ("Pull Requests", "Pull Requests / Child Work Items"),
    "Coverage Map",
    "Sequencing & Risks",
]
