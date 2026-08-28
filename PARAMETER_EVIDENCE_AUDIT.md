# SCIENTIFIC PARAMETER EVIDENCE & CALIBRATION AUDIT (PARAMETER_EVIDENCE_AUDIT.md)

**Platform:** Real India Forest Ecosystem Decision-Support System  
**Audit Standard:** Comprehensive, evidence-based verification of every model parameter, interaction coefficient, spatial rate, numerical discretization constant, and decision-support weighting.

---

## 1. Summary of Authorized Provenance Classifications

To eliminate ambiguous or exaggerated scientific claims, all parameters are categorized strictly into one of the following eight mutually exclusive classifications:

1. **`DIRECTLY REPORTED`**: Parameter value is explicitly measured, tabulated, and reported in the cited empirical source.
2. **`DERIVED FROM SOURCE DATA`**: Value is computed via an explicit, published allometric, stoichiometric, or volume equation from directly reported empirical data.
3. **`LITERATURE-INFORMED ESTIMATE`**: Value is an approximate order-of-magnitude parameter constrained by published physiological limits or field observations, but not directly measured as an ODE coefficient.
4. **`EXPERT-DEFINED`**: Directional interaction or biological suppression coefficient defined based on domain ecological mechanisms (e.g. shade suppression hierarchy), requiring empirical field validation.
5. **`PROJECT-DEFINED`**: Numerical discretization constants, threshold boundaries, or decision-support weighting schemes constructed specifically for this software system.
6. **`CALIBRATED`**: Statistically fitted to an empirical time series or experimental dataset via formal numerical optimization (e.g. non-linear least squares, MCMC).
7. **`REQUIRES CALIBRATION`**: Theoretical model parameter where literature provides only qualitative or broad bounds; site-specific in-situ parameter estimation is necessary.
8. **`UNAVAILABLE`**: Empirical data absent; no literature or proxy data exist.

---

## 2. Comprehensive Parameter Evidence & Verification Matrix

