# Author: AJ Khan

all: deployment-package packages

packages:
	python3 -m pip install --target ./packages boto3 ninjarmmpy -U

deployment-package: packages
	zip -r deployment-package.zip ./packages
	zip -g deployment-package.zip lambda_function.py

deploy-to-lambda:
	aws lambda update-function-code \
		--function-name pullandwritedatatobucket \
		--zip-file fileb://deployment-package.zip