from taskA.classes.FormulaAST import *
from taskA.classes.TruthTable import TruthTable
from pyparsing import infixNotation, opAssoc, Word, alphas, Suppress
from itertools import product

def to_string(formula: Operand) -> str:
    curPrecedence = formula.precedence
    if isinstance(formula, Atom):
        return formula.name
    elif isinstance(formula, Not):
        operand = f"({to_string(formula.operand)})" if curPrecedence > formula.operand.precedence else to_string(formula.operand)
        return f'¬{operand}'
    elif isinstance(formula, And):
        left = f"({to_string(formula.left)})" if curPrecedence > formula.left.precedence else to_string(formula.left)
        right = f"({to_string(formula.right)})" if curPrecedence > formula.right.precedence else to_string(formula.right)
        return f'{left} ∧ {right}'
    elif isinstance(formula, Or):
        left = f"({to_string(formula.left)})" if curPrecedence > formula.left.precedence else to_string(formula.left)
        right = f"({to_string(formula.right)})" if curPrecedence > formula.right.precedence else to_string(formula.right)
        return f'{left} ∨ {right}'
    elif isinstance(formula, Implies):
        left = f"({to_string(formula.left)})" if curPrecedence > formula.left.precedence else to_string(formula.left)
        right = f"({to_string(formula.right)})" if curPrecedence > formula.right.precedence else to_string(formula.right)
        return f'{left} → {right}'
    elif isinstance(formula, Iff):
        left = f"({to_string(formula.left)})" if curPrecedence > formula.left.precedence else to_string(formula.left)
        right = f"({to_string(formula.right)})" if curPrecedence > formula.right.precedence else to_string(formula.right)
        return f'{left} ↔ {right}'
    elif isinstance(formula, TrueConst):
        return '⊤'
    elif isinstance(formula, FalseConst):
        return '⊥'
    else:
        raise ValueError("Unknown formula type")

def parse(formula_str: str) -> Operand:
    atom = Word(alphas, exact=1).setParseAction(lambda t: Atom(t[0]))
    true_const = Suppress('⊤').setParseAction(lambda: TrueConst())
    false_const = Suppress('⊥').setParseAction(lambda: FalseConst())
    operand = atom | true_const | false_const

    def not_action(t):
        return Not(t[0][1])

    def and_action(t):
        return And(t[0][0], t[0][2])

    def or_action(t):
        return Or(t[0][0], t[0][2])

    def implies_action(t):
        return Implies(t[0][0], t[0][2])

    def iff_action(t):
        return Iff(t[0][0], t[0][2])

    formula_parser = infixNotation(operand,
        [
            ('¬', 1, opAssoc.RIGHT, not_action),
            ('∧', 2, opAssoc.LEFT, and_action),
            ('∨', 2, opAssoc.LEFT, or_action),
            ('→', 2, opAssoc.RIGHT, implies_action),
            ('↔', 2, opAssoc.RIGHT, iff_action),
        ])
    
    parsed = formula_parser.parseString(formula_str, parseAll=True)
    return parsed[0]

def eval(formula: Operand, interpretation: dict[str, bool]) -> bool:
    if isinstance(formula, Atom):
        return interpretation[formula.name]
    elif isinstance(formula, Not):
        return not eval(formula.operand, interpretation)
    elif isinstance(formula, And):
        return eval(formula.left, interpretation) and eval(formula.right, interpretation)
    elif isinstance(formula, Or):
        return eval(formula.left, interpretation) or eval(formula.right, interpretation)
    elif isinstance(formula, Implies):
        return not eval(formula.left, interpretation) or eval(formula.right, interpretation)
    elif isinstance(formula, Iff):
        return eval(formula.left, interpretation) == eval(formula.right, interpretation)
    elif isinstance(formula, TrueConst):
        return True
    elif isinstance(formula, FalseConst):
        return False
    else:
        raise ValueError("Unknown formula type")

def extract_atoms(formula: Operand) -> set[str]:
    if isinstance(formula, Atom):
        return {formula.name}
    elif isinstance(formula, Not):
        return extract_atoms(formula.operand)
    elif isinstance(formula, (And, Or, Implies, Iff)):
        return extract_atoms(formula.left) | extract_atoms(formula.right)
    elif isinstance(formula, (TrueConst, FalseConst)):
        return set()

def truth_table(formula: Operand) -> TruthTable:
    atoms = sorted(extract_atoms(formula))
    table = []
    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        result = eval(formula, interpretation)
        table.append((interpretation, result))
    return TruthTable(atoms, table, to_string(formula))

def is_tautology(formula: Operand) -> bool:
    atoms = sorted(extract_atoms(formula))
    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        if not eval(formula, interpretation):
            return False
    return True