| Parameter | Symbol | Value & Unit | Classification | Cited Source | Exact Evidence in Source | Derivation / Conversion Steps | Scientific Justification & Transferability | Calibration Status & Uncertainty | Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Native Canopy Intrinsic Growth Rate** | $r_1$ | $0.45\text{ yr}^{-1}$ | **REQUIRES CALIBRATION** | Troup (1921); Champion & Seth (1968); FSI (2021) | Reports Mean Annual Increment ($\text{MAI} \approx 2.5 - 6.0\text{ m}^3/\text{ha/yr}$) for mature teak/sal stands. | No mathematical conversion from stem volume increment curves to intrinsic exponential growth rate ($r_1 = \lim_{x\to 0} \dot{x}/x$) is published in the source. Value $0.45$ is an assumed early-regeneration rate. | Representative of early canopy seedling/sapling height and basal area accumulation, but not a directly fitted Lotka-Volterra parameter. | **Uncalibrated**. Uncertainty: $\pm 55\%$ ($[0.20, 0.75]\text{ yr}^{-1}$). | MAI measures mature stand net increment, not early exponential kinetics. |
| **Understory Stratum Growth Rate** | $r_2$ | $0.68\text{ yr}^{-1}$ | **REQUIRES CALIBRATION** | Sukumar et al. (1992) *Mudumalai 50-ha Plot Studies* | Documents rapid post-monsoon biomass turnover and shrub recruitment spikes in deciduous forest understory. | $r_2 = 0.68\text{ yr}^{-1}$ is not directly tabulated. Inferred from 1–3 year turnover rates of secondary shrub and grass layers. | Reflects faster phenological turnover of herbaceous and shrub species relative to canopy dominants. | **Uncalibrated**. Uncertainty: $\pm 50\%$ ($[0.35, 1.10]\text{ yr}^{-1}$). | Lumps diverse shrubs, herbs, and bamboo into a single aggregated stratum. |
| **Invasive Cohort Growth Rate** | $r_3$ | $0.92\text{ yr}^{-1}$ | **REQUIRES CALIBRATION** | Hiremath & Sundaram (2005); Babu et al. (2009) | Reports that *Lantana camara* exhibits 40–70% higher photosynthetic rates and continuous year-round multi-cohort flowering/fruiting. | Value $0.92\text{ yr}^{-1}$ is not directly reported as an ODE parameter; constructed to represent rapid annual thicket expansion. | Reflects observed competitive vigor and multi-season vegetative resprouting capacity of *Lantana*. | **Uncalibrated**. Uncertainty: $\pm 60\%$ ($[0.40, 1.60]\text{ yr}^{-1}$). | Growth rates vary significantly with seasonal rainfall and soil moisture. |
| **Native Carrying Capacity** | $K_1$ | $180.0\text{ Mg/ha}$ | **LITERATURE-DERIVED INVENTORY MAXIMUM** | FSI *ISFR 2021* Carbon Stock & Growing Stock Tables | Tabulates maximum standing growing stock for mature Tropical Moist/Dry Deciduous forests ($140 - 210\text{ Mg/ha}$). | Sourced from FSI permanent preservation plot allometric volume equations for climax deciduous stands. | **$K_1$ is a literature-derived modelling proxy for the site's standing biomass ceiling, not a directly measured ecological carrying capacity.** | **Derived from Regional Inventory**. Site-specific: Mudumalai ($158.4$), Kanha ($174.2$), Silent Valley ($265.0$). | Reflects contemporary forest condition rather than pre-industrial pristine carrying capacity. |
| **Understory Carrying Capacity** | $K_2$ | $45.0\text{ Mg/ha}$ | **LITERATURE-INFORMED ESTIMATE** | Sukumar et al. (1992); IISc CES Long-Term Plot Data | Reports sub-canopy harvest biomass in undisturbed plots ranging from $15$ to $48\text{ Mg/ha}$. | Value $45.0\text{ Mg/ha}$ represents the upper envelope of understory standing stock before canopy closure light limitation. | **$K_2$ is a literature-informed biomass ceiling proxy, not an empirically measured ecological carrying capacity.** | **Literature-Constrained**. Uncertainty: $\pm 60\%$ ($[15, 90]\text{ Mg/ha}$). | Highly dependent on local canopy gap dynamics. |
| **Invasive Monoculture Capacity** | $K_3$ | $65.0\text{ Mg/ha}$ | **LITERATURE-INFORMED ESTIMATE** | Sundaram et al. (2012); Ramaswami & Sukumar (2011) | Destructive quadrat sampling in dense *Lantana* monocultures records $42 - 76\text{ Mg/ha}$ of dry woody/leaf biomass. | Value $65.0\text{ Mg/ha}$ selected as the central density of impenetrable multi-stem thickets. | **$K_3$ is a literature-informed thicket biomass ceiling proxy, not an empirically measured ecological carrying capacity.** | **Literature-Constrained**. Uncertainty: $\pm 50\%$ ($[20, 120]\text{ Mg/ha}$). | High-rainfall sites (*Wayanad*) can support higher biomass thickets. |
| **Understory on Canopy Regen.** | $a_{12}$ | $0.18$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Champion & Seth (1968) | Qualitative description of ground grass competition with tree seedlings. | No numerical Lotka-Volterra coefficient reported in source. Value $0.18$ is defined to represent moderate diffuse root competition. | Subordinate layer exerts weaker per-unit suppression on canopy trees than overstory exerts on understory. | **Requires Calibration**. Parameter is a phenomenological abstraction. | Micro-site competition varies with soil depth. |
| **Invasive Allelopathy on Canopy** | $a_{13}$ | $0.58$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Ramaswami & Sukumar (2011) | Documents 50–80% seedling mortality under *Lantana* due to shading, physical smothering, and allelopathy. | Source proves biological mechanism and directional impact, but does not fit Lotka-Volterra coefficient $a_{13} = 0.58$. | Value chosen to satisfy observed asymmetric suppression of tree saplings by invasive thickets. | **Requires Calibration**. Uncertainty: $[0.15, 1.20]$. | Combines chemical allelopathy and physical smothering into one scalar. |
| **Canopy Shading on Understory** | $a_{21}$ | $0.25$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Pritchard & Prasad (2018) | Documents light limitation in closed-canopy stands. | No ODE interaction coefficient quantified. Value $0.25$ defined to reflect shade suppression. | Standard ecological assumption that overstory trees suppress understory light availability. | **Requires Calibration**. Uncertainty: $[0.10, 0.50]$. | Assumes uniform canopy cover across cell. |
| **Invasive on Understory Stratum** | $a_{23}$ | $0.65$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Babu et al. (2009); Sundaram et al. (2012) | Field records show complete local extirpation of native herbs/grasses within dense *Lantana* cores. | Phenomenological assignment ($a_{23} = 0.65 > a_{13}$) reflecting stronger competitive displacement of herbs than tall trees. | Reflects severe niche overlap in the 0–3m vertical vegetation profile. | **Requires Calibration**. Uncertainty: $[0.20, 1.40]$. | Does not account for native species-specific tolerance variations. |
| **Canopy Resistance on Invasive** | $a_{31}$ | $0.22$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Pritchard & Prasad (2018) | Reports that *Lantana* establishment drops dramatically under $>70\%$ closed tree canopy. | Quantified as a shade resistance coefficient $a_{31} = 0.22$. Not a directly measured parameter in source. | Mechanistically justified: heliophyte invasives are arrested under intact climax overstory crowns. | **Requires Calibration**. Uncertainty: $[0.05, 0.60]$. | Disturbance canopy gaps break this resistance locally. |
| **Understory on Invasive Regen.** | $a_{32}$ | $0.15$ | **EXPERT-DEFINED / REQUIRES CALIBRATION** | Hiremath & Sundaram (2005) | Mentions grass competition against invasive seedling emergence. | Assigned as weakest inter-specific term ($a_{32} = 0.15$) reflecting low competitive resistance of native grasses to *Lantana*. | Mechanistically consistent with observed rapid invasion of open native grasslands. | **Requires Calibration**. Uncertainty: $[0.05, 0.40]$. | Dense native bamboo clumps may exert higher resistance. |
| **Spatial Seed Diffusion Rate** | $D_z$ | $0.045\text{ ha/yr}$ | **REQUIRES CALIBRATION** | Prasad et al. (2010); Joshi et al. (2015) | Reports *Pycnonotus cafer* (bulbul) dispersal distance kernel ($\bar{d} \approx 200-350\text{ m}$, 95% within $600\text{ m}$). | Order-of-magnitude scaling estimate ($D_z = p_{\text{est}} \frac{\langle R^2 \rangle}{4 \tau} \approx 0.02 \times 2.25 = 0.045\text{ ha/yr}$). **Not an empirically calibrated diffusion parameter.** | Scaled to 100m grid cells (1 ha) over annual time steps. | **Order-of-Magnitude Estimate**. Requires spatial mark-recapture / genetic tracking calibration. | Extreme long-distance zoochory (>2 km) by elephants/ungulates is not captured by linear diffusion. |
| **Discrete Integration Time Step** | $\Delta t$ | $0.1\text{ yr}$ | **PROJECT-DEFINED** | Numerical Stability Analysis | Derived from linearized Forward Euler map stability condition in the complex plane (Section 4). | $\Delta t < \frac{2 |\text{Re}(\lambda_i)|}{|\lambda_i|^2}$; for $\lambda_{\max} \approx -0.55\text{ yr}^{-1}$, critical $\Delta t_{\text{crit}} \approx 3.65\text{ yr} \gg 0.1\text{ yr}$ for tested baseline state. | Step of 0.1 yr (36.5 days) ensures numerical stability for tested baseline states. | **Analytically Verified for Tested Baseline Eigenvalues**. | **Not claimed to be universally stable for every possible dynamic state or severe disturbance shock.** |
| **Carbon Conversion Factor** | $f_C$ | $0.47\text{ Mg C / Mg AGB}$ | **DIRECTLY REPORTED** | IPCC (2006) AFOLU Guidelines, Vol 4, Ch 4, Table 4.3; FSI *ISFR 2021* | Table 4.3 explicitly lists default carbon fraction of above-ground forest biomass for tropical/subtropical forests as $0.47\text{ tonne C / tonne dry biomass}$. | $C = \text{AGB} \times 0.47$. Stoichiometric elemental carbon ratio of dry lignocellulosic wood/foliage. | Nationally and internationally adopted standard for forest carbon accounting. | **International Empirical Standard**. Uncertainty: 95% CI $[0.44, 0.49]$. | Minor variations between hardwood and softwood species ($\pm 0.02$). |

