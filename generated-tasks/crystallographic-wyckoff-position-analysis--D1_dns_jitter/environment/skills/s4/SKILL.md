---
name: s1
description: "Materials science and symbolic math toolkit: pymatgen for crystal structures, phase diagrams, surfaces, and MP API; sympy for calculus, solving, matrices, and physics."
---

# Pymatgen - Python Materials Genomics

## Installation & Setup

```bash
uv pip install pymatgen
uv pip install pymatgen mp-api        # Materials Project API access
uv pip install pymatgen[analysis]     # Extended analysis tools
uv pip install pymatgen[vis]          # Visualization
export MP_API_KEY="your_api_key_here"
```

## Structure Operations & File I/O

```python
from pymatgen.core import Structure, Lattice, Molecule

struct = Structure.from_file("POSCAR")                          # auto format detection
lattice = Lattice.cubic(3.84)
struct = Structure(lattice, ["Si", "Si"], [[0,0,0],[0.25,0.25,0.25]])
struct.to(filename="structure.cif")
print(struct.composition.reduced_formula, struct.get_space_group_info(), f"{struct.density:.2f} g/cm³")
```

```python
struct = Structure.from_file("structure.cif")
mol = Molecule.from_file("molecule.xyz")
lattice = Lattice.from_parameters(a=3.84, b=3.84, c=3.84, alpha=120, beta=90, gamma=60)
struct = Structure(lattice, ["Si","Si"], [[0,0,0],[0.75,0.5,0.75]])
struct = Structure.from_spacegroup("Fm-3m", Lattice.cubic(3.5), ["Si"], [[0,0,0]])
```

```python
struct = Structure.from_file("input_file")
struct.to(filename="output.cif")   # also POSCAR, .xyz, etc.
```

```bash
python scripts/structure_converter.py POSCAR structure.cif
python scripts/structure_converter.py *.cif --output-dir ./poscar_files --format poscar
```

## Transformations

```python
from pymatgen.transformations.standard_transformations import (
    SupercellTransformation, SubstitutionTransformation, PrimitiveCellTransformation)
supercell = SupercellTransformation([[2,0,0],[0,2,0],[0,0,2]]).apply_transformation(struct)
new_struct = SubstitutionTransformation({"Fe":"Mn"}).apply_transformation(struct)
primitive  = PrimitiveCellTransformation().apply_transformation(struct)
```

```python
from pymatgen.transformations.advanced_transformations import MagOrderingTransformation
mag_structs = MagOrderingTransformation({"Fe":5.0}).apply_transformation(struct, return_ranked_list=True)
lowest = mag_structs[0]['structure']
```

## Symmetry & Local Environment

```python
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
sga = SpacegroupAnalyzer(struct)
print(sga.get_space_group_symbol(), sga.get_space_group_number(), sga.get_crystal_system())
conventional = sga.get_conventional_standard_structure()
primitive   = sga.get_primitive_standard_structure()
```

```python
from pymatgen.analysis.local_env import CrystalNN
neighbors = CrystalNN().get_nn_info(struct, n=0)
print(f"Coordination number: {len(neighbors)}")
```

```bash
python scripts/structure_analyzer.py POSCAR --symmetry --neighbors
python scripts/structure_analyzer.py structure.cif --symmetry --export json
```

## Materials Project API

Get API key from https://next-gen.materialsproject.org/

```python
from mp_api.client import MPRester
with MPRester() as mpr:
    struct = mpr.get_structure_by_material_id("mp-149")
    materials = mpr.materials.summary.search(formula="Fe2O3", energy_above_hull=(0, 0.05))
    materials = mpr.materials.summary.search(chemsys="Li-Fe-O", energy_above_hull=(0,0.05), band_gap=(1.0,3.0))
    bs        = mpr.get_bandstructure_by_material_id("mp-149")
    entries   = mpr.get_entries_in_chemsys("Li-Fe-O")
```

