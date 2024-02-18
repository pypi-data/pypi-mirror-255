import os


try:
    TEIA_API_KEY = os.environ["TEIA_API_KEY"]
    MELT_API_URL = os.getenv("MELT_API_URL", "https://meltingface.teialabs.com.br/api")
except KeyError:
    m = "[red]MissingEnvironmentVariables[/red]: "
    m += "[yellow]'TEIA_API_KEY'[/yellow] cannot be empty."
    print(m)
    exit(1)

