.PHONY: update update_history

activate_env := . activate && conda activate scraper
csvdir := history
first_file := first_run.csv

update: update_history latest.csv readme_table.csv README.md history/letters history/agencies

update_history:
	@$(activate_env) && python scraper.py

latest.csv:$(csvdir)
	@$(shell if [ -f latest.csv ];then head -1 latest.csv > latest.csv.tmp && mv latest.csv.tmp latest.csv;else head -1 $(csvdir)/$(first_file) > latest.csv;fi)
	@for i in $(shell ls -t $(csvdir));do tail -n +2 $(csvdir)/$$i >> latest.csv; done

readme_table.md: latest.csv
	@$(activate_env) && python generate_readme_table.py

README.md: CONTENT.md readme_table.md
	@cat CONTENT.md > README.md && cat readme_table.md  >> README.md

history/letters: latest.csv
	@$(activate_env) && python generate_mailid_mds.py

history/agencies: latest.csv
	@$(activate_env) && python generate_reply_agency_mds.py
