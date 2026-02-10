limits = "100:120,20:1,99:120,9:12"
counts = "1:120,1:1,2:120,3:12"

limits = limits.split(",")
counts = counts.split(",")

limits_counts = list(zip(limits, counts))

def get_rate(_limit_count):
    requests, per_second = _limit_count[0].split(":")
    return float(requests) / float(per_second)

sorted_limits_counts = sorted(limits_counts, key = get_rate)

print(sorted_limits_counts[0])