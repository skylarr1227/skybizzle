style:
	black --check -l 120 -N --diff `git ls-files "*.py"`
allstyle:
	black --check -l 120 -N --diff .
reformat:
	black -l 120 -N `git ls-files "*.py"`
allreformat:
	black -l 120 -N .
coverage:
	pytest --cov=seplib ./tests --cov-report=html --cov-config tox.ini --cov-fail-under 95
test-coverage:
	pytest --cov seplib ./tests --cov-config tox.ini --cov-fail-under 95
relative-imports:
	./checks.sh