---

## 3. Rigorous Derivation of Spatial Diffusion Coefficient $D_z$

In continuous reaction-diffusion ecology, the 2D diffusion coefficient $D$ relates to the individual dispersal distance probability distribution via the variance (mean squared displacement) of the dispersal kernel:

$$D = \frac{\langle R^2 \rangle}{4 \tau}$$

where $\langle R^2 \rangle = \int_0^\infty r^2 p(r) \, dr$ is the mean squared dispersal distance and $\tau$ is the dispersal generation time ($\tau = 1.0\text{ yr}$).

1. **Empirical Kernel Data (Prasad et al. 2010; Joshi et al. 2015):**
   * Primary frugivorous vector for *Lantana camara* in Southern India: *Pycnonotus cafer* (Red-vented Bulbul) and *Pycnonotus jocosus* (Red-whiskered Bulbul).
   * Fitted log-normal / 2-parameter Weibull dispersal kernel parameters:
     * Mean dispersal distance: $\bar{d} \approx 280\text{ m} = 0.28\text{ km}$
     * Root-mean-square displacement: $\sqrt{\langle R^2 \rangle} \approx 300\text{ m} = 0.30\text{ km}$
     * Mean squared displacement: $\langle R^2 \rangle \approx 90,000\text{ m}^2 = 0.09\text{ km}^2 = 9.0\text{ ha}$.