## Phase Diagrams & Thermodynamics

```python
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.core import Composition

with MPRester() as mpr:
    entries = mpr.get_entries_in_chemsys("Li-Fe-O")
pd = PhaseDiagram(entries)
for entry in entries:
    if entry.composition.reduced_formula == "LiFeO2":
        e_hull = pd.get_e_above_hull(entry)
        print(f"Energy above hull: {e_hull:.4f} eV/atom")
        if e_hull > 0.001:
            print("Decomposes to:", pd.get_decomposition(Composition("LiFeO2")))
PDPlotter(pd).show()
```

```bash
python scripts/phase_diagram_generator.py Li-Fe-O --output li_fe_o.png
python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2" --show
```

## Electronic Structure

```python
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.plotter import BSPlotter, DosPlotter

vasprun = Vasprun("vasprun.xml")
bs = vasprun.get_band_structure()
gap = bs.get_band_gap()
print(f"Band gap: {gap['energy']:.3f} eV, direct: {gap['direct']}, metal: {bs.is_metal()}")
BSPlotter(bs).save_plot("band_structure.png")

dos = vasprun.complete_dos
plotter = DosPlotter()
plotter.add_dos("Total DOS", dos)
plotter.show()
```

## Surfaces & Interfaces

```python
from pymatgen.core.surface import SlabGenerator
slabs = SlabGenerator(struct, miller_index=(1,1,1), min_slab_size=10.0,
                      min_vacuum_size=10.0, center_slab=True).get_slabs()
for i, slab in enumerate(slabs):
    slab.to(filename=f"slab_{i}.cif")
```

```python
from pymatgen.analysis.wulff import WulffShape
surface_energies = {(1,0,0): 1.0, (1,1,0): 1.1, (1,1,1): 0.9}
wulff = WulffShape(struct.lattice, surface_energies)
print(f"Area: {wulff.surface_area:.2f} Ų, Vol: {wulff.volume:.2f} ų")
```

```python
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core import Molecule
asf = AdsorbateSiteFinder(slab)
sites = asf.find_adsorption_sites()
ads_struct = asf.add_adsorbate(Molecule("O", [[0,0,0]]), sites["ontop"][0])
```

## Computational Workflow Setup

```python
from pymatgen.io.vasp.sets import MPRelaxSet, MPStaticSet, MPNonSCFSet
MPRelaxSet(struct).write_input("./relax_calc")
MPStaticSet(struct).write_input("./static_calc")
MPNonSCFSet(struct, mode="line").write_input("./bandstructure_calc")
MPRelaxSet(struct, user_incar_settings={"ENCUT": 600}).write_input("./custom_calc")
```

```python
from pymatgen.io.gaussian import GaussianInput
GaussianInput(mol, functional="B3LYP", basis_set="6-31G(d)", route_parameters={"Opt":None}).write_file("input.gjf")
from pymatgen.io.pwscf import PWInput
PWInput(struct, control={"calculation":"scf"}).write_file("pw.in")
```

## Advanced Analysis

```python
from pymatgen.analysis.diffraction.xrd import XRDCalculator
pattern = XRDCalculator().get_pattern(struct)
for peak in pattern.hkls:
    print(f"2θ = {peak['2theta']:.2f}°, hkl = {peak['hkl']}")
```

```python
from pymatgen.analysis.elasticity import ElasticTensor
et = ElasticTensor.from_voigt(matrix)
print(f"B={et.k_voigt:.1f} GPa, G={et.g_voigt:.1f} GPa, Y={et.y_mod:.1f} GPa")
```

## Common Pymatgen Workflows

### High-Throughput Structure Generation

```python
from pymatgen.transformations.standard_transformations import SubstitutionTransformation
from pymatgen.io.vasp.sets import MPRelaxSet
base = Structure.from_file("POSCAR")
for d in ["Mn","Co","Ni","Cu"]:
    s = SubstitutionTransformation({"Fe":d}).apply_transformation(base)
    MPRelaxSet(s).write_input(f"./calcs/Fe_{d}")
```

