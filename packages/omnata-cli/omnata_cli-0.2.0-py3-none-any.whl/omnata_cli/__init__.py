import typer

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.command()
def docs():
    """Open the Omnata CLI documentation in your browser."""
    typer.launch("https://docs.omnata.com")


try:
    from omnata_plugin_devkit import cli  # pylint: disable=import-error

    # If the import is successful, we can add its commands to our application
    app.add_typer(cli.app, name="plugin_dev")

except ImportError as import_error:
    if "No module named 'omnata_plugin_devkit'" not in str(import_error):
        raise

    @app.command()
    def plugin_dev():
        "To use the plugin-dev subcommand, run `pip install omnata-plugin-devkit`."
        print(
            "To use the plugin_dev subcommand, run `pip install omnata-plugin-devkit`."
        )
        raise typer.Abort()


def check_env_conf(env_conf, environment):
    if env_conf is None:
        print(
            f"The {environment} environment is not configured in app.toml "
            f"yet, please run `snow configure {environment}` first before continuing.",
        )
        raise typer.Abort()
