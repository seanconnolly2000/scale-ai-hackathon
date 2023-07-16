import os
from jira import JIRA
from typing import Dict, List

#Research:
#    http://pythonjira.com/create-a-jira-ticket-with-python/
#    https://datageeks.medium.com/automate-your-jira-tasks-in-python-bbbcb3145a95

class Jira(object):
    def __init__(self): 
            jira_email = os.environ.get("JIRA_EMAIL")
            jira_api_token = os.environ.get("JIRA_API_TOKEN")
            jira_server = os.environ.get("JIRA_SERVER")
            options =  {'server': jira_server}
            self.jira_connection = JIRA(options, basic_auth=(jira_email, jira_api_token))


    def create_issue(self, project_key: str, issue_type: str, summary: str, description: str):

        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }

        new_issue = self.jira_connection.create_issue(fields=issue_dict)
        return new_issue

    def searchIssuesByProjectName(self, projectName: str) -> List:
        retList = []
        for issue in self.jira_connection.search_issues('project=' + projectName):
            parent = None
            acceptance_criteria=None
            if hasattr(issue.fields, 'parent'):
                parent = issue.fields.parent.key
            if hasattr(issue.fields, 'customfield_10036'):
                acceptance_criteria = issue.fields.customfield_10036
            retList.append({ 'key':issue.key, 'parent':parent, 'status':issue.fields.status.name, 'summary':issue.fields.summary, 'description':issue.fields.description, 'acceptance_criteria': acceptance_criteria})
        return retList

    def searchIssueByUniqueId(self, Id: str) -> List:
        issue = self.jira_connection.issue(Id)
        json_issue = issue.raw
        # print(json_issue)
        return {issue.key, issue.fields.summary, issue.fields.reporter.displayName}
