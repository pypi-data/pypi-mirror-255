from getpass import getpass
from dektools.cfg import ObjectCfg
from dektools.file import sure_dir
from gitea import Gitea, Organization

cfg = ObjectCfg('dekcli/gitea')

default_name = 'index'


def pull(path, name=default_name):
    # sure_dir(path)
    ins = get_ins(name)
    for org in ins.get_orgs():
        for repo in org.get_repositories():
            print(repo.ssh_url)
            print(repo.get_full_name())

def get_ins(name):
    data = cfg.get()
    if data:
        entry = data.get(name)
        if entry:
            return Gitea(entry['url'], entry['token'])
    else:
        typer.echo(f"Can't find name, you should add it firstly: {name}")
        raise typer.Exit()

if __name__ == '__main__':
    pull('')
