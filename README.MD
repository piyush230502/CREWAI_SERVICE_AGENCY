# Quickstart & Deployment

## Local Development

1. **Create a virtual environment (optional but recommended):**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Flask app (development mode):**

   ```powershell
   $env:FLASK_APP = "app.py"
   $env:FLASK_ENV = "development"
   python app.py
   ```

   - Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Production Deployment (Windows)

1. **Install Gunicorn (for WSGI):**

   ```powershell
   pip install gunicorn
   ```

2. **Run Gunicorn:**

   ```powershell
   gunicorn app:app --bind 0.0.0.0:8000 --workers 4
   ```

   - The app will be available at [http://localhost:8000](http://localhost:8000)

3. **(Optional) Use Nginx as a reverse proxy**
   - See `DEPLOYMENT.md` for a sample Nginx config.

## Docker Deployment

1. **Build the Docker image:**

   ```powershell
   docker build -t crewai-agency .
   ```

2. **Run the Docker container:**

   ```powershell
   docker run -d -p 8000:8000 crewai-agency
   ```

   - Visit [http://localhost:8000](http://localhost:8000)

## Environment Variables
- The Groq API key is provided via the frontend form for each request.
- For persistent keys, set `GROQ_API_KEY` in your environment or use a `.env` file (with `python-dotenv`).

## Notes
- For production, always use HTTPS (see Nginx + Let's Encrypt).
- Never commit your API keys.
- For scaling, use a process manager (systemd, supervisor, etc.) for Gunicorn.

---

For more, see `DEPLOYMENT.md`.

# AI Services Agency 👨‍💼

An AI application that simulates a full-service digital agency using multiple AI agents to analyze and plan software projects. Each agent represents a different role in the project lifecycle, from strategic planning to technical implementation.

## Demo: 

https://github.com/user-attachments/assets/a0befa3a-f4c3-400d-9790-4b9e37254405

## Features

### Five specialized AI agents 

- **CEO Agent**: Strategic leader and final decision maker
  - Analyzes startup ideas using structured evaluation
  - Makes strategic decisions across product, technical, marketing, and financial domains
  - Uses AnalyzeStartupTool and MakeStrategicDecision tools

- **CTO Agent**: Technical architecture and feasibility expert
  - Evaluates technical requirements and feasibility
  - Provides architecture decisions
  - Uses QueryTechnicalRequirements and EvaluateTechnicalFeasibility tools

- **Product Manager Agent**: Product strategy specialist
  - Defines product strategy and roadmap
  - Coordinates between technical and marketing teams
  - Focuses on product-market fit

- **Developer Agent**: Technical implementation expert
  - Provides detailed technical implementation guidance
  - Suggests optimal tech stack and cloud solutions
  - Estimates development costs and timelines

- **Client Success Agent**: Marketing strategy leader
  - Develops go-to-market strategies
  - Plans customer acquisition approaches
  - Coordinates with product team

### Custom Tools

The agency uses specialized tools built with OpenAI Schema for structured analysis:
- **Analysis Tools**: AnalyzeProjectRequirements for market evaluation and analysis of startup idea
- **Technical Tools**: CreateTechnicalSpecification for technical assessment

### 🔄 Asynchronous Communication

The agency operates in async mode, enabling:
- Parallel processing of analyses from different agents
- Efficient multi-agent collaboration
- Real-time communication between agents
- Non-blocking operations for better performance

### 🔗 Agent Communication Flows
- CEO ↔️ All Agents (Strategic Oversight)
- CTO ↔️ Developer (Technical Implementation)
- Product Manager ↔️ Marketing Manager (Go-to-Market Strategy)
- Product Manager ↔️ Developer (Feature Implementation)
- (and more!)

## How to Run

Follow the steps below to set up and run the application:
Before anything else, Please get your OpenAI API Key here: https://platform.openai.com/api-keys

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd awesome-llm-apps/ai_agent_tutorials/ai_services_agency
   ```

2. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Streamlit app**:
    ```bash
    streamlit run ai_services_agency/agency.py
    ```

4. **Run the Flask app**:
    ```bash
    python app.py
    ```

5. **Open the Frontend**:
    - Visit [http://localhost:5000](http://localhost:5000) in your browser for the new UI.

---

**Note:** The legacy Streamlit instructions are for reference only. For the new Flask + frontend deployment, use the steps above.