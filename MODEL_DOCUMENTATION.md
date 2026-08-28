# SCIENTIFIC MATHEMATICAL MODEL DOCUMENTATION (MODEL_DOCUMENTATION.md)

## 1. Governing Nonlinear Population Kinetics

The reduced-order mathematical ecology layer models continuous interaction between three forest biomass strata:

$$\frac{dx}{dt} = r_1 x \left(1 - \frac{x + a_{12} y + a_{13} z}{K_1}\right)$$

$$\frac{dy}{dt} = r_2 y \left(1 - \frac{y + a_{21} x + a_{23} z}{K_2}\right)$$

$$\frac{dz}{dt} = r_3 z \left(1 - \frac{z + a_{31} x + a_{32} y}{K_3}\right)$$

Where:
- x: Native climax timber canopy biomass (Mg/ha)
- y: Native understory / shrub biomass (Mg/ha)
- z: Candidate / invasive alien plant biomass (Mg/ha)
- r_i: Modulated intrinsic growth rates: r_i' = r_i * S_i * (1 - 0.5 D_i)
- K_i: Asymptotic carrying capacities (Mg/ha)
- a_ij: Interspecific competition coefficients

---

## 2. Analytical Continuous Jacobian Matrix J_F

The 3x3 Continuous Jacobian matrix is computed explicitly by partial differentiation:

$$\mathbf{J}_F(x,y,z) = \begin{bmatrix}
r_1 \left(1 - \frac{2x + a_{12}y + a_{13}z}{K_1}\right) & -\frac{r_1 a_{12} x}{K_1} & -\frac{r_1 a_{13} x}{K_1} \\[6pt]
-\frac{r_2 a_{21} y}{K_2} & r_2 \left(1 - \frac{2y + a_{21}x + a_{23}z}{K_2}\right) & -\frac{r_2 a_{23} y}{K_2} \\[6pt]
-\frac{r_3 a_{31} z}{K_3} & -\frac{r_3 a_{32} z}{K_3} & r_3 \left(1 - \frac{2z + a_{31}x + a_{32}y}{K_3}\right)
\end{bmatrix}$$

---

## 3. Discrete-Time Map & Spectral Radius

For a discrete integration time step dt = 0.1 yr:

$$\mathbf{J}_{map} = \mathbf{I} + \Delta t \,\mathbf{J}_F$$

$$\rho(\mathbf{J}_{map}) = \max_{i \in \{1,2,3\}} |\lambda_i(\mathbf{J}_{map})|$$

**Theorem (Local Discrete Stability):**
- rho(J_map) < 1.0: The discrete linearized map is **locally asymptotically stable**.
- rho(J_map) > 1.0: The discrete linearized map is **locally unstable** (perturbations amplify).
- rho(J_map) ≈ 1.0: System is near a critical bifurcation threshold.

---

## 4. Central Finite-Difference Cross-Verification

The analytical Jacobian is automatically validated at every state point using central finite differences:

$$\left(\mathbf{J}_{num}\right)_{i,j} = \frac{f_i(\mathbf{x} + h\mathbf{e}_j) - f_i(\mathbf{x} - h\mathbf{e}_j)}{2h}, \quad h = 10^{-6}$$

$$\text{Verification Criterion: } \max_{i,j} |\mathbf{J}_{F}(i,j) - \mathbf{J}_{num}(i,j)| < 10^{-4}$$
