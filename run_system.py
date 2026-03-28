#!/usr/bin/env python3
"""
Main System Runner
Complete system orchestration for Cloud Cost Governance
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        if cwd:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True
            )
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_prerequisites():
    """Check system prerequisites"""
    print("🔍 Checking System Prerequisites...")
    print("=" * 50)
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python not found")
        return False
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI: {result.stdout.strip()}")
        else:
            print("⚠️  AWS CLI not found (optional)")
    except:
        print("⚠️  AWS CLI not found (optional)")
    
    # Check required directories
    base_dir = Path(__file__).parent
    required_dirs = ['pipeline', 'web', 'sample_data']
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
            return False
    
    return True

def setup_environment():
    """Setup the environment"""
    print("\n🔧 Setting Up Environment...")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Create data directory
    data_dir = base_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    
    # Copy sample data if data directory is empty
    if not any(data_dir.iterdir()):
        sample_dir = base_dir / 'sample_data'
        if sample_dir.exists():
            import shutil
            for file_path in sample_dir.glob('*.json'):
                shutil.copy2(file_path, data_dir / file_path.name)
            print("✅ Sample data copied to data directory")
    
    return True

def test_aws_setup():
    """Test AWS configuration"""
    print("\n☁️  Testing AWS Configuration...")
    print("=" * 50)
    
    return run_command("python aws_setup.py", "AWS Setup Test")

def run_data_pipeline():
    """Run the data collection pipeline"""
    print("\n📊 Running Data Pipeline...")
    print("=" * 50)
    
    return run_command("python pipeline/run_pipeline.py", "Data Collection Pipeline")

def start_dashboard():
    """Start the web dashboard"""
    print("\n🌐 Starting Web Dashboard...")
    print("=" * 50)
    
    # Check if data exists
    data_dir = Path(__file__).parent / 'data'
    if not any(data_dir.glob('*.json')):
        print("⚠️  No data found. Running pipeline first...")
        if not run_data_pipeline():
            return False
    
    print("🚀 Starting Flask dashboard...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Change to web directory and start Flask
        web_dir = Path(__file__).parent / 'web'
        subprocess.run(['python', 'app.py'], cwd=web_dir)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting dashboard: {str(e)}")
        return False

def show_menu():
    """Show interactive menu"""
    print("\n" + "=" * 60)
    print("🚀 Cloud Cost Governance System")
    print("=" * 60)
    print("1. 📊 Run Data Pipeline (collect live AWS data)")
    print("2. 🌐 Start Dashboard (with current data)")
    print("3. ☁️  Test AWS Configuration")
    print("4. 🔄 Complete System Run (pipeline + dashboard)")
    print("5. 📋 Show System Status")
    print("6. ❌ Exit")
    print("-" * 60)

def show_system_status():
    """Show current system status"""
    print("\n📋 System Status")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    
    # Check data files
    data_files = ['inventory.json', 'metrics_inventory.json', 'cost_metrics_inventory.json', 'optimization_report.json']
    for file_name in data_files:
        file_path = data_dir / file_name
        if file_path.exists():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - file_time
            print(f"✅ {file_name} (updated {age.total_seconds()/3600:.1f} hours ago)")
        else:
            print(f"❌ {file_name} (missing)")
    
    # Check data source
    inventory_path = data_dir / 'inventory.json'
    if inventory_path.exists():
        try:
            with open(inventory_path) as f:
                data = json.load(f)
                if data.get('account_id') == '123456789012':
                    print("📊 Data Source: Sample Data")
                else:
                    print("☁️  Data Source: Live AWS Data")
        except:
            print("⚠️  Data Source: Unknown")
    
    print("\nNext steps:")
    if not inventory_path.exists():
        print("1. Run option 1 to collect data")
    else:
        print("1. Run option 2 to start dashboard")
        print("2. Run option 4 to refresh data and start dashboard")

def main():
    """Main function"""
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues and try again.")
        return False
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        return False
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_data_pipeline()
            elif choice == '2':
                start_dashboard()
            elif choice == '3':
                test_aws_setup()
            elif choice == '4':
                print("\n🔄 Running Complete System...")
                if run_data_pipeline():
                    start_dashboard()
            elif choice == '5':
                show_system_status()
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)
