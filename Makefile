PYTHON ?= python
PYTEST ?= pytest
.DEFAULT_GOAL := help

.PHONY: help run evaluate test

run:
	$(PYTHON) -m app.main 

test:
	$(PYTEST) tests/ 

evaluate:
	 $(PYTHON) -m app.benchmark_evaluation.benchmark
	
