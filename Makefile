.PHONY: all update

activate_env := source .venv/bin/activate
csvdir := category

all: update README.md category/letters category/agencies

update:
	@$(activate_env) && python scraper.py

README.md: CONTENT.md latest.csv
	@cat CONTENT.md > README.md && $(activate_env) && python append_readme_table.py && python plots.py

category/letters: latest.csv
	@$(activate_env) && python generate_mailid_mds.py

category/agencies: latest.csv
	@$(activate_env) && python generate_reply_agency_mds.py

create_environment:
	pip -m venv .venv && $(activate_env) && pip install -r requirements.txt
