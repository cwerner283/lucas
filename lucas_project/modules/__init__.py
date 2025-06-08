"""Domain modules for Lucas project."""

from importlib import import_module

MODULES = [
    "lucas_project.modules.1_trend_discovery",
    "lucas_project.modules.2_domain_generator",
]

for mod in MODULES:
    import_module(mod)


