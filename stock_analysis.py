import os
import pandas as pd
import pdfplumber
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import math # Needed for math.ceil for subplot calculations

# --- Configuration ---
data_folder = "./stock_files/"
history_file = "stock_history.csv"
output_csv_file = "output.csv" # Name for the final processed CSV

# --- Data Collection ---
all_data = [] # This list will hold all extracted stock data from all PDFs

# Ensure the data folder exists
if not os.path.exists(data_folder):
    print(f"Error: Data folder '{data_folder}' not found. Please create it and place your PDF files inside.")
    exit() # Exit if the folder doesn't exist

files = os.listdir(data_folder)

if files:
    print(f"Found {len(files)} items in '{data_folder}'. Processing PDF files...")
    for file_name in files:
        if file_name.endswith(".pdf"):
            try:
                # Extract date from filename
                # Example filename: DAILY_PRICE_LIST_May_20_2024.pdf
                file_date_str = file_name.replace("DAILY_PRICE_LIST", "").replace(".pdf", "").lstrip("_")
                file_date = datetime.strptime(file_date_str, "%B_%d_%Y").strftime("%Y-%m-%d")

                file_path = os.path.join(data_folder, file_name)
                print(f"Processing: {file_path}")

                current_pdf_stock_data = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            # Skip header row and append data rows
                            for row in table[1:]:
                                # Ensure row is a list and append the date to it
                                row_list = list(row) if isinstance(row, (tuple, list)) else [row]
                                current_pdf_stock_data.append(row_list + [file_date])

                # Filter out rows containing "NIGERIAN EXCHANGE" (assuming it's a footer/header in table)
                # This filter needs to be applied after adding the date, before extending all_data
                filtered_current_pdf_stock_data = [
                    row for row in current_pdf_stock_data if "NIGERIAN EXCHANGE" not in row
                ]
                all_data.extend(filtered_current_pdf_stock_data)

            except Exception as e:
                print(f"Error processing {file_name}: {e}")
                continue # Continue to the next file if an error occurs

    if all_data:
        print("\n--- Data Cleaning and Analysis ---")
        # Define columns including the 'Date' which was appended
        columns = ["S/N", "Symbol", "P_Close", "Open", "High", "Low", "Close",
                   "Change", "%", "Deals", "Volume", "Value", "VWAP", "Date"]

        df = pd.DataFrame(all_data, columns=columns)

        # Select relevant columns for analysis
        df = df[["Symbol", "Close", "Volume", "Date"]]

        # Convert 'Close' and 'Volume' to numeric
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        # Remove commas from 'Volume' strings before converting
        df['Volume'] = pd.to_numeric(df['Volume'].astype(str).str.replace(',', ''), errors='coerce')

        # Convert 'Date' to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])

        # Drop rows where 'Close' or 'Volume' became NaN after conversion
        # And replace empty strings/whitespace with NA and drop those rows
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(subset=["Close", "Volume", "Symbol", "Date"])

        if df.empty:
            print("No valid stock data remaining after cleaning. Exiting.")
            exit()

        # Sort data for time-series analysis
        df = df.sort_values(by=["Symbol", "Date"])

        # Calculate 'Day' as a sequential count for each symbol
        df["Day"] = df.groupby("Symbol").cumcount() + 1

        # --- Aggregate Analysis ---
        print("Performing aggregations...")
        total_volume = df.groupby('Symbol')['Volume'].sum().reset_index().sort_values(by='Volume', ascending=False)
        average_close = df.groupby('Symbol')['Close'].mean().reset_index().sort_values(by='Close', ascending=False)

        # Combine analyses
        combined_analysis = pd.merge(total_volume, average_close, on="Symbol")
        print("\n--- Combined Analysis (Top by Volume) ---")
        print(combined_analysis.head())

        # Calculate correlation
        correlation = combined_analysis["Volume"].corr(combined_analysis["Close"])
        print(f"\nCorrelation between total volume and average close price: {correlation:.2f}")

        # --- Calculate Returns ---
        print("\nCalculating returns...")
        df["Close_pct_change"] = df.groupby("Symbol")["Close"].pct_change() * 100
        df["Growth"] = (df["Close_pct_change"] / 100) + 1
        # Fill NA in Growth for the first entry of each symbol (where pct_change is NA) with 1 (no growth yet)
        df["Growth"] = df.groupby("Symbol")["Growth"].transform(lambda x: x.fillna(1))
        df["Cumulative_Return"] = df.groupby("Symbol")["Growth"].cumprod()
        df['Cumulative_Return'] = (df['Cumulative_Return'] - 1) * 100 # Convert to percentage

        # --- Save Processed Data ---
        print("\nSaving processed data...")
        # Save the main processed DataFrame to output.csv
        df.to_csv(output_csv_file, index=False)
        print(f"Full processed data saved to '{output_csv_file}'")

        # Save to history file (append or write)
        if os.path.exists(history_file):
            df.to_csv(history_file, mode="a", header=False, index=False)
            print(f"Appended data to '{history_file}'")
        else:
            df.to_csv(history_file, mode="w", header=True, index=False)
            print(f"Created and saved data to '{history_file}'")

        print("Stock data successfully extracted, processed, and saved!")

        # --- Visualizations ---
        print("\nGenerating visualizations...")

        # Prepare data for top/bottom volume plots
        top_10_volume = total_volume.head(10)
        bottom_10_volume = total_volume.tail(10).sort_values(by='Volume', ascending=True) # Sort bottom 10 for better visualization

        # Plot Top 10 companies by total volume
        plt.figure(figsize=(12, 6))
        sns.barplot(x="Symbol", y="Volume", data=top_10_volume, palette="Blues_d")
        plt.title("Top 10 Companies by Total Volume Traded", fontsize=16)
        plt.xlabel("Company Symbol", fontsize=14)
        plt.ylabel("Total Volume Traded", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        print("Generated 'Top 10 Companies by Total Volume Traded' plot.")


        # Plot Bottom 10 companies by total volume
        plt.figure(figsize=(12, 6))
        sns.barplot(x="Symbol", y="Volume", data=bottom_10_volume, palette="Blues_d")
        plt.title("Bottom 10 Companies by Total Volume Traded", fontsize=16)
        plt.xlabel("Company Symbol", fontsize=14)
        plt.ylabel("Total Volume Traded", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        print("Generated 'Bottom 10 Companies by Total Volume Traded' plot.")

        # Plot Closing Price for Each Symbol (using corrected subplot logic)
        unique_symbols = df["Symbol"].unique()
        num_symbols = len(unique_symbols)
        num_cols = 3 # Number of columns for subplots
        num_rows = math.ceil(num_symbols / num_cols)

        fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(16, 4 * num_rows))
        axes = axes.flatten() # Flatten the 2D array of axes for easy iteration

        for i, symbol in enumerate(unique_symbols):
            symbol_data = df[df['Symbol'] == symbol].sort_values(by='Day') # Ensure data is sorted by day for plotting
            ax = axes[i]

            ax.plot(symbol_data['Day'], symbol_data['Close'], label=symbol, marker='o', markersize=2)
            ax.set_title(f'Closing Price for {symbol}', fontsize=10)
            ax.set_xlabel('Day', fontsize=8)
            ax.set_ylabel('Close Price', fontsize=8)
            ax.tick_params(axis='x', rotation=45, labelsize=6)
            ax.tick_params(axis='y', labelsize=8)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.5)

        # Hide any unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()
        print("Generated individual stock closing price plots.")

    else:
        print("No valid stock data found in the PDF files after initial extraction. No analysis performed.")
else:
    print(f"No files found in the directory: {data_folder}")

print("\n--- Script Finished ---")