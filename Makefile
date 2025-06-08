.PHONY: dev test run dash

DEV?=python -m venv .venv && ./.venv/bin/pip install -r requirements.txt

dev:
$(DEV)

test:
pytest -q

run:
python main.py

dash:
cd lucas_project/dashboard/ui && npm run dev
