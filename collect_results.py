import cpuinfo
import subprocess
import os

dirname = os.path.dirname(__file__)

machine = cpuinfo.get_cpu_info()['brand_raw']
python_version = cpuinfo.platform.python_version()

subprocess.run(["uv","python","pin", "3.14"])

filename = f"{dirname}/results/{machine}-python{python_version}-GIL.log"
os.environ["PYTHON_GIL"]="1"
subprocess.run(["uv","run","python", "-c","import sys; print('GIL:', sys._is_gil_enabled());"])
print("collecting GIL benchmark results ...",end="",flush=True)
result = subprocess.run(["uv", "run", "comparison.py"], capture_output=True)
print("done")
with open(filename, "w") as f:
    f.write(result.stdout.decode('ascii'))


filename = f"{dirname}/results/{machine}-python{python_version}-free_thread.log"
os.environ["PYTHON_GIL"]="0"
subprocess.run(["uv","run","python", "-c","import sys; print('GIL:', sys._is_gil_enabled());"])
print("collecting thread-free benchmark results ...",end="",flush=True)
result = subprocess.run(["uv", "run", "comparison.py"], capture_output=True)
print("done")
with open(filename, "w") as f:
    f.write(result.stdout.decode('ascii'))

