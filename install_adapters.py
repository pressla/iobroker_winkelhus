import subprocess
import json
import yaml
from icecream import ic
import pendulum
from tqdm import tqdm

def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def install_adapter(adapter):
    """Install an ioBroker adapter and return the result."""
    command = f"iobroker add {adapter}"
    stdout, stderr, returncode = run_command(command)
    return {
        "adapter": adapter,
        "success": returncode == 0,
        "output": stdout,
        "error": stderr
    }

def verify_instance(adapter):
    """Verify if a valid instance of the adapter exists."""
    command = f"iobroker list {adapter}"
    stdout, _, _ = run_command(command)
    return any(adapter in line and "enabled" in line for line in stdout.split('\n'))

def main():
    # Read the list of adapters from YAML file
    with open("installedadapters.yaml", "r") as f:
        data = yaml.safe_load(f)
        adapters = data['adapters']

    results = []
    # Use tqdm for the progress bar
    for adapter in tqdm(adapters, desc="Installing adapters", unit="adapter"):
        ic(f"Installing adapter: {adapter}")
        install_result = install_adapter(adapter)
        install_result["instance_verified"] = verify_instance(adapter)
        results.append(install_result)

    # Log results
    timestamp = pendulum.now().to_iso8601_string()
    with open(f"install_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    ic("Installation Summary:")
    for result in results:
        status = "SUCCESS" if result["success"] and result["instance_verified"] else "FAILED"
        ic(f"{result['adapter']}: {status}")

if __name__ == "__main__":
    main()