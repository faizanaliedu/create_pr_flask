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

def get_ticket_info_from_jira(ticket_number):
    jira = JIRA(OPTIONS, basic_auth=(app.config['JIRA_USER'], app.config['JIRA_TOKEN']))
    issue = jira.issue(ticket_number)
    return (issue.fields.summary, issue.fields.description)


def create_pull_request(summary, description, head_branch, labels):
    g = Github(app.config['GITHUB_TOKEN'])
    r = g.get_repo(EDU_REPO_ID)

    desciption_template = f"## Description: \n\n {description} \n\n ### Migrations \n\n - None (Add if necessary, and add the run-migration label to the PR.) \n\n ### Author Checklist: \n\n Add an X between [] and remove whitespace to check off. \n\n - [ ] Tests have been added/updated. \n\n - [ ] Relevant documentation has been added/updated (add doc link if applicable). \n\n - [ ] Ran lighthouse tests and added the scores in PR description (if applicable). \n\n - [ ] Appropriate labels have been applied to the PR. Every PR should have at least one label."

    pr = r.create_pull(title=summary, body=desciption_template, head=head_branch, base="master")

    if labels:
        pr.set_labels(labels)

    pr.add_to_assignees(app.config['GITHUB_USER'])

    return pr.html_url

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        jira = request.form["jira"]
        github = request.form["github"]
        labels = request.form["labels"]

        link = ''

        try:
            summary, description = get_ticket_info_from_jira(jira)

            link = create_pull_request(f"{jira}: {summary}", description, github, labels)
        except:
            return render_template("home.html", message = "Something went wrong")

        return render_template("home.html", message = "Successfully created PR.", href=link)
    
    return render_template("home.html")

@app.route("/all_prs", methods=["GET", "POST"])
def all_prs():
    prs = []
    if request.method == "POST":
        try:
            g = Github(app.config['GITHUB_TOKEN'])
            r = g.get_repo(EDU_REPO_ID)
            user = app.config['GITHUB_USER']
            for pull in r.get_pulls(state="open"):
                if pull.user.login == user:
                    prs.append((pull.title, pull.html_url))
        except:
            return render_template("all_prs.html", message = "Something went wrong")

        return render_template("all_prs.html", message = "Successfully Fetched.", prs=prs)
    
    return render_template("all_prs.html")


if __name__ == "__main__":
    app.config['JIRA_USER'] = environ.get('JIRA_USER')
    app.config['JIRA_TOKEN'] = environ.get('JIRA_TOKEN')
    app.config['GITHUB_TOKEN'] = environ.get('GITHUB_TOKEN')
    app.config['GITHUB_USER'] = environ.get('GITHUB_USER')

    app.run(debug=True, host="0.0.0.0", port=3000)
