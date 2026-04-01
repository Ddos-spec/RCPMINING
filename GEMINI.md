# Project: Tambang Production Dashboard

## Overview
A daily operational dashboard for mining production. Designed for checkers/site admins to input data and management to view automated KPIs.

## Key Performance Indicators (KPIs)
*   Production Plan vs Actual
*   Unit Productivity
*   MOHH/EWH (Meter/Operating Hours/Engine Working Hours)
*   PA/UA (Physical Availability / Use of Availability)
*   Delay factors
*   Ore hauling/barging
*   Stock positions (Initial & Final)

## Features
*   Drill-down capabilities: Unit, Driver, Activity, Date/Shift, Loss Time causes.
*   AI Insights (Dummy): A feature to generate summary explanations of the displayed data when clicked.

## Implementation Strategy
1.  **Data Parsing**: Read and consolidate the monthly Excel files.
2.  **Dashboard Framework**: Use Python with **Streamlit** (highly recommended for rapid data dashboards) or a Flask + HTML/JS stack.
3.  **Dummy AI**: Implement a simple LLM prompt or rules-based text generator that takes current filtered data and outputs a textual summary.
