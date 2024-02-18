import typer

from .melting import chat_prompts
from .search import search
from .plugins import plugins
from .private_workspaces import private_workspaces


def main():
    app = typer.Typer()
    app.add_typer(search.app, name="search")
    app.add_typer(chat_prompts.app, name="chat-prompts")
    app.add_typer(plugins.app, name="plugins")
    app()


if __name__ == "__main__":
    main()
