def parse_cpu_millis(cpu: str) -> int:
    cpu = int(cpu.replace('m', '').replace('"', ''))
    if cpu <= 10:
        # in case resource request is 1 (== 1 core) == 1000m
        return cpu * 1000
    return cpu
