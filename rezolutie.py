import time
import tracemalloc
import csv
from heapq import heappush, heappop

def parse_input():
    print("Introdu clauzele (ex: 'A -B C'). Pentru a termina, lasă o linie goală:")
    clauses = []
    while True:
        line = input().strip()
        if not line and clauses:
            break
        if not line and not clauses:
            print("Introdu cel puțin o clauză!")
            continue
        literals = line.split()
        clause = frozenset(literals)
        clauses.append(clause)
    return clauses

def negate(literal):
    return literal[1:] if literal.startswith('-') else '-' + literal

def unit_propagation(clauses):
    units = [c for c in clauses if len(c) == 1]
    while units:
        unit = units.pop()
        literal = next(iter(unit))
        neg_lit = negate(literal)
        
        new_clauses = []
        for clause in clauses:
            if literal in clause:
                continue 
            if neg_lit in clause:
                new_clause = clause - {neg_lit}
                if not new_clause:
                    return None 
                new_clauses.append(new_clause)
                if len(new_clause) == 1:
                    units.append(new_clause)
            else:
                new_clauses.append(clause)
        clauses = new_clauses
    return clauses

def select_clause(clauses):
    return min(clauses, key=len)

def resolution(clauses, max_steps=100000):
    steps = 0
    processed = set()
    active = set(clauses)
    
    while active and steps < max_steps:
        steps += 1
        ci = select_clause(active)
        active.remove(ci)
        
        for cj in list(active):
            resolvents = resolve(ci, cj)
            for r in resolvents:
                if not r:
                    return True 
                if r not in processed:
                    processed.add(r)
                    active.add(r)
    
    return False if steps < max_steps else None

def resolve(ci, cj):
    resolvents = set()
    for lit in ci:
        neg_lit = negate(lit)
        if neg_lit in cj:
            new_clause = (ci - {lit}) | (cj - {neg_lit})
            resolvents.add(frozenset(new_clause))
    return resolvents

def run_solver():
    clauses = parse_input()
    if not clauses:
        return
    
    print("\nClauze de procesat:", len(clauses))
    start = time.time()
    simplified = unit_propagation(clauses)
    if simplified is None:
        print("Rezultat: NESATISFIABILĂ (prin unit propagation)")
        return True
    tracemalloc.start()
    start_time = time.perf_counter()
    try:
        result = resolution(simplified)
    except Exception as e:
        print(f"Eroare: {str(e)}")
        result = None
    end_time = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    durata = end_time - start_time
    mem_mb = peak / (1024 * 1024)
    
    if result is None:
        print("Limită depășită - nu s-a putut determina")
    elif result:
        print("Rezultat: NESATISFIABILĂ")
    else:
        print("Rezultat: SATISFIABILĂ")
    
    print(f"Timp: {durata:.2f}s, Memorie: {mem_mb:.2f}MB")
    save_results(
        len(clauses),
        sum(len(c) for c in clauses),
        durata,
        mem_mb,
        "UNSAT" if result else "SAT" if result is False else "UNKNOWN"
    )

def save_results(n_clauses, n_literals, time_sec, mem_mb, result):
    try:
        with open("results.csv", "a") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["Clauses", "Literals", "Time(s)", "Memory(MB)", "Result"])
            writer.writerow([n_clauses, n_literals, f"{time_sec:.2f}", f"{mem_mb:.2f}", result])
    except Exception as e:
        print(f"Eroare la salvare: {e}")

if __name__ == "__main__":
    print("=== SAT Solver Optimizat ===")
    run_solver()
