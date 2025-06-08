"""Domain modules for Lucas project."""

from importlib import import_module

MODULES = [
    "lucas_project.modules.1_trend_discovery",
    "lucas_project.modules.2_domain_generator",
    "lucas_project.modules.3_availability_checker",
    "lucas_project.modules.4_valuation",
    "lucas_project.modules.5_monitoring",
    "lucas_project.modules.6_backordering",
    "lucas_project.modules.7_portfolio_manager",
    "lucas_project.modules.8_monetization",
]

for mod in MODULES:
    import_module(mod)


