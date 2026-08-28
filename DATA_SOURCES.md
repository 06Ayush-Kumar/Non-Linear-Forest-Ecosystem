# REAL SCIENTIFIC DATA SOURCES & APIS (DATA_SOURCES.md)

This platform strictly enforces zero synthetic placeholders for real-world environmental and ecological metrics. Every dataset is either fetched live from recognized public scientific APIs or cited from official government forest publications.

---

## 1. External Scientific APIs

### A. Open-Meteo Historical / ERA5 Land Reanalysis
- **Provider:** ECMWF (European Centre for Medium-Range Weather Forecasts) via Open-Meteo
- **Endpoint:** https://archive-api.open-meteo.com/v1/archive
- **Variables Retrieved:**
  - 	emperature_2m_mean (°C): Daily 2m mean air temperature
  - 	emperature_2m_max (°C): Daily 2m maximum temperature
  - 	emperature_2m_min (°C): Daily 2m minimum temperature
  - precipitation_sum (mm): Daily total precipitation
  - shortwave_radiation_sum (MJ/m²): Daily solar irradiance
- **Spatial Resolution:** 0.1° (~11 km grid)
- **Temporal Resolution:** Daily time series aggregated across 365 days
- **Caching Mechanism:** Local disk cache (data_layer/.cache/openmeteo_era5_*.json) with fallback on network failure.

### B. NASA / USGS SRTM Digital Elevation Model
- **Provider:** NASA Jet Propulsion Laboratory / USGS via Open-Elevation API
- **Endpoint:** https://api.open-elevation.com/api/v1/lookup
- **Variable Retrieved:** elevation (m ASL)
- **Spatial Resolution:** 90m (SRTM 3 arc-second)
- **Method:** Bilinear interpolation from global raster tiles at exact centroid coordinates.

### C. Global Biodiversity Information Facility (GBIF)
- **Provider:** GBIF Secretariat & Indian Partner Herbaria (BSI, WII, IISc)
- **Endpoint:** https://api.gbif.org/v1/occurrence/search
- **Variables Retrieved:**
  - Total verified occurrence count in India (country=IN)
  - Georeferenced point observations (latitude, longitude, collection date, basis of record, herbarium dataset name)
- **Taxonomic Resolution:** Canonical species binomial resolved via synonym dictionary.

---

## 2. Government Forestry Inventories & Literature Datasets

### A. Forest Survey of India (FSI ISFR 2021)
- **Source Agency:** Ministry of Environment, Forest and Climate Change (MoEFCC), Govt. of India
- **Publication:** *India State of Forest Report (ISFR 2021)*, Dehradun
- **Parameters Utilized:**
  - State and Protected Area forest cover classes (VDF: Very Dense Forest, MDF: Moderately Dense Forest, OF: Open Forest)
  - Growing stock per hectare by forest type (m³/ha and Mg/ha)
  - Aboveground carbon pool accounting coefficients (IPCC 2006 conversion factor: 0.47)
  - Major forest types according to Champion & Seth (1968) revised classification.

### B. Protected Area Working Plans & Management Plans
- **Source Agencies:** Tamil Nadu Forest Department, Karnataka Forest Department, Madhya Pradesh Forest Department, Uttarakhand Forest Department, Assam Forest Department, Gujarat Forest Department, Kerala Forest Department
- **Parameters Utilized:**
  - Cadastral gazetted boundary areas (ha / km²)
  - Key native canopy timber species (*Tectona grandis*, *Shorea robusta*, *Dalbergia latifolia*, *Terminalia tomentosa*, *Pterocarpus marsupium*)
  - Documented invasive alien plant species (*Lantana camara*, *Senna spectabilis*, *Prosopis juliflora*, *Parthenium hysterophorus*, *Chromolaena odorata*, *Mikania micrantha*)
  - Historic fire return intervals and management zoning boundaries.

### C. Silvicultural & Ecological Literature
- **Troup, R.S. (1921):** *The Silviculture of Indian Trees*, Vols. I-III, Clarendon Press, Oxford. (Phenology, germination, shade tolerance, longevity).
- **Champion, H.G. and Seth, S.K. (1968):** *A Revised Survey of the Forest Types of India*, Manager of Publications, Delhi.
- **Babu, S. et al. (2009):** *Ecology and Management of Lantana camara in Indian Forests*, Tropical Ecology 50(1): 185-197.
- **Ramaswami, G. and Sukumar, R. (2011):** *Long-term dynamics of invasive plants in a tropical dry forest*, Forest Ecology and Management 262(10): 1888-1896.
- **KFRI (2018):** *Invasion and Management of Senna spectabilis in the Protected Areas of Kerala*, KFRI Research Report 532, Peechi.
