---
name: s1
description: "Materials science toolkit with pymatgen and sympy for crystal structure analysis, Wyckoff positions, and symbolic mathematics."
---

# Pymatgen - Python Materials Genomics

## Installation & Setup

```bash
uv pip install pymatgen mp-api
uv pip install pymatgen[analysis]
export MP_API_KEY="your_api_key_here"
```

## Structure Operations

```python
from pymatgen.core import Structure, Lattice

struct = Structure.from_file("POSCAR")
lattice = Lattice.cubic(3.84)
struct = Structure(lattice, ["Si", "Si"], [[0,0,0], [0.25,0.25,0.25]])
struct.to(filename="structure.cif")
print(f"Formula: {struct.composition.reduced_formula}")
print(f"Space group: {struct.get_space_group_info()}")
print(f"Density: {struct.density:.2f} g/cm³")
```

**From scratch:**
```python
from pymatgen.core import Structure, Lattice

lattice = Lattice.from_parameters(a=3.84, b=3.84, c=3.84,
                                  alpha=120, beta=90, gamma=60)
struct = Structure(lattice, ["Si", "Si"], [[0, 0, 0], [0.75, 0.5, 0.75]])
struct = Structure.from_spacegroup("Fm-3m", Lattice.cubic(3.5), ["Si"], [[0, 0, 0]])
```

**Transformations:**
```python
from pymatgen.transformations.standard_transformations import (
    SupercellTransformation, SubstitutionTransformation, PrimitiveCellTransformation
)

supercell = SupercellTransformation([[2,0,0],[0,2,0],[0,0,2]]).apply_transformation(struct)
new_struct = SubstitutionTransformation({"Fe": "Mn"}).apply_transformation(struct)
primitive = PrimitiveCellTransformation().apply_transformation(struct)
```

## File Format Conversion

```python
struct = Structure.from_file("input_file")
struct.to(filename="output.cif")
struct.to(filename="POSCAR")
```

```bash
python scripts/structure_converter.py POSCAR structure.cif
python scripts/structure_converter.py *.cif --output-dir ./poscar_files --format poscar
```

## Symmetry & Analysis

```python
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

sga = SpacegroupAnalyzer(struct)
print(f"Space group: {sga.get_space_group_symbol()}")
print(f"Number: {sga.get_space_group_number()}")
print(f"Crystal system: {sga.get_crystal_system()}")
conventional = sga.get_conventional_standard_structure()
primitive = sga.get_primitive_standard_structure()
```

**Coordination environment:**
```python
from pymatgen.analysis.local_env import CrystalNN

cnn = CrystalNN()
neighbors = cnn.get_nn_info(struct, n=0)
print(f"Coordination number: {len(neighbors)}")
```

```bash
python scripts/structure_analyzer.py POSCAR --symmetry --neighbors
```

## Phase Diagrams & Thermodynamics

```python
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.core import Composition

with MPRester() as mpr:
    entries = mpr.get_entries_in_chemsys("Li-Fe-O")

pd = PhaseDiagram(entries)
comp = Composition("LiFeO2")

for entry in entries:
    if entry.composition.reduced_formula == comp.reduced_formula:
        e_above_hull = pd.get_e_above_hull(entry)
        print(f"Energy above hull: {e_above_hull:.4f} eV/atom")
        if e_above_hull > 0.001:
            print("Decomposes to:", pd.get_decomposition(comp))

PDPlotter(pd).show()
```

```bash
python scripts/phase_diagram_generator.py Li-Fe-O --output li_fe_o.png
python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2" --show
```

## Electronic Structure

**Band structure:**
```python
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.plotter import BSPlotter

bs = Vasprun("vasprun.xml").get_band_structure()
band_gap = bs.get_band_gap()
print(f"Band gap: {band_gap['energy']:.3f} eV, Direct: {band_gap['direct']}, Is metal: {bs.is_metal()}")
BSPlotter(bs).save_plot("band_structure.png")
```

**Density of states:**
```python
from pymatgen.electronic_structure.plotter import DosPlotter

dos = Vasprun("vasprun.xml").complete_dos
plotter = DosPlotter()
plotter.add_dos("Total DOS", dos)
plotter.show()
```

## Surface & Interface Analysis

**Slab generation:**
```python
from pymatgen.core.surface import SlabGenerator

slabgen = SlabGenerator(struct, miller_index=(1, 1, 1), min_slab_size=10.0, min_vacuum_size=10.0, center_slab=True)
for i, slab in enumerate(slabgen.get_slabs()):
    slab.to(filename=f"slab_{i}.cif")
```

**Wulff shape:**
```python
from pymatgen.analysis.wulff import WulffShape

surface_energies = {(1, 0, 0): 1.0, (1, 1, 0): 1.1, (1, 1, 1): 0.9}
wulff = WulffShape(struct.lattice, surface_energies)
print(f"Surface area: {wulff.surface_area:.2f} Ų, Volume: {wulff.volume:.2f} ų")
```

