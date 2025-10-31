#!/usr/bin/env python3
"""
Dago Domenai Generator - CLI Entry Point

A comprehensive toolkit for generating domain name lists using multiple algorithmic approaches.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generators.brute_generator import BruteForceGenerator


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate domain name lists using various algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 2-4 character domains with default settings
  python main.py brute

  # Generate 3-character domains only
  python main.py brute --length 3

  # Generate 3-5 character alphanumeric domains with hyphens
  python main.py brute --min 3 --max 5 --charset alphanumeric --hyphen-mode with

  # Generate only domains that contain hyphens
  python main.py brute --hyphen-mode only --output hyphen_domains.txt

  # Generate numeric domains only
  python main.py brute --charset numbers --min 1 --max 3
        """
    )

    subparsers = parser.add_subparsers(dest='generator', help='Generator type')

    # Brute force generator
    brute_parser = subparsers.add_parser('brute', help='Brute force domain generation')
    brute_parser.add_argument(
        '--charset', '-c',
        choices=['numbers', 'letters', 'alphanumeric'],
        default='alphanumeric',
        help='Character set to use (default: alphanumeric)'
    )
    brute_parser.add_argument(
        '--min', '-m',
        type=int, default=2,
        help='Minimum domain length (default: 2)'
    )
    brute_parser.add_argument(
        '--max', '-M',
        type=int, default=4,
        help='Maximum domain length (default: 4)'
    )
    brute_parser.add_argument(
        '--length', '-l',
        type=int,
        help='Domain length (sets both min and max to this value)'
    )
    brute_parser.add_argument(
        '--hyphen-mode',
        choices=['with', 'without', 'only'],
        default='with',
        help='Hyphen handling mode (default: with)'
    )
    brute_parser.add_argument(
        '--tld',
        default='lt',
        help='Top-level domain (default: lt)'
    )
    brute_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: auto-generated)'
    )
    brute_parser.add_argument(
        '--estimate-only', '-e',
        action='store_true',
        help='Only estimate count, do not generate'
    )

    return parser


def generate_brute_force(args):
    """Handle brute force generation."""
    # Handle --length parameter
    if args.length is not None:
        if args.min != 2 or args.max != 4:  # Check if min/max were also specified
            print("Error: Cannot specify both --length and --min/--max", file=sys.stderr)
            return 1
        args.min = args.max = args.length
    
    try:
        generator = BruteForceGenerator(
            char_type=args.charset,
            min_len=args.min,
            max_len=args.max,
            hyphen_mode=args.hyphen_mode,
            tld=args.tld
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Estimate count
    estimated = generator.estimate_count()
    print(f"Estimated domains to generate: {estimated:,}")

    if args.estimate_only:
        return 0

    # Generate output filename if not provided
    if not args.output:
        output_file = f"assets/output/brute_{args.charset}_{args.min}-{args.max}_{args.hyphen_mode}_{args.tld}.txt"
    else:
        output_file = args.output

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating domains to: {output_file}")

    try:
        count = generator.generate_to_file(str(output_path))
        print(f"Successfully generated {count:,} domains")
        return 0
    except Exception as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.generator:
        parser.print_help()
        return 1

    if args.generator == 'brute':
        return generate_brute_force(args)
    else:
        print(f"Generator '{args.generator}' not implemented yet", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())