import sys
import time
import multiprocessing


def stress_single_cpu():
    """Charge un CPU à 100% en utilisant une boucle intensive."""
    while True:
        pass


def stress_fractional_cpu(fraction):
    """Charge un CPU à une fraction spécifique."""
    interval = 0.1
    while True:
        start = time.time()
        while (time.time() - start) < fraction * interval:
            pass
        time.sleep(interval - fraction * interval)


def stress_cpu(cpu_count, fraction):
    """Simule l'utilisation de CPU avec un nombre total de CPUs simulés."""
    processes = []
    try:
        for _ in range(int(cpu_count)):
            p = multiprocessing.Process(target=stress_single_cpu)
            p.daemon = True
            p.start()
            processes.append(p)
        if fraction > 0:
            p = multiprocessing.Process(target=stress_fractional_cpu, args=(fraction,))
            p.daemon = True
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cpu_stress.py <cpu_load>")
        print("<cpu_load> can be a fractional value (e.g., 2.5 for 2 CPUs + 50%).")
        sys.exit(1)

    cpu_load = float(sys.argv[1])
    if cpu_load <= 0:
        print("Error: CPU load must be greater than 0.")
        sys.exit(1)

    full_cpus = int(cpu_load)
    fractional_cpu = cpu_load - full_cpus
    stress_cpu(full_cpus, fractional_cpu)
