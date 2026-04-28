#!/usr/bin/env python3
"""
sentinel_config.py - Sentinel Hub Configuration Guide and Setup Helper

[STUB] Sentinel Hub is a commercial data provider for alternative data.
This script provides configuration guidance and setup assistance.

Sentinel Hub offers:
- Satellite imagery analysis
- Supply chain monitoring
- Geospatial intelligence
- Alternative data feeds

Usage:
    python sentinel_config.py --guide          # Show configuration guide
    python sentinel_config.py --check           # Check current config
    python sentinel_config.py --setup           # Interactive setup wizard

Requirements:
    pip install requests python-dotenv
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional


# Configuration file paths
CONFIG_DIR = Path.home() / ".fincept"
CONFIG_FILE = CONFIG_DIR / "sentinel_config.json"
ENV_FILE = Path.home() / ".fincept" / ".env"


class SentinelConfigHelper:
    """Helper class for Sentinel Hub configuration"""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.env_file = ENV_FILE
        
    def show_guide(self):
        """Display comprehensive configuration guide"""
        guide = """
╔══════════════════════════════════════════════════════════════╗
║         SENTINEL HUB CONFIGURATION GUIDE                   ║
╚══════════════════════════════════════════════════════════════╝

📋 OVERVIEW
─────────────────────────────────────────────────────────────
Sentinel Hub provides satellite imagery and geospatial data.
This is OPTIONAL - Fincept Terminal works fully without it.

⚠️  [STUB] This requires COMMERCIAL subscription from Sentinel Hub
   Visit: https://www.sentinel-hub.com/

🔑 STEP 1: Obtain Credentials
─────────────────────────────────────────────────────────────
1. Sign up at https://account.sentinel-hub.com/
2. Choose a plan (Free tier available with limits)
3. Go to Dashboard → User Settings → API Keys
4. Copy your:
   - Client ID
   - Client Secret
   - Instance ID (for specific datasets)

💾 STEP 2: Store Credentials Securely
─────────────────────────────────────────────────────────────
Option A: Environment Variables (Recommended)
  export SENTINEL_CLIENT_ID=your_client_id
  export SENTINEL_CLIENT_SECRET=your_secret
  export SENTINEL_INSTANCE_ID=your_instance_id

Option B: Configuration File
  Create ~/.fincept/sentinel_config.json:
  {
    "client_id": "your_client_id",
    "client_secret": "your_secret",
    "instance_id": "your_instance_id"
  }

Option C: .env File
  Create ~/.fincept/.env:
  SENTINEL_CLIENT_ID=your_client_id
  SENTINEL_CLIENT_SECRET=your_secret
  SENTINEL_INSTANCE_ID=your_instance_id

⚙️  STEP 3: Configure in Fincept Terminal
─────────────────────────────────────────────────────────────
1. Open Fincept Terminal
2. Navigate to: Settings → Data Sources → Sentinel Hub
3. Enter your credentials
4. Click "Test Connection"
5. Save configuration

📊 STEP 4: Available Datasets
─────────────────────────────────────────────────────────────
Once configured, you can access:
• Sentinel-2 L2A (10m resolution)
• Landsat 8 & 9
• MODIS products
• Custom composites
• NDVI, NDWI indices
• Change detection

🔧 STEP 5: Python Integration (Optional)
─────────────────────────────────────────────────────────────
Install Sentinel Hub Python package:
  pip install sentinelhub

Example usage:
  from sentinelhub import SHConfig, DataCollection
  config = SHConfig()
  config.sh_client_id = os.getenv('SENTINEL_CLIENT_ID')
  config.sh_client_secret = os.getenv('SENTINEL_CLIENT_SECRET')

❓ TROUBLESHOOTING
─────────────────────────────────────────────────────────────
Problem: Authentication failed
Solution: Verify client_id and client_secret are correct

Problem: No data returned
Solution: Check instance_id matches your subscription

Problem: Rate limit exceeded
Solution: Free tier has daily limits, upgrade if needed

📚 RESOURCES
─────────────────────────────────────────────────────────────
• Documentation: https://docs.sentinel-hub.com/
• API Reference: https://docs.sentinel-hub.com/api/latest/
• Python SDK: https://github.com/sentinel-hub/sentinelhub-py
• Community Forum: https://forum.sentinel-hub.com/

