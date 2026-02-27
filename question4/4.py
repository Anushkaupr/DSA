#  Input Data 
DEMAND = {
    6: {'A': 20, 'B': 15, 'C': 25},
    7: {'A': 22, 'B': 16, 'C': 28},
    8: {'A': 25, 'B': 18, 'C': 30},
    9: {'A': 28, 'B': 20, 'C': 32},
    10: {'A': 30, 'B': 22, 'C': 35},
    17: {'A': 35, 'B': 28, 'C': 40},
    18: {'A': 38, 'B': 30, 'C': 42},
}

SOURCES = [
    {'id': 'S1', 'type': 'Solar', 'cap': 50, 'start': 6, 'end': 18, 'cost': 1.0},
    {'id': 'S2', 'type': 'Hydro', 'cap': 40, 'start': 0, 'end': 24, 'cost': 1.5},
    {'id': 'S3', 'type': 'Diesel', 'cap': 60, 'start': 17, 'end': 23, 'cost': 3.0},
]

TOLERANCE = 0.10
DISTRICTS = ['A', 'B', 'C']


def get_available_sources(hour):
    """Return sources active at 'hour', sorted by increasing cost."""
    active = [s for s in SOURCES if s['start'] <= hour < s['end']]
    return sorted(active, key=lambda x: x['cost'])


def allocate_hour(hour, demand_dict):
    """
    Allocate energy to districts for one hour using a greedy approach.
    Cheapest source is used first. Allows up to 10% shortfall.
    
    Returns:
        alloc: dict keyed by source id with energy allocated (kWh)
        hour_cost: total cost for this hour (Rs.)
    """
    sources = get_available_sources(hour)
    alloc = {s['id']: 0.0 for s in SOURCES}
    unmet = {d: demand_dict[d] for d in DISTRICTS}
    hour_cost = 0.0

    for src in sources:
        cap = src['cap']
        for district in DISTRICTS:
            if unmet[district] <= 0 or cap <= 0:
                continue
            give = min(unmet[district], cap)
            alloc[src['id']] += give
            unmet[district] -= give
            cap -= give
            hour_cost += give * src['cost']

    # Check for tolerance violations
    for d in DISTRICTS:
        if unmet[d] > demand_dict[d] * TOLERANCE:
            print(f" [WARNING] Hour {hour} District {d}: shortfall {unmet[d]:.1f} kWh exceeds 10% tolerance.")

    return alloc, hour_cost


def run_simulation():
    """Run the hourly allocation simulation and print results."""
    print(f"\n{'Hour':<6}{'Dist':<6}{'Solar':>8}{'Hydro':>8}{'Diesel':>8}"
          f"{'Total':>7}{'Demand':>8}{'% Met':>7}")
    print("-" * 58)

    grand_cost = 0.0
    total_energy = 0.0
    total_renew = 0.0
    diesel_hours = []

    for hour in sorted(DEMAND.keys()):
        dem = DEMAND[hour]
        alloc, cost = allocate_hour(hour, dem)
        grand_cost += cost
        if alloc['S3'] > 0:
            diesel_hours.append(hour)
        tot_dem = sum(dem.values())

        for district in DISTRICTS:
            share = dem[district] / tot_dem
            solar = round(alloc['S1'] * share, 1)
            hydro = round(alloc['S2'] * share, 1)
            diesel = round(alloc['S3'] * share, 1)
            total = solar + hydro + diesel
            pct = min(100.0, round(total / dem[district] * 100, 1))
            print(f"{hour:<6}{district:<6}{solar:>8.1f}{hydro:>8.1f}{diesel:>8.1f}"
                  f"{total:>7.1f}{dem[district]:>8.1f}{pct:>6.1f}%")
            total_energy += total
            total_renew += solar + hydro

    pct_renew = (total_renew / total_energy * 100) if total_energy else 0
    print("=" * 58)
    print(f"Total cost : Rs. {grand_cost:.2f}")
    print(f"Renewable share : {pct_renew:.1f}%")
    print(f"Diesel used at : {diesel_hours if diesel_hours else 'None'}")
    print("\nAlgorithm note : Greedy allocation by cheapest source first, O(H*S*logS).")
    print("Trade-off : Fast and near-optimal for independent hours; may not be globally optimal")
    print("if cross-hour reservoir or battery constraints exist.")


if __name__ == "__main__":
    run_simulation()