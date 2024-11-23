# Global Survival Rates and Education Impact Visualization

A data visualization project exploring the correlation between education and survival rates across the globe (2015-2021).

## Overview

This interactive visualization platform, built with Dash and Plotly, presents a narrative journey through global survival rate patterns and educational impact through three key perspectives:
- Global overview with interactive mapping
- Development gap analysis
- Success stories and case studies

## Prerequisites

- Python 3.8 or higher
- Git
- Internet connection for data download

## Getting Started

### Data Preparation

1. Download the dataset:
   - Visit [World Bank EdStats](https://datacatalog.worldbank.org/search/dataset/0038480)
   - Download the dataset in CSV format
   - Place the downloaded file in the `data/` directory

2. Process the dataset:
   ```bash
   python clean_dataset.py
   ```
   This will generate `worldbank_data_cleaned.csv` in the data directory.

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:sash7410/education_viz.git
   cd global-survival-visualization
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Unix/macOS:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

## Features

### Interactive Elements
- Guided narrative tour through the data
- Year selection slider (2015-2021)
- Country comparison tools
- Interactive global map
- Dynamic trend analysis graphs
- Real-time metric updates

### Visualization Sections

1. **Global Overview**
   - Interactive world map
   - Region-based color coding
   - Temporal data exploration

2. **Development Comparison**
   - Developed vs. developing nations analysis
   - Time-series comparisons
   - Country-specific metrics

3. **Success Stories**
   - Case studies of improvement
   - Educational impact analysis
   - Trend visualization

## Project Structure

```
./
├── app.py                  # Main application entry point
├── clean_dataset.py        # Data preprocessing script
├── requirements.txt        # Project dependencies
├── assets/
│   └── style.css          # Custom styling
└── data/
    └── datasets
```

## Dependencies

- Dash
- Plotly
- Pandas
- NumPy

## Deployment

A live version of this visualization is available at: https://education-viz.onrender.com/

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Course Information

- Course: CS-GY 6313 B Information Visualization
- Institution: New York University
- Semester: Fall 2024

## License

[Add your license information here]

## Author

Sashank RM

## Acknowledgments

- World Bank for providing the EdStats dataset
- NYU Faculty and Staff