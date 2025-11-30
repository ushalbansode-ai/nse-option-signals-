#!/bin/bash
echo "🚀 Setting up Option Chain Analyzer in GitHub Codespaces..."
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "✅ Setup complete!"
echo "🌐 Your app will be available at: https://${CODESPACE_NAME}-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo "💡 To start the app manually: cd backend && python codespaces_app.py"
