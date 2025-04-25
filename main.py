import csv
import sys
from itertools import combinations
from collections import defaultdict
import uuid

def load_data(filename):
    """Load the CSV file
       convert each row into a set of items.
      """
    transactions = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  

        for row in reader:
            transaction = set()
            for i, value in enumerate(row):
                if value.strip():  
                    item = f"{headers[i]}_{value.strip()}"
                    transaction.add(item)
            if transaction:  
                transactions.append(transaction)

    return transactions

def get_item_counts(transactions):
    """
    Count occurrences of individual items.
    """
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    return item_counts

def generate_candidates(prev_frequent, k):
    """Generate candidate itemsets of size k from frequent itemsets of size k-1."""
    candidates = set()
    prev_frequent = [frozenset(itemset) for itemset in prev_frequent]
    
    for i, itemset1 in enumerate(prev_frequent):
        for itemset2 in prev_frequent[i+1:]:
            union = itemset1 | itemset2
            if len(union) == k:
                # Check if all subsets of size k-1 are frequent
                subsets = [frozenset(c) for c in combinations(union, k-1)]
                if all(subset in prev_frequent for subset in subsets):
                    candidates.add(union)
    return candidates

def apriori(transactions, min_sup):
    """
     A-priori algorithm 
    """
    total_transactions = len(transactions)
    min_sup_count = min_sup * total_transactions
    
    #Find frequent 1-itemsets
    item_counts = get_item_counts(transactions)
    frequent_itemsets = []
    support_data = {}
    
    # Filter items with sufficient support
    for item, count in item_counts.items():
        if count >= min_sup_count:
            frequent_itemsets.append({item})
            support_data[frozenset([item])] = count / total_transactions
    

    k = 2
    while frequent_itemsets:
        candidates = generate_candidates(frequent_itemsets, k)
        candidate_counts = defaultdict(int)
        

        for transaction in transactions:
            transaction_set = frozenset(transaction)
            for candidate in candidates:
                if candidate.issubset(transaction_set):
                    candidate_counts[candidate] += 1
        

        frequent_itemsets = []
        for candidate, count in candidate_counts.items():
            if count >= min_sup_count:
                frequent_itemsets.append(set(candidate))
                support_data[candidate] = count / total_transactions
        
        k += 1
    
    return support_data

def generate_rules(frequent_itemsets, support_data, min_conf, total_transactions):
    """
    Generate high-confidence 
    association rules from frequent itemsets.
    """
    rules = []
    for itemset in frequent_itemsets:
        if len(itemset) < 2:  
            continue
        itemset = frozenset(itemset)
        for item in itemset:
            
            antecedent = itemset - frozenset([item])
            if antecedent:  
                conf = support_data[itemset] / support_data[antecedent]
                if conf >= min_conf:
                    rule = {
                        'antecedent': antecedent,
                        'consequent': frozenset([item]),
                        'confidence': conf,
                        'support': support_data[itemset]
                    }
                    rules.append(rule)
    return rules

def write_output(frequent_itemsets, rules, total_transactions):
    """
    Write frequent itemsets 
    and rules to output.txt in the specified format.
    """
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(f"==Frequent itemsets (min_sup={min_sup*100:.2f}%)\n")
       
        sorted_itemsets = sorted(
            frequent_itemsets.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for itemset, support in sorted_itemsets:
            items = sorted(list(itemset))  
            f.write(f"{items}, {support*100:.4f}%\n")
        
        f.write(f"\n==High-confidence association rules (min_conf={min_conf*100:.2f}%)\n")
        
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
        print("Usage: python3 main.py <filename> <min_sup> <min_conf>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        min_sup = float(sys.argv[2])
        min_conf = float(sys.argv[3])
        if not (0 <= min_sup <= 1 and 0 <= min_conf <= 1):
            raise ValueError("min_sup and min_conf must be between 0 and 1")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Load data
    transactions = load_data(filename)
    if not transactions:
        print("Error: No valid transactions found in the input file")
        sys.exit(1)
    
    frequent_itemsets = apriori(transactions, min_sup)
     
    rules = generate_rules(frequent_itemsets.keys(), frequent_itemsets, min_conf, len(transactions))
    
    # Write output
    write_output(frequent_itemsets, rules, len(transactions))