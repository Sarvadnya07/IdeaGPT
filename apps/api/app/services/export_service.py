import json
from typing import Dict, Any

class ExportService:
    @staticmethod
    def to_json(result_payload: dict) -> str:
        """
        Exports the result payload as a formatted JSON string.
        """
        return json.dumps(result_payload, indent=2)

    @staticmethod
    def to_markdown(result_payload: dict) -> str:
        """
        Exports the evaluation results as a clean Markdown report.
        """
        summary = result_payload.get("summary", "No summary provided.")
        score = result_payload.get("score", 70)
        strengths = "\n".join(f"- {s}" for s in result_payload.get("strengths", []))
        weaknesses = "\n".join(f"- {w}" for w in result_payload.get("weaknesses", []))
        recs = "\n".join(f"- {r}" for r in result_payload.get("recommendations", []))
        arch = result_payload.get("architecture_breakdown", "No architectural breakdown.")

        md = f"""# AI Idea Evaluation Report
## Overall Score: {score}/100

### Executive Summary
{summary}

### Key Strengths
{strengths}

### Potential Weaknesses
{weaknesses}

### Recommendations
{recs}

### Technical Feasibility & Architecture
{arch}
"""
        return md

    @staticmethod
    def to_pdf_mock(result_payload: dict) -> str:
        """
        Mock PDF exporting, returning formatted HTML content suitable for print-to-pdf pipelines.
        """
        md_content = ExportService.to_markdown(result_payload)
        html_formatted = f"""<html>
<head>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1, h2, h3 {{ color: #1a365d; }}
        pre {{ background: #f7fafc; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    {md_content.replace("\n", "<br/>")}
</body>
</html>"""
        return html_formatted

export_service = ExportService()
