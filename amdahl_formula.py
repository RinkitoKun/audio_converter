# Amdahl's Law formula for theoretical speedup

def amdahl_speedup(P, S):
    """
    Calculate the theoretical speedup using Amdahl's Law.

    Parameters:
        P (int): Number of parallel units (e.g., processes or cores)
        S (float): Fraction of the program that is strictly serial (0 <= S <= 1)

    Returns:
        float: Theoretical speedup
    """
    if P <= 0 or not (0 <= S <= 1):
        raise ValueError("P must be > 0 and S must be between 0 and 1")
    return 1 / (S + (1 - S) / P)

def estimate_parallel_fraction(total_serial_time, total_parallel_time):
    """
    Estimate the parallelizable fraction P for Amdahl's Law.

    Parameters:
        total_serial_time (float): Time spent in serial (non-parallelizable) parts (seconds)
        total_parallel_time (float): Time spent in parallelizable parts (seconds)

    Returns:
        float: Estimated P (0 <= P <= 1)
    """
    total_time = total_serial_time + total_parallel_time
    if total_time == 0:
        return 0.0
    return total_parallel_time / total_time

# Example usage:
# If you measured 1 second serial setup and 19 seconds spent converting files:
# P = estimate_parallel_fraction(total_serial_time=1, total_parallel_time=19)
# print(f"Estimated parallel fraction P: {P:.2f}")
# speedup = amdahl_speedup(P=16, S=1-P)
# print(f"Theoretical speedup: {speedup:.2f}x")