def is_satisfiable(formula: Operand) -> bool:
    atoms = sorted(extract_atoms(formula))
    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        if eval(formula, interpretation):
            return True
    return False

def is_contradiction(formula: Operand) -> bool:
    atoms = sorted(extract_atoms(formula))
    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        if eval(formula, interpretation):
            return False
    return True

def to_nnf(formula: Operand) -> Operand:
    if isinstance(formula, (Atom, TrueConst, FalseConst)):
        return formula
    elif isinstance(formula, Not):
        operand = formula.operand
        if isinstance(operand, (Atom, TrueConst, FalseConst)):
            return formula
        elif isinstance(operand, Not):
            return to_nnf(operand.operand)
        elif isinstance(operand, And):
            return Or(to_nnf(Not(operand.left)), to_nnf(Not(operand.right)))
        elif isinstance(operand, Or):
            return And(to_nnf(Not(operand.left)), to_nnf(Not(operand.right)))
        elif isinstance(operand, Implies):
            return And(to_nnf(operand.left), to_nnf(Not(operand.right)))
        elif isinstance(operand, Iff):
            left_part = And(to_nnf(operand.left), to_nnf(Not(operand.right)))
            right_part = And(to_nnf(Not(operand.left)), to_nnf(operand.right))
            return Or(left_part, right_part)
    elif isinstance(formula, And):
        return And(to_nnf(formula.left), to_nnf(formula.right))
    elif isinstance(formula, Or):
        return Or(to_nnf(formula.left), to_nnf(formula.right))
    elif isinstance(formula, Implies):
        return Or(to_nnf(Not(formula.left)), to_nnf(formula.right))
    elif isinstance(formula, Iff):
        left_part = And(to_nnf(formula.left), to_nnf(formula.right))
        right_part = And(to_nnf(Not(formula.left)), to_nnf(Not(formula.right)))
        return Or(left_part, right_part)
    else:
        raise ValueError("Unknown formula type")

def distribute(left: Operand, right: Operand) -> Operand:
    if isinstance(left, And):
        return And(distribute(left.left, right), distribute(left.right, right))
    elif isinstance(right, And):
        return And(distribute(left, right.left), distribute(left, right.right))
    else:
        return Or(left, right)

def to_cnf_direct(formula: Operand) -> Operand:
    if isinstance(formula, And):
        return And(to_cnf_direct(formula.left), to_cnf_direct(formula.right))
    elif isinstance(formula, Or):
        return distribute(to_cnf_direct(formula.left), to_cnf_direct(formula.right))
    else:
        return formula

def make_or(*args: Operand) -> Operand:
    if not args: raise ValueError("Empty Or")
    res = args[0]
    for a in args[1:]:
        res = Or(res, a)
    return res

def make_and(*args: Operand) -> Operand:
    if not args: raise ValueError("Empty And")
    res = args[0]
    for a in args[1:]:
        res = And(res, a)
    return res

def tseitin_recurse(formula: Operand, counter: list) -> tuple:
    if isinstance(formula, (Atom, Not, TrueConst, FalseConst)):
        return formula, []

    counter[0] += 1
    fresh = Atom(f"N{counter[0]}")
    clauses = []

    if isinstance(formula, And):
        l_var, l_cls = tseitin_recurse(formula.left, counter)
        r_var, r_cls = tseitin_recurse(formula.right, counter)
        clauses = l_cls + r_cls
        clauses.append(make_or(Not(fresh), l_var))
        clauses.append(make_or(Not(fresh), r_var))
        clauses.append(make_or(fresh, Not(l_var), Not(r_var)))
        return fresh, clauses
    elif isinstance(formula, Or):
        l_var, l_cls = tseitin_recurse(formula.left, counter)
        r_var, r_cls = tseitin_recurse(formula.right, counter)
        clauses = l_cls + r_cls
        clauses.append(make_or(Not(fresh), l_var, r_var))
        clauses.append(make_or(fresh, Not(l_var)))
        clauses.append(make_or(fresh, Not(r_var)))
        return fresh, clauses
    else:
        raise ValueError("Tseitin expects NNF input")

def to_cnf(formula: Operand, tseitin: bool = False) -> Operand:
    nnf = to_nnf(formula)
    if tseitin:
        counter = [0]
        root, clauses = tseitin_recurse(nnf, counter)
        return make_and(root, *clauses)
    else:
        return to_cnf_direct(nnf)

def equivalent(formula1: Operand, formula2: Operand) -> bool:
    atoms = sorted(extract_atoms(formula1) | extract_atoms(formula2))
    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        if eval(formula1, interpretation) != eval(formula2, interpretation):
            return False
    return True