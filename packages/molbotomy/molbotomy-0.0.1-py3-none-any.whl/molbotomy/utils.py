"""
A collection of utility functions

- canonicalize_smiles: Canonicalize a list of SMILES strings with the RDKit SMILES canonicalization algorithm
- smiles_to_mols: Convert a list of SMILES strings to RDkit molecules (and sanitize them)
- mols_to_smiles: Convert a list of RDkit molecules back into SMILES strings
- mols_to_scaffolds: Convert a list of RDKit molecules objects into scaffolds (bismurcko or bismurcko_generic)
- map_scaffolds: Find which molecules share the same scaffold
- smiles_tokenizer: tokenize a SMILES strings into individual characters

Derek van Tilborg
Eindhoven University of Technology
Jan 2024
"""

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Mol
from rdkit.Chem.Scaffolds.MurckoScaffold import GetScaffoldForMol, MakeScaffoldGeneric
from collections import defaultdict
from typing import Union
import re


def canonicalize_smiles(smiles: Union[str, list[str]]) -> Union[str, list[str]]:
    """ Canonicalize a list of SMILES strings with the RDKit SMILES canonicalization algorithm """
    if type(smiles) is str:
        return Chem.MolToSmiles(Chem.MolFromSmiles(smiles))

    return [Chem.MolToSmiles(Chem.MolFromSmiles(smi)) for smi in smiles]


def smiles_to_mols(smiles: list[str], sanitize: bool = True, partial_charges: bool = False) -> list:
    """ Convert a list of SMILES strings to RDkit molecules (and sanitize them)

    :param smiles: List of SMILES strings
    :param sanitize: toggles sanitization of the molecule. Defaults to True.
    :param partial_charges: toggles the computation of partial charges (default = False)
    :return: List of RDKit mol objects
    """
    mols = []
    for smi in smiles:
        molecule = Chem.MolFromSmiles(smi, sanitize=sanitize)

        # If sanitization is unsuccessful, catch the error, and try again without
        # the sanitization step that caused the error
        if sanitize:
            flag = Chem.SanitizeMol(molecule, catchErrors=True)
            if flag != Chem.SanitizeFlags.SANITIZE_NONE:
                Chem.SanitizeMol(molecule, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL ^ flag)

        Chem.AssignStereochemistry(molecule, cleanIt=True, force=True)

        if partial_charges:
            Chem.rdPartialCharges.ComputeGasteigerCharges(molecule)

        mols.append(molecule)

    return mols


def mols_to_smiles(mols: list[Mol]) -> list[str]:
    """ Convert a list of RDKit molecules objects into a list of SMILES strings"""
    return [Chem.MolToSmiles(m) for m in mols]


def mols_to_scaffolds(mols: list[Mol], scaffold_type: str = 'bismurcko') -> list:
    """ Convert a list of RDKit molecules objects into scaffolds (bismurcko or bismurcko_generic)

    :param mols: list of RDKit mol objects, e.g., as obtained through smiles_to_mols()
    :param scaffold_type: type of scaffold: bismurcko, bismurcko_generic (default = 'bismurcko')
    :return: RDKit mol objects of the scaffolds
    """
    if scaffold_type == 'bismurcko_generic':
        scaffolds = [MakeScaffoldGeneric(m) for m in mols]
    else:
        scaffolds = [GetScaffoldForMol(m) for m in mols]

    return scaffolds


def map_scaffolds(mols: list) -> (list, dict[str, list[int]]):
    """ Find which molecules share the same scaffold

    :param mols: RDKit mol objects, e.g., as obtained through smiles_to_mols()
    :return: scaffolds, dict of unique scaffolds and which molecules (indices) share them -> {'c1ccccc1': [0, 12, 47]}
    """

    scaffolds = mols_to_scaffolds(mols)

    uniques = defaultdict(list)
    for i, s in enumerate(scaffolds):
        uniques[Chem.MolToSmiles(s)].append(i)

    return scaffolds, uniques


def smiles_tokenizer(smiles: str, extra_patterns: list[str] = None) -> list[str]:
    """ Tokenize a SMILES. By default, we use the base SMILES grammar tokens and the reactive nonmetals H, C, N, O, F,
    P, S, Cl, Se, Br, I:

    '(\\[|\\]|Cl|Se|se|Br|H|C|c|N|n|O|o|F|P|p|S|s|I|\\(|\\)|\\.|=|#|-|\\+|\\\\|\\/|:|~|@|\\?|>|\\*|\\$|\\%\\d{2}|\\d)'

    :param smiles: SMILES string
    :param extra_patterns: extra tokens to consider (default = None)
        e.g. metalloids: ['Si', 'As', 'Te', 'te', 'B', 'b']  (in ChEMBL33: B+b=0.23%, Si=0.13%, As=0.01%, Te+te=0.01%).
        Mind you that the order matters. If you place 'C' before 'Cl', all Cl tokens will actually be tokenized as C,
        meaning that subsets should always come after superset strings, aka, place two letter elements first in the list
    :return: list of tokens extracted from the smiles string in their original order
    """
    base_smiles_patterns = "(\[|\]|insert_here|\(|\)|\.|=|#|-|\+|\\\\|\/|:|~|@|\?|>|\*|\$|\%\d{2}|\d)"
    reactive_nonmetals = ['Cl', 'Se', 'se', 'Br', 'H', 'C', 'c', 'N', 'n', 'O', 'o', 'F', 'P', 'p', 'S', 's', 'I']

    # Add all allowed elements to the base SMILES tokens
    extra_patterns = reactive_nonmetals if extra_patterns is None else extra_patterns + reactive_nonmetals
    pattern = base_smiles_patterns.replace('insert_here', "|".join(extra_patterns))

    regex = re.compile(pattern)
    tokens = [token for token in regex.findall(smiles)]

    return tokens
