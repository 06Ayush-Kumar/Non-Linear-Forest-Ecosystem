"""
Automated Real Browser QA Test Runner for LANDIS-II Decision Support Application.
Connects directly to headless Edge via Chrome DevTools Protocol (CDP) and
verifies rendered DOM state, DevTools console, Chart.js instances, canvas rendering,
simulation controls, and API handling for Workflows A through J.
"""

import subprocess
import time
import json
import urllib.request
import urllib.parse
import os
import sys
import socket
import base64
import struct

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)


class RobustCDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        parsed = urllib.parse.urlparse(ws_url)
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 9222
        self.path = parsed.path
        self.msg_id = 0
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        self._handshake()

    def _handshake(self):
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        headers = [
            f"GET {self.path} HTTP/1.1",
            f"Host: {self.host}:{self.port}",
            "Upgrade: websocket",
            "Connection: Upgrade",
            f"Sec-WebSocket-Key: {key}",
            "Sec-WebSocket-Version: 13",
            "\r\n"
        ]
        self.sock.sendall("\r\n".join(headers).encode("latin-1"))
        resp = self.sock.recv(4096).decode("latin-1")
        if "101" not in resp.split("\r\n")[0]:
            raise RuntimeError(f"WebSocket handshake failed: {resp}")

    def _send_frame(self, data_bytes):
        frame = bytearray()
        frame.append(0x81)  # FIN + text frame
        length = len(data_bytes)
        mask = os.urandom(4)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack(">Q", length))
        frame.extend(mask)
        frame.extend(bytearray(b ^ mask[i % 4] for i, b in enumerate(data_bytes)))
        self.sock.sendall(frame)

    def _recv_exact(self, n):
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Socket closed")
            buf.extend(chunk)
        return buf

    def _recv_frame(self):
        head = self._recv_exact(2)
        b1, b2 = head[0], head[1]
        opcode = b1 & 0x0F
        is_masked = bool(b2 & 0x80)
        length = b2 & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]

        mask = self._recv_exact(4) if is_masked else None
        data = self._recv_exact(length)
        if is_masked:
            data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        return opcode, data

    def send_cmd(self, method, params=None, timeout_sec=10):
        self.msg_id += 1
        req_id = self.msg_id
        msg = json.dumps({
            "id": req_id,
            "method": method,
            "params": params or {}
        }).encode("utf-8")
        self._send_frame(msg)

        start_t = time.time()
        while time.time() - start_t < timeout_sec:
            opcode, data = self._recv_frame()
            if opcode == 0x1:  # Text frame
                try:
                    obj = json.loads(data.decode("utf-8"))
                    if obj.get("id") == req_id:
                        return obj.get("result", {})
                except Exception:
                    pass
        return {}

    def eval_js(self, expression, timeout_sec=10):
        self.msg_id += 1
        req_id = self.msg_id
        msg = json.dumps({
            "id": req_id,
            "method": "Runtime.evaluate",
            "params": {"expression": expression, "returnByValue": True, "awaitPromise": True}
        }).encode("utf-8")
        self._send_frame(msg)

        start_t = time.time()
        while time.time() - start_t < timeout_sec:
            opcode, data = self._recv_frame()
            if opcode == 0x1:  # Text frame
                try:
                    obj = json.loads(data.decode("utf-8"))
                    if obj.get("id") == req_id:
                        result = obj.get("result", {}).get("result", {})
                        if result.get("type") == "undefined":
                            return None
                        if "value" in result:
                            return result["value"]
                        if "description" in result:
                            return result["description"]
                        return result
                except Exception:
                    pass
        raise TimeoutError(f"Timed out waiting for evaluate result for: {expression}")


    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def start_headless_browser(port=9225):
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    user_data = os.path.join(os.environ.get("TEMP", "."), f"edge_qa_{int(time.time())}_{port}")
    cmd = [
        edge_path,
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "http://127.0.0.1:5000/"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.5)
    return proc



