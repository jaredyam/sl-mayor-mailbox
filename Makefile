.PHONY: update update_history update_readme

update: update_history update_readme

update_history:
	@. activate && conda activate scraper && python scraper.py

csvdir := history
latest.csv: $(csvdir)
	@[ -n latest.csv ] && head -1 latest.csv > latest.csv.tmp && mv latest.csv.tmp latest.csv
	@for i in $(shell ls -t $(csvdir));do tail -n +2 $(csvdir)/$$i >> latest.csv; done

md_table.csv: latest.csv
	@. activate && conda activate scraper && python prepare.py

update_readme: md_table.csv
	@cat CONTENT.md > README.md \
	&& printf "<pre><b>LAST UPDATE : $(shell date +"%Y-%m-%d")</b><br \><b>TOTAL MAILS : %10s</b></pre>\n" $(shell tail -n +2 md_table.csv | wc -l | sed 's/ //g') >> README.md \
	&& csv2markdown md_table.csv ccll >> README.md
