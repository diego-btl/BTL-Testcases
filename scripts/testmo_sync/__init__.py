"""
BTL Testmo Sync Framework

Core package for synchronizing test cases between local YAML files and Testmo.

Modules:
- reader: MCP-based read operations (folders, cases)
- writer: REST API write operations (create, update)
- hasher: Content hashing for change detection
- mapper: Bidirectional path ↔ ID mapping
- validator: YAML format validation
- converter: Testmo ↔ YAML format conversion
- sync_engine: Smart bidirectional sync logic

Version: 1.0.0
"""

__version__ = "1.0.0"
__all__ = [
    "reader",
    "writer",
    "hasher",
    "mapper",
    "validator",
    "converter",
    "sync_engine"
]
