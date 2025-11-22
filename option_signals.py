#!/usr/bin/env python3
# option_signals.py
# Fixed and cleaned version of your Advanced NSE Option Signals script

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time as time_module
import json
import os
import math

PRINT_PREFIX = "🛰️"

class AdvancedOptionSignalGenerator:
    def __init__(self):
        self.symbols = [
            "NIFTY", "BANKNIFTY",
            "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
            "KOTAKBANK", "HDFC", "BHARTIARTL", "ITC", "SBIN"
        ]

    def _session(self):
        """Return a requests session primed for NSE."""
        s = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        s.headers.update(headers)
        # Try a warm request to the homepage (best-effort)
        try:
            s.get("https://www.nseindia.com", timeout=5)
        except Exception:
            pass
        return s

    def fetch_option_chain(self, symbol):
        """Fetch option chain JSON from NSE for symbol."""
        try:
            session = self._session()
            if symbol in ['NIFTY', 'BANKNIFTY']:
                url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            else:
                url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

            r = session.get(url, timeout=12)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"{PRINT_PREFIX} ❌ Failed to fetch {symbol}: HTTP {r.status_code}")
                return None
        except Exception as e:
            print(f"{PRINT_PREFIX} ❌ Error fetching {symbol}: {e}")
            return None

    def analyze_atm_strikes(self, data, symbol):
        """Return dict with ATM +/-5 strike data and metadata."""
        if not data or 'records' not in data:
            return None

        records = data.get('records', {})
        current_price = records.get('underlyingValue', None)
        expiry_dates = records.get('expiryDates', []) or []

        if current_price is None or not expiry_dates:
            return None

        # pick nearest expiry (first non-past if possible)
        today = datetime.now().date()
        parsed = []
        for d in expiry_dates:
            try:
                parsed_dt = datetime.strptime(d, "%d-%b-%Y").date()
                parsed.append(parsed_dt)
            except Exception:
                continue
        parsed = sorted(parsed)
        expiry_dt = next((dt for dt in parsed if dt >= today), parsed[0] if parsed else None)
        if expiry_dt:
            current_expiry = expiry_dt.strftime("%d-%b-%Y")
        else:
            current_expiry = expiry_dates[0]

        option_rows = [item for item in records.get('data', []) if item.get('expiryDate') == current_expiry]
        if not option_rows:
            return None

        # Build strike list and find nearest (ATM)
        strikes = sorted({int(item.get('strikePrice', 0)) for item in option_rows})
        if not strikes:
            return None

        # nearest strike
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))
        # pick ±5 strikes around ATM
        try:
            atm_index = strikes.index(atm_strike)
        except ValueError:
            atm_index = 0
        start_idx = max(0, atm_index - 5)
        end_idx = min(len(strikes), atm_index + 6)
        relevant_strikes = strikes[start_idx:end_idx]

        # filter rows for relevant strikes
        relevant_rows = [r for r in option_rows if int(r.get('strikePrice', 0)) in relevant_strikes]

        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'atm_strike': int(atm_strike),
            'expiry': current_expiry,
            'strikes_analyzed': relevant_strikes,
            'data': relevant_rows,
            'all_data': option_rows
        }

    def calculate_pcr(self, data_rows):
        """Compute PCR based on aggregated OI and volume."""
        total_ce_oi = total_pe_oi = 0
        total_ce_vol = total_pe_vol = 0

        for r in data_rows:
            ce = r.get('CE')
            pe = r.get('PE')
            if ce:
                total_ce_oi += int(ce.get('openInterest', 0))
                total_ce_vol += int(ce.get('totalTradedVolume', 0) or 0)
            if pe:
                total_pe_oi += int(pe.get('openInterest', 0))
                total_pe_vol += int(pe.get('totalTradedVolume', 0) or 0)

        pcr_oi = (total_pe_oi / total_ce_oi) if total_ce_oi > 0 else 0.0
        pcr_vol = (total_pe_vol / total_ce_vol) if total_ce_vol > 0 else 0.0
        return round(pcr_oi, 2), round(pcr_vol, 2)

    def select_optimal_strike(self, analysis_data, option_type):
        """Select strike from ATM window using multi-parameter scoring."""
        if not analysis_data:
            return None

        current_price = analysis_data['current_price']
        atm = analysis_data['atm_strike']
        rows = analysis_data['data']
        strikes_list = analysis_data['strikes_analyzed']

        candidates = []
        for r in rows:
            strike = int(r.get('strikePrice', 0))
            try:
                strike_idx = strikes_list.index(strike)
                atm_idx = strikes_list.index(atm)
            except ValueError:
                continue
            dist = abs(strike_idx - atm_idx)

            if option_type == 'CE':
                side = r.get('CE')
                if not side:
                    continue
                # consider ATM or OTM CE (strike >= current_price)
                if strike < math.floor(current_price):
                    continue
            else:
                side = r.get('PE')
                if not side:
                    continue
                # consider ATM or OTM PE (strike <= current_price)
                if strike > math.ceil(current_price):
                    continue

            oi = int(side.get('openInterest', 0) or 0)
            coi = int(side.get('changeinOpenInterest', 0) or 0)
            vol = int(side.get('totalTradedVolume', 0) or 0)
            iv = float(side.get('impliedVolatility', 0) or 0)
            ltp = float(side.get('lastPrice', 0) or 0)
            change = float(side.get('change', 0) or 0)
            pchg = float(side.get('pChange', 0) or 0)
            delta = side.get('delta', 0)
            gamma = side.get('gamma', 0)

            candidates.append({
                'strike': strike,
                'distance_from_atm': dist,
                'is_atm': strike == atm,
                'is_near_atm': dist <= 1,
                'oi': oi,
                'coi': coi,
                'volume': vol,
                'iv': iv,
                'ltp': ltp,
                'change': change,
                'change_percentage': pchg,
                'delta': delta,
                'gamma': gamma
            })

        if not candidates:
            return None

        # scoring
        for c in candidates:
            score = 0.0
            # proximity strong weight
            if c['is_atm']:
                score += 60.0
            elif c['is_near_atm']:
                score += 50.0
            else:
                score += max(0.0, 40.0 - (c['distance_from_atm'] * 5.0))
            # OI/COI
            score += min(c['oi'] / 10000.0, 5.0) * 2.0
            score += (c['coi'] / 500.0) if c['coi'] else 0.0
            # volume
            score += min(c['volume'] / 1000.0, 3.0)
            # iv (lower preferred)
            score += max(0.0, 5.0 - (c['iv'] / 5.0)) if c['iv'] is not None else 0.0
            # momentum
            if c['change_percentage'] > 0:
                score += 2.0
            c['score'] = round(score, 2)
            # selection reason
            c['selection_reason'] = self.get_selection_reason(c)

        # prefer high score then volume
        candidates.sort(key=lambda x: (x['score'], x['volume']), reverse=True)
        return candidates[0]

    def get_selection_reason(self, candidate):
        """Translate candidate metrics into human-readable reasons."""
        reasons = []
        if candidate.get('is_atm'):
            reasons.append("ATM Strike")
        elif candidate.get('is_near_atm'):
            reasons.append("Near-ATM")
        else:
            reasons.append(f"{candidate.get('distance_from_atm')} steps from ATM")
        coi = candidate.get('coi', 0)
        if coi > 0:
            reasons.append("Fresh Long Buildup")
        elif coi < 0:
            reasons.append("Long Unwinding")
        if candidate.get('volume', 0) > 1000:
            reasons.append("High Volume")
        iv = candidate.get('iv') or 0
        if iv and iv < 20:
            reasons.append("Low IV")
        return " | ".join(reasons)

    def generate_advanced_signal(self, analysis_data):
        """Combine the metrics into final trading signal and pick strike."""
        if not analysis_data:
            return None

        sym = analysis_data['symbol']
        current_price = analysis_data['current_price']

        pcr_oi, pcr_vol = self.calculate_pcr(analysis_data['all_data'])

        total_ce_oi = sum(int(r.get('CE', {}).get('openInterest', 0) or 0) for r in analysis_data['data'])
        total_pe_oi = sum(int(r.get('PE', {}).get('openInterest', 0) or 0) for r in analysis_data['data'])
        oi_ratio = (total_pe_oi / total_ce_oi) if total_ce_oi > 0 else 0.0

        bullish = 0
        bearish = 0

        # interpret PCR: higher => relatively more put-interest
        if pcr_oi > 1.5:
            bullish += 2
        elif pcr_oi > 1.2:
            bullish += 1
        if pcr_oi < 0.6:
            bearish += 2
        elif pcr_oi < 0.8:
            bearish += 1
        # OI ratio
        if oi_ratio > 1.3:
            bullish += 1
        elif oi_ratio < 0.7:
            bearish += 1

        # build signal
        signal = None
        option_type = None
        strike_choice = None
        reason = ""

        if bullish >= 3:
            signal = "STRONG BUY"; option_type = "CE"
            strike_choice = self.select_optimal_strike(analysis_data, "CE")
            reason = f"Strong Bullish: PCR({pcr_oi}), OI_Ratio({oi_ratio:.2f})"
        elif bullish >= 2:
            signal = "BUY"; option_type = "CE"
            strike_choice = self.select_optimal_strike(analysis_data, "CE")
            reason = f"Bullish: PCR({pcr_oi}), OI_Ratio({oi_ratio:.2f})"
        elif bearish >= 3:
            signal = "STRONG SELL"; option_type = "PE"
            strike_choice = self.select_optimal_strike(analysis_data, "PE")
            reason = f"Strong Bearish: PCR({pcr_oi}), OI_Ratio({oi_ratio:.2f})"
        elif bearish >= 2:
            signal = "SELL"; option_type = "PE"
            strike_choice = self.select_optimal_strike(analysis_data, "PE")
            reason = f"Bearish: PCR({pcr_oi}), OI_Ratio({oi_ratio:.2f})"

        if not signal or not strike_choice:
            return None

        return {
            'symbol': sym,
            'signal': signal,
            'option_type': option_type,
            'strike_price': strike_choice['strike'],
            'current_price': current_price,
            'atm_strike': analysis_data['atm_strike'],
            'distance_from_atm': strike_choice['distance_from_atm'],
            'option_ltp': strike_choice['ltp'],
            'option_change': strike_choice['change'],
            'option_change_percentage': strike_choice['change_percentage'],
            'oi': strike_choice['oi'],
            'coi': strike_choice['coi'],
            'volume': strike_choice['volume'],
            'iv': strike_choice['iv'],
            'delta': strike_choice.get('delta', 0),
            'gamma': strike_choice.get('gamma', 0),
            'pcr_oi': pcr_oi,
            'pcr_volume': pcr_vol,
            'oi_ratio': round(oi_ratio, 2),
            'strike_score': strike_choice['score'],
            'selection_reason': strike_choice['selection_reason'],
            'signal_reason': reason,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def run_complete_analysis(self):
        """Main loop: fetch, analyze and return signals + market overview."""
        print(f"{PRINT_PREFIX} 🎯 RUNNING COMPLETE OPTION CHAIN ANALYSIS...")
        all_signals = []
        market_data = []

        for sym in self.symbols:
            print(f"{PRINT_PREFIX} 🔍 Analyzing {sym} ...")
            data = self.fetch_option_chain(sym)
            if not data:
                print(f"{PRINT_PREFIX} ❌ No data for {sym}")
                time_module.sleep(1)
                continue

            analysis = self.analyze_atm_strikes(data, sym)
            if not analysis:
                print(f"{PRINT_PREFIX} ❌ No ATM analysis for {sym}")
                time_module.sleep(1)
                continue

            print(f"{PRINT_PREFIX}   ATM {analysis['atm_strike']}, Range {analysis['strikes_analyzed'][0]} - {analysis['strikes_analyzed'][-1]}")
            signal = self.generate_advanced_signal(analysis)
            if signal:
                all_signals.append(signal)
                print(f"{PRINT_PREFIX}   ✅ {signal['signal']} {signal['option_type']} {signal['strike_price']}")
                print(f"{PRINT_PREFIX}      Reason: {signal['selection_reason']}")
            else:
                print(f"{PRINT_PREFIX}   ⏸ No strong signal for {sym}")

            # market overview entry
            market_data.append({
                'symbol': sym,
                'current_price': analysis['current_price'],
                'atm_strike': analysis['atm_strike'],
                'strikes_analyzed': len(analysis['strikes_analyzed']),
                'pcr_oi': None,
                'pcr_volume': None,
                'oi_ratio': None,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            time_module.sleep(1)

        print(f"{PRINT_PREFIX} 📊 Analysis complete, {len(all_signals)} signals found")
        return all_signals, market_data


# -------------------------
# Dashboard & main runner
# -------------------------
def generate_advanced_dashboard(signals, market_data, out_path="docs/index.html"):
    """Generate a simple HTML dashboard and save to docs/index.html"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Advanced NSE Option Signals</title>
    <style>
      body{{font-family:Arial,Helvetica,sans-serif;background:#f5f7fa;color:#111;padding:16px}}
      .card{{background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.08);margin-bottom:12px}}
      table{{width:100%;border-collapse:collapse}}
      th,td{{padding:8px;border-bottom:1px solid #eee;text-align:left}}
      th{{background:#fafafa}}
    </style>
    </head><body>
    <h1>Advanced NSE Option Signals</h1>
    <p>Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    """

    if signals:
        html += "<h2>Signals</h2><table><thead><tr><th>Symbol</th><th>Signal</th><th>Opt</th><th>Strike</th><th>ATM</th><th>LTP</th><th>OI</th><th>COI</th><th>IV</th><th>Score</th></tr></thead><tbody>"
        for s in signals:
            html += f"<tr><td>{s['symbol']}</td><td>{s['signal']}</td><td>{s['option_type']}</td><td>{s['strike_price']}</td><td>{s['atm_strike']}</td><td>{s['option_ltp']}</td><td>{s['oi']}</td><td>{s['coi']}</td><td>{s['iv']}</td><td>{s['strike_score']}</td></tr>"
        html += "</tbody></table>"
    else:
        html += "<div class='card'><strong>No strong signals detected</strong></div>"

    if market_data:
        html += "<h2>Market Overview</h2><table><thead><tr><th>Symbol</th><th>Price</th><th>ATM</th><th>Strikes</th><th>Updated</th></tr></thead><tbody>"
        for m in market_data:
            html += f"<tr><td>{m['symbol']}</td><td>{m['current_price']}</td><td>{m['atm_strike']}</td><td>{m['strikes_analyzed']}</td><td>{m['timestamp']}</td></tr>"
        html += "</tbody></table>"

    html += "</body></html>"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{PRINT_PREFIX} ✅ Dashboard written to {out_path}")


def main():
    print(f"{PRINT_PREFIX} Starting analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    gen = AdvancedOptionSignalGenerator()
    signals, market_data = gen.run_complete_analysis()

    # Save CSVs
    os.makedirs("output", exist_ok=True)
    if signals:
        pd.DataFrame(signals).to_csv("output/option_signals.csv", index=False)
        print(f"{PRINT_PREFIX} ✅ Signals saved: output/option_signals.csv")
    else:
        pd.DataFrame(columns=[
            'symbol','signal','option_type','strike_price','current_price','atm_strike',
            'distance_from_atm','option_ltp','option_change','option_change_percentage',
            'oi','coi','volume','iv','delta','gamma','pcr_oi','pcr_volume',
            'oi_ratio','strike_score','selection_reason','signal_reason','timestamp'
        ]).to_csv("output/option_signals.csv", index=False)
        print(f"{PRINT_PREFIX} ℹ️ No signals -> empty CSV written")

    if market_data:
        pd.DataFrame(market_data).to_csv("output/detailed_option_data.csv", index=False)
        print(f"{PRINT_PREFIX} ✅ Market data saved: output/detailed_option_data.csv")

    # Write docs/index.html for GitHub Pages
    generate_advanced_dashboard(signals, market_data, out_path="docs/index.html")
    print(f"{PRINT_PREFIX} Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
            
