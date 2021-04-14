usage:
	@echo "Available commands: "
	@echo
	@echo "\t run - run application"
	@echo "\t lint - run static code linter"
	@echo "\t mypy - run static type checker"
	@echo "\t test - run unit tests"
	@echo

run:
	 uvicorn main:app --host 0.0.0.0 --port 8000

lint:
	pylint --extension-pkg-whitelist='pydantic' parser/ *.py

mypy:
	mypy main.py

test:
	PYTHONPATH=. pytest -v
