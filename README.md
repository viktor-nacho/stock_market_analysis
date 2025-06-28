# Nigeria Stock Market PDF Data Extractor & Analyzer 📈📊

Tired of manually sifting through PDF reports for stock data? This project automates the entire process! It's a powerful Python script designed to extract daily stock price information from PDF files, clean it up, perform insightful analysis, and visualize key market trends.

Perfect for anyone tracking the Nigerian Exchange or looking for a robust example of data extraction and analysis from unstructured sources.

## ✨ Features

* **Automated PDF Data Extraction:** Effortlessly pulls tabular stock data directly from your daily PDF reports.
* **Intelligent Data Cleaning:** Handles messy data, parses dates from filenames, converts data types, and manages missing values automatically.
* **Comprehensive Stock Analysis:**
    * Calculates daily percentage changes and cumulative returns for each stock.
    * Aggregates total trading volumes and average closing prices.
    * Identifies correlations between key market metrics (e.g., volume and price).
* **Insightful Visualizations:** Generates clear, beautiful plots to highlight:
    * Top and bottom companies by trading volume.
    * Individual stock price movements over time.
* **Data Persistence:** Saves all processed and analyzed data to convenient CSV files for easy access and future use.

## 🛠️ Technologies Used

* **Python 3.x**
* **Pandas:** The go-to library for powerful data manipulation and analysis.
* **pdfplumber:** For robust and accurate data extraction from PDF tables.
* **Matplotlib:** For creating static, interactive, and animated visualizations.
* **Seaborn:** For making statistical graphics more attractive and informative.

## 🚀 How to Use (Quick Start)

1.  **Clone this repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
    *(Remember to replace `your-username` and `your-repo-name` with your actual GitHub details!)*
2.  **Install the required libraries:**
    ```bash
    pip install pandas pdfplumber matplotlib seaborn
    ```
3.  **Prepare your PDF files:**
    * Create a folder named `stock_files` in the root directory of the project.
    * Place your daily stock PDF files inside this `stock_files/` folder.
    * **Important:** Ensure your PDF filenames follow a consistent pattern for date extraction (e.g., `DAILY_PRICE_LIST_May_20_2024.pdf`). The script expects the date format `%B_%d_%Y` (e.g., "May_20_2024") after removing "DAILY_PRICE_LIST" and ".pdf".
4.  **Run the Jupyter Notebook:**
    ```bash
    jupyter notebook stock_analysis_v5.ipynb
    ```
    Open the `stock_analysis_v5.ipynb` file in your browser and run all the cells. The script will process your PDFs, perform the analysis, generate plots, and save the results (`stock_history.csv` and `output.csv`).

---

**Stop copying, start analyzing!** This project empowers you to turn raw, unorganized PDF data into actionable insights with minimal effort. Happy trading!