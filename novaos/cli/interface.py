import click
from novaos.app import app

@click.group()
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

    print(f"Received command: {text}")

    structured = interpret(text)

    # If it's a directory action and not forced → ask confirmation
    if structured.get("action") == "organize_directory" and not force:
        confirm = input("This will modify files. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Operation cancelled.")
            return
        structured["dry_run"] = False
    elif force:
        structured["dry_run"] = False

    result = process(structured)

    print("Result:")
    if isinstance(result, list):
        for item in result:
            print(" -", item)
    else:
        print(result)

if __name__ == "__main__":
    cli()