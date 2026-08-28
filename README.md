# LANDIS-II Coupled India Forest Decision Support & Ecological Intelligence Platform

An academic and research-grade decision-support system coupling the **LANDIS-II Forest Landscape Simulation Framework** with our original **Nonlinear Population Dynamics, Spatial Invasive Spread, and Jacobian Stability Analysis Layer** for Indian forest ecosystems.

---

## 🏛️ System Architecture

```plaintext
                     LANDIS-II v8 ARCHITECTURE
                                CORE
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
     SUCCESSION              DISTURBANCE              OUTPUT
 (Biomass, NECN, PnET)    (Dynamic Fire, BDA)     (Spatial Rasters)
         |                       |                       |
         +-----------------------+-----------------------+
                                 |
                         LANDSCAPE STATE
                                 |
                                 v
                 OUR ORIGINAL SCIENTIFIC ECOLOGY LAYER
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
    Species Dynamics        Invasive Dynamics        Stability
   - Competition (a_ij)   - Spread & Diffusion    - Continuous J_F
   - Establishment (S_i)  - Gaussian Niche S_T    - Discrete J_map
   - Modulated Growth     - Invasive Impact (IIS) - Spectral Radius
         |                       |                       |
         +-----------------------+-----------------------+
                                 |
                                 v
                       INDIA DECISION LAYER
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
    India GIS Maps         10 Management           Scientific
   - 28 States & UTs         Scenarios             Traceability
   - 40+ Tiger Reserves   - Baseline / EDRR      - FSI / BSI / GBIF
   - Real Baselines       - CRD / Restoration    - Audit Logger
         |                       |                       |
         +-----------------------+-----------------------+
                                 |
                                 v
                 PROFESSIONAL SCIENTIFIC WORKSTATION UI
              (10 Distinct Workspaces & 3D WebGL Visualization)
```

---

## 🔬 Mathematical & Ecological Formulation

### 1. Coupled Nonlinear 3-State Population Dynamics
$$\frac{dx}{dt} = r_1 x \left(1 - \frac{x + a_{12} y + a_{13} z}{K_1}\right)$$
$$\frac{dy}{dt} = r_2 y \left(1 - \frac{y + a_{21} x + a_{23} z}{K_2}\right)$$
$$\frac{dz}{dt} = r_3 z \left(1 - \frac{z + a_{31} x + a_{32} y}{K_3}\right)$$

Where:
* $x$: Native climax timber canopy biomass state (Mg/ha)
* $y$: Competing understory / subordinate vegetation state (Mg/ha)
* $z$: Introduced candidate / invasive species biomass state (Mg/ha)
* $r_i$: Modulated intrinsic growth rates $r_i' = r_i \cdot S_i \cdot (1 - D_i)$
* $K_i$: Asymptotic carrying capacities (Mg/ha)
* $a_{ij}$: Interspecific competition coefficients

### 2. Gaussian Abiotic Suitability Engine
$$S_T = \exp\left(-\frac{(T - T_{opt})^2}{2\sigma_T^2}\right), \quad S_E = \exp\left(-\frac{(E - E_{opt})^2}{2\sigma_E^2}\right), \quad S_M = \exp\left(-\frac{(M - M_{opt})^2}{2\sigma_M^2}\right)$$
$$S_{abiotic} = w_T S_T + w_E S_E + w_M S_M + w_S S_S, \quad \sum w_i = 1.0$$

### 3. Continuous & Discrete-Time Jacobian Stability
$$\mathbf{J}_F(x,y,z) = \begin{bmatrix}
r_1 \left(1 - \frac{2x + a_{12}y + a_{13}z}{K_1}\right) & -\frac{r_1 a_{12} x}{K_1} & -\frac{r_1 a_{13} x}{K_1} \\[6pt]
-\frac{r_2 a_{21} y}{K_2} & r_2 \left(1 - \frac{2y + a_{21}x + a_{23}z}{K_2}\right) & -\frac{r_2 a_{23} y}{K_2} \\[6pt]
-\frac{r_3 a_{31} z}{K_3} & -\frac{r_3 a_{32} z}{K_3} & r_3 \left(1 - \frac{2z + a_{31}x + a_{32}y}{K_3}\right)
\end{bmatrix}$$

$$\mathbf{J}_{map} = \mathbf{I} + \Delta t \,\mathbf{J}_F$$
$$\rho(\mathbf{J}_{map}) = \max_{i} |\lambda_i|$$
* $\rho < 1.0$: Locally asymptotically stable
* $\rho > 1.0$: Locally unstable (perturbations amplify)
* $\rho \approx 1.0$: Near critical bifurcation boundary

### 4. Numerical Finite-Difference Cross-Verification
$$\frac{\partial f_i}{\partial x_j} \approx \frac{f_i(\mathbf{x} + h\mathbf{e}_j) - f_i(\mathbf{x} - h\mathbf{e}_j)}{2h}$$
Automatically verified in test suite with maximum error $< 10^{-4}$.

---

## 🗺️ Workspaces Overview

1. **India GIS & Area Selection:** Interactive spatial selector for all Indian States, Protected Areas (Mudumalai, Bandipur, Kanha, Corbett, Gir, Wayanad, etc.), with spatial resolution selection (30m, 100m, 250m).
2. **Forest Baseline & Empirical Inventory:** Real FSI ISFR carbon stocks and observed species occurrences with provenance labels (`OBSERVED`, `EXTERNAL DATA`, `DERIVED`, `CALIBRATED`).
3. **Species Library & Canonical Taxonomy:** 40+ species records with synonym resolver (e.g. *Lantana camara L.* $\to$ *Lantana camara*), shade tolerance, fire tolerance, and allelopathy.
4. **Candidate Species Introduction Assessment:** 12-step evaluation distinguishing Native vs Non-native vs Documented Invasive vs Insufficient Evidence.
5. **Spatial Landscape Simulator & Time Machine:** 2D cellular automata with multi-layer raster visualization, diffusion $D_z \nabla^2 z$, and hover cell inspector.
6. **Jacobian & Stability Analysis:** Analytical continuous Jacobian, numerical finite-difference cross-check, discrete map eigenvalues, and equilibria table.
7. **10 Comparative Management Scenarios:** Evaluated from the identical baseline state over 30 years (Baseline, EDRR, Containment, CRD Rootstock Removal, Active Restoration, Climate Stress, Drought, Wildfire, High Propagule Pressure, Integrated Policy).
8. **3D WebGL Forest Landscape Visualizer:** High-performance instanced Three.js forest terrain, native canopy, invasive hotspots, and disturbance zones.
9. **Sources, Traceability & API Audit Log:** Full provenance chains and live API query logs.
10. **Decision Report Exporter:** Comprehensive generated report exportable as Markdown (.md), JSON, and printable PDF format.

---

## 🚀 Running the Workstation

Double-click **`Launch_Platform.bat`** or run:
```bash
py app.py
```
Open **`http://127.0.0.1:5000/`** in any modern web browser.

### Running Automated Scientific Tests:
```bash
py -m pytest tests/
```
