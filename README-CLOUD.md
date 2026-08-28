# Cloud Deployment Guide — FORESTDYN Scientific Platform
### Nonlinear Forest Ecosystem Dynamics | Spatial Modelling • Stability Analysis • Invasion Risk

## 1. System Architecture Overview

The **FORESTDYN Platform** utilizes a robust dual-layer architecture designed for high availability, cloud portability, and scientific rigor:


```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLOUD WEB PLATFORM                               │
│                   (Render / Railway / Fly.io / Linux VM)                    │
│                                                                             │
│  ┌─────────────────────────┐          ┌──────────────────────────────────┐  │
│  │   Interactive Frontend  │          │      Flask + Gunicorn (WSGI)     │  │
│  │ (Leaflet GIS, 30x30 Map,│◄────────►│      Multithreaded REST API      │  │
│  │  KaTeX Math, 3D Mesh)   │   HTTP   │       (0.0.0.0:$PORT)            │  │
│  └─────────────────────────┘          └─────────────────┬────────────────┘  │
│                                                         │                   │
│  ┌──────────────────────────────────────────────────────┴────────────────┐  │
│  │  LAYER 2: Mathematical Core & Decision Support                        │  │
│  │  • 3-State Coupled Nonlinear ODE Stability Model                      │  │
│  │  • Analytical Jacobian J_F & Discrete Map J_map = I + dt*J_F          │  │
│  │  • Spectral Radius rho(J_map) Stability & Numerical Cross-Check       │  │
│  │  • 30x30 Spatial Landscape Cellular Automaton                         │  │
│  │  • 10 Policy Management Scenario Rankings                             │  │
│  │  • 12-Step Candidate Species Evaluator                                │  │
│  │  • 26-Section Academic Decision-Support Report Generator              │  │
│  │  • Public External APIs (Open-Meteo ERA5, SRTM DEM, GBIF Occurrences) │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │ Optional Hybrid Bridge
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WINDOWS RUNNER WORKSTATION                          │
│                      (Presenter Laptop / Windows VM)                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 1: Official LANDIS-II 7.0 Engine Execution                      │  │
│  │  • Landis.Console.exe (.NET Framework 4.8 Runtime)                    │  │
│  │  • Biomass Succession 7.2 + Output Biomass 4.1 Extensions             │  │
│  │  • GDAL 2.0.2 Windows C++ Native Shared Library (gdal202.dll)         │  │
│  │  • 9,801-Cell (99x99) Landscape Simulation & 108 GeoTIFF Rasters      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Cloud Compatibility Matrix

| Platform Component | Linux Cloud Container | Windows Workstation | Scientific Functionality |
|:---|:---:|:---:|:---|
| **India GIS & Leaflet Maps** | ✅ Active | ✅ Active | 9 Protected Areas polygon & spatial metadata |
| **Forest Baseline & Species Library** | ✅ Active | ✅ Active | FSI 2021 Table 9.20.1 stocks, native & invasive taxa |
| **Live Climatology & DEM Profiling** | ✅ Active | ✅ Active | Open-Meteo ECMWF ERA5 & SRTM elevation + disk caching |
| **30×30 Reduced-Order Simulator** | ✅ Active | ✅ Active | Spatial ODE cellular automaton |
| **Jacobian Stability Engine** | ✅ Active | ✅ Active | Exact analytical continuous Jacobian, discrete map, eigenvalues, spectral radius |
| **10 Management Scenarios** | ✅ Active | ✅ Active | Multi-criteria policy ranking matrices |
| **12-Step Candidate Introduction Evaluator** | ✅ Active | ✅ Active | Abiotic suitability & invasive impact scoring |
| **26-Section Scientific Report Generator** | ✅ Active | ✅ Active | KaTeX mathematical formatting & provenance badges |
| **System Reality Status Dashboard** | ✅ Active | ✅ Active | 10-component live verification |
| **Layer 1 LANDIS-II Execution (`Landis.Console.exe`)** | ⚠️ Notice Displayed | ✅ Full Subprocess | Full landscape raster generation |

> [!NOTE]
> **Linux Cloud Behavior for Layer 1:** When *"Run Real LANDIS-II Simulation"* is clicked in Linux cloud mode, the workstation safely displays:  
> `LANDIS-II native engine unavailable in this Linux environment. (Requires Windows .NET Framework 4.8 & GDAL runtime. Please use the Layer 2 Reduced-Order Spatial Simulator for cloud modeling).`  
> Zero mock results are invented; zero crashes occur; Layer 2 modeling remains 100% operational.

---

## 3. Quickstart Deployment Guide

### Option A: Render / Railway (Direct Git Integration)

1. **Push repository to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "feat: production cloud deployment setup"
   git remote add origin https://github.com/<your-username>/Landis2_India_Platform.git
   git branch -M main
   git push -u origin main
   ```

2. **Configure on Cloud Platform (e.g. Render Web Service):**
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
   * **Health Check Path:** `/health`

---

### Option B: Docker Container Deployment

1. **Build the container image:**
   ```bash
   docker build -t landis2-india-platform .
   ```

2. **Run locally or on any cloud container host:**
   ```bash
   docker run -p 5000:5000 -e PORT=5000 landis2-india-platform
   ```

3. **Verify health:**
   ```bash
   curl http://localhost:5000/health
   ```

---

## 4. Environment Variables

| Variable | Default | Purpose |
|:---|:---:|:---|
| `PORT` | `5000` | Port assigned dynamically by cloud provider |
| `HOST` | `0.0.0.0` | Network interface binding |
| `PYTHONUNBUFFERED` | `1` | Real-time diagnostic logging to container stdout |
| `FLASK_ENV` | `production` | Production mode |

---

## 5. Scientific Core Integrity Notice

The underlying scientific equations, parameters, IPCC 2006 carbon factors, interaction matrices, stability criteria, and provenance classifications are strictly **frozen** and run identically in both Linux Cloud and Windows local environments.
