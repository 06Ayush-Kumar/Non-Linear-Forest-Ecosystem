# SCIENTIFIC PARAMETER PROVENANCE & CALIBRATION AUDIT (PARAMETER_PROVENANCE.md)

**Platform:** Real India Forest Ecosystem Decision-Support System  
**Audit Standard:** Comprehensive, evidence-based verification of every model parameter, interaction coefficient, spatial rate, numerical discretization constant, and decision-support weighting.

---

## 1. Complete Parameter Derivation & Provenance Table

| Parameter | Symbol | Default Value | Value Range $[\\theta_{min}, \\theta_{max}]$ | Authorized Classification | Cited Source | Exact Evidence in Source | Derivation / Calibration Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Native Tree Intrinsic Growth Rate** | $r_1$ | $0.45\text{ yr}^{-1}$ | $[0.20, 0.75]$ | **REQUIRES CALIBRATION** | Troup (1921); Champion & Seth (1968); FSI (2021) | Mean Annual Increment ($\text{MAI} \approx 2.5 - 6.0\text{ m}^3/\text{ha/yr}$) for mature timber. | Literature-informed estimate of early regeneration rate. No mathematical conversion from MAI published in source. |
| **Understory Veg. Growth Rate** | $r_2$ | $0.68\text{ yr}^{-1}$ | $[0.35, 1.10]$ | **REQUIRES CALIBRATION** | Sukumar et al. (1992) *Mudumalai 50-ha Plot Studies* | Documents 1–3 year turnover rates of secondary shrub and grass layers. | Inferred from understory turnover dynamics. Requires site-specific plot calibration. |
| **Invasive Cohort Growth Rate** | $r_3$ | $0.92\text{ yr}^{-1}$ | $[0.40, 1.60]$ | **REQUIRES CALIBRATION** | Hiremath & Sundaram (2005); Babu et al. (2009) | Reports 40–70% higher photosynthetic rate and continuous flowering in *Lantana*. | Theoretical maximum growth rate parameter representing aggressive thicket expansion. |
| **Native Carrying Capacity** | $K_1$ | $180.0\text{ Mg/ha}$ | $[80.0, 350.0]$ | **LITERATURE-DERIVED INVENTORY MAXIMUM** | FSI *ISFR 2021* Carbon Stock & Growing Stock Tables | Tabulates maximum standing growing stock for mature deciduous forest types ($140 - 210\text{ Mg/ha}$). | **$K_1$ is a literature-derived modelling proxy for the site's standing biomass ceiling, not a directly measured ecological carrying capacity.** |
| **Understory Carrying Capacity** | $K_2$ | $45.0\text{ Mg/ha}$ | $[15.0, 90.0]$ | **LITERATURE-INFORMED ESTIMATE** | Sukumar et al. (1992); IISc CES Long-Term Plot Data | Sub-canopy harvest biomass in undisturbed plots ranges from $15$ to $48\text{ Mg/ha}$. | **$K_2$ is a literature-informed sub-canopy biomass ceiling proxy, not an empirically measured ecological carrying capacity.** |
| **Invasive Monoculture Capacity** | $K_3$ | $65.0\text{ Mg/ha}$ | $[20.0, 120.0]$ | **LITERATURE-INFORMED ESTIMATE** | Sundaram et al. (2012); Ramaswami & Sukumar (2011) | Destructive quadrat sampling in dense *Lantana* monocultures records $42 - 76\text{ Mg/ha}$ dry biomass. | **$K_3$ is a literature-informed thicket biomass ceiling proxy, not an empirically measured ecological carrying capacity.** |
| **Canopy Shading on Understory** | $a_{21}$ | $0.25$ | $[0.10, 0.50]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Pritchard & Prasad (2018) | Documents light limitation under closed tree canopy. | Directional interaction coefficient satisfying shade suppression hierarchy. |
| **Understory on Canopy Regen.** | $a_{12}$ | $0.18$ | $[0.05, 0.40]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Champion & Seth (1968) | Qualitative description of ground grass root competition with tree seedlings. | Directional interaction coefficient representing diffuse root competition. |
| **Invasive Allelopathy on Canopy** | $a_{13}$ | $0.58$ | $[0.15, 1.20]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Ramaswami & Sukumar (2011) | Documents 50–80% seedling mortality under *Lantana* thickets. | Directional interaction coefficient representing allelopathic and physical smothering. |
| **Invasive on Understory Stratum** | $a_{23}$ | $0.65$ | $[0.20, 1.40]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Babu et al. (2009); Sundaram et al. (2012) | Local extirpation of native herbs and grasses within dense *Lantana* cores. | Directional interaction coefficient representing severe niche overlap in the 0–3m profile. |
| **Canopy Resistance on Invasive** | $a_{31}$ | $0.22$ | $[0.05, 0.60]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Pritchard & Prasad (2018) | *Lantana* establishment drops sharply under $>70\%$ closed tree canopy. | Directional interaction coefficient representing heliophyte shade suppression. |
| **Understory on Invasive Regen.** | $a_{32}$ | $0.15$ | $[0.05, 0.40]$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Hiremath & Sundaram (2005) | Mentions grass competition against invasive seedling emergence. | Weakest inter-specific term representing low competitive resistance of native grasses. |
| **Spatial Seed Diffusion Rate** | $D_z$ | $0.045\text{ ha/yr}$ | $[0.005, 0.150]$ | **REQUIRES CALIBRATION** | Prasad et al. (2010); Joshi et al. (2015) | *Pycnonotus cafer* dispersal distance kernel ($\bar{d} \approx 280\text{ m}$, $\sqrt{\langle R^2 \rangle} \approx 300\text{ m}$). | Order-of-magnitude scaling estimate ($D_z = p_{\text{est}} \frac{\langle R^2 \rangle}{4 \tau} \approx 0.02 \times 2.25 = 0.045\text{ ha/yr}$). **Not an empirically calibrated diffusion parameter.** |
| **Discrete Integration Time Step** | $\Delta t$ | $0.1\text{ yr}$ | $[0.01, 0.25]$ | **PROJECT-DEFINED** | Numerical Stability Analysis | Derived from linearized Forward Euler map stability condition in the complex plane ($\Delta t < \frac{2 |\text{Re}(\lambda_i)|}{|\lambda_i|^2}$). | Analytically verified for tested baseline state ($\Delta t_{\text{crit}} \approx 3.65\text{ yr} \gg 0.1\text{ yr}$). **Not claimed to be universally stable for every dynamic state.** |
| **Carbon Conversion Factor** | $f_C$ | $0.47\text{ Mg C / Mg AGB}$ | Fixed | **DIRECTLY REPORTED** | IPCC (2006) AFOLU Guidelines, Vol 4, Ch 4, Table 4.3; FSI *ISFR 2021* | Table 4.3 explicitly lists default carbon fraction as $0.47\text{ tonne C / tonne dry biomass}$. | Directly applied stoichiometric conversion: $\text{Carbon (Mg C/ha)} = \text{AGB (Mg/ha)} \times 0.47$. |

