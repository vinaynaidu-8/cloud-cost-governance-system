#!/bin/bash

# Cloud Cost Governance - EC2 Deployment Script
echo "🚀 Starting Cloud Cost Governance Deployment on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Python and required packages
echo "🐍 Installing Python and dependencies..."
sudo yum install python3 python3-pip git -y

# Install Python packages
echo "📚 Installing Python packages..."
pip3 install flask boto3

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/cloud-cost-governance
sudo chown ec2-user:ec2-user /opt/cloud-cost-governance

# Navigate to application directory
cd /opt/cloud-cost-governance

# Create log directory
mkdir -p logs

echo "✅ Setup complete!"
echo "🌐 Dashboard will be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "🔧 To start the application:"
echo "   python3 run_system.py"
echo "   python3 web/app.py"
echo ""
echo "📊 To access dashboard:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
