
n = int(input())
target = int(input())
nums = list(map(int, input().split()))

numset = set(nums)

for i in range(n):
    # Oops, let's say our solution here is bugged because we are not allowed to use the same number twice
    y = target - nums[i]
    if y in numset:
        print('YES')
        exit(0)

print('NO')