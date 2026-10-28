from winring.geometry import slot_at, slot_center, page_count, page_slice
import math

# 8 slot: slot 0 di atas, searah jarum jam
assert slot_at(0, -100, 8, 20) == 0          # atas
assert slot_at(100, 0, 8, 20) == 2           # kanan
assert slot_at(0, 100, 8, 20) == 4           # bawah
assert slot_at(-100, 0, 8, 20) == 6          # kiri
assert slot_at(5, 5, 8, 20) == -1            # dead zone
assert slot_at(10, -10, 0, 0) == -1          # tanpa slot
assert slot_at(1, -100, 1, 20) == 0          # satu slot
# pusat slot konsisten dengan hit-test
for n in (1, 2, 3, 5, 7, 12):
    for i in range(n):
        x, y = slot_center(i, n, 100)
        assert slot_at(x, y, n, 20) == i, (n, i)
assert page_count(0) == 1 and page_count(12) == 1 and page_count(13) == 2
assert page_slice(list(range(30)), 2) == list(range(24, 30))
print("geometry OK")
