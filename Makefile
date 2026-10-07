.PHONY: reproduce install clean

install:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

reproduce: install
	QUANT_EDGE_FAST=1 .venv/bin/python -m src.run_all
	.venv/bin/python scripts/build_report_pdf.py

clean:
	rm -rf outputs/* report/assets/* data/etf_prices_*.csv
