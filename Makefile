VENV := .venv
BIN := $(VENV)/bin
SCRIPT_DIR := scripts

all: update README.md category/letters category/agencies

.PHONY: update
update:
	@$(BIN)/python $(SCRIPT_DIR)/scraper.py

README.md: CONTENT.md latest.csv
	@cat CONTENT.md > README.md && $(BIN)/python $(SCRIPT_DIR)/append_readme_table.py && $(BIN)/python $(SCRIPT_DIR)/plots.py

category/letters: latest.csv
	@$(BIN)/python $(SCRIPT_DIR)/generate_mailid_mds.py

category/agencies: latest.csv
	@$(BIN)/python $(SCRIPT_DIR)/generate_reply_agency_mds.py

create_environment:
	python -m venv $(VENV) && $(BIN)/pip install -r requirements.txt
