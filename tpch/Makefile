URL      = https://github.com/electrum/tpch-dbgen/archive/master.zip
ZIPBALL  = tpch-dbgen.zip
DATABASE = tpch.db
TABLES   = nation region part supplier partsupp customer orders lineitem
SCALE    = 1

all: $(DATABASE)

dbgen:
	@wget -O $(ZIPBALL) $(URL)
	@unzip $(ZIPBALL)
	@rm $(ZIPBALL)
	@mv tpch-dbgen-master dbgen
	@make -C dbgen clean

dbgen/dbgen: dbgen
	@cat dbgen/makefile.suite | \
	  sed -e 's/CC[ ]*=/CC = gcc/' | \
	  sed -e 's/DATABASE[ ]*=/DATABASE = SQLSERVER/' | \
	  sed -e 's/MACHINE[ ]*=/MACHINE = LINUX/' | \
	  sed -e 's/WORKLOAD[ ]*=/WORKLOAD = TPCH/' > dbgen/Makefile 
	@make -C dbgen

$(DATABASE): dbgen/dbgen
	@echo "Generate data with scale $(SCALE)"
	@cd dbgen; ./dbgen -vf -s $(SCALE)
	@for t in $(TABLES); do echo "fixing $$t"; sed --in-place 's/|$$//' dbgen/$$t.tbl; done 
	@sqlite3 $(DATABASE) < sqlite-ddl.sql
	@for t in $(TABLES); do echo "importing $$t"; sqlite3 $(DATABASE) ".import dbgen/$$t.tbl $$t"; done
	@du -h $(DATABASE)

clean:
	@- rm -rf dbgen $(DATABASE)
