"""
Free Macro Data Aggregator
Aggregates macroeconomic data from FREE sources only:
- World Bank Open Data API
- IMF Statistics
- FRED (Federal Reserve Economic Data)
- OECD Statistics
- AKShare China Macro
- ECB Statistical Data Warehouse
- BIS Statistics

All endpoints are FREE - no API keys required (except optional FRED key for higher limits)
Returns JSON output for Qt/C++ integration
"""

import sys
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import traceback

# Import free data sources
try:
    from worldbank_data import WorldBankWrapper
except ImportError:
    WorldBankWrapper = None

try:
    from imf_data import IMFDataWrapper
except ImportError:
    IMFDataWrapper = None

try:
    from fred_data import FREDEconomicData
except ImportError:
    FREDEconomicData = None

try:
    from oecd_data import OECDDataWrapper
except ImportError:
    OECDDataWrapper = None

try:
    from akshare_macro import AKShareMacroWrapper
except ImportError:
    AKShareMacroWrapper = None

try:
    from ecb_data import ECBDataWrapper
except ImportError:
    ECBDataWrapper = None

try:
    from bis_data import BISDataWrapper
except ImportError:
    BISDataWrapper = None


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super().default(obj)


class FreeMacroAggregator:
    """Aggregate macro data from multiple FREE sources"""
    
    def __init__(self):
        self.worldbank = WorldBankWrapper() if WorldBankWrapper else None
        self.imf = IMFDataWrapper() if IMFDataWrapper else None
        self.fred = FREDEconomicData() if FREDEconomicData else None
        self.oecd = OECDDataWrapper() if OECDDataWrapper else None
        self.akshare = AKShareMacroWrapper() if AKShareMacroWrapper else None
        self.ecb = ECBDataWrapper() if ECBDataWrapper else None
        self.bis = BISDataWrapper() if BISDataWrapper else None
        
    def get_central_bank_rates(self, country: str = "US") -> Dict[str, Any]:
        """Get central bank policy rates from free sources"""
        result = {
            "success": True,
            "data": {},
            "sources": [],
            "timestamp": int(datetime.now().timestamp())
        }
        
        try:
            # FRED: Federal Funds Rate
            if self.fred and country.upper() == "US":
                fred_data = self.fred.get_federal_funds_rate()
                if fred_data.get("success"):
                    result["data"]["us_fed_funds"] = fred_data["data"]
                    result["sources"].append("FRED")
            
            # ECB: Main Refinancing Rate
            if self.ecb and country.upper() in ["EU", "EUR"]:
                ecb_data = self.ecb.get_main_refinancing_rate()
                if ecb_data.get("success"):
                    result["data"]["ecb_mrr"] = ecb_data["data"]
                    result["sources"].append("ECB")
            
            # World Bank: Policy rates for emerging markets
            if self.worldbank:
                wb_data = self.worldbank.get_interest_rates(country)
                if wb_data.get("success"):
                    result["data"]["worldbank"] = wb_data["data"]
                    result["sources"].append("World Bank")
                    
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
    
    def get_inflation_data(self, country: str = "US") -> Dict[str, Any]:
        """Get inflation data (CPI, PCE) from free sources"""
        result = {
            "success": True,
            "data": {},
            "sources": [],
            "timestamp": int(datetime.now().timestamp())
        }
        
        try:
            # FRED: US CPI
            if self.fred and country.upper() == "US":
                cpi_data = self.fred.get_cpi_data()
                if cpi_data.get("success"):
                    result["data"]["us_cpi"] = cpi_data["data"]
                    result["sources"].append("FRED")
                
                pce_data = self.fred.get_pce_data()
                if pce_data.get("success"):
                    result["data"]["us_pce"] = pce_data["data"]
                    result["sources"].append("FRED")
            
            # World Bank: Global inflation
            if self.worldbank:
                wb_inflation = self.worldbank.get_inflation_data(country)
                if wb_inflation.get("success"):
                    result["data"]["worldbank"] = wb_inflation["data"]
                    result["sources"].append("World Bank")
                    
            # AKShare: China CPI
            if self.akshare and country.upper() in ["CN", "CHINA"]:
                china_cpi = self.akshare.get_china_cpi()
                if china_cpi.get("success"):
                    result["data"]["china_cpi"] = china_cpi["data"]
                    result["sources"].append("AKShare")
                    
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
    
    def get_gdp_data(self, country: str = "US") -> Dict[str, Any]:
        """Get GDP data from free sources"""
        result = {
            "success": True,
            "data": {},
            "sources": [],
            "timestamp": int(datetime.now().timestamp())
        }
        
        try:
            # World Bank: GDP for all countries
            if self.worldbank:
                wb_gdp = self.worldbank.get_gdp_data(country)
                if wb_gdp.get("success"):
                    result["data"]["worldbank"] = wb_gdp["data"]
                    result["sources"].append("World Bank")
            
            # FRED: US GDP
            if self.fred and country.upper() == "US":
                us_gdp = self.fred.get_gdp_data()
                if us_gdp.get("success"):
                    result["data"]["us_gdp"] = us_gdp["data"]
                    result["sources"].append("FRED")
                    
            # AKShare: China GDP
            if self.akshare and country.upper() in ["CN", "CHINA"]:
                china_gdp = self.akshare.get_china_gdp()
                if china_gdp.get("success"):
                    result["data"]["china_gdp"] = china_gdp["data"]
                    result["sources"].append("AKShare")
                    
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
    
    def get_sovereign_debt(self, country: str = "US") -> Dict[str, Any]:
        """Get sovereign debt metrics from free sources"""
        result = {
            "success": True,
            "data": {},
            "sources": [],
            "timestamp": int(datetime.now().timestamp())
        }
        
        try:
            # World Bank: Government debt
            if self.worldbank:
                wb_debt = self.worldbank.get_government_debt(country)
                if wb_debt.get("success"):
                    result["data"]["worldbank"] = wb_debt["data"]
                    result["sources"].append("World Bank")
            
            # FRED: US Treasury debt
            if self.fred and country.upper() == "US":
                us_debt = self.fred.get_treasury_debt()
                if us_debt.get("success"):
                    result["data"]["us_debt"] = us_debt["data"]
                    result["sources"].append("FRED")
                    
            # BIS: Global debt statistics
            if self.bis:
                bis_debt = self.bis.get_debt_statistics(country)
                if bis_debt.get("success"):
                    result["data"]["bis"] = bis_debt["data"]
                    result["sources"].append("BIS")
                    
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
    
    def get_emerging_markets(self) -> Dict[str, Any]:
        """Get emerging market indicators from free sources"""
        result = {
            "success": True,
            "data": {
                "countries": ["BR", "RU", "IN", "CN", "ZA", "MX", "TR", "ID"],
                "indicators": {}
            },
            "sources": [],
            "timestamp": int(datetime.now().timestamp())
        }
        
        try:
            # World Bank: Key EM indicators
            if self.worldbank:
                em_data = self.worldbank.get_emerging_markets_summary()
                if em_data.get("success"):
                    result["data"]["indicators"]["worldbank"] = em_data["data"]
                    result["sources"].append("World Bank")
            
            # IMF: EM financial stability
            if self.imf:
                imf_em = self.imf.get_emerging_markets_data()
                if imf_em.get("success"):
                    result["data"]["indicators"]["imf"] = imf_em["data"]
                    result["sources"].append("IMF")
                    
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
    
    def get_comprehensive_dashboard(self, country: str = "US") -> Dict[str, Any]:
        """Get comprehensive macro dashboard combining all free sources"""
        result = {
            "success": True,
            "data": {
                "country": country,
                "central_bank_rates": {},
                "inflation": {},
                "gdp": {},
                "sovereign_debt": {},
                "emerging_markets": {}
            },
            "sources_used": [],
            "timestamp": int(datetime.now().timestamp()),
            "note": "All data from FREE sources - no API keys required"
        }
        
        # Aggregate all data
        rates = self.get_central_bank_rates(country)
        if rates["success"]:
            result["data"]["central_bank_rates"] = rates["data"]
            result["sources_used"].extend(rates.get("sources", []))
        
        inflation = self.get_inflation_data(country)
        if inflation["success"]:
            result["data"]["inflation"] = inflation["data"]
            result["sources_used"].extend(inflation.get("sources", []))
        
        gdp = self.get_gdp_data(country)
        if gdp["success"]:
            result["data"]["gdp"] = gdp["data"]
            result["sources_used"].extend(gdp.get("sources", []))
        
        debt = self.get_sovereign_debt(country)
        if debt["success"]:
            result["data"]["sovereign_debt"] = debt["data"]
            result["sources_used"].extend(debt.get("sources", []))
        
        if country.upper() in ["GLOBAL", "ALL"]:
            em = self.get_emerging_markets()
            if em["success"]:
                result["data"]["emerging_markets"] = em["data"]
                result["sources_used"].extend(em.get("sources", []))
        
        # Deduplicate sources
        result["sources_used"] = list(set(result["sources_used"]))
        
        return result


