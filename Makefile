test:
	py.test -v -s

coverage:
	coverage run --source domain_event_broker -m py.test && coverage report -m --omit=domain_event_broker/_version.py
