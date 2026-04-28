#!/usr/bin/env python3
"""
performance_benchmark.py - Performance Benchmark for Free Data Sources

Tests the speed and reliability of free data sources used in Fincept Terminal.
Helps identify bottlenecks and optimize configuration.

Usage:
    python performance_benchmark.py                    # Run all benchmarks
    python performance_benchmark.py --source yahoo     # Test specific source
    python performance_benchmark.py --quick            # Quick test (1 request each)
    python performance_benchmark.py --output results.json  # Save results

Requirements:
    pip install requests yfinance pandas akshare
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


try:
    import yfinance as yf
    import pandas as pd
    import requests
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install requests yfinance pandas")
    sys.exit(1)


class PerformanceBenchmark:
    """Benchmark free data sources performance"""
    
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FinceptTerminal/1.0 Performance Benchmark"
        })
    
    def benchmark_source(self, name: str, test_func, iterations: int = 5) -> Dict[str, Any]:
        """
        Benchmark a single data source
        
        Args:
            name: Source name
            test_func: Function that performs the test
            iterations: Number of test iterations
            
        Returns:
            Dictionary with benchmark results
        """
        print(f"\n🔍 Testing {name}...")
        
        latencies = []
        successes = 0
        failures = 0
        errors = []
        
        for i in range(iterations):
            try:
                start_time = time.time()
                result = test_func()
                elapsed = time.time() - start_time
                
                if result:
                    latencies.append(elapsed)
                    successes += 1
                    print(f"  Iteration {i+1}/{iterations}: ✅ {elapsed:.3f}s")
                else:
                    failures += 1
                    errors.append("No data returned")
                    print(f"  Iteration {i+1}/{iterations}: ❌ No data")
                    
            except Exception as e:
                failures += 1
                error_msg = str(e)
                errors.append(error_msg)
                print(f"  Iteration {i+1}/{iterations}: ❌ Error: {error_msg[:80]}")
            
            # Small delay between iterations
            if i < iterations - 1:
                time.sleep(1)
        
        # Calculate statistics
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = sorted(latencies)[len(latencies) // 2]
        else:
            avg_latency = min_latency = max_latency = median_latency = 0
        
        success_rate = (successes / iterations * 100) if iterations > 0 else 0
        
        result = {
            "source": name,
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
            "successes": successes,
            "failures": failures,
            "success_rate_pct": round(success_rate, 2),
            "latency_stats": {
                "avg_seconds": round(avg_latency, 3),
                "min_seconds": round(min_latency, 3),
                "max_seconds": round(max_latency, 3),
                "median_seconds": round(median_latency, 3),
            },
            "errors": errors[:5],  # Store first 5 errors
        }
        
        print(f"  Summary: {successes}/{iterations} successful, avg={avg_latency:.3f}s")
        
        return result
    
    def test_yahoo_finance(self) -> bool:
        """Test Yahoo Finance API"""
        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            return info is not None and "symbol" in info
        except Exception:
            return False
    
    def test_fred_api(self) -> bool:
        """Test FRED API (no key needed for some endpoints)"""
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "GDP",
                "api_key": "demo",  # Demo key has limited access
                "file_type": "json",
                "limit": 1
            }
            response = self.session.get(url, params=params, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_world_bank(self) -> bool:
        """Test World Bank Open Data API"""
        try:
            url = "http://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.CD"
            params = {"format": "json", "per_page": 1}
            response = self.session.get(url, params=params, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_imf_api(self) -> bool:
        """Test IMF API"""
        try:
            url = "https://sdmxcentral.imf.org/ws/public/sdmxapi/rest/dataflow/IMF/ECOFIN_DFD/latest"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_oecd_api(self) -> bool:
        """Test OECD Statistics API"""
        try:
            url = "https://stats.oecd.org/SDMXJSVNEXT03/GetGenericData/?datasetCode=QNA"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_ecb_api(self) -> bool:
        """Test ECB Statistical Data Warehouse"""
        try:
            url = "https://data-api.ecb.europa.eu/service/dataflow/ECB/ECB_EXR1/latest"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_bis_api(self) -> bool:
        """Test BIS Statistics"""
        try:
            url = "https://stats.bis.org/api/v1/dataflow/BIS/WS_DER/latest"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_akshare(self) -> bool:
        """Test AKShare (China market data)"""
        try:
            import akshare as ak
            stock_df = ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="")
            return stock_df is not None and len(stock_df) > 0
        except Exception:
            return False
    
    def test_coingecko(self) -> bool:
        """Test CoinGecko API (no key needed)"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "bitcoin", "vs_currencies": "usd"}
            response = self.session.get(url, params=params, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def run_all_benchmarks(self, iterations: int = 5, quick: bool = False):
        """Run benchmarks for all data sources"""
        if quick:
            iterations = 1
        
        print("="*70)
        print("  FINCEPT TERMINAL - FREE DATA SOURCES PERFORMANCE BENCHMARK")
        print("="*70)
        print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Iterations per source: {iterations}")
        print("\nStarting benchmarks...\n")
        
        tests = [
            ("Yahoo Finance", self.test_yahoo_finance),
            ("FRED (Demo)", self.test_fred_api),
            ("World Bank", self.test_world_bank),
            ("IMF", self.test_imf_api),
            ("OECD", self.test_oecd_api),
            ("ECB", self.test_ecb_api),
            ("BIS", self.test_bis_api),
            ("CoinGecko", self.test_coingecko),
        ]
        
        # Add AKShare if available
        try:
            import akshare
            tests.append(("AKShare", self.test_akshare))
        except ImportError:
            print("⚠️  AKShare not installed, skipping...")
        
        # Run tests sequentially to avoid rate limiting
        for name, test_func in tests:
            result = self.benchmark_source(name, test_func, iterations)
            self.results[name] = result
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*70)
        print("  BENCHMARK SUMMARY")
        print("="*70)
        
        print(f"\n{'Source':<20} {'Success Rate':<15} {'Avg Latency':<15} {'Status'}")
        print("-"*70)
        
        for name, result in self.results.items():
            success_rate = result["success_rate_pct"]
            avg_latency = result["latency_stats"]["avg_seconds"]
            
            if success_rate >= 80:
                status = "✅ GOOD"
            elif success_rate >= 50:
                status = "⚠️  FAIR"
            else:
                status = "❌ POOR"
            
            print(f"{name:<20} {success_rate:>6.1f}%      {avg_latency:>8.3f}s    {status}")
        
        print("\n" + "="*70)
        print("  RECOMMENDATIONS")
        print("="*70)
        
        # Find best and worst performers
        best = max(self.results.items(), key=lambda x: x[1]["success_rate_pct"])
        worst = min(self.results.items(), key=lambda x: x[1]["success_rate_pct"])
        
        print(f"\n✅ Best performer: {best[0]} ({best[1]['success_rate_pct']:.1f}% success)")
        print(f"❌ Worst performer: {worst[0]} ({worst[1]['success_rate_pct']:.1f}% success)")
        
        print("\n💡 Tips:")
        print("  • Use multiple sources for redundancy")
        print("  • Enable caching to reduce API calls")
        print("  • Monitor rate limits in production")
        print("  • Consider paid alternatives for critical data\n")


def main():
    parser = argparse.ArgumentParser(description="Performance Benchmark for Free Data Sources")
    parser.add_argument("--source", help="Test specific source only")
    parser.add_argument("--iterations", type=int, default=5, help="Number of test iterations (default: 5)")
    parser.add_argument("--quick", action="store_true", help="Quick test (1 iteration)")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    
    if args.source:
        # Test specific source
        print(f"Testing {args.source}...")
        # Implementation for single source test would go here
        print("Single source test not yet implemented. Run without --source for full benchmark.")
    else:
        # Run all benchmarks
        benchmark.run_all_benchmarks(iterations=args.iterations, quick=args.quick)
    
    # Save results if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(benchmark.results, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")


if __name__ == "__main__":
    main()