# CLI entry point
if __name__ == "__main__":
    aggregator = FreeMacroAggregator()
    
    if len(sys.argv) < 2:
        # Default: comprehensive dashboard for US
        result = aggregator.get_comprehensive_dashboard("US")
    else:
        command = sys.argv[1]
        
        if command == "rates":
            country = sys.argv[2] if len(sys.argv) > 2 else "US"
            result = aggregator.get_central_bank_rates(country)
        elif command == "inflation":
            country = sys.argv[2] if len(sys.argv) > 2 else "US"
            result = aggregator.get_inflation_data(country)
        elif command == "gdp":
            country = sys.argv[2] if len(sys.argv) > 2 else "US"
            result = aggregator.get_gdp_data(country)
        elif command == "debt":
            country = sys.argv[2] if len(sys.argv) > 2 else "US"
            result = aggregator.get_sovereign_debt(country)
        elif command == "emerging":
            result = aggregator.get_emerging_markets()
        elif command == "dashboard":
            country = sys.argv[2] if len(sys.argv) > 2 else "US"
            result = aggregator.get_comprehensive_dashboard(country)
        else:
            result = {"success": False, "error": f"Unknown command: {command}"}
    
    print(json.dumps(result, cls=DateTimeEncoder, indent=2, ensure_ascii=False))
