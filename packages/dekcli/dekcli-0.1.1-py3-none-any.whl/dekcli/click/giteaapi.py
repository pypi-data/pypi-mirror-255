import os
import git
import typer
from getpass import getpass
from dektools.cfg import ObjectCfg
from dektools.file import sure_dir, normal_path
from ..core import giteaapi

cfg = ObjectCfg('dekcli/gitea')

default_name = 'index'

app = typer.Typer(add_completion=False)


@app.command()
def site(url, name=default_name):  # url: {schema}://{host}{port}
    token = getpass(f"Please input token: ")
    cfg.update({name: dict(url=url, token=token.strip())})


@app.command()
def pull(path, name=default_name):
    path = normal_path(path)
    sure_dir(path)
    ins = giteaapi.get_ins(name)
    for org in giteaapi.get_orgs(ins):
        for repo in org.get_repositories():
            path_repo = os.path.join(path, repo.get_full_name())
            sure_dir(path_repo)
            git.Repo.clone_from(repo.ssh_url, path_repo)


@app.command()
def push(path, name=default_name):
    path = normal_path(path)
    ins = giteaapi.get_ins(name)
    ors = giteaapi.OrgRepoSure(ins)
    for org_name in os.listdir(path):
        path_org = os.path.join(path, org_name)
        for repo_name in os.listdir(path_org):
            path_repo = os.path.join(path_org, repo_name)
            print(f"enter: {path_repo}", flush=True)
            try:
                git_repo = git.Repo(path_repo)
                for remote in git_repo.remotes:
                    git_repo.delete_remote(remote)
                push_list = [ref.path.split('/', 2)[-1] for ref in git_repo.refs]
                repo = ors.get_or_create(org_name, repo_name, push_list)
                origin = git_repo.create_remote('origin', repo.ssh_url)
                print(f"pushing: {repo.ssh_url}", flush=True)
                for name in push_list:
                    origin.push(refspec=f"{name}:{name}")
            except git.InvalidGitRepositoryError:
                pass


def get_refs_name(origin):
    result = []
    for ref in origin.refs:
        result.append(ref.name[len(origin.name) + 1:])
    return result
