VENV := .venv
BIN := $(VENV)/bin

all: update README.md category/letters category/agencies

.PHONY: update
update:
	@$(BIN)/python scraper.py

README.md: CONTENT.md latest.csv
	@cat CONTENT.md > README.md && $(BIN)/python append_readme_table.py && $(BIN)/python plots.py

category/letters: latest.csv
	@$(BIN)/python generate_mailid_mds.py

category/agencies: latest.csv
	@$(BIN)/python generate_reply_agency_mds.py

create_environment:
	python -m venv $(VENV) && $(BIN)/pip install -r requirements.txt
