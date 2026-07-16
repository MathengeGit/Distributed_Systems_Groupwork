# Tests

## Unit test: consistent hash map

Run with:
    python3 test_consistent_hash.py

This verifies:
- Servers register correctly with K=9 virtual nodes each
- Requests route deterministically (same ID always maps to same server)
- Removing a server only redistributes that server's share, not the whole ring
- Distribution across 10,000 random 6-digit request IDs is reasonably even

## Manual endpoint tests (Task 1 & 3)

With the stack running (`make up` from repo root), from any terminal:

    curl http://localhost:5000/home
    curl -i http://localhost:5000/heartbeat
    curl http://localhost:5000/rep
    curl -X POST http://localhost:5000/add -H "Content-Type: application/json" -d '{"n":2,"hostnames":["S5","S4"]}'
    curl -X DELETE http://localhost:5000/rm -H "Content-Type: application/json" -d '{"n":1,"hostnames":["S5"]}'
    curl http://localhost:5000/nonexistent

Expected results are documented in the main README under "Testing".
