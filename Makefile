bump-version:
	bumpversion --current-version $(version) $(type) setup.py gitflow_linter/__init__.py docs/conf.py

create-distro:
	rm dist/*
	python setup.py sdist bdist_wheel
	twine check dist/*

test-push-distro:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

push-distro:
	twine upload dist/*