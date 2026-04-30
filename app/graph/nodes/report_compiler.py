import os
import json
from datetime import datetime
from weasyprint import HTML


class ReportCompiler:

    def __init__(self, config):
        self.config = config

    def status_icon(self, status):
        return {"red": "🔴", "amber": "🟡", "green": "🟢"}.get(status, "⚪")

    def run(self, state):

        print("FINAL STATE KPIs:", state.get("kpis"))

        report_id = state["request_id"]
        folder = f"reports/{report_id}"
        os.makedirs(folder, exist_ok=True)

        kpis = state.get("kpis", [])
        forecast = state.get("forecast", [])
        recommendations = state.get("recommendations", [])

        # SORT KPIs
        kpis = sorted(kpis, key=lambda x: x.get("gap_pct", 0))

        # KPI TABLE
        kpi_rows = ""
        for k in kpis:
            kpi_rows += f"""
            <tr>
                <td>{k.get('kpi_name', k.get('raw_kpi', 'Unknown KPI'))}</td>
                <td>{k['company_value']}</td>
                <td>{k['peer_value']}</td>
                <td>{round(k['gap_pct'],2)}%</td>
                <td>{self.status_icon(k['status'])}</td>
            </tr>
            """

        # EXECUTIVE SUMMARY
        worst_kpis = kpis[:2] if len(kpis) >= 2 else kpis

        if worst_kpis:
            summary = f"""
            {state['company']} shows the most significant ESG gaps in 
            <b>{worst_kpis[0]['kpi_name']}</b>
            """
            if len(worst_kpis) > 1:
                summary += f" and <b>{worst_kpis[1]['kpi_name']}</b>"

            summary += """
            These gaps indicate operational inefficiencies relative to peer benchmarks.
            """
        else:
            summary = f"""
            {state['company']} is broadly aligned with ESG peer benchmarks.
            """

        if forecast:
            summary += f"""
            Emissions are projected to move from {forecast[0]} to {forecast[-1]} 
            over the next 5 years.
            """

        # PRIORITY SECTION
        priority_section = ""
        if kpis:
            worst = kpis[0]
            priority_section = f"""
            <h2>Top Priority Area</h2>
            <p>
            Immediate focus is required on <b>{worst['kpi_name']}</b>.
            </p>
            """

        # HTML BASE
        html_content = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial; padding: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; }}
            th {{ background-color: #f4f4f4; }}
        </style>
        </head>
        <body>

        <h1>ESG Strategy Report</h1>
        <p><b>Company:</b> {state['company']}</p>
        <p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}</p>

        <h2>Executive Summary</h2>
        <p>{summary}</p>

        {priority_section}

        <h2>KPI Scorecard</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Company</th>
                <th>Peer Avg</th>
                <th>Gap %</th>
                <th>Status</th>
            </tr>
            {kpi_rows}
        </table>

        <h2>Top Recommendations</h2>
        """

        # RECOMMENDATIONS
        for rec in recommendations[:3]:
            html_content += f"""
            <div>
                <b>{rec['kpi_name']}</b>
                <ul>
            """

            lines = rec["content"].split("-")
            for line in lines:
                clean = line.strip()
                if clean:
                    html_content += f"<li>{clean}</li>"

            html_content += """
                </ul>
            </div>
            """

        # TRAJECTORY
        if forecast:
            html_content += f"""
            <h2>5-Year Carbon Trajectory</h2>
            <p>
            Emissions projected from {forecast[0]} to {forecast[-1]}.
            </p>
            """

        html_content += """
        </body>
        </html>
        """

        # SAVE FILES
        html_path = f"{folder}/report.html"
        pdf_path = f"{folder}/report.pdf"
        json_path = f"{folder}/report.json"

        with open(html_path, "w") as f:
            f.write(html_content)

        HTML(html_path).write_pdf(pdf_path)

        with open(json_path, "w") as f:
            json.dump(state, f, indent=2)

        state["report_path"] = pdf_path
        return state