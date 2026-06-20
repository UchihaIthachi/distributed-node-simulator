def plot_energy(all_nodes, output_path="output/energy_plot.png"):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping plot")
        return

    plt.figure(figsize=(10, 5))

    for n in all_nodes:
        if n.energy_history:
            plt.plot(n.energy_history, label=f"Node {n.id} ({n.role})")

    plt.xlabel("Tick")
    plt.ylabel("Energy")
    plt.title("Node energy over time")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Energy plot saved to {output_path}")
