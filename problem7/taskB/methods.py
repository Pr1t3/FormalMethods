from classes.FitchProof import *
from taskA.classes.FormulaAST import And, Or, Implies, Not, FalseConst

def check_proof(proof: Proof) -> tuple[bool, list]:
    steps = proof.steps
    if not steps:
        return (False, ["Proof is empty."])

    if steps[0].line != 1 or steps[0].level < 0:
        return (False, ["First step must be line 1 with non-negative level."])
    for i, step in enumerate(steps):
        if step.line != i + 1 or step.level < 0:
            return (False, [f"Line numbering or level invalid at line {step.line}."])
        if i > 0 and step.level > steps[i - 1].level + 1:
            return (False, [f"Level jump too large at line {step.line}."])

    def get_step(line: int, current_line: int) -> Step | None:
        if line < 1 or line >= current_line:
            return None
        return steps[line - 1]

    def is_accessible(cited_line: int, current_idx: int) -> bool:
        cited_idx = cited_line - 1
        cited = steps[cited_idx]
        current = steps[current_idx]

        if cited.level > current.level:
            return False

        for k in range(cited_idx + 1, current_idx):
            if steps[k].level < cited.level:
                return False
        return True

    def is_false(formula: Operand) -> bool:
        return isinstance(formula, FalseConst)

    def contradiction(a: Operand, b: Operand) -> bool:
        return (isinstance(a, Not) and a.operand == b) or (isinstance(b, Not) and b.operand == a)

    SUBPROOF_RULES = {Rule.IMPLIES_INTRO, Rule.NOT_INTRO, Rule.OR_ELIM}

    for i, step in enumerate(steps):
        need_refs = step.rule.num_refs
        if len(step.references) != need_refs:
            return (False, [f"Wrong number of references for rule {step.rule.display_name} on line {step.line}. Expected {need_refs}, got {len(step.references)}."])

        for ref in step.references:
            cited = get_step(ref, step.line)
            if cited is None:
                return (False, [f"Cites nonexistent or future line {ref} on line {step.line}."])
            if step.rule not in SUBPROOF_RULES:
                if not is_accessible(ref, i):
                    return (False, [f"Cites unavailable line {ref} on line {step.line}."])

        if step.rule == Rule.PREMISE:
            if step.references or step.level != 0:
                return (False, [f"Premise at line {step.line} should have no references and level 0."])

        elif step.rule == Rule.ASSUMPTION:
            if step.references:
                return (False, [f"Assumption at line {step.line} should have no references."])

        elif step.rule == Rule.AND_INTRO:
            a = steps[step.references[0] - 1].formula
            b = steps[step.references[1] - 1].formula
            if not isinstance(step.formula, And):
                return (False, [f"Line {step.line}: ∧I must produce a conjunction."])
            ok = (step.formula.left == a and step.formula.right == b) or (step.formula.left == b and step.formula.right == a)
            if not ok:
                return (False, [f"Line {step.line}: ∧I cites lines that do not form the conjuncts."])

        elif step.rule == Rule.AND_ELIM:
            src = steps[step.references[0] - 1].formula
            if not isinstance(src, And):
                return (False, [f"Line {step.line}: ∧E must cite a conjunction."])
            if step.formula != src.left and step.formula != src.right:
                return (False, [f"Line {step.line}: ∧E cited the wrong conjunct."])

        elif step.rule == Rule.OR_INTRO:
            src = steps[step.references[0] - 1].formula
            if not isinstance(step.formula, Or):
                return (False, [f"Line {step.line}: ∨I must produce a disjunction."])
            if step.formula.left != src and step.formula.right != src:
                return (False, [f"Line {step.line}: ∨I does not contain the cited disjunct."])

        elif step.rule == Rule.IMPLIES_ELIM:
            f1 = steps[step.references[0] - 1].formula
            f2 = steps[step.references[1] - 1].formula
            worked = (
                isinstance(f1, Implies) and f1.left == f2 and f1.right == step.formula
            ) or (
                isinstance(f2, Implies) and f2.left == f1 and f2.right == step.formula
            )
            if not worked:
                return (False, [f"Line {step.line}: →E not correctly applied with cited lines."])

        elif step.rule == Rule.IMPLIES_INTRO:
            s_line, e_line = step.references
            s = steps[s_line - 1]
            e = steps[e_line - 1]
            if not isinstance(step.formula, Implies):
                return (False, [f"Line {step.line}: →I must produce an implication."])
            if s.rule != Rule.ASSUMPTION:
                return (False, [f"Line {step.line}: →I must cite an assumption start line."])
            if not (s_line < e_line < step.line):
                return (False, [f"Line {step.line}: →I cites invalid subproof range."])
            if step.formula.left != s.formula or step.formula.right != e.formula:
                return (False, [f"Line {step.line}: →I conclusion does not match subproof."])

        elif step.rule == Rule.NOT_INTRO:
            s_line, e_line = step.references
            s = steps[s_line - 1]
            e = steps[e_line - 1]
            if not isinstance(step.formula, Not):
                return (False, [f"Line {step.line}: ¬I must produce a negation."])
            if s.rule != Rule.ASSUMPTION:
                return (False, [f"Line {step.line}: ¬I must cite an assumption start line."])
            if not (s_line < e_line < step.line):
                return (False, [f"Line {step.line}: ¬I cites invalid subproof range."])
            if step.formula.operand != s.formula:
                return (False, [f"Line {step.line}: ¬I's negated formula does not match the subproof assumption."])
            if not is_false(e.formula):
                return (False, [f"Line {step.line}: ¬I requires a contradiction at the end of the subproof."])

        elif step.rule == Rule.NOT_ELIM:
            a = steps[step.references[0] - 1].formula
            b = steps[step.references[1] - 1].formula
            if not is_false(step.formula):
                return (False, [f"Line {step.line}: ¬E must derive contradiction (⊥)."])
            if not contradiction(a, b):
                return (False, [f"Line {step.line}: ¬E's cited lines are not contradictory."])

        elif step.rule == Rule.BOTTOM_ELIM:
            src = steps[step.references[0] - 1].formula
            if not is_false(src):
                return (False, [f"Line {step.line}: ⊥E must cite a contradiction (⊥)."])

        elif step.rule == Rule.OR_ELIM:
            disj_line, a_start, a_end, b_start, b_end = step.references
            disj = steps[disj_line - 1].formula
            sa = steps[a_start - 1]
            ea = steps[a_end - 1]
            sb = steps[b_start - 1]
            eb = steps[b_end - 1]

            if not isinstance(disj, Or):
                return (False, [f"Line {step.line}: ∨E must cite a disjunction."])
            if sa.rule != Rule.ASSUMPTION or sb.rule != Rule.ASSUMPTION:
                return (False, [f"Line {step.line}: ∨E's subproofs must start with assumptions."])
            if not (a_start < a_end < step.line and b_start < b_end < step.line):
                return (False, [f"Line {step.line}: ∨E cites invalid subproof ranges."])
            if ea.formula != step.formula or eb.formula != step.formula:
                return (False, [f"Line {step.line}: ∨E's subproofs must end with the same conclusion as this line."])

            worked = (
                sa.formula == disj.left and sb.formula == disj.right
            ) or (
                sa.formula == disj.right and sb.formula == disj.left
            )
            if not worked:
                return (False, [f"Line {step.line}: ∨E subproof assumptions do not match disjuncts."])

    return (True, [])