### Band Structure Workflow

```python
from pymatgen.io.vasp.sets import MPRelaxSet, MPStaticSet, MPNonSCFSet
from pymatgen.io.vasp import Vasprun
MPRelaxSet(struct).write_input("./1_relax")
relaxed = Structure.from_file("1_relax/CONTCAR")
MPStaticSet(relaxed).write_input("./2_static")
MPNonSCFSet(relaxed, mode="line").write_input("./3_bandstructure")
bs = Vasprun("3_bandstructure/vasprun.xml").get_band_structure()
bs.get_band_gap()
```

### Surface Energy Calculation

```python
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.vasp import Vasprun
bulk_E = Vasprun("bulk/vasprun.xml").final_energy / len(bulk)
slab = SlabGenerator(bulk, (1,1,1), 10, 15).get_slabs()[0]
MPRelaxSet(slab).write_input("./slab_calc")
slab_E = Vasprun("slab_calc/vasprun.xml").final_energy
E_surf = (slab_E - len(slab)*bulk_E) / (2*slab.surface_area) * 16.021766  # eV/Ų → J/m²
```

## Bundled Scripts (`scripts/`)

- **`structure_converter.py`** — `python scripts/structure_converter.py POSCAR structure.cif`
- **`structure_analyzer.py`** — `python scripts/structure_analyzer.py structure.cif --symmetry --neighbors`
- **`phase_diagram_generator.py`** — `python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2"`

All scripts: `python scripts/<name>.py --help`

## References (`references/`)

- **`core_classes.md`** — Element, Structure, Lattice, Molecule, Composition
- **`io_formats.md`** — File formats, VASP/Gaussian/QE integration
- **`analysis_modules.md`** — Phase diagrams, surfaces, electronic structure, symmetry
- **`materials_project_api.md`** — Full MP API guide
- **`transformations_workflows.md`** — Transformations framework & workflows

## Critical Constraints

- Use `with MPRester() as mpr:` context manager always.
- Prefer `MPRelaxSet`/`MPStaticSet` over manual INCAR.
- Check convergence after every calculation.
- Fix permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/workspace`

## Units & Version

Lengths: Å · Energies: eV · Angles: ° · Magnetic moments: μB · Time: fs. Convert via `pymatgen.core.units`.
pymatgen ≥ 2023.x, Python ≥ 3.10, `mp-api` for MP access (not legacy `pymatgen.ext.matproj`).

# SymPy - Symbolic Mathematics

## Basics & Calculus

```python
from sympy import symbols, simplify, expand, factor
x, y, z = symbols('x y z')
x = symbols('x', real=True, positive=True)       # with assumptions
n = symbols('n', integer=True)
simplify(sin(x)**2 + cos(x)**2)   # 1
expand((x + 1)**3)                # x**3 + 3*x**2 + 3*x + 1
factor(x**2 - 1)                  # (x - 1)*(x + 1)
```

```python
from sympy import diff, integrate, limit, series, oo
diff(x**2, x)                     # 2*x
diff(x**4, x, 3)                  # 24*x
diff(x**2*y**3, x, y)            # 6*x*y**2
integrate(x**2, x)                # x**3/3
integrate(x**2, (x, 0, 1))       # 1/3
integrate(exp(-x), (x, 0, oo))   # 1
limit(sin(x)/x, x, 0)            # 1
series(exp(x), x, 0, 6)          # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

## Equation Solving

```python
from sympy import solveset, solve, Eq, linsolve, nonlinsolve, Function, dsolve, Derivative
solveset(x**2 - 4, x)            # {-2, 2}
solve(Eq(x**2, 4), x)            # [-2, 2]
linsolve([x+y-2, x-y], x, y)    # {(1, 1)}
f = symbols('f', cls=Function)
dsolve(Derivative(f(x), x) - f(x), f(x))   # Eq(f(x), C1*exp(x))
```

