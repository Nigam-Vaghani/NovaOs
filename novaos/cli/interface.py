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
def command(text):
    """Process a NovaOS command"""
    from novaos.core.interpreter import interpret
    from novaos.core.executor import execute

    print(f"Received command: {text}")

    structured = interpret(text)
    result = execute(structured)

    print("Result:", result)

if __name__ == "__main__":
    cli()