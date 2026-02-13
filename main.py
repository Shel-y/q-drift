import typer
import random
import math
import json
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
app = typer.Typer(help="⚛️ Q-Drift CLI - Quantum-Inspired Structural Drift Analyzer")


def quantum_gate_simulation(noise_level: float) -> int:
    """Simulates qubit collapse with amplitude damping."""
    base_probability: float = 0.9 
    shifted_probability: float = base_probability * (1.0 - noise_level)
    shifted_probability = max(0.0, min(1.0, shifted_probability))
    return 1 if random.random() < shifted_probability else 0


def calculate_entropy(states: list[int]) -> float:
    """Computes Shannon entropy of binary states."""
    total: int = len(states)
    if total == 0:
        return 0.0
    counts = Counter(states)
    entropy: float = 0.0
    for count in counts.values():
        p: float = count / total
        entropy -= p * math.log2(p)
    return entropy


def calculate_collapse_bias(states: list[int]) -> float:
    """Measures deviation from perfect equilibrium (0.5)."""
    total: int = len(states)
    if total == 0:
        return 0.0
    ones_ratio: float = states.count(1) / total
    return abs(ones_ratio - 0.5)


def render_distribution_chart(count_0: int, count_1: int) -> None:
    """Renders ASCII distribution chart."""
    total = count_0 + count_1
    if total == 0:
        return
    bar_width = 40
    ratio_0 = count_0 / total
    ratio_1 = count_1 / total
    bar_0 = "█" * int(ratio_0 * bar_width)
    bar_1 = "█" * int(ratio_1 * bar_width)
    console.print(Panel.fit(
        f"[cyan]State |0> (Fail)[/cyan]  {bar_0} {count_0} ({round(ratio_0*100, 1)}%)\n"
        f"[magenta]State |1> (Pass)[/magenta]  {bar_1} {count_1} ({round(ratio_1*100, 1)}%)",
        title="📊 Qubit Collapse Distribution",
        border_style="blue"
    ))

@app.command()
def analyze(
    simulations: int = typer.Option(1000, help="Number of simulated executions"),
    noise: float = typer.Option(0.3, help="Instability level (0.0 - 1.0)"),
    seed: int = typer.Option(None, help="Deterministic seed for reproducibility"),
    output: str = typer.Option(None, help="Path to export results as JSON"),
    graph: bool = typer.Option(default=True, help="Show ASCII distribution graph"),
    ci_mode: bool = typer.Option(default=False, help="Disable visual output for CI environments")
):
    """Analyze structural fragility under probabilistic drift."""

    if seed is not None:
        random.seed(seed)
        if not ci_mode:
            console.print(f"[dim]⚙️ Deterministic mode enabled. Seed: {seed}[/dim]")

    if simulations <= 0:
        console.print("[bold red]❌ Simulations must be > 0[/bold red]")
        raise typer.Exit(code=1)

    if not 0.0 <= noise <= 1.0:
        console.print("[bold red]❌ Noise must be between 0.0 and 1.0[/bold red]")
        raise typer.Exit(code=1)

    if not ci_mode:
        with console.status("[bold green]Simulating probabilistic state collapse..."):
            results: list[int] = [quantum_gate_simulation(noise) for _ in range(simulations)]
    else:
        results: list[int] = [quantum_gate_simulation(noise) for _ in range(simulations)]

    entropy: float = calculate_entropy(results)
    bias: float = calculate_collapse_bias(results)
    
    counts = Counter(results)
    state_0_count = counts.get(0, 0)
    state_1_count = counts.get(1, 0)

    if graph and not ci_mode:
        console.print("")
        render_distribution_chart(state_0_count, state_1_count)
        console.print("")

    
    if not ci_mode:
        table = Table(title="⚛️ Q-Drift Analysis Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Simulations", str(simulations))
        table.add_row("Noise Level", f"{round(noise * 100, 2)}%")
        table.add_row("Collapse Bias", f"{round(bias, 6)}")
        table.add_row("Drift Entropy Score", f"{round(entropy, 6)}")
        console.print(table)

    
    status_msg = ""
    exit_code = 0

    if entropy > 0.8:
        status_msg = "CRITICAL: High structural fragility detected."
        if not ci_mode:
            console.print(f"[bold red]🚨 {status_msg}[/bold red]")
        exit_code = 1
    elif entropy > 0.4:
        status_msg = "WARNING: Moderate drift detected."
        if not ci_mode:
            console.print(f"[bold yellow]⚠️ {status_msg}[/bold yellow]")
    else:
        status_msg = "STABLE: System appears robust."
        if not ci_mode:
            console.print(f"[bold green]✅ {status_msg}[/bold green]")

    
    if output:
        data = {
            "simulations": simulations,
            "noise_level": noise,
            "seed": seed,
            "metrics": {
                "entropy": entropy,
                "bias": bias,
                "distribution": {
                    "0_fail": state_0_count,
                    "1_pass": state_1_count
                }
            },
            "status": status_msg
        }
        try:
            with open(output, "w") as f:
                json.dump(data, f, indent=4)
            if not ci_mode:
                console.print(f"[dim]💾 Report saved to: {output}[/dim]")
        except IOError as e:
            console.print(f"[bold red]❌ Error saving JSON: {e}[/bold red]")
            raise typer.Exit(code=1)

    if exit_code != 0:
        raise typer.Exit(code=exit_code)



@app.command()
def version():
    """Show version"""
    console.print("q-drift v0.3.0 ⚛️")


if __name__ == "__main__":
    app()