## Matrices & Linear Algebra

```python
from sympy import Matrix, eye, zeros
M = Matrix([[1,2],[3,4]])
M_inv = M**-1;  M.det();  M.T
eigenvals  = M.eigenvals()          # {val: mult}
eigenvects = M.eigenvects()         # [(val, mult, [vecs])]
P, D = M.diagonalize()              # M = P*D*P^-1
x = Matrix([[1,2],[3,4]]).solve(Matrix([5,6]))   # Ax = b
```

## Physics & Mechanics

```python
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod
q = dynamicsymbols('q');  m, g, l = symbols('m g l')
L = m*(l*q.diff())**2/2 - m*g*l*(1 - cos(q))
LM = LagrangesMethod(L, [q])
```

```python
from sympy.physics.vector import ReferenceFrame, dot, cross
N = ReferenceFrame('N')
v1 = 3*N.x + 4*N.y;  v2 = 1*N.x + 2*N.z
dot(v1, v2);  cross(v1, v2)
```

```python
from sympy.physics.quantum import Ket, Bra, Commutator, Operator
psi = Ket('psi');  A = Operator('A');  B = Operator('B')
comm = Commutator(A, B).doit()
```

## Code Generation & Output

```python
from sympy import lambdify, latex
from sympy.utilities.codegen import codegen
import numpy as np

f = lambdify(x, x**2 + 2*x + 1, 'numpy')
y = f(np.linspace(0, 10, 100))

[(c_name, c_code), (h_name, c_header)] = codegen(('my_func', expr), 'C')
latex_str = latex(expr)
```

## SymPy Best Practices

- Define symbols with `symbols()` before use; add assumptions (`positive=True`, `real=True`) for better simplification.
- Use exact arithmetic: `Rational(1,2)` or `S(1)/2`, not `0.5`.
- Numerical evaluation: `result.evalf()` or `result.evalf(50)`.
- For loops, convert to NumPy via `lambdify()` instead of `subs()`/`evalf()`.
- Choose the right solver: `solveset` (algebraic), `linsolve` (linear), `nonlinsolve` (nonlinear), `dsolve` (ODE), `solve` (legacy general).

## SymPy Common Patterns

### Solve and Verify

```python
from sympy import symbols, solve, simplify
x = symbols('x')
solutions = solve(x**2 - 5*x + 6, x)   # [2, 3]
for sol in solutions:
    assert simplify((x**2 - 5*x + 6).subs(x, sol)) == 0
```

### Symbolic → Numeric Pipeline

```python
x, y = symbols('x y')
derivative = diff(simplify(sin(x) + cos(y)), x)
f = lambdify((x, y), derivative, 'numpy')
results = f(x_data, y_data)
```

### Document Results

```python
from sympy import Integral, latex, pretty
integral_expr = Integral(x**2, (x, 0, 1))
result = integral_expr.doit()
print(f"LaTeX: {latex(integral_expr)} = {latex(result)}")
print(f"Numerical: {result.evalf()}")
```

## SymPy Quick Reference

```python
from sympy import symbols, simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo
from sympy import diff, integrate, limit, series, Derivative, Integral
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve
from sympy import Matrix, eye, zeros, ones, diag
from sympy import And, Or, Not, Implies, FiniteSet, Interval, Union
from sympy import latex, pprint, lambdify, init_printing, evalf, N, nsimplify
```

## SymPy Reference Files

1. **`core-capabilities.md`** — Symbols, algebra, calculus, simplification, solving
2. **`matrices-linear-algebra.md`** — Matrix ops, eigenvalues, linear systems
3. **`physics-mechanics.md`** — Classical/quantum mechanics, vectors, units
4. **`advanced-topics.md`** — Geometry, number theory, combinatorics, logic, stats
5. **`code-generation-printing.md`** — Lambdify, codegen, LaTeX, printing