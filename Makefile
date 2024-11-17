

publish-pypi:
	hatch publish -u __token__

docs-deploy:
	wrangler pages deploy docs/_build/html --project-name kitchenai-docs
