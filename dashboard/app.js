// LANDIS-II Interactive Simulation Engine & Dynamic Landscape Model
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  // --- Landscape Grid Simulation State ---
  const GRID_SIZE = 50; // 50x50 = 2500 landscape cells
  let currentYear = 0;
  let isRunning = false;
  let simTimer = null;
  let simSpeed = 600; // ms per year

  // Tree Species Definitions
  const SPECIES = [
    { id: 'pipo', name: 'Ponderosa Pine (Pinus ponderosa)', color: '#22c55e', longevity: 400, shadeTol: 1, fireTol: 5, bdaSuscept: 0.8 },
    { id: 'psme', name: 'Douglas Fir (Pseudotsuga menziesii)', color: '#16a34a', longevity: 500, shadeTol: 3, fireTol: 4, bdaSuscept: 0.4 },
    { id: 'pila', name: 'Sugar Pine (Pinus lambertiana)', color: '#059669', longevity: 450, shadeTol: 2, fireTol: 3, bdaSuscept: 0.7 },
    { id: 'abco', name: 'White Fir (Abies concolor)', color: '#38bdf8', longevity: 300, shadeTol: 4, fireTol: 2, bdaSuscept: 0.3 },
    { id: 'potr', name: 'Quaking Aspen (Populus tremuloides)', color: '#eab308', longevity: 150, shadeTol: 1, fireTol: 1, bdaSuscept: 0.5 },
    { id: 'quke', name: 'Black Oak (Quercus kelloggii)', color: '#f97316', longevity: 350, shadeTol: 2, fireTol: 4, bdaSuscept: 0.2 }
  ];

  // Ecoregions Definitions
  const ECOREGIONS = [
    { id: 1, name: 'Lower Montane Pine', color: '#1e3a24', maxBiomass: 18000 },
    { id: 2, name: 'Mixed Conifer Forest', color: '#14382c', maxBiomass: 24000 },
    { id: 3, name: 'Upper Montane Fir', color: '#162e3b', maxBiomass: 20000 },
    { id: 4, name: 'Subalpine Ridge', color: '#25213b', maxBiomass: 12000 }
  ];

  // Initialize Landscape Cells
  let landscape = [];

  function initLandscape() {
    landscape = [];
    currentYear = 0;
    for (let r = 0; r < GRID_SIZE; r++) {
      let row = [];
      for (let c = 0; c < GRID_SIZE; c++) {
        // Ecoregion elevation gradient
        const distFromCenter = Math.sqrt(Math.pow(r - 25, 2) + Math.pow(c - 25, 2));
        let ecoIdx = 0;
        if (distFromCenter < 12) ecoIdx = 1;
        else if (distFromCenter < 20) ecoIdx = 2;
        else if (distFromCenter < 28) ecoIdx = 0;
        else ecoIdx = 3;

        const eco = ECOREGIONS[ecoIdx];

        // Pick initial species based on ecoregion
        let spec = SPECIES[0];
        if (ecoIdx === 1) spec = Math.random() > 0.4 ? SPECIES[1] : SPECIES[0];
        else if (ecoIdx === 2) spec = Math.random() > 0.5 ? SPECIES[3] : SPECIES[2];
        else if (ecoIdx === 3) spec = Math.random() > 0.6 ? SPECIES[4] : SPECIES[1];

        const initialBiomass = Math.floor(eco.maxBiomass * (0.4 + Math.random() * 0.45));
        
        row.push({
          r, c,
          ecoregion: eco,
          species: spec,
          biomass: initialBiomass, // g/m²
          cohorts: [
            { age: Math.floor(20 + Math.random() * 80), biomass: initialBiomass * 0.7 },
            { age: Math.floor(5 + Math.random() * 15), biomass: initialBiomass * 0.3 }
          ],
          fuelLoad: 4.0 + Math.random() * 5.0, // tonnes/ha
          disturbance: null, // 'fire', 'bda', 'harvest', 'wind'
          disturbTimer: 0,
          burnedSeverity: 0
        });
      }
      landscape.push(row);
    }
    updateTelemetry();
    renderMap();
    initCharts();
  }

  // --- Canvas Rendering Engine ---
  const canvas = document.getElementById('landscape-canvas');
  const ctx = canvas.getContext('2d');
  const viewSelector = document.getElementById('map-view-mode');
  const cellSize = canvas.width / GRID_SIZE;

  function renderMap() {
    const viewMode = viewSelector.value;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        const cell = landscape[r][c];
        const x = c * cellSize;
        const y = r * cellSize;

        if (cell.disturbTimer > 0) {
          // Render Active Disturbance Fronts
          if (cell.disturbance === 'fire') {
            ctx.fillStyle = cell.disturbTimer > 1 ? '#ff3b30' : '#ff9500';
            ctx.fillRect(x, y, cellSize, cellSize);
            // Glowing ember effect
            ctx.fillStyle = '#ffcc00';
            ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
            continue;
          } else if (cell.disturbance === 'bda') {
            ctx.fillStyle = '#ec4899';
            ctx.fillRect(x, y, cellSize, cellSize);
            continue;
          } else if (cell.disturbance === 'harvest') {
            ctx.fillStyle = '#eab308';
            ctx.fillRect(x, y, cellSize, cellSize);
            continue;
          }
        }

        // Standard Layers
        if (viewMode === 'biomass') {
          const ratio = Math.min(1, cell.biomass / cell.ecoregion.maxBiomass);
          const greenVal = Math.floor(60 + ratio * 180);
          ctx.fillStyle = `rgb(10, ${greenVal}, 40)`;
          ctx.fillRect(x, y, cellSize, cellSize);
        } else if (viewMode === 'species') {
          ctx.fillStyle = cell.species.color;
          ctx.fillRect(x, y, cellSize, cellSize);
        } else if (viewMode === 'disturbance') {
          if (cell.burnedSeverity > 0) {
            ctx.fillStyle = `rgba(180, 50, 20, ${cell.burnedSeverity})`;
          } else {
            ctx.fillStyle = '#1a222d';
          }
          ctx.fillRect(x, y, cellSize, cellSize);
        } else if (viewMode === 'ecoregions') {
          ctx.fillStyle = cell.ecoregion.color;
          ctx.fillRect(x, y, cellSize, cellSize);
        } else if (viewMode === 'carbon') {
          const cVal = Math.floor((cell.biomass * 0.47) / 100);
          ctx.fillStyle = `rgb(20, ${Math.min(220, cVal * 2)}, 180)`;
          ctx.fillRect(x, y, cellSize, cellSize);
        }

        // Subtle grid line
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.strokeRect(x, y, cellSize, cellSize);
      }
    }
    updateLegend();
  }

  // Legend Bar
  function updateLegend() {
    const leg = document.getElementById('map-legend');
    const viewMode = viewSelector.value;
    leg.innerHTML = '';

    if (viewMode === 'species') {
      SPECIES.forEach(s => {
        leg.innerHTML += `<div class="legend-item"><span class="legend-color" style="background:${s.color}"></span><span>${s.name.split(' ')[0]} ${s.name.split(' ')[1]}</span></div>`;
      });
    } else if (viewMode === 'biomass') {
      leg.innerHTML = `
        <div class="legend-item"><span class="legend-color" style="background:#0a4020"></span><span>Low (< 5,000 g/m²)</span></div>
        <div class="legend-item"><span class="legend-color" style="background:#0fa030"></span><span>Moderate (12,000 g/m²)</span></div>
        <div class="legend-item"><span class="legend-color" style="background:#15f030"></span><span>High (> 20,000 g/m²)</span></div>
      `;
    } else if (viewMode === 'ecoregions') {
      ECOREGIONS.forEach(e => {
        leg.innerHTML += `<div class="legend-item"><span class="legend-color" style="background:${e.color}"></span><span>${e.name}</span></div>`;
      });
    } else if (viewMode === 'disturbance') {
      leg.innerHTML = `
        <div class="legend-item"><span class="legend-color" style="background:#ff3b30"></span><span>Active Wildfire Front</span></div>
        <div class="legend-item"><span class="legend-color" style="background:#ec4899"></span><span>Bark Beetle Defoliation</span></div>
        <div class="legend-item"><span class="legend-color" style="background:#eab308"></span><span>Silvicultural Harvest</span></div>
      `;
    }
  }

  // --- Step Simulation (Succession & Disturbance Engine) ---
  let totalBurnedHa = 0;
  let historyYears = [0];
  let historyBiomass = [12450];
  let historyBurned = [0];

  function stepYear() {
    currentYear += 1;
    document.getElementById('current-year-display').textContent = `Year ${currentYear}`;

    let totalBiomass = 0;
    let bdaCount = 0;

    // 1. Process Biomass Succession on every cell
    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        const cell = landscape[r][c];

        // Age cohorts & Biomass increment (Logistic growth with climate modifier)
        const maxB = cell.ecoregion.maxBiomass;
        const growthRate = 0.04 * (1 - (cell.biomass / maxB));
        cell.biomass = Math.min(maxB, Math.floor(cell.biomass * (1 + Math.max(0.005, growthRate))));

        // Age cohorts
        cell.cohorts.forEach(co => co.age += 1);

        // Fuel load accumulation
        cell.fuelLoad = Math.min(18, cell.fuelLoad + 0.25);

        // Decrease active disturbance visual timers
        if (cell.disturbTimer > 0) {
          cell.disturbTimer -= 1;
          if (cell.disturbTimer === 0) cell.disturbance = null;
        }

        totalBiomass += cell.biomass;
        if (cell.disturbance === 'bda') bdaCount++;
      }
    }

    // 2. Stochastic Fire Ignitions (Dynamic Fire Module)
    const fireProb = parseFloat(document.getElementById('param-fire-prob')?.value || 0.015);
    if (Math.random() < fireProb * 3) {
      const fr = Math.floor(Math.random() * GRID_SIZE);
      const fc = Math.floor(Math.random() * GRID_SIZE);
      simulateFireSpread(fr, fc, 3 + Math.floor(Math.random() * 5));
    }

    // Telemetry updates
    const avgBiomass = Math.floor(totalBiomass / (GRID_SIZE * GRID_SIZE));
    const carbonKt = ((totalBiomass * 2500 * 0.47) / 1e6).toFixed(1);

    document.getElementById('metric-avg-biomass').innerHTML = `${avgBiomass.toLocaleString()} <small>g/m²</small>`;
    document.getElementById('metric-burned-ha').innerHTML = `${totalBurnedHa} <small>ha</small>`;
    document.getElementById('metric-carbon').innerHTML = `${carbonKt} <small>kt C</small>`;
    document.getElementById('metric-bda-pct').innerHTML = `${((bdaCount / 2500) * 100).toFixed(1)} <small>%</small>`;

    // Append to charts
    historyYears.push(currentYear);
    historyBiomass.push(avgBiomass);
    historyBurned.push(totalBurnedHa);
    if (historyYears.length > 30) {
      historyYears.shift();
      historyBiomass.shift();
      historyBurned.shift();
    }
    updateCharts();
    renderMap();

    // Log periodic milestone
    if (currentYear % 5 === 0) {
      addLog(`Succession timestep finished. Mean landscape biomass: ${avgBiomass} g/m². Total C: ${carbonKt} kt.`, 'info');
    }
  }

  // Fire Spread Cellular Automaton (Dynamic Fire System)
  function simulateFireSpread(startR, startC, intensity) {
    let queue = [{ r: startR, c: startC, power: intensity }];
    let burnedThisFire = 0;

    while (queue.length > 0) {
      const { r, c, power } = queue.shift();
      if (r < 0 || r >= GRID_SIZE || c < 0 || c >= GRID_SIZE) continue;
      const cell = landscape[r][c];

      if (cell.disturbTimer > 0 && cell.disturbance === 'fire') continue;

      // Burn cell
      cell.disturbance = 'fire';
      cell.disturbTimer = 3;
      cell.burnedSeverity = Math.min(1.0, cell.burnedSeverity + 0.35);
      
      // Biomass consumption & mortality
      const loss = Math.floor(cell.biomass * (0.4 + power * 0.08));
      cell.biomass = Math.max(1200, cell.biomass - loss);
      cell.fuelLoad = 1.0;
      burnedThisFire += 1;
      totalBurnedHa += 1;

      // Spread to neighbors (wind-biased)
      if (power > 1) {
        const neighbors = [
          { r: r - 1, c: c },
          { r: r + 1, c: c },
          { r: r, c: c - 1 },
          { r: r, c: c + 1 },
          { r: r - 1, c: c + 1 } // Wind spread SW -> NE
        ];
        neighbors.forEach(n => {
          if (Math.random() < 0.65) {
            queue.push({ r: n.r, c: n.c, power: power - 1 });
          }
        });
      }
    }

    addLog(`🔥 Wildfire ignition at [${startR}, ${startC}] burned ${burnedThisFire} ha across ${intensity} severity zones.`, 'fire');
  }

  // Bark Beetle BDA Outbreak
  function triggerBDA() {
    let infected = 0;
    const centerR = Math.floor(10 + Math.random() * 30);
    const centerC = Math.floor(10 + Math.random() * 30);

    for (let dr = -4; dr <= 4; dr++) {
      for (let dc = -4; dc <= 4; dc++) {
        const r = centerR + dr;
        const c = centerC + dc;
        if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
          const cell = landscape[r][c];
          if (cell.species.bdaSuscept > 0.5 && Math.random() < 0.7) {
            cell.disturbance = 'bda';
            cell.disturbTimer = 4;
            cell.biomass = Math.floor(cell.biomass * 0.75);
            infected++;
          }
        }
      }
    }
    addLog(`🐛 BDA Outbreak (Dendroctonus ponderosae) defoliated ${infected} stands in Montane Pine zone.`, 'bda');
    renderMap();
  }

  // Silvicultural Harvest Cut
  function triggerHarvest() {
    let harvested = 0;
    const startR = Math.floor(Math.random() * (GRID_SIZE - 6));
    const startC = Math.floor(Math.random() * (GRID_SIZE - 6));

    for (let r = startR; r < startR + 6; r++) {
      for (let c = startC; c < startC + 6; c++) {
        const cell = landscape[r][c];
        cell.disturbance = 'harvest';
        cell.disturbTimer = 3;
        cell.biomass = Math.floor(cell.biomass * 0.3); // Thinning
        cell.fuelLoad = 2.0;
        harvested++;
      }
    }
    addLog(`🪓 Base Harvest: Thinning prescription executed over ${harvested} ha management block.`, 'harvest');
    renderMap();
  }

  // Windthrow Event
  function triggerWind() {
    let windthrow = 0;
    const stripRow = Math.floor(5 + Math.random() * 40);
    for (let c = 0; c < GRID_SIZE; c++) {
      if (Math.random() < 0.7) {
        const cell = landscape[stripRow][c];
        cell.disturbance = 'wind';
        cell.disturbTimer = 2;
        cell.biomass = Math.floor(cell.biomass * 0.5);
        cell.fuelLoad += 5.0; // Coarse debris
        windthrow++;
      }
    }
    addLog(`🌪️ Extreme Windthrow: Derecho storm path felled cohorts along corridor (${windthrow} ha affected).`, 'info');
    renderMap();
  }

  // --- Event Logger ---
  function addLog(msg, type = 'info') {
    const logBox = document.getElementById('event-logs');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="log-time">[Year ${currentYear}]</span> ${msg}`;
    logBox.appendChild(entry);
    logBox.scrollTop = logBox.scrollHeight;
  }

  document.getElementById('clear-logs').addEventListener('click', () => {
    document.getElementById('event-logs').innerHTML = '';
  });

  // --- Hover Tooltip on Canvas ---
  const tooltip = document.getElementById('cell-hover-card');
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const c = Math.floor(x / cellSize);
    const r = Math.floor(y / cellSize);

    if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
      const cell = landscape[r][c];
      tooltip.classList.remove('hidden');
      tooltip.style.left = `${Math.min(rect.width - 200, x + 15)}px`;
      tooltip.style.top = `${Math.min(rect.height - 180, y + 15)}px`;

      document.getElementById('tt-coords').textContent = `Site Location [R:${r}, C:${c}]`;
      document.getElementById('tt-ecoregion').textContent = cell.ecoregion.name;
      document.getElementById('tt-species').textContent = cell.species.name;
      document.getElementById('tt-biomass').textContent = `${cell.biomass.toLocaleString()} g/m²`;
      document.getElementById('tt-cohorts').textContent = cell.cohorts.map(co => `${co.age}y`).join(', ');
      document.getElementById('tt-fuel').textContent = `${cell.fuelLoad.toFixed(1)} t/ha`;
      document.getElementById('tt-status').textContent = cell.disturbance ? `Active ${cell.disturbance.toUpperCase()}` : 'Stable / Intact';
    }
  });

  canvas.addEventListener('mouseleave', () => {
    tooltip.classList.add('hidden');
  });

  // Canvas Click: Ignite manual fire
  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const c = Math.floor((e.clientX - rect.left) / cellSize);
    const r = Math.floor((e.clientY - rect.top) / cellSize);
    if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
      simulateFireSpread(r, c, 5);
      renderMap();
    }
  });

  // --- Charts (Chart.js) ---
  let miniBiomassChart = null;
  let speciesChart = null;
  let compositionPie = null;
  let disturbanceBreakdown = null;

  function initCharts() {
    const ctxMini = document.getElementById('miniBiomassChart').getContext('2d');
    if (miniBiomassChart) miniBiomassChart.destroy();
    miniBiomassChart = new Chart(ctxMini, {
      type: 'line',
      data: {
        labels: historyYears,
        datasets: [{
          label: 'Biomass (g/m²)',
          data: historyBiomass,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } },
          y: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } }
        }
      }
    });

    // Species Abundance chart
    const ctxSpec = document.getElementById('speciesAbundanceChart')?.getContext('2d');
    if (ctxSpec) {
      if (speciesChart) speciesChart.destroy();
      speciesChart = new Chart(ctxSpec, {
        type: 'line',
        data: {
          labels: historyYears,
          datasets: SPECIES.map((s, i) => ({
            label: s.name.split(' ')[0],
            data: [3000 + i * 1500],
            borderColor: s.color,
            borderWidth: 2,
            tension: 0.3
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#f0f6fc' } } },
          scales: {
            x: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } },
            y: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } }
          }
        }
      });
    }
  }

  function updateCharts() {
    if (miniBiomassChart) {
      miniBiomassChart.data.labels = historyYears;
      miniBiomassChart.data.datasets[0].data = historyBiomass;
      miniBiomassChart.update('none');
    }
  }

  function updateTelemetry() {
    document.getElementById('current-year-display').textContent = `Year ${currentYear}`;
  }

  // --- Controls & Listeners ---
  const btnPlay = document.getElementById('btn-play');
  btnPlay.addEventListener('click', () => {
    isRunning = !isRunning;
    if (isRunning) {
      btnPlay.innerHTML = '<i data-lucide="pause"></i> <span>Pause</span>';
      btnPlay.classList.replace('btn-primary', 'btn-danger');
      simTimer = setInterval(stepYear, simSpeed);
    } else {
      btnPlay.innerHTML = '<i data-lucide="play"></i> <span>Run Simulation</span>';
      btnPlay.classList.replace('btn-danger', 'btn-primary');
      clearInterval(simTimer);
    }
    if (window.lucide) lucide.createIcons();
  });

  document.getElementById('btn-step').addEventListener('click', stepYear);
  document.getElementById('btn-step5').addEventListener('click', () => {
    for (let i = 0; i < 5; i++) stepYear();
  });
  document.getElementById('btn-reset').addEventListener('click', () => {
    if (isRunning) btnPlay.click();
    initLandscape();
    addLog('Simulation reset to Year 0.', 'info');
  });

  document.getElementById('sim-speed').addEventListener('input', (e) => {
    simSpeed = 1600 - parseInt(e.target.value);
    document.getElementById('speed-label').textContent = simSpeed < 400 ? 'Fast' : (simSpeed > 800 ? 'Slow' : 'Normal');
    if (isRunning) {
      clearInterval(simTimer);
      simTimer = setInterval(stepYear, simSpeed);
    }
  });

  viewSelector.addEventListener('change', renderMap);

  // Disturbance Trigger Buttons
  document.getElementById('trigger-fire').addEventListener('click', () => simulateFireSpread(Math.floor(Math.random() * 50), Math.floor(Math.random() * 50), 6));
  document.getElementById('trigger-bda').addEventListener('click', triggerBDA);
  document.getElementById('trigger-harvest').addEventListener('click', triggerHarvest);
  document.getElementById('trigger-wind').addEventListener('click', triggerWind);

  // Tab Navigation
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const tabId = `tab-${btn.getAttribute('data-tab')}`;
      const panel = document.getElementById(tabId);
      if (panel) panel.classList.add('active');
    });
  });

  // Scenario file viewer
  const fileItems = document.querySelectorAll('.file-item');
  const fileContents = {
    'scenario.txt': `LandisData  "Scenario"\n\nDuration            100\nSpecies             species.txt\nEcoregions          ecoregions.txt\nEcoregionsMap       ecoregions.gis\nCellLength          100  << 100 meters (1 ha/cell)\n\n<< Succession Extension\nSuccession          "Biomass Succession"    biomass-succession.txt\n\n<< Disturbance Extensions\nDisturbancesRandomOrder  yes\nDisturbance         "Dynamic Fire System"   dynamic-fire.txt\nDisturbance         "Base Harvest"          harvest.txt\nDisturbance         "Biomass BDA"           bda.txt\n\n<< Output Extensions\nOutput              "Output Biomass"        output-biomass.txt`,
    'species.txt': `LandisData  "Species"\n\n>> Name   Longevity  Maturity  ShadeTol  FireTol  EffectiveSeedDist  MaxSeedDist  VegReprodProb\n>> ----------------------------------------------------------------------------------------\npipo     400        20        1         5        100                3000         0.0\npsme     500        25        3         4        150                2500         0.0\npila     450        30        2         3        80                 2000         0.0\nabco     300        20        4         2        100                1500         0.0\npotr     150        10        1         1        500                8000         0.9\nquke     350        25        2         4        50                 500          0.8`,
    'ecoregions.txt': `LandisData  "Ecoregions"\n\n>> MapCode  Name                  Description\n>> -------------------------------------------------\n   1        LowerMontanePine      Dry foothill pine forest (1200-1800m)\n   2        MixedConifer          Productive mid-elevation mixed conifer\n   3        UpperMontaneFir       Red & white fir zone (2200-2600m)\n   4        SubalpineRidge        Subalpine lodgepole/whitebark pine`,
    'biomass-succession.txt': `LandisData  "Biomass Succession"\n\nTimestep            1\nSeedingAlgorithm    WardSeedDispersal\n\nDynamicInputFile    biomass-dynamic-inputs.txt\nAgeOnlyMortality    species-age-mortality.txt\n\nLightEstablishmentTable\n>> ShadeClass   Pipo    Psme    Pila    Abco    Potr    Quke\n   1            0.8     0.4     0.6     0.1     0.9     0.7\n   2            0.6     0.7     0.7     0.3     0.4     0.5\n   3            0.3     0.8     0.5     0.6     0.1     0.2\n   4            0.1     0.5     0.3     0.9     0.0     0.1\n   5            0.0     0.2     0.1     0.8     0.0     0.0`,
    'dynamic-fire.txt': `LandisData  "Dynamic Fire System"\n\nTimestep                1\nFuelModel               FineCoarseWoodyDebris\nIgnitionProbabilityMap  ignition_prob.gis\nSpreadProbabilityMap    spread_prob.gis\nMaxFireSize             4000  << ha`
  };

  fileItems.forEach(item => {
    item.addEventListener('click', () => {
      fileItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      const filename = item.getAttribute('data-file');
      document.getElementById('active-file-name').textContent = filename;
      document.getElementById('file-viewer-content').textContent = fileContents[filename] || '// File content placeholder';
    });
  });

  // Start initialization
  initLandscape();
});
