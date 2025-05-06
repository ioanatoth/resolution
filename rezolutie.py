import time
import tracemalloc
import csv

def parse_input():
    print("Introdu clauzele în forma CNF (literali separați prin spațiu, - pentru negare).")
    print("Exemplu: A -B   înseamnă (A ∨ ¬B). Clauză vidă: apasă ENTER de 2 ori.")
    clauses = []
    while True:
        line = input().strip()
        if line == "":
            break
        literals = line.split()
        clause = frozenset(literals)
        clauses.append(clause)
    return set(clauses)

def negate(literal):
    return literal[1:] if literal.startswith("-") else "-" + literal

def resolve(ci, cj):
    resolvents = set()
    for lit in ci:
        if negate(lit) in cj:
            new_clause = (ci - {lit}) | (cj - {negate(lit)})
            resolvents.add(frozenset(new_clause))
    return resolvents

def resolution(clauses):
    processed = set(clauses)
    while True:
        new = set()
        clause_list = list(processed)
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = resolve(clause_list[i], clause_list[j])
                for r in resolvents:
                    if not r:
                        print(f"Clauză vidă generată din {clause_list[i]} și {clause_list[j]}.")
                        return True
                    if r not in processed:
                        new.add(r)
        if not new:
            return False
        processed.update(new)

def salveaza_performanta_csv(timp, memorie_kb, nr_clauze, nr_literali, medie_literali, rezultat, nume_test="Test", nume_fisier="rezultate_performanta.csv"):
    scrie_antet = False
    try:
        with open(nume_fisier, "r"):
            pass
    except FileNotFoundError:
        scrie_antet = True

    with open(nume_fisier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if scrie_antet:
            writer.writerow(["Nume test", "Nr. clauze", "Nr. literali (total)", "Medie literali/clauză","Timp (secunde)", "Memorie max (KB)", "Satisfiabilitate"])
        writer.writerow([nume_test, nr_clauze, nr_literali, f"{medie_literali:.2f}",f"{timp:.6f}", f"{memorie_kb:.2f}", rezultat])
        
if __name__ == "__main__":
    clauses = parse_input()
    print("\nClauzele introduse:")
    for clause in clauses:
        print(clause)

    nr_clauze = len(clauses)
    nr_literali = sum(len(cl) for cl in clauses)
    medie_literali = nr_literali / nr_clauze if nr_clauze > 0 else 0

    tracemalloc.start()
    start_time = time.perf_counter()

    is_unsatisfiable = resolution(clauses)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    durata = end_time - start_time
    memorie_kb = peak / 1024
    
    salveaza_performanta_csv(
    durata, memorie_kb, nr_clauze, nr_literali, medie_literali,
    rezultat="NESATISFIABILA" if is_unsatisfiable else "SATISFIABILA",
    nume_test=f"Test-{nr_clauze}cl-{nr_literali}lit"
)

    if is_unsatisfiable:
        print("\nFormula este nesatisfiabila.")
    else:
        print("\nFormula este satisfiabilă.")

    print(f"\nTimp de execuție: {durata:.6f} secunde")
    print(f"Memorie maximă utilizată: {memorie_kb:.2f} KB")
    print(f"Numar clauze: {nr_clauze}, numar total literali: {nr_literali}, medie/clauza: {medie_literali:.2f}")
