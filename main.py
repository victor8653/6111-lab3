import csv
import sys
from itertools import combinations
from collections import defaultdict
import uuid


def load_data(file):
    """Load the CSV file
       convert each row into a set of items.
      """
    baskets = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            transaction = set()
            for i, value in enumerate(row):
                if value.strip():
                    item = f"{headers[i]}_{value.strip()}"
                    transaction.add(item)
            if transaction:
                baskets.append(transaction)

    return baskets


def get_item_counts(baskets):
    """
    Count occurrences of individual items.
    """
    item_counts = defaultdict(int)
    for transaction in baskets:
        for item in transaction:
            item_counts[item] += 1
    return item_counts


def generate_candidates(prev_frequent, k):
    """Generate candidate itemsets of size k from frequent itemsets of size k-1."""
    candidates = set()
    prev_frequent = [frozenset(itemset) for itemset in prev_frequent]

    for i, itemset1 in enumerate(prev_frequent):
        for itemset2 in prev_frequent[i + 1:]:
            union = itemset1 | itemset2
            if len(union) == k:
                # Check if all subsets of size k-1 are frequent
                subsets = [frozenset(c) for c in combinations(union, k - 1)]
                if all(subset in prev_frequent for subset in subsets):
                    candidates.add(union)
    return candidates


def apriori(baskets, min_sup):
    """
     A-priori algorithm
    """
    total_transactions = len(baskets)
    min_sup_count = min_sup * total_transactions

    # Find frequent 1-itemsets
    item_counts = get_item_counts(baskets)
    freqs = []
    sup_dict = {}

    # Filter items with sufficient support
    for item, count in item_counts.items():
        if count >= min_sup_count:
            freqs.append({item})
            sup_dict[frozenset([item])] = count / total_transactions

    k = 2
    while freqs:
        candidates = generate_candidates(freqs, k)
        candidate_counts = defaultdict(int)

        for transaction in baskets:
            transaction_set = frozenset(transaction)
            for candidate in candidates:
                if candidate.issubset(transaction_set):
                    candidate_counts[candidate] += 1

        freqs = []
        for candidate, count in candidate_counts.items():
            if count >= min_sup_count:
                freqs.append(set(candidate))
                sup_dict[candidate] = count / total_transactions

        k += 1

    return sup_dict


def make_rules(freqs, sup_dict, min_conf, total_transactions):
    """
    Generate high-confidence
    association rules from frequent itemsets.
    """
    rules = []
    for itemset in freqs:
        if len(itemset) < 2:
            continue
        itemset = frozenset(itemset)
        for item in itemset:

            antecedent = itemset - frozenset([item])
            if antecedent:
                conf = sup_dict[itemset] / sup_dict[antecedent]
                if conf >= min_conf:
                    rule = {
                        'antecedent': antecedent,
                        'consequent': frozenset([item]),
                        'confidence': conf,
                        'support': sup_dict[itemset]
                    }
                    rules.append(rule)
    return rules


def write_output(freqs, rules, total_transactions):
    """
    Write frequent itemsets
    and rules to output.txt in the specified format.
    """
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(f"==Frequent itemsets (min_sup={min_sup * 100:.2f}%)\n")

        sorted_itemsets = sorted(
            freqs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for itemset, support in sorted_itemsets:
            items = sorted(list(itemset))
            f.write(f"{items}, {support * 100:.4f}%\n")

        f.write(f"\n==High-confidence association rules (min_conf={min_conf * 100:.2f}%)\n")

        sorted_rules = sorted(
            rules,
            key=lambda x: (x['confidence'], x['support']),
            reverse=True
        )
        for rule in sorted_rules:
            antecedent = sorted(list(rule['antecedent']))
            consequent = sorted(list(rule['consequent']))
            conf = rule['confidence'] * 100
            supp = rule['support'] * 100
            f.write(f"{antecedent} => {consequent} (Conf: {conf:.1f}%, Supp: {supp:.4f}%)\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <file> <min_sup> <min_conf>")
        sys.exit(1)

    file = sys.argv[1]
    try:
        min_sup = float(sys.argv[2])
        min_conf = float(sys.argv[3])
        if not (0 <= min_sup <= 1 and 0 <= min_conf <= 1):
            raise ValueError("min_sup and min_conf must be between 0 and 1")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load data
    baskets = load_data(file)
    if not baskets:
        print("Error: No valid transactions found in the input file")
        sys.exit(1)

    freqs = apriori(baskets, min_sup)

    rules = make_rules(freqs.keys(), freqs, min_conf, len(baskets))

    # Write output
    write_output(freqs, rules, len(baskets))