import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "generated_scripts"


def load_agent(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def format_product_catalog(catalog: dict) -> str:
    tiers = catalog.get("tiers", [])
    modules = catalog.get("industry_modules", [])
    integrations = catalog.get("integrations", [])
    compliance = catalog.get("compliance", [])

    tier_lines = [
        f"- {t['name']}: {t['price_aed']} | Timeline: {t['timeline']} | Best for: {t['best_for']}"
        for t in tiers
    ]
    module_lines = [f"- {m}" for m in modules]
    integration_lines = [f"- {i}" for i in integrations]
    compliance_lines = [f"- {c}" for c in compliance]

    return dedent(
        f"""
        Product Catalog
        Tiers:
        {chr(10).join(tier_lines)}

        Industry Modules:
        {chr(10).join(module_lines)}

        Integrations:
        {chr(10).join(integration_lines)}

        Compliance Stack:
        {chr(10).join(compliance_lines)}
        """
    ).strip()


def build_multi_turn_script(agent: dict) -> str:
    name = agent["persona_name"]
    business = agent["company_business"]
    purpose = agent["conversation_purpose"]
    target = agent.get("target_persona", "Decision-maker")
    pains = agent.get("key_pains", [])
    discovery = agent.get("discovery_questions", [])
    objections = agent.get("objection_handlers", [])

    pain_list = "\n".join([f"- {p}" for p in pains])
    discovery_list = "\n".join([f"- {q}" for q in discovery])

    objection_blocks = []
    for i, obj in enumerate(objections, start=1):
        objection_blocks.append(
            dedent(
                f"""
                Turn {6 + i} - Objection Handling #{i}
                Prospect: "{obj['objection']}"
                Agent: "{obj['response']}"
                """
            ).strip()
        )

    objections_text = "\n\n".join(objection_blocks)

    return dedent(
        f"""
        ==================================================
        {agent['company_name']} | Multi-Turn Sales Script
        Persona: {name}
        Target: {target}
        Goal: {purpose}
        ==================================================

        Positioning:
        {business}

        Top Pain Hooks:
        {pain_list}

        Discovery Questions:
        {discovery_list}

        {format_product_catalog(agent['product_catalog'])}

        ------------------ CALL FLOW ------------------
        Turn 1 - Pattern Interrupt Opener
        Agent: "Hi [Name], this is [Agent Name] from {agent['company_name']}. We help UAE operators replace spreadsheets, WhatsApp threads, and disconnected systems with fixed-price, fixed-timeline Odoo + AI delivery. Can I take 90 seconds?"

        Turn 2 - Permission + Relevance
        Prospect: "Depends, what is this about?"
        Agent: "You're likely balancing finance accuracy, operations speed, and compliance pressure at once. We help teams close faster and stay audit-ready without long ERP projects."

        Turn 3 - Qualification
        Agent: "Before I continue, are you currently involved in approving systems or should we include Finance/CFO/Operations in the next call?"

        Turn 4 - Discovery + Cost of Inaction
        Agent: "To see if this is relevant: how long is month-end close today, where do manual reconciliations happen, and how much team time is consumed every week?"

        Turn 5 - Tailored Pitch
        Agent: "Based on what you shared, this is exactly where our {name} package fit is strongest. We deploy in phases, align to UAE compliance from day one, and link finance to operations with live dashboards and AI copilots."

        {objections_text}

        Turn {6 + len(objections) + 1} - Meeting Lock
        Agent: "Best next step is a 30-minute scoping call where we map your current flow and show the target architecture with ROI ranges. I can do Tuesday 10:00 or Thursday 14:00 UAE time. Which is better?"

        Turn {6 + len(objections) + 2} - Follow-Up WhatsApp
        Agent: "Thanks [Name]. As promised, I’ll send your tailored scope summary and module map. Confirming our scoping call on [Day, Time UAE]."
        """
    ).strip() + "\n"


def write_output(input_file: Path, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = input_file.stem.replace("_agent", "_multi_turn_script") + ".txt"
    out_path = OUTPUT_DIR / out_name
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main() -> None:
    input_files = [
        ROOT / "sgc_real_estate_agent.json",
        ROOT / "sgc_construction_agent.json",
        ROOT / "sgc_heavy_industry_agent.json",
    ]

    missing = [str(p.name) for p in input_files if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing input files: {', '.join(missing)}")

    for path in input_files:
        agent = load_agent(path)
        script = build_multi_turn_script(agent)
        out = write_output(path, script)
        print(f"Generated: {out}")


if __name__ == "__main__":
    main()
