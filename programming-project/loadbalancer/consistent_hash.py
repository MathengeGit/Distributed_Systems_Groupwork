"""
Consistent hash map as specified in the assignment (Appendix B).

M        = total slots in the ring (default 512)
K        = virtual servers per physical server (default log2(M) = 9)
H(i)     = request-mapping hash:   i^2 + 2*i + 17
PHI(i,j) = server-mapping hash:    i^2 + j^2 + 2*j + 25

Collisions are resolved with linear probing (clockwise) on the ring.
"""


def H(request_id: int, M: int) -> int:
    return (request_id ** 2 + 2 * request_id + 17) % M


def PHI(server_num_id: int, replica_id: int, M: int) -> int:
    return (server_num_id ** 2 + replica_id ** 2 + 2 * replica_id + 25) % M


class ConsistentHashMap:
    def __init__(self, M: int = 512, K: int = 9):
        self.M = M
        self.K = K
        self.slots = [None] * M          # slot -> hostname
        self.hostname_slots = {}         # hostname -> list[int] of occupied slots

    def _next_free_slot(self, start: int) -> int:
        slot = start % self.M
        first = slot
        while self.slots[slot] is not None:
            slot = (slot + 1) % self.M
            if slot == first:
                raise RuntimeError("Consistent hash map is full")
        return slot

    def add_server(self, server_num_id: int, hostname: str):
        if hostname in self.hostname_slots:
            raise ValueError(f"{hostname} already present in hash map")
        placed = []
        for j in range(self.K):
            ideal = PHI(server_num_id, j, self.M)
            slot = self._next_free_slot(ideal)
            self.slots[slot] = hostname
            placed.append(slot)
        self.hostname_slots[hostname] = placed

    def remove_server(self, hostname: str):
        for slot in self.hostname_slots.pop(hostname, []):
            self.slots[slot] = None

    def get_server_for_request(self, request_id: int):
        slot = H(request_id, self.M)
        first = slot
        while self.slots[slot] is None:
            slot = (slot + 1) % self.M
            if slot == first:
                return None  # no servers registered
        return self.slots[slot]

    def servers(self):
        return list(self.hostname_slots.keys())
