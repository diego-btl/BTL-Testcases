# Tests

Unit tests will be added here to validate:

- Content hashing (hasher.py)
- Path ↔ ID mapping (mapper.py)
- YAML validation (validator.py)
- MCP read operations (reader.py)
- REST API write operations (writer.py)
- Conversion logic (converter.py)
- Sync engine (sync_engine.py)

Tests will use pytest framework.

Run tests:
```bash
pytest tests/
```

Coverage report:
```bash
pytest --cov=testmo_sync tests/
```
