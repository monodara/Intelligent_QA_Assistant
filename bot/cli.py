#!/usr/bin/env python3
"""
RAG Knowledge Base Management CLI
Used to build/update knowledge base and launch conversation bot
"""
import argparse
from .knowledge_base import KnowledgeBaseManager
from .build_kb import build_or_update_knowledge_base, main as run_build
from .main import main as run_bot
from .config import DOCS_DIR, IMG_DIR


def main():
    parser = argparse.ArgumentParser(description="RAG Knowledge Base Management Tool")
    subparsers = parser.add_subparsers(dest="action", help="Available operations")
    
    # Build subcommand
    build_parser = subparsers.add_parser("build", help="Build/update knowledge base (supports nested directories)")
    build_parser.add_argument(
        "--docs-dir",
        default=DOCS_DIR,
        help="Document directory path (default: %(default)s), supports recursive scanning of subdirectories"
    )
    build_parser.add_argument(
        "--img-dir",
        default=IMG_DIR,
        help="Image directory path (default: %(default)s), supports recursive scanning of subdirectories"
    )
    build_parser.add_argument(
        "--incremental",
        action="store_true",
        default=True,
        help="Incremental update mode (default: True)"
    )
    build_parser.add_argument(
        "--full-rebuild",
        action="store_true",
        default=False,
        help="Full rebuild mode"
    )
    
    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run conversation bot")
    run_parser.add_argument(
        "--docs-dir",
        default=DOCS_DIR,
        help="Document directory path (default: %(default)s)"
    )
    run_parser.add_argument(
        "--img-dir",
        default=IMG_DIR,
        help="Image directory path (default: %(default)s)"
    )

    args = parser.parse_args()

    if args.action == "build":
        incremental = args.incremental and not args.full_rebuild
        print(f"Starting {'incremental update' if incremental else 'full rebuild'} of knowledge base...")
        print(f"Document directory: {args.docs_dir} (recursively scanning subdirectories)")
        print(f"Image directory: {args.img_dir} (recursively scanning subdirectories)")
        print(f"Incremental mode: {incremental}")
        run_build(docs_dir=args.docs_dir, img_dir=args.img_dir, incremental=incremental)
        print("Knowledge base building/update completed!")

    elif args.action == "run":
        print("Starting RAG conversation bot...")
        run_bot()
    
    elif args.action is None:
        parser.print_help()

if __name__ == "__main__":
    main()