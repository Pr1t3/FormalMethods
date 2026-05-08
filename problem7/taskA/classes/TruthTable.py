class TruthTable:
    formula: str
    atoms: list[str]
    table: list[tuple[dict[str, bool], bool]]

    def __init__(self, atoms, table, formula):
        object.__setattr__(self, 'atoms', atoms)
        object.__setattr__(self, 'table', table)
        object.__setattr__(self, 'formula', formula)

    def __str__(self):
        header = ' | '.join(self.atoms) + ' | ' + self.formula
        empty_line = '-|-'.join('-' * len(atom) for atom in self.atoms) + '-|-' + '-' * len(self.formula)
        lines = [header, empty_line]
        for interpretation, result in self.table:
            line = ' | '.join(str(int(interpretation[atom])) for atom in self.atoms)
            line += ' | ' + ' ' * (len(self.formula) // 2) + str(int(result))
            lines.append(line)
        return '\n'.join(lines)