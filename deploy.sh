#!/bin/bash
# Quick Deployment Script for S&P 500 Dashboard (Linux/Mac)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}S&P 500 AI PREDICTION DASHBOARD - DEPLOYMENT TOOL${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

function show_menu() {
    echo ""
    echo "Select deployment option:"
    echo ""
    echo "1. Deploy with Docker Compose (Recommended)"
    echo "2. Build Docker Image Only"
    echo "3. Deploy to Cloud (Heroku)"
    echo "4. Install Production Dependencies"
    echo "5. View Running Containers"
    echo "6. Stop All Containers"
    echo "7. View Logs"
    echo "8. Exit"
    echo ""
}

function docker_compose_deploy() {
    echo -e "${GREEN}Starting deployment with Docker Compose...${NC}"
    docker-compose down
    docker-compose up -d --build
    echo ""
    echo -e "${GREEN}Dashboard is running at: http://localhost:5000${NC}"
    echo ""
    docker-compose ps
}

function docker_build() {
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t sp500-dashboard .
    echo ""
    echo -e "${GREEN}Image built successfully!${NC}"
    echo -e "${YELLOW}To run: docker run -d -p 5000:5000 sp500-dashboard${NC}"
}

function deploy_heroku() {
    echo -e "${GREEN}Deploying to Heroku...${NC}"

    # Check if heroku is installed
    if ! command -v heroku &> /dev/null; then
        echo -e "${RED}Heroku CLI not found. Please install it first.${NC}"
        echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        return
    fi

    # Check if git is initialized
    if [ ! -d .git ]; then
        echo -e "${YELLOW}Initializing git repository...${NC}"
        git init
        git add .
        git commit -m "Initial commit"
    fi

    echo "Creating Heroku app..."
    heroku create sp500-prediction-dashboard-$(date +%s)

    echo "Deploying to Heroku..."
    git push heroku main

    echo ""
    echo -e "${GREEN}Deployment complete!${NC}"
    heroku open
}

function install_deps() {
    echo -e "${GREEN}Installing production dependencies...${NC}"
    pip install -r requirements_dashboard.txt
    pip install gunicorn gevent
    echo ""
    echo -e "${GREEN}Dependencies installed!${NC}"
}

function view_containers() {
    echo -e "${GREEN}Running containers:${NC}"
    docker-compose ps
}

function stop_containers() {
    echo -e "${YELLOW}Stopping all containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Containers stopped!${NC}"
}

function view_logs() {
    echo -e "${GREEN}Viewing container logs (Ctrl+C to exit):${NC}"
    docker-compose logs -f
}

while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice

    case $choice in
        1)
            docker_compose_deploy
            ;;
        2)
            docker_build
            ;;
        3)
            deploy_heroku
            ;;
        4)
            install_deps
            ;;
        5)
            view_containers
            ;;
        6)
            stop_containers
            ;;
        7)
            view_logs
            ;;
        8)
            echo -e "${BLUE}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done
