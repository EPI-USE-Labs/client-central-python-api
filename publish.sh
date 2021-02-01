/usr/local/bin/python3 --version
ssh -T git@git.labs.epiuse.com -p 22

git remote set-url origin git@git.labs.epiuse.com:SWAT/clientcentral-api-python.git
git config --global user.email "thomas@labs.epiuse.com"
git config --global user.name "Thomas Scholtz"
git pull origin master --tags
git checkout master
git merge $(cat release.txt)
git push origin master

rm -rf dist

/usr/local/bin/python3 --version
/usr/local/bin/python3 setup.py sdist bdist_wheel
twine upload dist/*
