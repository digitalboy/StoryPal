#!/usr/bin/env python3
"""
Script to process original stories with AI-based tokenization and save to database with unknown_words field.

This script triggers the background processing of all original stories,
performing AI-based tokenization and calculating unknown words for each story.
"""

import argparse
import sys
import time
import threading
from typing import Optional

# Add the project root to Python path so we can import app modules
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.original_story_service import OriginalStoryService
from app.utils.literacy_calculator import LiteracyCalculator
from app.services.word_service import WordService


def main():
    parser = argparse.ArgumentParser(
        description="Process original stories with AI-based tokenization and calculate unknown words"
    )
    parser.add_argument(
        "--ai-service",
        type=str,
        default="qwen",
        choices=["qwen", "gemini", "deepseek"],
        help="AI service to use for tokenization (default: qwen)"
    )
    parser.add_argument(
        "--start-level",
        type=int,
        help="Start processing from this level (inclusive)"
    )
    parser.add_argument(
        "--end-level",
        type=int,
        help="Stop processing at this level (inclusive)"
    )
    parser.add_argument(
        "--force-retokenize",
        action="store_true",
        help="Force re-tokenization even if stories already have tokenized content"
    )
    parser.add_argument(
        "--status-interval",
        type=int,
        default=30,
        help="Interval in seconds to print status updates (default: 30)"
    )

    args = parser.parse_args()

    print(f"Starting original stories processing with AI service: {args.ai_service}")
    print(f"Level range: {args.start_level or 'start'} to {args.end_level or 'end'}")
    print(f"Force retokenize: {args.force_retokenize}")
    
    # Initialize the service
    service = OriginalStoryService()
    
    # Check if a processing task is already running
    if service._processing_status["is_running"]:
        print("A processing task is already running. Please wait for it to complete or restart the application.")
        sys.exit(1)
    
    # Start the background processing
    service.start_processing_stories(
        ai_service_name=args.ai_service,
        start_level=args.start_level,
        end_level=args.end_level,
        force_retokenize=args.force_retokenize
    )
    
    print("Background processing started. Monitoring progress...")
    print("Press Ctrl+C to stop monitoring (processing will continue in background)")
    
    try:
        while service._processing_status["is_running"]:
            time.sleep(args.status_interval)
            with service._processing_status["lock"]:
                if service._processing_status["total"] > 0:
                    progress = (
                        service._processing_status["processed"] 
                        / service._processing_status["total"] 
                        * 100
                    )
                    print(
                        f"Progress: {service._processing_status['processed']}/"
                        f"{service._processing_status['total']} "
                        f"({progress:.1f}%)"
                    )
                else:
                    print("Initializing... waiting for total count.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped. Processing continues in background.")
    
    print("Original stories processing completed!")


if __name__ == "__main__":
    main()