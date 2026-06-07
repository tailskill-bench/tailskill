#!/bin/bash
set -e
mkdir -p /root/workspace
cat > /root/workspace/solution.py << 'EOF'
#!/usr/bin/env python3
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from collections import Counter, defaultdict
from sympy import Rational

def analyze_wyckoff_position_multiplicities_and_coordinates(filepath: str):
    structure = Structure.from_file(filepath)
    sga = SpacegroupAnalyzer(structure)
    dataset = sga.get_symmetry_dataset()
    if dataset is None:
        return {'wyckoff_multiplicity_dict': {}, 'wyckoff_coordinates_dict': {}}
    wyckoff_letters = dataset.wyckoffs
    wyckoff_multiplicities = Counter(wyckoff_letters)
    multiplicity_dict = dict(sorted(wyckoff_multiplicities.items()))
    wyckoff_sites = defaultdict(list)
    for i, site in enumerate(structure):
        letter = wyckoff_letters[i]
        wyckoff_sites[letter].append(site)
    coordinates_dict = {}
    for letter, sites in sorted(wyckoff_sites.items()):
        site = sites[0]
        coords = site.frac_coords
        exact = []
        for c in coords:
            rat = Rational(c).limit_denominator(12)
            exact.append(str(rat))
        coordinates_dict[letter] = exact
    return {'wyckoff_multiplicity_dict': multiplicity_dict, 'wyckoff_coordinates_dict': coordinates_dict}
EOF
echo "Solution written to /root/workspace/solution.py"
