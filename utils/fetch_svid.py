#!/usr/bin/env python3
"""
Helper script to fetch the current workload's SPIFFE ID.
This works around issues with CLI-based SVID fetching when selectors don't match.
"""
import sys
import argparse
from pyspiffe.workloadapi import default_workload_api_client


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch SPIFFE ID from SPIRE agent workload API"
    )
    parser.add_argument(
        "--socketpath",
        "-s",
        type=str,
        default="/tmp/agent.sock",
        help="Path to spire-agent socket (default: /tmp/agent.sock)",
    )
    return parser.parse_args()


def main():
    options = parse_arguments()

    try:
        # Connect to the workload API
        with default_workload_api_client.DefaultWorkloadApiClient(
            spiffe_socket=f"unix://{options.socketpath}"
        ) as client:
            # Fetch X509 SVID
            svid = client.fetch_x509_svid()
            # Print just the SPIFFE ID
            print(svid.spiffe_id)
            return 0
    except Exception as e:
        print(f"Error fetching SVID: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