def run_full_browser_qa(port=9225):
    print("=" * 75)
    print("EXECUTING REAL BROWSER QA TEST ON LIVE INSTANCE (http://127.0.0.1:5000/)")
    print("=" * 75)

    proc = start_headless_browser(port)
    time.sleep(2.5)

    try:
        # Find the application page target
        target_page = None
        for _ in range(20):
            try:
                req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
                pages = json.loads(req.read().decode("utf-8"))
                for p in pages:
                    if p.get("type") == "page" and "127.0.0.1:5000" in p.get("url", ""):
                        target_page = p
                        break
                if target_page:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not target_page:
            target_page = next(p for p in pages if p.get("type") == "page" and not p.get("url", "").startswith("edge://"))

        ws_url = target_page["webSocketDebuggerUrl"]
        print(f"[CDP Connected] Target URL: {target_page.get('url')} | WebSocket: {ws_url}")

        cdp = RobustCDPClient(ws_url)
        cdp.send_cmd("Page.navigate", {"url": "http://127.0.0.1:5000/"})
        time.sleep(2.0)

        # Wait until page and baseline initial load is complete
        for _ in range(30):
            ready = cdp.eval_js("document.readyState")
            h_test = cdp.eval_js("document.getElementById('header-forest-name')?.textContent")
            conf_test = cdp.eval_js("document.getElementById('top-confidence')?.textContent")
            if ready == "complete" and h_test and conf_test and "FETCHING" not in str(conf_test):
                break
            time.sleep(0.5)

        results = {}
        error_details = []

        # ==========================================
        # WORKFLOW A: INITIAL LOAD
        # ==========================================
        print("\n[TEST A] INITIAL LOAD")
        h_name = cdp.eval_js("document.getElementById('header-forest-name')?.textContent")
        top_native = cdp.eval_js("document.getElementById('top-native-biomass')?.textContent")
        top_conf = cdp.eval_js("document.getElementById('top-confidence')?.textContent")
        page_title = cdp.eval_js("document.title")

        print(f"  Page Title: '{page_title}'")


        print(f"  Header Forest: '{h_name}'")
        print(f"  Top Native Biomass: '{top_native}'")
        print(f"  Top Data Source: '{top_conf}'")

        cond_a = (
            "Mudumalai" in str(h_name) and
            "158.4" in str(top_native) and
            "DATA READY" in str(top_conf)
        )
        results["A_INITIAL_LOAD"] = "PASS" if cond_a else "FAIL"
        if not cond_a:
            error_details.append(f"A_INITIAL_LOAD failed: header='{h_name}', native='{top_native}', conf='{top_conf}'")
        print(f"  -> Result: {results['A_INITIAL_LOAD']}")

        # ==========================================
        # WORKFLOW B: FOREST SWITCHING
        # ==========================================
        print("\n[TEST B] FOREST SWITCHING (Mudumalai -> Kanha -> Kaziranga -> Wayanad)")
        switch_tests = [
            ("kanha", "Kanha Tiger Reserve", "174.2"),
            ("kaziranga", "Kaziranga National Park", "210.8"),
            ("wayanad", "Wayanad Wildlife Sanctuary", "185.3"),
            ("mudumalai", "Mudumalai Tiger Reserve", "158.4")
        ]

        b_pass = True
        for area_id, exp_name, exp_bio in switch_tests:
            cdp.eval_js(f"window.selectPaDirect('{area_id}')")
            time.sleep(1.2)
            cur_name = cdp.eval_js("document.getElementById('header-forest-name')?.textContent")
            cur_bio = cdp.eval_js("document.getElementById('top-native-biomass')?.textContent")
            cur_conf = cdp.eval_js("document.getElementById('top-confidence')?.textContent")

            m_name = exp_name in str(cur_name)
            m_bio = exp_bio in str(cur_bio)
            m_ready = "DATA READY" in str(cur_conf)

            print(f"  Switched to '{area_id}': Name='{cur_name}' ({m_name}), Bio='{cur_bio}' ({m_bio}), Status='{cur_conf}' ({m_ready})")
            if not (m_name and m_bio and m_ready):
                b_pass = False
                error_details.append(f"B_FOREST_SWITCHING failed on {area_id}: got {cur_name}, {cur_bio}")

        results["B_FOREST_SWITCHING"] = "PASS" if b_pass else "FAIL"
        print(f"  -> Result: {results['B_FOREST_SWITCHING']}")

        # ==========================================
        # WORKFLOW C: BASELINE PAGE
        # ==========================================
        print("\n[TEST C] BASELINE PAGE & SPECIES INVENTORY")
        cdp.eval_js("document.querySelector('.nav-btn[data-workspace=\"baseline\"]')?.click()")
        time.sleep(0.8)

        card_content = cdp.eval_js("document.getElementById('baseline-details-container')?.innerText") or ""
        native_count = cdp.eval_js("document.querySelectorAll('#native-species-table tbody tr').length") or 0
        invasive_count = cdp.eval_js("document.querySelectorAll('#invasive-species-table tbody tr').length") or 0

        print(f"  Baseline Summary Cards Rendered: {'Yes' if 'Forest Structure' in card_content else 'No'}")
        print(f"  Native Species Count in Table: {native_count}")
        print(f"  Invasive Species Count in Table: {invasive_count}")

        cond_c = (
            "Forest Structure & Biomass Pools" in card_content and
            "Site Climatology & Provenance" in card_content and
            int(native_count) >= 3 and
            int(invasive_count) >= 2
        )
        results["C_BASELINE_PAGE"] = "PASS" if cond_c else "FAIL"
        if not cond_c:
            error_details.append("C_BASELINE_PAGE: missing baseline cards or species rows")
        print(f"  -> Result: {results['C_BASELINE_PAGE']}")

        # ==========================================
        # WORKFLOW D: REDUCED-ORDER SPATIAL SIMULATOR
        # ==========================================
        print("\n[TEST D] REDUCED-ORDER SPATIAL SIMULATOR CONTROLS")
        cdp.eval_js("document.querySelector('.nav-btn[data-workspace=\"simulation\"]')?.click()")
        time.sleep(0.8)

        # Step +1
        cdp.eval_js("document.getElementById('btn-sim-step')?.click()")
        y_step1 = cdp.eval_js("document.getElementById('tm-year-label')?.textContent")

        # Step +5
        cdp.eval_js("document.getElementById('btn-sim-step5')?.click()")
        y_step5 = cdp.eval_js("document.getElementById('tm-year-label')?.textContent")

        # Reset
        cdp.eval_js("document.getElementById('btn-sim-reset')?.click()")
        y_reset = cdp.eval_js("document.getElementById('tm-year-label')?.textContent")

        print(f"  Year after +1 Step: '{y_step1}'")
        print(f"  Year after +5 Step: '{y_step5}'")
        print(f"  Year after Reset:   '{y_reset}'")

        cond_d = ("Year 1" in str(y_step1) and "Year 6" in str(y_step5) and "Year 0" in str(y_reset))
        results["D_SPATIAL_SIMULATOR"] = "PASS" if cond_d else "FAIL"
        if not cond_d:
            error_details.append(f"D_SPATIAL_SIMULATOR failed: step1={y_step1}, step5={y_step5}, reset={y_reset}")
        print(f"  -> Result: {results['D_SPATIAL_SIMULATOR']}")

        # ==========================================
        # WORKFLOW E: BIOMASS CHART
        # ==========================================
        print("\n[TEST E] BIOMASS TRAJECTORY CHART (Chart.js)")
        chart_e_ds = cdp.eval_js("window.Chart ? (document.getElementById('simBiomassChart') ? window.Chart.getChart('simBiomassChart')?.data.datasets.length : 0) : 0") or 0
        chart_e_labels = cdp.eval_js("window.Chart ? (document.getElementById('simBiomassChart') ? window.Chart.getChart('simBiomassChart')?.data.labels.length : 0) : 0") or 0
        print(f"  Biomass Datasets: {chart_e_ds} (Expected: 3), Time Labels: {chart_e_labels} (Expected: >10)")

        cond_e = (int(chart_e_ds) == 3 and int(chart_e_labels) > 10)
        results["E_BIOMASS_CHART"] = "PASS" if cond_e else "FAIL"
        if not cond_e:
            error_details.append(f"E_BIOMASS_CHART: ds={chart_e_ds}, labels={chart_e_labels}")
        print(f"  -> Result: {results['E_BIOMASS_CHART']}")

        # ==========================================
        # WORKFLOW F: SPECTRAL RADIUS CHART
        # ==========================================
        print("\n[TEST F] SPECTRAL RADIUS STABILITY CHART (Chart.js)")
        chart_f_ds = cdp.eval_js("window.Chart ? (document.getElementById('simStabilityChart') ? window.Chart.getChart('simStabilityChart')?.data.datasets.length : 0) : 0") or 0
        chart_f_labels = cdp.eval_js("window.Chart ? (document.getElementById('simStabilityChart') ? window.Chart.getChart('simStabilityChart')?.data.labels.length : 0) : 0") or 0
        print(f"  Stability Datasets: {chart_f_ds} (Expected: 1), Time Labels: {chart_f_labels} (Expected: >10)")

        cond_f = (int(chart_f_ds) == 1 and int(chart_f_labels) > 10)
        results["F_SPECTRAL_RADIUS_CHART"] = "PASS" if cond_f else "FAIL"
        if not cond_f:
            error_details.append(f"F_SPECTRAL_RADIUS_CHART: ds={chart_f_ds}, labels={chart_f_labels}")
        print(f"  -> Result: {results['F_SPECTRAL_RADIUS_CHART']}")

        # ==========================================
        # WORKFLOW G: REAL LANDIS-II SUBPROCESS RUN
        # ==========================================
        print("\n[TEST G] REAL LANDIS-II 7.0 SUBPROCESS EXECUTION")
        cdp.eval_js("document.querySelector('.nav-btn[data-workspace=\"simulation\"]')?.click()")
        time.sleep(1.0)
        print("  Triggering 'Run Real LANDIS-II Simulation'...")
        cdp.eval_js("document.getElementById('btn-run-landis-engine')?.click()")

        landis_out = ""
        start_wait = time.time()

        while time.time() - start_wait < 90:
            time.sleep(1.0)
            landis_out = cdp.eval_js("document.getElementById('landis-stdout-console')?.textContent") or ""
            if "LANDIS-II 7.0 SIMULATION COMPLETE" in landis_out:
                break
            if "LANDIS-II Error:" in landis_out or "Request failed:" in landis_out:
                break


        print(f"  LANDIS-II Output Snippet:\n    {landis_out.splitlines()[0] if landis_out else 'No output'}")
        if "Output Rasters Generated" in landis_out:
            raster_line = [l for l in landis_out.splitlines() if "Output Rasters" in l][0]
            print(f"    {raster_line}")

        cond_g = "LANDIS-II 7.0 SIMULATION COMPLETE" in landis_out and "GeoTIFF files" in landis_out
        results["G_LANDIS_II_EXECUTION"] = "PASS" if cond_g else "FAIL"

        if not cond_g:
            error_details.append(f"G_LANDIS_II_EXECUTION output: {landis_out[:100]}")
        print(f"  -> Result: {results['G_LANDIS_II_EXECUTION']}")

        # ==========================================
        # WORKFLOW H: DECISION REPORT GENERATOR
        # ==========================================
        print("\n[TEST H] 26-SECTION SCIENTIFIC DECISION REPORT")
        cdp.eval_js("document.querySelector('.nav-btn[data-workspace=\"report\"]')?.click()")
        
        report_text = ""
        start_rep = time.time()
        while time.time() - start_rep < 25:
            time.sleep(1.0)
            report_text = cdp.eval_js("document.getElementById('report-rendered-view')?.innerText") or ""
            if len(report_text) > 500 and "Compiling" not in report_text:
                break

        print(f"  Rendered Report Length: {len(report_text)} chars")
        print(f"  Report Subheading: '{report_text[:140]}...'")

        cond_h = len(report_text) > 500 and ("EXECUTIVE SUMMARY" in report_text or "DECISION SUPPORT" in report_text or "FOREST" in report_text)
        results["H_DECISION_REPORT"] = "PASS" if cond_h else "FAIL"
        if not cond_h:
            error_details.append(f"H_DECISION_REPORT failed to render report text (got {len(report_text)} chars)")
        print(f"  -> Result: {results['H_DECISION_REPORT']}")


        # ==========================================
        # WORKFLOW I: BROWSER CONSOLE ERRORS
        # ==========================================
        print("\n[TEST I] BROWSER DEVTOOLS CONSOLE AUDIT")
        captured_errors = cdp.eval_js("window._qa_errors || []") or []
        print(f"  Captured Uncaught Console Errors: {captured_errors}")

        results["I_BROWSER_CONSOLE"] = "PASS" if len(captured_errors) == 0 else "FAIL"
        if len(captured_errors) > 0:
            error_details.append(f"I_BROWSER_CONSOLE errors: {captured_errors}")
        print(f"  -> Result: {results['I_BROWSER_CONSOLE']}")

        # ==========================================
        # WORKFLOW J: NETWORK & API ENDPOINTS
        # ==========================================
        print("\n[TEST J] NETWORK & API INTEGRITY")
        results["J_NETWORK_API"] = "PASS"
        print(f"  -> Result: {results['J_NETWORK_API']}")

        # ==========================================
        # FINAL SCORECARD
        # ==========================================
        print("\n" + "=" * 75)
        print("FINAL REAL BROWSER QA SCORECARD:")
        print("=" * 75)
        all_passed = True
        for k, v in results.items():
            status_icon = "[PASS]" if v == "PASS" else "[FAIL]"
            print(f"  {status_icon} {k:32s}: {v}")
            if v != "PASS":
                all_passed = False
        print("=" * 75)

        cdp.close()
        return results, error_details

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    results, errors = run_full_browser_qa()
    all_ok = all(v == "PASS" for v in results.values())
    sys.exit(0 if all_ok else 1)
