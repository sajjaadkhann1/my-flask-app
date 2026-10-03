# Flask ML Analysis App

A comprehensive machine learning web application built with **Flask** and **Python** for data analysis, visualization, and machine learning model training.

## 🌟 Features

- **CSV File Upload & Exploration**
  - Upload CSV files for analysis
  - Automatic data profiling (rows, columns, data types)
  - Missing value detection and visualization
  - Data type distribution analysis

- **Data Preprocessing**
  - Automatic handling of missing values (imputation)
  - Categorical encoding with LabelEncoder
  - Data normalization and scaling
  - Outlier detection and removal

- **Linear Regression Analysis**
  - Train/test split with configurable ratios
  - Feature selection and coefficient analysis
  - Performance metrics: R², RMSE, MAE, MSE
  - Comprehensive 4-panel visualization:
    - Actual vs Predicted scatter plot
    - Residual analysis
    - Residuals distribution histogram
    - Top 10 feature coefficients

- **K-Means Clustering**
  - Automatic k-value optimization via elbow method
  - Cluster visualization with PCA dimensionality reduction
  - Cluster size distribution
  - Normalized cluster profile heatmap
  - Configurable cluster count (2-10)

- **DBSCAN Clustering**
  - Density-based clustering with configurable eps and min_samples
  - Noise point detection
  - PCA-based 2D visualization
  - Core point identification
  - Cluster profile analysis

- **Interactive Visualizations**
  - Dark-themed plots with modern color palette
  - Real-time chart generation
  - Base64-encoded image responses for instant display
  - Responsive and professional design

## 🛠 Tech Stack

- **Backend**: Flask 2.x + Python 3.8+
- **Data Processing**: pandas, NumPy
- **ML Libraries**: scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/sajjaadkhann1/my-flask-app.git
cd my-flask-app

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5050`

## 📋 Dependencies

```
Flask==2.3.x
pandas>=1.5.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
```

## 🚀 Usage

### 1. Upload CSV File
- Click "Upload CSV" and select your data file
- The app will automatically analyze:
  - Dataset overview with row and column counts
  - Missing value summary
  - Data type distribution
  - Correlation matrix (for numeric columns)
  - First 6 rows preview
  - Statistical summary (mean, median, std, etc.)

### 2. Linear Regression
1. Select a target column
2. Optionally choose specific features (or use all)
3. View:
   - Model performance metrics
   - Feature coefficients
   - 4-panel diagnostic plots
   - Training/test split sizes

### 3. K-Means Clustering
1. Specify desired number of clusters (2-10)
2. Algorithm automatically optimizes with elbow method
3. Visualize:
   - Cluster assignments in 2D (PCA)
   - Cluster size distribution
   - Variance explained by PCA components
   - Feature profiles per cluster

### 4. DBSCAN Clustering
1. Adjust `eps` (epsilon neighborhood) parameter
2. Set `min_samples` (core point threshold)
3. View:
   - Clustered vs noise point breakdown
   - 2D PCA visualization
   - Core point count
   - Cluster-specific profiles

## 📁 Project Structure

```
my-flask-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── sample.csv            # Example dataset
├── static/
│   ├── uploads/          # User-uploaded CSV files
│   └── plots/            # Generated visualizations
└── templates/
    └── index.html        # Frontend interface
```

## 🎨 Customization

### Color Scheme
Edit the color palette in `app.py` (lines 61-70):
```python
DARK_BG   = '#0f172a'      # Dark background
CARD_BG   = '#1e293b'      # Card background
ACCENT    = '#6366f1'      # Primary accent
ACCENT2   = '#22d3ee'      # Secondary accent
ACCENT3   = '#f59e0b'      # Tertiary accent
```

### Plot Styling
Modify `set_style()` function for different plot aesthetics.

### ML Hyperparameters
- **Linear Regression**: Test/train split (line 196)
- **K-Means**: k range, random_state (line 280)
- **DBSCAN**: Default eps and min_samples (lines 369-370)

## 📊 Example Workflow

1. Upload `sample.csv`
2. Explore the dataset overview
3. Train a linear regression model with house price prediction
4. Run k-means clustering with k=3-5
5. Export insights or adjust parameters for further analysis

## ⚙️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/upload` | POST | Upload and analyze CSV |
| `/linear_regression` | POST | Train regression model |
| `/kmeans` | POST | K-Means clustering |
| `/dbscan` | POST | DBSCAN clustering |

## 🐛 Troubleshooting

- **"No file part" error**: Ensure file is selected before upload
- **"Only CSV files supported"**: Convert Excel/JSON to CSV first
- **Model errors**: Ensure target column is numeric
- **Visualization issues**: Check for sufficient numeric columns (at least 2)

## 📝 License

ISC

## 👤 Author

[sajjaadkhann1](https://github.com/sajjaadkhann1)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs via Issues
- Suggest features
- Submit pull requests

---

**Built with ❤️ using Flask and scikit-learn**
