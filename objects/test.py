l1 = [1,2,3,4]
l2 = ["A", "B", "C", "D"]


newLatestStartTime = dict.fromkeys(l1, 1440)

print(newLatestStartTime)

print(max(list(newLatestStartTime.values())))