---

## 2. Invasive Impact Score (IIS) Weighting Scheme

The Invasive Impact Score is a **PROJECT-DEFINED MULTI-CRITERIA DECISION INDEX**:

$$\text{IIS} = 100 \times \left(0.25 f_{\text{cov}} + 0.20 f_{\text{bio}} + 0.25 f_{\text{disp}} + 0.15 f_{\text{sprd}} + 0.15 f_{\text{div}}\right)$$

* **$w_{\text{cov}} = 0.25$ (Spatial Coverage %):** **`PROJECT-DEFINED`** — High weight reflecting ground occupancy thickets that arrest native succession.
* **$w_{\text{disp}} = 0.25$ (Canopy Displacement %):** **`PROJECT-DEFINED`** — High weight reflecting ecological irreversibility under IUCN EICAT criteria.
* **$w_{\text{bio}} = 0.20$ (Standing Biomass Ratio):** **`PROJECT-DEFINED`** — Moderate weight reflecting fuel loading and resource monopolization.
* **$w_{\text{sprd}} = 0.15$ (Spread Velocity):** **`PROJECT-DEFINED`** — Moderate weight reflecting spatial invasion front velocity.
* **$w_{\text{div}} = 0.15$ (Shannon Diversity Loss):** **`PROJECT-DEFINED`** — Moderate weight reflecting understory floristic homogenization.

> [!NOTE]
> Neither IUCN EICAT nor FSI publishes these exact five numerical weights. They represent a project-defined heuristic multi-attribute framework constructed for this decision-support system.
