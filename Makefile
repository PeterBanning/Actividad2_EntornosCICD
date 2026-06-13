PHONY: all build test-unit test-api test-e2e

build:
	docker build -t calculator-app .

test-unit:
	docker rm -f unit-tests || true
	docker run --name unit-tests --env PYTHONPATH=/opt/calc -w /opt/calc calculator-app:latest pytest --cov --cov-report=xml:results/coverage.xml --cov-report=html:results/coverage --junit-xml=results/unit_result.xml -m unit || true
	mkdir -p results
	docker cp unit-tests:/opt/calc/results/. results/ || true
	docker rm -f unit-tests || true

test-api:
	docker network create calc-test-api || true
	docker rm -f apiserver api-tests || true
	docker run -d --name apiserver --network calc-test-api --env PYTHONPATH=/opt/calc --env FLASK_APP=app/api.py -w /opt/calc calculator-app:latest flask run --host=0.0.0.0
	docker run --name api-tests --network calc-test-api --env PYTHONPATH=/opt/calc --env BASE_URL=http://apiserver:5000/ -w /opt/calc calculator-app:latest pytest --junit-xml=results/api_result.xml -m api || true
	mkdir -p results
	docker cp api-tests:/opt/calc/results/. results/ || true
	docker rm -f apiserver api-tests || true
	docker network rm calc-test-api || true

test-e2e:
	docker network create calc-test-e2e || true
	docker rm -f apiserver calc-web e2e-tests || true

	docker run -d --name apiserver --network calc-test-e2e --env PYTHONPATH=/opt/calc --env FLASK_APP=app/api.py -w /opt/calc calculator-app:latest flask run --host=0.0.0.0

	docker create --name calc-web --network calc-test-e2e nginx
	docker cp ./web/. calc-web:/usr/share/nginx/html
	docker cp ./web/constants.test.js calc-web:/usr/share/nginx/html/constants.js
	docker cp ./web/nginx.conf calc-web:/etc/nginx/conf.d/default.conf
	docker start calc-web

	docker create --network calc-test-e2e --name e2e-tests cypress/included:4.9.0 --browser chrome || true
	docker cp ./test/e2e/cypress.json e2e-tests:/cypress.json
	docker cp ./test/e2e/cypress e2e-tests:/cypress
	docker start -a e2e-tests || true

	mkdir -p results
	docker cp e2e-tests:/results/. results/ || true

	docker rm -f apiserver calc-web e2e-tests || true
	docker network rm calc-test-e2e || true
