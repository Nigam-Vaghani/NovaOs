import psutil


def execute(command: dict):
    action = command.get("action")

    if action == "check_system":
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
        }

    if action == "greet":
        return "Hello from NovaOS 🚀"

    return "Unknown command"