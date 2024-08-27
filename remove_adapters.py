import subprocess
import yaml
from icecream import ic
import pendulum
from tqdm import tqdm

def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def remove_adapter(adapter):
    """Remove all instances of an ioBroker adapter and return the result."""
    command = f"iobroker del {adapter}"
    stdout, stderr, returncode = run_command(command)
    return {
        "adapter": adapter,
        "success": returncode == 0,
        "output": stdout,
        "error": stderr
    }

def main():
    # Read the list of adapters from YAML file
    with open("installedadapters.yaml", "r") as f:
        data = yaml.safe_load(f)
        adapters = data['adapters']

    results = []
    # Use tqdm for the progress bar
    for adapter_info in tqdm(adapters, desc="Removing adapters", unit="adapter"):
        adapter = adapter_info['name']
        ic(f"Removing adapter: {adapter}")
        remove_result = remove_adapter(adapter)
        results.append(remove_result)

    # Log results
    timestamp = pendulum.now().to_iso8601_string()
    with open(f"remove_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    ic("Removal Summary:")
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        ic(f"{result['adapter']}: {status}")

if __name__ == "__main__":
    main()