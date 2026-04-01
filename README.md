# RCP Mining Operational Dashboard

A daily operational dashboard for mining production. Designed to streamline data entry for site admins and provide an automated, high-level view of KPIs for management.

## Key Features

*   **Management Dashboard:** High-level visualization of 12-month production metrics, Unit Performance (PA/UA, MOHH), and Delay Factors.
*   **Daily Input Form:** A simple, intuitive interface for Checkers/Site Admins to input daily Plan vs. Actual production data and unit delay logs.
*   **ETL Synchronization:** Automated script to extract and load data from monthly Excel sheets into a centralized SQLite database.
*   **AI Insights:** An automated executive summary generator based on current filtered data.

## Technology Stack

*   **Frontend & Framework:** Streamlit (Python)
*   **Database:** SQLite
*   **Data Processing:** Pandas
*   **Data Visualization:** Plotly

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ddos-spec/RCPMINING.git
    cd RCPMINING
    ```

2.  **Install dependencies:**
    ```bash
    pip install streamlit pandas plotly numpy openpyxl pyxlsb
    ```

3.  **Run the ETL script (Initial Sync):**
    Ensure your Excel files are in the root directory, then run:
    ```bash
    python etl_script.py
    ```

4.  **Launch the Dashboard:**
    ```bash
    streamlit run app.py
    ```
    The application will be accessible at `http://localhost:8501`.

## Project Structure

*   `app.py`: Main Streamlit application (Dashboard, Forms, and Sync UI).
*   `database.py`: SQLite database schema and connection handler.
*   `etl_script.py`: Script to extract data from 12 months of Excel files and load it into SQLite.
*   `tambang.db`: The generated SQLite database (excluded from git).
