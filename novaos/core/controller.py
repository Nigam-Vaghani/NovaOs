from novaos.core.executor import execute
from novaos.core.planner import create_plan
from novaos.utils.security import is_safe
from novaos.utils.logger import log_info, log_error


def process(command: dict):
    log_info(f"Received command: {command}")

    plan = create_plan(command)
    results = []

    for step in plan:
        if not is_safe(step):
            log_error(f"Blocked unsafe step: {step}")
            results.append("Blocked by security layer.")
            continue

        result = execute(step)
        results.append(result)
        log_info(f"Executed step: {step} → {result}")

    return results if len(results) > 1 else results[0]