**Adsorption sites:**
```python
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core import Molecule

asf = AdsorbateSiteFinder(slab)
ads_sites = asf.find_adsorption_sites()
ads_struct = asf.add_adsorbate(Molecule("O", [[0, 0, 0]]), ads_sites["ontop"][0])
```

## Materials Project Database

Get API key from https://next-gen.materialsproject.org/, set `MP_API_KEY`.

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    materials = mpr.materials.summary.search(chemsys="Li-Fe-O", energy_above_hull=(0, 0.05), band_gap=(1.0, 3.0))
    struct = mpr.get_structure_by_material_id("mp-149")
    bs = mpr.get_bandstructure_by_material_id("mp-149")
    entries = mpr.get_entries_in_chemsys("Li-Fe-O")
```

## Computational Workflow Setup

**VASP input generation:**
```python
from pymatgen.io.vasp.sets import MPRelaxSet, MPStaticSet, MPNonSCFSet

MPRelaxSet(struct).write_input("./relax_calc")
MPStaticSet(struct).write_input("./static_calc")
MPNonSCFSet(struct, mode="line").write_input("./bandstructure_calc")
MPRelaxSet(struct, user_incar_settings={"ENCUT": 600}).write_input("./custom_calc")
```

**Other codes:**
```python
from pymatgen.io.gaussian import GaussianInput
GaussianInput(mol, functional="B3LYP", basis_set="6-31G(d)", route_parameters={"Opt": None}).write_file("input.gjf")

from pymatgen.io.pwscf import PWInput
PWInput(struct, control={"calculation": "scf"}).write_file("pw.in")
```

## Advanced Analysis

**Diffraction patterns:**
```python
from pymatgen.analysis.diffraction.xrd import XRDCalculator

pattern = XRDCalculator().get_pattern(struct)
for peak in pattern.hkls:
    print(f"2θ = {peak['2theta']:.2f}°, hkl = {peak['hkl']}")
```

**Elastic properties:**
```python
from pymatgen.analysis.elasticity import ElasticTensor

et = ElasticTensor.from_voigt(matrix)
print(f"Bulk: {et.k_voigt:.1f} GPa, Shear: {et.g_voigt:.1f} GPa, Young's: {et.y_mod:.1f} GPa")
```

**Magnetic ordering:**
```python
from pymatgen.transformations.advanced_transformations import MagOrderingTransformation

mag_structs = MagOrderingTransformation({"Fe": 5.0}).apply_transformation(struct, return_ranked_list=True)
lowest_energy_struct = mag_structs[0]['structure']
```

## Common Workflows

### High-Throughput Structure Generation

```python
from pymatgen.transformations.standard_transformations import SubstitutionTransformation
from pymatgen.io.vasp.sets import MPRelaxSet

base_struct = Structure.from_file("POSCAR")
for dopant in ["Mn", "Co", "Ni", "Cu"]:
    doped = SubstitutionTransformation({"Fe": dopant}).apply_transformation(base_struct)
    MPRelaxSet(doped).write_input(f"./calcs/Fe_{dopant}")
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
from pymatgen.io.vasp import Vasprun, MPRelaxSet

bulk_vasprun = Vasprun("bulk/vasprun.xml")
bulk_E_per_atom = bulk_vasprun.final_energy / len(bulk)
slab = SlabGenerator(bulk, (1,1,1), 10, 15).get_slabs()[0]
MPRelaxSet(slab).write_input("./slab_calc")

slab_vasprun = Vasprun("slab_calc/vasprun.xml")
E_surf = (slab_vasprun.final_energy - len(slab) * bulk_E_per_atom) / (2 * slab.surface_area)
E_surf *= 16.021766  # eV/Ų to J/m²
```

## Key Practices & Reference

- Use `Structure.from_file()` for automatic format detection; `IStructure` for immutable
- Use `SpacegroupAnalyzer` to reduce to primitive cell
- Always use `with MPRester() as mpr:`
- Prefer `MPRelaxSet`, `MPStaticSet` over manual INCAR
- Verify calculations converged; use `TransformedStructure` for provenance
- Fix permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/workspace`

**Units**: Lengths: Å | Energies: eV | Angles: ° | Magnetic moments: μB
**Version**: Python ≥ 3.10, pymatgen ≥ 2023.x, mp-api for MP access.

**Scripts** (`scripts/`): `structure_converter.py`, `structure_analyzer.py`, `phase_diagram_generator.py` — use `--help`
**References** (`references/`): `core_classes.md`, `io_formats.md`, `analysis_modules.md`, `materials_project_api.md`, `transformations_workflows.md`

---

# SymPy - Symbolic Mathematics

## Symbolic Computation Basics

