import os
import platform
import subprocess

def print_hyperthreading_info():
    try:
        import psutil
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        print(f"Physical cores: {physical_cores}")
        print(f"Logical processors: {logical_cores}")
        if logical_cores > physical_cores:
            print("Hyperthreading/SMT is enabled.")
        else:
            print("No hyperthreading/SMT detected.")
    except ImportError:
        print("psutil not installed. Trying Windows WMIC method...")
        if platform.system() == "Windows":
            try:
                # WMIC is deprecated but still works on most Windows 10/11
                output = subprocess.check_output(
                    "wmic cpu get NumberOfCores,NumberOfLogicalProcessors /format:csv",
                    shell=True, encoding="utf-8"
                )
                lines = [line.strip() for line in output.splitlines() if line.strip()]
                if len(lines) >= 2:
                    headers = lines[0].split(",")
                    values = lines[1].split(",")
                    core_idx = headers.index("NumberOfCores")
                    logical_idx = headers.index("NumberOfLogicalProcessors")
                    physical_cores = int(values[core_idx])
                    logical_cores = int(values[logical_idx])
                    print(f"Physical cores: {physical_cores}")
                    print(f"Logical processors: {logical_cores}")
                    if logical_cores > physical_cores:
                        print("Hyperthreading/SMT is enabled.")
                    else:
                        print("No hyperthreading/SMT detected.")
                else:
                    print("Could not parse WMIC output.")
            except Exception as e:
                print(f"WMIC method failed: {e}")
                print("Please install psutil with: pip install psutil")
        else:
            print("psutil not installed and not running on Windows. Please install psutil.")

if __name__ == "__main__":
    print_hyperthreading_info()