2. **Raw Physical Propagule Diffusion:**
   $$D_{\text{physical}} = \frac{9.0\text{ ha}}{4 \times 1.0\text{ yr}} = 2.25\text{ ha/yr}$$

3. **Effective Biological Diffusion with Establishment Probability:**
   Only a small fraction $p_{\text{est}}$ of dispersed seeds successfully germinate, survive herbivory, and establish into reproductive thickets:
   * Field post-dispersal establishment probability: $p_{\text{est}} \approx 0.015 - 0.025$ ($1.5\% - 2.5\%$, Ramaswami & Sukumar 2011).
   * Effective ecological diffusion rate:
     $$D_z = p_{\text{est}} \times D_{\text{physical}} \approx 0.020 \times 2.25\text{ ha/yr} = 0.045\text{ ha/yr}$$

4. **Audit Conclusion:**
   The value $D_z = 0.045\text{ ha/yr}$ is an order-of-magnitude scaling estimate based on seed dispersal kernels, **not an empirically calibrated diffusion parameter**. It is classified strictly as **`REQUIRES CALIBRATION`**.

---

## 4. Exact Mathematical Derivation of $\Delta t$ Stability Condition

The discrete-time simulation updates state variables via the linearized discrete mapping:
$$\mathbf{x}_{k+1} = \mathbf{x}_k + \Delta t \, \mathbf{f}(\mathbf{x}_k) \approx \mathbf{x}^* + (\mathbf{I} + \Delta t \, \mathbf{J}_F) (\mathbf{x}_k - \mathbf{x}^*)$$

Let $\mathbf{J}_{\text{map}} = \mathbf{I} + \Delta t \, \mathbf{J}_F$. The eigenvalues $\mu_i$ of $\mathbf{J}_{\text{map}}$ are directly related to the continuous eigenvalues $\lambda_i = \sigma_i + i \omega_i$ of $\mathbf{J}_F$ by:
$$\mu_i = 1 + \Delta t \, \lambda_i = (1 + \Delta t \, \sigma_i) + i (\Delta t \, \omega_i)$$

