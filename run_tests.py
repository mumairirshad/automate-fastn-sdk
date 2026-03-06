"""
Main test runner for fastn-ai SDK CLI test automation.

Usage:
    python run_tests.py              # Run all CLI tests
    python run_tests.py --cli        # Same as above (explicit)
    python generate_report.py        # Generate full HTML + CSV report
"""
import sys
import subprocess


def main():
    args = sys.argv[1:]
    pytest_args = ["-v", "--tb=short"]

    if "--cli" in args:
        pytest_args.append("tests/cli/")
    else:
        pytest_args.append("tests/cli/")

    # Pass through any extra args (e.g. -k "test_flow", -m connector)
    for a in args:
        if a not in ("--cli",):
            pytest_args.append(a)

    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    print(f"Running: {' '.join(cmd)}")
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
