test:
	py.test -v -s

coverage:
	coverage run --source domain_events -m py.test && coverage report -m --omit=domain_events/_version.py
