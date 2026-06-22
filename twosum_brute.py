
n = int(input())
target = int(input())
nums = list(map(int, input().split()))

for i in range(n):
    for j in range(i+1, n):
        if nums[i] + nums[j] == target:
            print('YES')
            exit(0)

print('NO')
