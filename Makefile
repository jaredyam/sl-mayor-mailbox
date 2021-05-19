VENV := .venv
BIN := $(VENV)/bin
SCRIPT_DIR := scripts

all: update README.md categories/mails categories/agencies

.PHONY: update
update:
	@$(BIN)/python $(SCRIPT_DIR)/scraper.py

README.md: CONTENT.md latest.csv
	@cat CONTENT.md > README.md && $(BIN)/python $(SCRIPT_DIR)/append_readme_table.py && $(BIN)/python $(SCRIPT_DIR)/plots.py

categories/mails: latest.csv
	@$(BIN)/python $(SCRIPT_DIR)/generate_mailid_mds.py

categories/agencies: latest.csv
	@$(BIN)/python $(SCRIPT_DIR)/generate_reply_agency_mds.py

create_environment:
	python -m venv $(VENV) && $(BIN)/pip install -r requirements.txt
