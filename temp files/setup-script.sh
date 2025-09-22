#!/bin/bash

echo "🎨 ArtScape Microservices Setup Script"
echo "======================================"

# Create project directory structure
echo "📁 Creating directory structure..."
mkdir -p artscape-microservices

cd artscape-microservices

# Create service directories
mkdir -p auth-service/app
mkdir -p artwork-service/app
mkdir -p commerce-service/app
mkdir -p api-gateway/app

echo "✅ Directory structure created successfully!"

# Create virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."
python -m venv venv

echo ""
echo "🔧 Virtual environment created!"
echo ""
echo "📝 Next Steps:"
echo "1. Activate virtual environment:"
echo "   Linux/Mac: source venv/bin/activate"
echo "   Windows:   venv\\Scripts\\activate"
echo ""
echo "2. Copy all the generated code files to their respective directories"
echo ""
echo "3. Install dependencies:"
echo "   pip install -r auth-service/requirements.txt"
echo "   pip install -r artwork-service/requirements.txt"
echo "   pip install -r commerce-service/requirements.txt"
echo "   pip install -r api-gateway/requirements.txt"
echo ""
echo "4. Run the services (each in separate terminal):"
echo "   cd auth-service && uvicorn app.main:app --port 8001 --reload"
echo "   cd artwork-service && uvicorn app.main:app --port 8002 --reload"
echo "   cd commerce-service && uvicorn app.main:app --port 8003 --reload"
echo "   cd api-gateway && uvicorn app.main:app --port 8000 --reload"
echo ""
echo "5. Access the API documentation:"
echo "   Main Gateway: http://localhost:8000/docs"
echo ""
echo "✅ Setup complete! Ready for A2 assignment development."