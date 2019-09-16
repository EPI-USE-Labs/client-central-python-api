#!/usr/bin/env bash
ssh -T git@git.labs.epiuse.com -p 22
git remote set-url origin git@git.labs.epiuse.com:SWAT/clientcentral-api-python.git
git config --global user.email "thomas@labs.epiuse.com"
git config --global user.name "Thomas Scholtz"
git pull origin master --tags
git checkout master
git merge $(cat release.txt)
git push origin master
rm -rf dist
python3 setup.py sdist
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*