import typer
from typing import List
from dektools.cfg import ObjectCfg
from gitea import Gitea, Organization, Branch, Repository

cfg = ObjectCfg('dekcli/gitea')


def get_ins(name):
    data = cfg.get()
    if data:
        entry = data.get(name)
        if entry:
            return Gitea(entry['url'], entry['token'])
    else:
        typer.echo(f"Can't find name, you should add it firstly: {name}")
        raise typer.Exit()


def create_org(ins: Gitea, name):
    user = ins.get_user()
    result = ins.requests_post(
        Gitea.CREATE_ORG % user.username,
        data={
            "repo_admin_change_team_access": True,
            "username": name,
            "visibility": "private",
        },
    )
    assert "id" in result
    return Organization.parse_response(ins, result)


def get_orgs(ins):
    path = "/admin/orgs"
    results = ins.requests_get_paginated(path)
    return [Organization.parse_response(ins, result) for result in results]


def create_repo(ins: Gitea, org, name, branch_name_list):
    repo = ins.create_repo(org, name, autoInit=False, default_branch=branch_name_list[0])
    for branch_name in branch_name_list[1:]:
        add_branch(repo, branch_name)
    return repo


def get_branches(repo) -> List["Branch"]:
    results = repo.gitea.requests_get_paginated(
        Repository.REPO_BRANCHES % (repo.owner.username, repo.name)
    )
    return [Branch.parse_response(repo.gitea, result) for result in results]


def add_branch(repo, newname: str) -> "Branch":
    data = {"new_branch_name": newname}
    result = repo.gitea.requests_post(
        Repository.REPO_BRANCHES % (repo.owner.username, repo.name), data=data
    )
    return Branch.parse_response(repo.gitea, result)


class OrgRepoSure:
    def __init__(self, ins: Gitea):
        self.ins = ins
        self.orgs = {x.name: x for x in get_orgs(self.ins)}
        self.orgs_repos = {}

    def get_or_create(self, org_name, repo_name, branch_name_list):
        if org_name not in self.orgs:
            self.orgs[org_name] = create_org(self.ins, org_name)
        org = self.orgs[org_name]
        if org_name not in self.orgs_repos:
            self.orgs_repos[org_name] = {x.name: x for x in org.get_repositories()}
        org_repos = self.orgs_repos[org_name]
        if repo_name not in org_repos:
            org_repos[repo_name] = create_repo(self.ins, org, repo_name, branch_name_list)
        return org_repos[repo_name]
