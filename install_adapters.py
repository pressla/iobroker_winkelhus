#!/usr/bin/env python3

import subprocess
import json
import yaml
from icecream import ic
import pendulum

print("Debug: Script started")

def run_command(command):
    """Run a shell command and return its output."""
    print(f"Debug: Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Debug: Command stdout: {result.stdout}")
    print(f"Debug: Command stderr: {result.stderr}")
    print(f"Debug: Command returncode: {result.returncode}")
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def install_adapter(adapter):
    """Install an ioBroker adapter and return the result."""
    command = f"iobroker install {adapter}"
    stdout, stderr, returncode = run_command(command)
    return {
        "adapter": adapter,
        "success": returncode == 0,
        "output": stdout,
        "error": stderr
    }

def get_installed_adapters():
    """Get a list of all installed adapters and their instances."""
    command = "iobroker list instances"
    stdout, stderr, returncode = run_command(command)
    print(f"Debug: iobroker list instances raw output:\n{stdout}")
    adapters = {}
    for line in stdout.split('\n'):
        if 'system.adapter.' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                adapter_instance = parts[0].strip().split('.')
                adapter = adapter_instance[2]
                instance = adapter_instance[3]
                status = 'enabled' if 'enabled' in line.lower() else 'disabled'
                if adapter not in adapters:
                    adapters[adapter] = []
                adapters[adapter].append((instance, status))
    print(f"Debug: Parsed adapters: {adapters}")
    return adapters

def verify_adapter(adapter, installed_adapters):
    """Verify if the adapter is installed."""
    is_installed = adapter in installed_adapters
    print(f"Verifying adapter {adapter}: {'Installed' if is_installed else 'Not installed'}")
    return is_installed

def count_instances(adapter, installed_adapters):
    """Count the number of instances for an adapter."""
    instances = installed_adapters.get(adapter, [])
    count = len(instances)
    print(f"Counting instances for {adapter}: {count}")
    return count

def create_or_enable_instance(adapter, instance_number):
    """Create a new instance of the adapter or enable an existing one."""
    command = f"iobroker enable {adapter}.{instance_number}"
    stdout, stderr, returncode = run_command(command)
    if returncode != 0:
        command = f"iobroker add {adapter}"
        stdout, stderr, returncode = run_command(command)
    return {
        "adapter": adapter,
        "success": returncode == 0,
        "output": stdout,
        "error": stderr
    }

def main():
    print("Starting install_adapters.py")
    
    # Read the list of adapters from YAML file
    print("Debug: Reading installedadapters.yaml")
    try:
        with open("installedadapters.yaml", "r") as f:
            data = yaml.safe_load(f)
            adapters = data['adapters']
        print(f"Debug: Adapters from YAML: {adapters}")
    except Exception as e:
        print(f"Error reading installedadapters.yaml: {e}")
        return

    # Get all installed adapters
    installed_adapters = get_installed_adapters()
    print(f"Installed adapters: {installed_adapters}")

    results = []
    for adapter_info in adapters:
        adapter = adapter_info['name']
        desired_instances = adapter_info.get('instances', 1)
        
        print(f"\nProcessing adapter: {adapter}")
        
        if not verify_adapter(adapter, installed_adapters):
            print(f"Installing adapter: {adapter}")
            install_result = install_adapter(adapter)
            results.append(install_result)
            if not install_result["success"]:
                print(f"Failed to install adapter: {adapter}")
                continue
        else:
            print(f"Adapter {adapter} is already installed")
        
        existing_instances = count_instances(adapter, installed_adapters)
        print(f"Existing instances for {adapter}: {existing_instances}")
        
        if existing_instances < desired_instances:
            for i in range(existing_instances, desired_instances):
                print(f"Creating or enabling instance {i} for adapter: {adapter}")
                instance_result = create_or_enable_instance(adapter, i)
                results.append(instance_result)
                if not instance_result["success"]:
                    print(f"Failed to create or enable instance {i} for adapter: {adapter}")
                    break
                existing_instances += 1
        elif existing_instances > desired_instances:
            print(f"Warning: {adapter} has more instances ({existing_instances}) than desired ({desired_instances})")
        else:
            print(f"Adapter {adapter} already has the desired number of instances: {existing_instances}")
        
        results.append({
            "adapter": adapter,
            "success": True,
            "instances_count": existing_instances
        })

    # Log results
    timestamp = pendulum.now().to_iso8601_string()
    with open(f"install_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\nInstallation Summary:")
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        instances = result.get("instances_count", "N/A")
        print(f"{result['adapter']}: {status} (Instances: {instances})")

    print("install_adapters.py completed")

print("Debug: Script ended")

if __name__ == "__main__":
    main()