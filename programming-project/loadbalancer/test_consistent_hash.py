from consistent_hash import ConsistentHashMap

chm = ConsistentHashMap()

# Add 3 servers
chm.add_server(1, "S1")
chm.add_server(2, "S2")
chm.add_server(3, "S3")

print("Servers registered:", chm.servers())

# Route a batch of sample request IDs
sample_ids = [132574, 100001, 555555, 987654, 42]
for rid in sample_ids:
    print(f"Request {rid} -> {chm.get_server_for_request(rid)}")

# Check distribution across many requests
from collections import Counter
counts = Counter(chm.get_server_for_request(rid) for rid in range(100000, 110000))
print("\nDistribution over 10000 sample IDs:", counts)

# Test failure: remove S2, confirm its requests move to a different server
print("\nRemoving S2...")
chm.remove_server("S2")
print("Servers now:", chm.servers())
counts_after = Counter(chm.get_server_for_request(rid) for rid in range(100000, 110000))
print("Distribution after removing S2:", counts_after)