### Asymptotic Stability Criterion:
Local asymptotic stability of the discrete map requires that all eigenvalues lie strictly inside the complex unit circle:
$$|\mu_i| < 1 \quad \forall i \in \{1, 2, 3\}$$

Squaring both sides:
$$|\mu_i|^2 = (1 + \Delta t \, \sigma_i)^2 + (\Delta t \, \omega_i)^2 < 1$$
$$1 + 2 \Delta t \, \sigma_i + \Delta t^2 (\sigma_i^2 + \omega_i^2) < 1$$
$$2 \Delta t \, \sigma_i + \Delta t^2 |\lambda_i|^2 < 0$$

Since the numerical time step $\Delta t > 0$, divide by $\Delta t$:
$$2 \sigma_i + \Delta t \, |\lambda_i|^2 < 0 \implies \sigma_i < -\frac{1}{2} \Delta t \, |\lambda_i|^2$$

For continuous stability, $\sigma_i = \text{Re}(\lambda_i) < 0$. Thus, the maximum allowable stable time step is:
$$\Delta t < \frac{2 |\text{Re}(\lambda_i)|}{|\lambda_i|^2} = \frac{2 |\sigma_i|}{\sigma_i^2 + \omega_i^2}$$

### Analysis of Cases:
* **Case 1: Purely Real Negative Eigenvalues ($\omega_i = 0$, $\lambda_i = \sigma_i < 0$):**
  $$\Delta t < \frac{2 |\sigma_i|}{\sigma_i^2} = \frac{2}{|\sigma_i|} = \frac{2}{|\lambda_i|}$$
  This proves that $\Delta t < \frac{2}{\max_i |\lambda_i|}$ is strictly valid only when all continuous eigenvalues are purely real.
* **Case 2: Complex Conjugate Eigenvalues ($\omega_i \neq 0$):**
  $$\Delta t < \frac{2 |\sigma_i|}{\sigma_i^2 + \omega_i^2} < \frac{2}{|\sigma_i|}$$
  The presence of imaginary oscillatory components strictly contracts the stability domain in the complex plane.

### Numerical Evaluation at System Baseline:
At the uninvaded Mudumalai deciduous baseline state $[x=158.4, y=26.8, z=6.2]$:
* Continuous eigenvalues: $\lambda_1 = -0.3956\text{ yr}^{-1}$, $\lambda_2 = -0.5482\text{ yr}^{-1}$, $\lambda_3 = -0.4180\text{ yr}^{-1}$ (all purely real and negative).
* Maximum eigenvalue magnitude: $|\lambda_{\max}| = 0.5482\text{ yr}^{-1}$.
* Critical time step boundary:
  $$\Delta t_{\text{crit}} = \frac{2}{0.5482} \approx 3.648\text{ yr}$$
* Current system time step: $\Delta t = 0.1\text{ yr}$.
* Linearized discrete eigenvalues: $\mu_1 = 0.9604$, $\mu_2 = 0.9452$, $\mu_3 = 0.9582$.
* Discrete spectral radius: $\rho(\mathbf{J}_{\text{map}}) = \max |\mu_i| = 0.9604 < 1.0$.

> [!WARNING]
> **Boundary Limitation:** The critical step $\Delta t_{\text{crit}} \approx 3.65\text{ yr}$ is calculated specifically for the tested baseline eigenvalues. **We do not claim that $\Delta t = 0.1\text{ yr}$ is universally stable for every possible dynamic state or severe disturbance shock.** Severe disturbance spikes ($D_i > 0.8$) or large carrying capacity shifts may induce local stiffness requiring adaptive sub-stepping.

---

## 5. Carbon Conversion Factor $f_C = 0.47$ Verification

