limits = "100:120,20:1"
counts = "1:120,1:1"

limits = limits.split(",")
counts = counts.split(",")

limits_counts = list(zip(limits, counts))

def get_rates(_sorted_limits_count):
    requests, per_second = _sorted_limits_count[0].split(":")
    return float(requests) / float(per_second)


sorted_limits_counts = sorted(limits_counts, key = get_rates)

print(sorted_limits_counts)