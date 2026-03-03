import json
import click
from novaos.app import app
from novaos.memory.database import init_db
init_db()


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
    from novaos.memory.database import save_history
    save_history(text, str(result))
    
    print("Result:")

    if isinstance(result, dict):
        print(json.dumps(result, indent=4))

    elif isinstance(result, list):
        for item in result:
            print(" -", item)

    else:
        print(result)

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
    print("Result:")

    import json
    if isinstance(result, dict):
        print(json.dumps(result, indent=4))
    elif isinstance(result, list):
        for item in result:
            print(" -", item)
    else:
        print(result)
        
@cli.command()
def history():
    """Show command history"""
    from novaos.memory.database import get_history

    records = get_history()

    if not records:
        print("No history found.")
        return

    for cmd, result, timestamp in records:
        print(f"\n[{timestamp}]")
        print("Command:", cmd)
        print("Result:", result[:200])

if __name__ == "__main__":
    cli()