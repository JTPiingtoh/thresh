limits = "100:120,20:1"
counts = "1:120,1:20"

# limits = limits.split(",")
# counts = counts.split(",")

# limits_counts = list(zip(limits, counts))

# def get_rate(_limit_count):
#     requests, per_second = _limit_count[0].split(":")
#     return float(requests) / float(per_second)

# sorted_limits_counts = sorted(limits_counts, key = get_rate)

# print(sorted_limits_counts[0])



header_limits = {
    "app" : [[int(v) for v in t.split(':')] for t in limits.split(',')],
    "method" : [[int(v) for v in t.split(':')] for t in limits.split(',')]
}

print(len(header_limits["app"]))