"""Fetch GitHub Actions workflow logs using gh CLI."""

import subprocess
import sys
import json

def run_command(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def main():
    print("Fetching latest workflow runs...\n")

    # Get latest workflow runs
    cmd = 'gh run list --workflow="daily-digest.yml" --limit 5 --json databaseId,status,conclusion,createdAt,displayTitle'
    stdout, stderr, code = run_command(cmd)

    if code != 0:
        print(f"Error fetching runs: {stderr}")
        print("\nMake sure you have gh CLI installed and authenticated:")
        print("  gh auth login")
        return 1

    runs = json.loads(stdout)

    if not runs:
        print("No workflow runs found for 'daily-digest.yml'")
        return 0

    print("Recent workflow runs:")
    print("-" * 80)
    for i, run in enumerate(runs, 1):
        status = run['status']
        conclusion = run.get('conclusion', 'in_progress')
        run_id = run['databaseId']
        created = run['createdAt'][:19].replace('T', ' ')
        title = run['displayTitle']

        symbol = "✓" if conclusion == "success" else "✗" if conclusion == "failure" else "⋯"

        print(f"{i}. [{symbol}] Run #{run_id}")
        print(f"   Status: {status} | Conclusion: {conclusion}")
        print(f"   Created: {created}")
        print(f"   Title: {title}")
        print()

    # Get the latest run
    latest_run = runs[0]
    run_id = latest_run['databaseId']

    print(f"\nFetching detailed logs for run #{run_id}...\n")
    print("=" * 80)

    # Get the logs
    cmd = f'gh run view {run_id} --log'
    stdout, stderr, code = run_command(cmd)

    if code != 0:
        print(f"Error fetching logs: {stderr}")
        return 1

    print(stdout)

    # Also save to file
    log_file = f"workflow_run_{run_id}_logs.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"GitHub Actions Workflow Logs\n")
        f.write(f"Run ID: {run_id}\n")
        f.write(f"Status: {latest_run['status']}\n")
        f.write(f"Conclusion: {latest_run.get('conclusion', 'in_progress')}\n")
        f.write(f"Created: {latest_run['createdAt']}\n")
        f.write("=" * 80 + "\n\n")
        f.write(stdout)

    print("\n" + "=" * 80)
    print(f"\nLogs saved to: {log_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
