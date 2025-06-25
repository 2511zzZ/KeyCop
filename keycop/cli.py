import argparse
from keycop.searcher import CodeSearcher
from keycop.verifier import KeyVerifier
from keycop.notifier import Notifier

def main():
    parser = argparse.ArgumentParser(description="KeyCop: A tool to find and report leaked API keys on GitHub.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for leaked keys.')
    search_parser.add_argument('key_type', choices=['OPENAI', 'GEMINI'], help='The type of key to search for.')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify found keys.')

    # Notify command
    notify_parser = subparsers.add_parser('notify', help='Notify owners of valid leaked keys.')

    args = parser.parse_args()

    if args.command == 'search':
        searcher = CodeSearcher()
        searcher.search_leaked_keys(args.key_type)
    elif args.command == 'verify':
        verifier = KeyVerifier()
        verifier.run_verification()
    elif args.command == 'notify':
        notifier = Notifier()
        notifier.run_notification()

if __name__ == '__main__':
    main()