⚖️  LICENSING
─────────────────────────────────────────────────────────────
• Free tier: 500 units/month (limited resolution)
• Basic: $29/month (1000 units)
• Premium: $99/month (5000 units)
• Enterprise: Custom pricing

NOTE: Fincept Terminal does NOT include Sentinel Hub subscription.
You must purchase separately if needed.

══════════════════════════════════════════════════════════════
        [FREE-MODE] Sentinel Hub is OPTIONAL
        All core features work WITHOUT it!
══════════════════════════════════════════════════════════════
"""
        print(guide)
    
    def check_config(self):
        """Check current configuration status"""
        print("\n🔍 Checking Sentinel Hub Configuration...\n")
        
        # Check environment variables
        env_vars = {
            "SENTINEL_CLIENT_ID": os.getenv("SENTINEL_CLIENT_ID"),
            "SENTINEL_CLIENT_SECRET": os.getenv("SENTINEL_CLIENT_SECRET"),
            "SENTINEL_INSTANCE_ID": os.getenv("SENTINEL_INSTANCE_ID"),
        }
        
        print("Environment Variables:")
        for var, value in env_vars.items():
            if value:
                masked = value[:4] + "****" if len(value) > 4 else "****"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ❌ {var}: Not set")
        
        # Check config file
        print("\nConfiguration File:")
        if self.config_file.exists():
            print(f"  ✅ Config file exists: {self.config_file}")
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                for key in ["client_id", "client_secret", "instance_id"]:
                    if key in config:
                        masked = config[key][:4] + "****" if len(config[key]) > 4 else "****"
                        print(f"  ✅ {key}: {masked}")
                    else:
                        print(f"  ❌ {key}: Missing")
            except Exception as e:
                print(f"  ⚠️  Error reading config: {e}")
        else:
            print(f"  ❌ Config file not found: {self.config_file}")
        
        # Check .env file
        print("\nEnvironment File (.env):")
        if self.env_file.exists():
            print(f"  ✅ .env file exists: {self.env_file}")
        else:
            print(f"  ❌ .env file not found: {self.env_file}")
        
        # Overall status
        print("\n" + "="*60)
        configured = any(v for v in env_vars.values() if v)
        if configured:
            print("✅ Sentinel Hub is CONFIGURED")
            print("   You can use satellite imagery features")
        else:
            print("⚠️  Sentinel Hub is NOT configured")
            print("   This is OK - all core features still work!")
            print("   Run 'python sentinel_config.py --setup' to configure")
        print("="*60 + "\n")
    
    def setup_wizard(self):
        """Interactive setup wizard"""
        print("\n🔧 Sentinel Hub Setup Wizard\n")
        print("[STUB] This will guide you through configuration")
        print("Note: You need a Sentinel Hub account first!\n")
        
        response = input("Do you have a Sentinel Hub account? (yes/no): ").strip().lower()
        if response != "yes":
            print("\nPlease sign up first at: https://account.sentinel-hub.com/")
            print("Then run this wizard again.\n")
            return
        
        print("\nStep 1: Get your credentials from Sentinel Hub dashboard")
        print("  - Client ID")
        print("  - Client Secret")
        print("  - Instance ID\n")
        
        client_id = input("Enter Client ID: ").strip()
        client_secret = input("Enter Client Secret: ").strip()
        instance_id = input("Enter Instance ID: ").strip()
        
        if not all([client_id, client_secret, instance_id]):
            print("\n❌ Error: All fields are required!")
            return
        
        # Save to config file
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "instance_id": instance_id,
            "configured_at": "2026-04-20",
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved to: {self.config_file}")
        print("\nNext steps:")
        print("  1. Restart Fincept Terminal")
        print("  2. Go to Settings → Data Sources → Sentinel Hub")
        print("  3. Click 'Test Connection' to verify")
        print("\nDone! 🎉\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sentinel Hub Configuration Helper")
    parser.add_argument("--guide", action="store_true", help="Show configuration guide")
    parser.add_argument("--check", action="store_true", help="Check current configuration")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    
    args = parser.parse_args()
    
    helper = SentinelConfigHelper()
    
    if args.guide:
        helper.show_guide()
    elif args.check:
        helper.check_config()
    elif args.setup:
        helper.setup_wizard()
    else:
        parser.print_help()
        print("\n💡 Tip: Run with --guide for detailed instructions")


if __name__ == "__main__":
    main()
