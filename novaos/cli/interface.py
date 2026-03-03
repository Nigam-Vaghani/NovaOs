import json
import click
from novaos.app import app
from novaos.memory.database import init_db
init_db()


class NovaGroup(click.Group):
    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:
            default_cmd = self.get_command(ctx, "command")
            if default_cmd is None:
                raise
            return "command", default_cmd, args


def _infer_color(value) -> str:
    text = str(value).lower()

    error_tokens = [
        "error",
        "failed",
        "invalid",
        "unknown command",
        "blocked",
    ]
    warning_tokens = [
        "warning",
        "dry run",
        "would",
        "no ",
        "not configured",
        "not found",
        "quota",
        "truncated",
    ]

    if any(token in text for token in error_tokens):
        return "red"
    if any(token in text for token in warning_tokens):
        return "yellow"
    return "green"


def _print_result(result):
    if isinstance(result, dict):
        ai_summary = result.get("ai_summary")
        if ai_summary:
            payload = dict(result)
            payload.pop("ai_summary", None)
            click.secho(json.dumps(payload, indent=4), fg=_infer_color(payload))
            click.secho("\nAI Summary:", fg="green")
            click.secho(str(ai_summary), fg=_infer_color(ai_summary))
            return

        click.secho(json.dumps(result, indent=4), fg=_infer_color(result))
        return

    if isinstance(result, list):
        for item in result:
            click.secho(f" - {item}", fg=_infer_color(item))
        return

    click.secho(str(result), fg=_infer_color(result))


@click.group(cls=NovaGroup)
def cli():
    """ NovaOs command line interface """
    pass
@cli.command()
def run():
    """Start NovaOS server"""
    print("Strting novaOS server...")
    app.run(debug=True)
    
@cli.command()
@click.argument("text")
@click.option("--force", is_flag=True, help="Force execution without confirmation")
def command(text, force):
    """Process a NovaOS command"""
    from novaos.core.interpreter import interpret
    from novaos.core.controller import process

    click.secho(f"Received command: {text}", fg="green")

    structured = interpret(text)

    # If it's a directory action and not forced → ask confirmation
    if structured.get("action") == "organize_directory" and not force:
        confirm = input("This will modify files. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            click.secho("Operation cancelled.", fg="yellow")
            return
        structured["dry_run"] = False
    elif force:
        structured["dry_run"] = False

    result = process(structured)
    from novaos.memory.database import save_history
    save_history(text, str(result))
    
    click.secho("Result:", fg="green")
    _print_result(result)

@cli.command()
def listen():
    """Start voice command listener"""
    from novaos.input.voice import listen as voice_listen
    from novaos.core.interpreter import interpret
    from novaos.core.controller import process

    text = voice_listen()

    if not text:
        return

    structured = interpret(text)
    result = process(structured)
    from novaos.memory.database import save_history
    save_history(text, str(result))
    click.secho("Result:", fg="green")
    _print_result(result)
        
@cli.command()
def history():
    """Show command history"""
    from novaos.memory.database import get_history

    records = get_history()

    if not records:
        click.secho("No history found.", fg="yellow")
        return

    for cmd, result, timestamp in records:
        click.secho(f"\n[{timestamp}]", fg="green")
        click.secho(f"Command: {cmd}", fg="green")
        click.secho(f"Result: {result[:200]}", fg=_infer_color(result[:200]))

if __name__ == "__main__":
    cli()