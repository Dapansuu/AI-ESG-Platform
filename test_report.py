from app.graph.nodes.report_compiler import ReportCompiler  # change filename if needed

# 🔹 Dummy config
config = {}

# 🔹 Dummy state (simulate pipeline output)
state = {
    "request_id": "test123",
    "company": "ABC Corp",
    "kpis": [
        {
            "kpi_name": "Water Usage",
            "raw_kpi": "water",
            "company_value": 200,
            "peer_value": 150,
            "gap_pct": 25,
            "status": "amber",
            "performance": "worse"
        },
        {
            "kpi_name": "Carbon Emissions",
            "raw_kpi": "emissions",
            "company_value": 100,
            "peer_value": 70,
            "gap_pct": 30,
            "status": "red",
            "performance": "worse"
        }
    ],
    "forecast": [100, 110, 120, 130],
    "recommendations": [
        {"kpi_name": "Carbon Emissions", "content": "Reduce emissions"}
    ]
}

compiler = ReportCompiler(config)
result = compiler.run(state)

print("\nReport generated at:", result["report_path"])