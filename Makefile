.PHONY: all update

activate_env := . activate && conda activate scraper
csvdir := category

all: update README.md category/letters category/agencies

update:
	@$(activate_env) && python scraper.py

README.md: CONTENT.md latest.csv
	@cat CONTENT.md > README.md && $(activate_env) && python append_readme_table.py

category/letters: latest.csv
	@$(activate_env) && python generate_mailid_mds.py

category/agencies: latest.csv
	@$(activate_env) && python generate_reply_agency_mds.py
