#!/usr/bin/env python3
"""
A simple test script to interact with the Proxy-Lite Docker API.
"""

import argparse
import json
import sys
import time
import requests


def print_json(data):
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2))


def run_task(base_url, task_text):
    """Submit a new task to the API."""
    url = f"{base_url}/run"
    response = requests.post(url, json={"task": task_text})
    
    if response.status_code == 200:
        result = response.json()
        task_id = result.get("task_id")
        print(f"Task submitted successfully with ID: {task_id}")
        return task_id
    else:
        print(f"Error submitting task: {response.status_code}")
        print_json(response.json())
        return None


def get_task_status(base_url, task_id):
    """Get the status of a specific task."""
    url = f"{base_url}/tasks/{task_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Task status: {result.get('status')}")
        print_json(result)
        return result
    else:
        print(f"Error getting task status: {response.status_code}")
        print_json(response.json())
        return None


def list_all_tasks(base_url):
    """List all tasks."""
    url = f"{base_url}/tasks"
    response = requests.get(url)
    
    if response.status_code == 200:
        tasks = response.json()
        print(f"Found {len(tasks)} task(s)")
        print_json(tasks)
        return tasks
    else:
        print(f"Error listing tasks: {response.status_code}")
        print_json(response.json())
        return None


def wait_for_task_completion(base_url, task_id, poll_interval=2.0, timeout=300):
    """Wait for a task to complete, with progress updates."""
    start_time = time.time()
    elapsed = 0
    
    print(f"Waiting for task {task_id} to complete...")
    
    while elapsed < timeout:
        task_info = get_task_status(base_url, task_id)
        
        if not task_info:
            print("Failed to get task info.")
            return None
        
        status = task_info.get("status")
        
        if status == "completed":
            print(f"Task completed successfully in {elapsed:.1f} seconds.")
            return task_info
        elif status == "failed":
            print(f"Task failed after {elapsed:.1f} seconds.")
            print(f"Error: {task_info.get('error')}")
            return task_info
        
        # Still running, wait and try again
        time.sleep(poll_interval)
        elapsed = time.time() - start_time
        print(f"Task still in progress... ({elapsed:.1f}s elapsed)")
    
    print(f"Timeout reached ({timeout}s). Task is still running.")
    return None


def check_health(base_url):
    """Check the health of the API."""
    url = f"{base_url}/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("API health check: OK")
            return True
        else:
            print(f"API health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"API health check failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test the Proxy-Lite Docker API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Run task command
    run_parser = subparsers.add_parser("run", help="Run a new task")
    run_parser.add_argument("task", help="Task text to submit")
    run_parser.add_argument("--wait", action="store_true", help="Wait for task to complete")
    
    # Get task status command
    status_parser = subparsers.add_parser("status", help="Get task status")
    status_parser.add_argument("task_id", help="Task ID to check")
    
    # List all tasks command
    subparsers.add_parser("list", help="List all tasks")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "health":
        check_health(args.url)
    elif args.command == "run":
        task_id = run_task(args.url, args.task)
        if task_id and args.wait:
            wait_for_task_completion(args.url, task_id)
    elif args.command == "status":
        get_task_status(args.url, args.task_id)
    elif args.command == "list":
        list_all_tasks(args.url)


if __name__ == "__main__":
    main() 