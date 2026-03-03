
from novaos.core.executor import execute
from novaos.utils.security import is_safe
from novaos.utils.logger import log_info, log_error

def process(command: dict):
    log_info(f"Processing command: {command}")

    if not is_safe(command):
        log_error("Blocked unsafe command.")
        return "Blocked by security layer."

    result = execute(command)

    log_info(f"Execution result: {result}")
    return result