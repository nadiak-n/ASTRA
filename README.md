# ASTRA
ASTRA - Astronaut Smart Health Companion | AI-powered astronaut health monitoring platform.
# ASTRA – AI-Powered Astronaut Health Monitoring System

<p align="center">
  <strong>Making Astronaut Health Monitoring Smarter</strong>
</p>

ASTRA is an intelligent software prototype designed to support astronaut health monitoring during space missions. It brings health data, analysis, visualizations, alerts, mission simulations, and AI-powered interaction together in one platform.

Our vision is to move beyond simply collecting health measurements and make them easier to understand, analyze, and use.

---

## About the Project

Imagine an astronaut far away from Earth, where immediate medical support may be limited.

How can we monitor their health, understand changes in their condition, and identify possible warning signs?

This is the challenge that inspired us to develop ASTRA.

ASTRA is designed to organize available health information, analyze changes over time, and present useful insights through an interactive web application.

The project aims to support smarter health monitoring and contribute to the development of future space-health technologies.

## Key Features

ASTRA brings several systems together in one platform:

### 1. Astronaut Digital Health Profile
Organizes astronaut health information in a clear and accessible profile.

### 2. ASTRA Intelligence Engine
Analyzes available health data and generates useful insights.

### 3. Health Trend Prediction
Examines health data over time and demonstrates possible future trends.

### 4. Mission Simulation Lab
Allows users to explore different health-monitoring scenarios during simulated missions.

### 5. Real-Time Monitoring Architecture
Provides a software foundation for future integration with physical monitoring devices.

### 6. Explainable Health Alerts
Highlights possible health concerns and explains why an alert may be generated.

### 7. Automated Health Reports
Creates organized reports based on available health information.

### 8. Crew Health Overview
Provides an overview of health information across multiple crew members.

### 9. Mission Comparison
Allows users to compare different mission scenarios and their health-monitoring results.

### 10. ASTRA AI Assistant
An interactive assistant that supports Arabic and English communication through text and voice.

---

## How ASTRA Works

The platform follows a simple workflow:

1. **Health Data Input:** Health information is entered manually or provided through available sample data and supported input methods.
2. **Data Processing:** The system organizes and processes the available information.
3. **Health Analysis:** ASTRA analyzes the data and examines possible changes and trends.
4. **Insights and Alerts:** The platform presents understandable results and possible warning signs.
5. **Reports and Visualization:** Users can explore charts, summaries, and health reports.
6. **AI Interaction:** Users can communicate with the ASTRA Assistant to ask questions and explore information.

---

## Technologies Used

ASTRA was developed using the following technologies:

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application framework |
| Pandas | Data processing and organization |
| Plotly | Interactive data visualization |
| Streamlit Mic Recorder | Voice recording interface |
| SpeechRecognition | Speech recognition |
| gTTS | Text-to-speech |
| Google Gemini API | AI-powered assistant |
| Google Gen AI SDK | Gemini integration |
| Visual Studio Code | Development environment |
| Git & GitHub | Version control and project hosting |

---

## Project Structure

```text
ASTRA/
│
├── dashboard/
│   └── app.py
│
├── src/
│   ├── data_loader.py
│   └── health_analysis.py
│
├── data/
│   └── sample_health_data.csv
│
├── .streamlit/
│   └── secrets.toml
│
├── requirements.txt
├── .gitignore
└── README.md
```

*Note: The structure above describes the main project files. Additional modules and files may be included in the complete version.*

---

## Installation & Setup

Follow these steps to run ASTRA locally.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/ASTRA-Astronaut-Health-Monitoring.git
```

### 2. Open the Project Folder

```bash
cd ASTRA-Astronaut-Health-Monitoring
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the Gemini API Key

If you want to use the AI Assistant, configure your Gemini API key using Streamlit secrets.

Create a file named `secrets.toml` inside the `.streamlit` folder:

```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

**Important:** Never upload your API key or `secrets.toml` file to GitHub.

### 7. Run ASTRA

```bash
streamlit run dashboard/app.py
```

The application will open in your browser.

---

## Current Development Status

ASTRA is currently a working software prototype.

The current version demonstrates its main software modules using sample and simulated health data in parts of the system.

Physical health-monitoring hardware has not yet been integrated or validated under real spaceflight conditions.

The current prototype is intended for demonstration and development purposes. It is not a certified medical device and does not provide medical diagnosis.

---

## Future Development

Our future plans include:

- Developing a physical health-monitoring hardware unit.
- Integrating suitable sensors with the ASTRA software platform.
- Testing real sensor readings and data transmission.
- Improving health analysis and trend-monitoring capabilities.
- Exploring relevant space-agency datasets for further testing and validation.
- Expanding the AI Assistant and its interaction capabilities.
- Testing the platform through more realistic mission simulations.

Our long-term vision is to develop ASTRA into an integrated astronaut health-monitoring platform that combines software intelligence with physical monitoring technology.

---

## NASA & Space Agency Resources

No NASA or other space agency datasets were directly integrated into the current prototype.

The project was inspired by the challenges of astronaut health monitoring and the importance of supporting human health during space exploration.

Future versions may explore publicly available space-agency datasets for further testing and development.

---

## Project Team

**Developed by:**

1. Nadia Khaled
2. Youssef Salah
3. Nadia Galal
4. Rawan Wael
5. Sarah Mohamed
6. Ingy Ahmed

---

## Acknowledgments

We acknowledge the developers and communities behind the open-source libraries and tools used in this project.

We also acknowledge Google Gemini as the AI service integrated into the ASTRA Assistant and the AI tools used to support parts of the development process.

---

## Our Vision

We believe that the future of space exploration depends not only on reaching farther destinations, but also on protecting the people who make those missions possible.

**ASTRA – From Health Monitoring to Intelligent Health Understanding.**
