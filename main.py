#!/usr/bin/env python3
"""
Restaurant AI Main Entry Point
"""

from src.web_server import WebServer
from src.ai_processor import AIProcessor

def main():
    """Main application entry point"""
    processor = AIProcessor()
    server = WebServer()
    print("Restaurant AI starting...")

if __name__ == "__main__":
    main()