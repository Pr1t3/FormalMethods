import subprocess
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_random_3sat_dimacs(n_vars, n_clauses):
    clauses = []
    for _ in range(n_clauses):
        vars = random.sample(range(1, n_vars + 1), 3)
        clause = [v if random.random() < 0.5 else -v for v in vars]
        clauses.append(clause)

    lines = [f"p cnf {n_vars} {n_clauses}"]
    for cl in clauses:
        lines.append(" ".join(map(str, cl)) + " 0")
    return "\n".join(lines)

def solve_with_cadical(dimacs_str, timeout=30):
    start = time.time()
    try:
        Path("temp.cnf").write_text(dimacs_str)
        result = subprocess.run(
            ["cadical", "temp.cnf"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = (time.time() - start) * 1000
        is_sat = "s SATISFIABLE" in result.stdout
        return is_sat, elapsed
    except subprocess.TimeoutExpired:
        return None, (time.time() - start) * 1000
    except FileNotFoundError:
        return None, 0
    finally:
        Path("temp.cnf").unlink(missing_ok=True)

def plot_phase_transition():
    n = 50
    ratios = [3.0, 3.5, 4.0, 4.267, 4.5, 5.0, 6.0]
    trials = 100
    results = []

    for alpha in ratios:
        m = int(n * alpha)
        sat_count = 0
        times = []
        
        for t in range(trials):
            dimacs = generate_random_3sat_dimacs(n, m)
            is_sat, elapsed = solve_with_cadical(dimacs)
            if is_sat is not None:
                sat_count += is_sat
                times.append(elapsed)

        prob = sat_count / trials
        median_time = np.median(times) if times else 0
        results.append((alpha, prob, median_time))

    alphas, probs, _ = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(alphas, probs, 'bo-', markersize=6, linewidth=2, label='Empirical P(SAT)')
    plt.axvline(x=4.267, color='red', linestyle='--', linewidth=1.5, label=r'Theoretical threshold $\alpha_c \approx 4.267$')
    plt.xlabel(r"Clause ratio $\alpha = m/n$")
    plt.ylabel("Probability of SAT")
    plt.title(f"Phase Transition in Random 3-SAT (n={n}, {trials} instances per ratio)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-0.05, 1.05)
    plt.tight_layout()
    plt.savefig('phase_transition.png', dpi=300, bbox_inches='tight')
    plt.show()

    return results

def plot_runtime_vs_ratio(results):
    alphas, _, times = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(alphas, times, 'ro-', markersize=6, linewidth=2)
    plt.axvline(x=4.267, color='blue', linestyle='--', linewidth=1.5, label=r'Theoretical threshold $\alpha_c \approx 4.267$')
    plt.xlabel(r"Clause ratio $\alpha = m/n$")
    plt.ylabel("Median runtime (ms)")
    plt.title("Solver Runtime at Phase Transition (n=50)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('runtime_threshold.png', dpi=300, bbox_inches='tight')
    plt.show()

    peak_idx = np.argmax(times)
    print(f"Peak runtime: {times[peak_idx]:.1f}ms at alpha={alphas[peak_idx]:.3f}")

def plot_scaling_behavior():
    ns = [50, 100, 150, 200]
    alpha = 4.267
    trials = 20
    results = []

    for n in ns:
        m = int(n * alpha)
        times = []

        for t in range(trials):
            dimacs = generate_random_3sat_dimacs(n, m)
            _, elapsed = solve_with_cadical(dimacs, timeout=60)
            if elapsed > 0:
                times.append(elapsed)

        median_time = np.median(times) if times else 0
        results.append((n, median_time))

    ns_plot, times_plot = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(ns_plot, times_plot, 'go-', markersize=8, linewidth=2, label='Median runtime')

    log_times = np.log(np.array(times_plot) + 1)
    coeffs = np.polyfit(ns_plot, log_times, 1)
    b = coeffs[0]
    fit_times = np.exp(np.polyval(coeffs, ns_plot)) - 1

    plt.plot(ns_plot, fit_times, 'b--', linewidth=1.5, label=fr'Exp fit: $T \\sim e^{{{b:.3f}n}}$')

    plt.xlabel("Number of variables $n$")
    plt.ylabel("Median runtime (ms, log scale)")
    plt.yscale('log')
    plt.title(fr"Scaling at Critical Ratio $\alpha$={alpha}")
    plt.legend()
    plt.grid(True, alpha=0.3, which='both')
    plt.tight_layout()
    plt.savefig('scaling_behavior.png', dpi=300, bbox_inches='tight')
    plt.show()

random.seed(42)
results = plot_phase_transition()
plot_runtime_vs_ratio(results)
plot_scaling_behavior()