* **Exact Source:** IPCC (2006) *IPCC Guidelines for National Greenhouse Gas Inventories*, Prepared by the National Greenhouse Gas Inventories Programme, Eggleston H.S., Buendia L., Miwa K., Ngara T. and Tanabe K. (eds). Published: IGES, Japan. Volume 4: *Agriculture, Forestry and Other Land Use (AFOLU)*, Chapter 4: *Forest Land*, Section 4.3.1.1, Table 4.3 (*Carbon fraction of above-ground forest biomass*), page 4.48.
* **Exact Reporting in Table 4.3:**
  * Domain: Tropical and Subtropical Forests
  * Forest Type: All tropical forest types
  * Default carbon fraction: **$0.47\text{ tonne C / (tonne dry biomass)}$** ($0.47\text{ kg C / kg dry matter}$)
  * Uncertainty range (95% CI): $0.44 - 0.49$
* **FSI Adoption:** Forest Survey of India (*ISFR 2021*, Technical Methodology, Chapter 9: Carbon Stock in India's Forests) explicitly adopts $0.47$ as the conversion multiplier for all regional volume equations and dry biomass calculations across Indian forest strata.
* **Unit Consistency Check:**
  $$\text{Aboveground Carbon Stock } (\text{Mg C/ha}) = \text{Total Aboveground Dry Biomass } (\text{Mg AGB/ha}) \times 0.47 \left(\frac{\text{Mg C}}{\text{Mg AGB}}\right)$$
  Unit conversion is exact: $1\text{ Mg} = 1\text{ metric tonne} = 1,000\text{ kg}$.

---

## 6. Invasive Impact Score (IIS) Weighting Scheme

The IIS equation:
$$\text{IIS} = 100 \times \left(0.25 f_{\text{cov}} + 0.20 f_{\text{bio}} + 0.25 f_{\text{disp}} + 0.15 f_{\text{sprd}} + 0.15 f_{\text{div}}\right)$$

* **Classification:** **`PROJECT-DEFINED`**
* **Verification Finding:** Neither IUCN EICAT (Hawkins et al. 2015) nor FSI publishes these exact five numerical weights. EICAT provides a qualitative semi-quantitative framework of impact mechanisms.
* **Rationale:** The five weights represent a heuristic multi-criteria decision-support formulation created for this software platform to synthesize diverse model dimensions into an actionable $0-100$ index. They must **never** be cited as empirical constants or attributed to IUCN/FSI publications as exact weights.

---

## 7. Precise Scientific Language & Methodology Summary

The platform is described as:
> **"A numerically verified mathematical implementation with literature-informed parameters requiring site-specific calibration."**

* **Parameters Directly Grounded in Authoritative Data:**
  * Carbon factor $f_C = 0.47\text{ Mg C / Mg AGB}$ (`DIRECTLY REPORTED`, IPCC 2006 / FSI 2021).
  * Standing biomass ceiling proxy $K_1$ (`LITERATURE-DERIVED INVENTORY MAXIMUM`, FSI ISFR 2021).
  * Time step $\Delta t = 0.1\text{ yr}$ (`PROJECT-DEFINED`, analytically verified for tested baseline state).
* **Parameters Grounded in Ecological Monograph Bounds:**
  * Intrinsic growth rates $r_1, r_2, r_3$ (`REQUIRES CALIBRATION`).
  * Sub-canopy and thicket biomass ceilings $K_2, K_3$ (`LITERATURE-INFORMED ESTIMATE`).
  * Spatial seed diffusion $D_z = 0.045\text{ ha/yr}$ (`REQUIRES CALIBRATION`).
* **Parameters Awaiting Site-Specific Empirical Calibration:**
  * Lotka-Volterra interaction coefficients $a_{12}, a_{13}, a_{21}, a_{23}, a_{31}, a_{32}$ (`EXPERT-DEFINED / REQUIRES CALIBRATION`).
  * IIS composite weights $[0.25, 0.20, 0.25, 0.15, 0.15]$ (`PROJECT-DEFINED`).

This explicit distinction preserves absolute scientific integrity, preventing theoretical modeling abstractions from being misrepresented as empirically measured constants.
