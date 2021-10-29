from flask import Flask, render_template, request
from github import Github
from jira import JIRA
import argparse
import sys
from os import environ

from dotenv import load_dotenv

dotenv_path = '.env'  # Path to .env file
load_dotenv(dotenv_path)


app = Flask(__name__)

OPTIONS = {
 'server': 'https://educative.atlassian.net'
}
EDU_REPO_ID = 24544786

def get_ticket_info_from_jira(ticket_number, jira_user, jira_api_key):
	jira = JIRA(OPTIONS, basic_auth=(jira_user, jira_api_key))
	issue = jira.issue(ticket_number)
	return (issue.fields.summary, issue.fields.description)


def create_pull_request(git_token,summary, description, head_branch, labels, user_name):
	g = Github(git_token)
	r = g.get_repo(EDU_REPO_ID)

	desciption_template = f"## Description: \n\n {description} \n\n ### Migrations \n\n - None (Add if necessary, and add the run-migration label to the PR.) \n\n ### Author Checklist: \n\n Add an X between [] and remove whitespace to check off. \n\n - [ ] Tests have been added/updated. \n\n - [ ] Relevant documentation has been added/updated (add doc link if applicable). \n\n - [ ] Ran lighthouse tests and added the scores in PR description (if applicable). \n\n - [ ] Appropriate labels have been applied to the PR. Every PR should have at least one label."

	pr = r.create_pull(title=summary, body=desciption_template, head=head_branch, base="master")

	pr.set_labels(labels)
	pr.add_to_assignees(user_name)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        jira = request.form["jira"]
        github = request.form["github"]
        labels = request.form["labels"]
        try:
            summary, description = get_ticket_info_from_jira(jira, app.config['JIRA_USER'], app.config['JIRA_TOKEN'])
            create_pull_request(app.config['GITHUB_TOKEN'], f"{jira}: {summary}", description, github, labels, app.config['GITHUB_USER'])
        except:
            return render_template("base.html", message = "Something went wrong")

        return render_template("base.html", message = "Successfully created PR.")
    
    return render_template("base.html")


if __name__ == "__main__":
    app.config['JIRA_USER'] = environ.get('JIRA_USER')
    app.config['JIRA_TOKEN'] = environ.get('JIRA_TOKEN')
    app.config['GITHUB_TOKEN'] = environ.get('GITHUB_TOKEN')
    app.config['GITHUB_USER'] = environ.get('GITHUB_USER')

    print(app.config['JIRA_TOKEN'])

    app.run(debug=True, host="0.0.0.0", port=3000)
