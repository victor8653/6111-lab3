import sys
import pandas as pd
from itertools import combinations
from collections import defaultdict

# Parse command-line arguments
if len(sys.argv) != 4:
    print("Usage: python3 main.py INTEGRATED-DATASET.csv min_sup min_conf")
    sys.exit(1)

filename = sys.argv[1]
minsup = float(sys.argv[2])
minconf = float(sys.argv[3])

# Load dataset
df = pd.read_csv(filename)

# Convert each row into a transaction (set of items)
transactions = []
for _, row in df.iterrows():
    # Get rid of null values
    transaction = [str(item).strip() for item in row if pd.notna(item) and str(item).strip().lower() != "nan"]
    transactions.append(set(transaction))

# Generate frequent 1-itemsets
item_counts = defaultdict(int)
total_transactions = len(transactions)

for txn in transactions:
    for item in txn:
        item_counts[(item,)] += 1

L1_frequent = []
count_record_dict = {}

for item, count in item_counts.items():
    support = count / total_transactions
    if support >= minsup:
        L1_frequent.append(item)
        count_record_dict[item] = support

L_list = [L1_frequent]

# Generate higher-order frequent itemsets
k = 2
while True:
    prev_frequents = L_list[-1]
    candidates = []

    prev_itemsets = set(prev_frequents)
    items = set(i for tup in prev_frequents for i in tup)

    for comb in combinations(items, k):
        comb = tuple(sorted(comb))
        # Only consider if all subsets are frequent
        if all(tuple(sorted(subset)) in prev_itemsets for subset in combinations(comb, k - 1)):
            # Calculate support
            count = sum(1 for txn in transactions if all(item in txn for item in comb))
            support = count / total_transactions
            if support >= minsup:
                candidates.append(comb)
                count_record_dict[comb] = support

    if not candidates:
        break

    L_list.append(candidates)
    k += 1

# Generate association rules
rules = []
for layer in L_list[1:]:
    for itemset in layer:
        for i in range(len(itemset)):
            antecedent = itemset[:i] + itemset[i+1:]
            consequent = itemset[i]
            if not antecedent:
                continue
            if antecedent in count_record_dict:
                conf = count_record_dict[itemset] / count_record_dict[antecedent]
                if conf >= minconf:
                    rules.append((antecedent, consequent, conf, count_record_dict[itemset]))

# Output results
with open("example-run.txt", "w") as f:
    f.write(f"==Frequent itemsets (min_sup={int(minsup*100)}%)\n")
    all_frequents = [(k, v) for k, v in count_record_dict.items()]
    all_frequents.sort(key=lambda x: -x[1])
    for itemset, support in all_frequents:
        items = ",".join(itemset)
        f.write(f"[{items}], {support*100:.4f}%\n")

    f.write(f"\n==High-confidence association rules (min_conf={int(minconf*100)}%)\n")
    rules.sort(key=lambda x: -x[2])
    for antecedent, consequent, conf, supp in rules:
        antecedent_str = ",".join(antecedent)
        f.write(f"[{antecedent_str}] => [{consequent}] (Conf: {conf*100:.1f}%, Supp: {supp*100:.4f}%)\n")
