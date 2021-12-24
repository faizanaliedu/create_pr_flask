from github import Github
import sys

g = Github(sys.argv[1])
r = g.get_repo(24544786)
user = sys.argv[2]

for pull in r.get_pulls(state="open"):
	if pull.user.login == user:
		print(pull.html_url)
