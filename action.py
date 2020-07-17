#!/usr/bin/env python
from github import Github, Deployment, DeploymentStatus
from datetime import datetime


def main():
    inputs = ActionsContext("input")
    context = ActionsContext("github")
    repo = Github(inputs.access_token).get_repo(context.repository)

    deployment = create_deployment(
        repo,
        {
            "ref": context.ref,
            "environment": inputs.environment,
            "required_contexts": [],
            "production_environment": False,
            "transient_environment": False,
        },
    )

    status_payload = {
        "state": inputs.state,
        "log_url": context.server_url + "/" + context.repository + "/actions/runs/" + context.run_id,
        "auto_inactive": True,
    }
    if hasattr(inputs, 'environment_url'):
        status_payload["environment_url"] = inputs.environment_url

    create_status(
        deployment,
        status_payload,
    )


def create_status(deployment, input):
    headers, data = deployment._requester.requestJsonAndCheck(
        "POST",
        deployment.url + "/statuses",
        headers={
            "Accept": "application/vnd.github.ant-man-preview+json,application/vnd.github.flash-preview+json"
        },
        input=input,
    )
    return DeploymentStatus.DeploymentStatus(
        deployment._requester, headers, data, completed=True
    )


def create_deployment(repo, input):
    headers, data = repo._requester.requestJsonAndCheck(
        "POST",
        repo.url + "/deployments",
        headers={
            "Accept": "application/vnd.github.ant-man-preview+json,application/vnd.github.flash-preview+json"
        },
        input=input,
    )
    return Deployment.Deployment(repo._requester, headers, data, completed=True)


class ActionsContext:
    def __init__(self, namespace):
        from os import environ

        if namespace == "input":
            prefix = "INPUT_"
        elif namespace == "github":
            prefix = "GITHUB_"
        else:
            print(f"Context for {namespace} not found.")
            exit(2)

        for env in environ:
            if env.startswith(prefix):
                setattr(self, env[len(prefix) :].lower(), environ[env])

        del environ


if __name__ == "__main__":
    main()