```python
from sympy import symbols, simplify, expand, factor

x, y, z = symbols('x y z')
x = symbols('x', real=True, positive=True)
n = symbols('n', integer=True)

simplify(sin(x)**2 + cos(x)**2)  # 1
expand((x + 1)**3)                # x**3 + 3*x**2 + 3*x + 1
factor(x**2 - 1)                  # (x - 1)*(x + 1)
```

## Calculus

```python
from sympy import diff, integrate, limit, series, oo

diff(x**2, x)                    # 2*x
diff(x**4, x, 3)                 # 24*x
diff(x**2*y**3, x, y)            # 6*x*y**2

integrate(x**2, x)               # x**3/3
integrate(x**2, (x, 0, 1))       # 1/3
integrate(exp(-x), (x, 0, oo))   # 1

limit(sin(x)/x, x, 0)            # 1
series(exp(x), x, 0, 6)          # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

## Equation Solving

```python
from sympy import solveset, solve, Eq, linsolve, nonlinsolve
from sympy import Function, dsolve, Derivative

solveset(x**2 - 4, x)            # {-2, 2}
solve(Eq(x**2, 4), x)            # [-2, 2]
linsolve([x + y - 2, x - y], x, y)  # {(1, 1)}
nonlinsolve([x**2 + y - 2, x + y**2 - 3], x, y)

f = symbols('f', cls=Function)
dsolve(Derivative(f(x), x) - f(x), f(x))  # Eq(f(x), C1*exp(x))
```

## Matrices and Linear Algebra

```python
from sympy import Matrix, eye, zeros

M = Matrix([[1, 2], [3, 4]])
M_inv = M**-1
M.det()
M.T

M.eigenvals()       # {eigenvalue: multiplicity}
M.eigenvects()      # [(eigenval, mult, [eigenvectors])]
P, D = M.diagonalize()  # M = P*D*P^-1

A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
x = A.solve(b)      # Solve Ax = b
```

## Physics and Mechanics

```python
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod
from sympy.physics.vector import ReferenceFrame, dot, cross
from sympy.physics.quantum import Ket, Bra, Commutator

q = dynamicsymbols('q')
m, g, l = symbols('m g l')
L = m*(l*q.diff())**2/2 - m*g*l*(1 - cos(q))
LM = LagrangesMethod(L, [q])

N = ReferenceFrame('N')
v1 = 3*N.x + 4*N.y
v2 = 1*N.x + 2*N.z
dot(v1, v2)
cross(v1, v2)
```

## Code Generation and Output

```python
from sympy import lambdify, latex
from sympy.utilities.codegen import codegen
import numpy as np

expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')
y_vals = f(np.linspace(0, 10, 100))

[(c_name, c_code), (h_name, c_header)] = codegen(('my_func', expr), 'C')
latex_str = latex(expr)
```

## SymPy Best Practices

- Define symbols first with `symbols()` before use
- Use assumptions: `x = symbols('x', positive=True, real=True)` ensures `sqrt(x**2)` → `x`
- Use exact arithmetic: `Rational(1, 2)` or `S(1)/2` instead of `0.5`
- Numerical evaluation: `result.evalf()` or `result.evalf(50)` for 50 digits
- Use `lambdify()` instead of `subs()`/`evalf()` in loops
- Solvers: `solveset` (algebraic), `linsolve` (linear), `nonlinsolve` (nonlinear), `dsolve` (differential)

## Common SymPy Patterns

### Solve and Verify

```python
from sympy import symbols, solve, simplify

x = symbols('x')
solutions = solve(x**2 - 5*x + 6, x)  # [2, 3]
for sol in solutions:
    assert simplify((x**2 - 5*x + 6).subs(x, sol)) == 0
```

### Symbolic to Numeric Pipeline

```python
from sympy import symbols, sin, diff, simplify, lambdify

x, y = symbols('x y')
derivative = diff(simplify(sin(x) + cos(y)), x)
f = lambdify((x, y), derivative, 'numpy')
results = f(x_data, y_data)
```

### Document Mathematical Results

```python
from sympy import symbols, Integral, latex, pretty

x = symbols('x')
integral_expr = Integral(x**2, (x, 0, 1))
result = integral_expr.doit()
print(f"LaTeX: {latex(integral_expr)} = {latex(result)}")
print(f"Numerical: {result.evalf()}")
```

## Quick Reference: Common Functions

```python
from sympy import symbols, simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo
from sympy import diff, integrate, limit, series, Derivative, Integral
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve
from sympy import Matrix, eye, zeros, ones, diag
from sympy import And, Or, Not, Implies, FiniteSet, Interval, Union
from sympy import latex, pprint, lambdify, init_printing
from sympy import evalf, N, nsimplify
```

**SymPy References** (`references/`): `core-capabilities.md`, `matrices-linear-algebra.md`, `physics-mechanics.md`, `advanced-topics.md`, `code-generation-printing.md`