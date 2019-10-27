#!/usr/bin/env sh
pytest --cov=irbt tests/ && coverage xml && python-codacy-coverage -r coverage.xml
