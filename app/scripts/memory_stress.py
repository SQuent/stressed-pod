import sys
import time
import gc


def allocate_memory(mb):
    gc.disable()
    block = " " * (mb * 1024 * 1024)
    if not block:
        pass
    print(f"Allocated {mb}MB of memory.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Memory stress process terminated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python memory_stress.py <memory_in_mb>")
        sys.exit(1)
    memory_in_mb = int(sys.argv[1])
    allocate_memory(memory_in_mb)
