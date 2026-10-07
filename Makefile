.PHONY: reproduce install test report zip clean

PY := .venv/bin/python

install:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

test:
	$(PY) -m pytest -q tests

reproduce:
	$(PY) -m src.run_all
	$(PY) scripts/build_report_pdf.py

report:
	$(PY) scripts/build_report_pdf.py

zip:
	bash scripts/make_submission_zip.sh

clean:
	rm -rf outputs/* report/assets/*
