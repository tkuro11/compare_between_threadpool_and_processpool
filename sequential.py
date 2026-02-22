import timeit

bt = timeit.default_timer()
count = 0
for i in range(100_000_000):
    count += 1
print(count)
print(f"in global scope: elapsed time: {timeit.default_timer()-bt}")


def bench_local():
    count = 0
    for i in range(100_000_000):
        count += 1
    return count

bt = timeit.default_timer()
print(bench_local())
print(f"in function scope: elapsed time: {timeit.default_timer()-bt}")

def bench_global():
    global count, i
    count = 0
    for i in range(100_000_000):
        count += i
    return count

bt = timeit.default_timer()
print(bench_global())
print(f"in global scope(in function): elapsed time: {timeit.default_timer()-bt}")

import dis

print("## disassemble  of 'bench_local'")
print(dis.dis(bench_local))
print("## disassemble  of 'bench_global'")
print(dis.dis(bench_global))
