
# 🥗 Nutrition Tracker

A Streamlit-based web application for tracking daily nutrition intake, visualizing progress, and managing dietary goals.

## Features

- **Log Food Entries**: Record your meals with date, time, calories, and protein information
- **Dashboard**: View your daily progress with interactive gauges showing calorie and protein intake relative to your goals
- **History**: Analyze your nutrition data over time with interactive charts and detailed logs
- **Data Export**: Export your nutrition data to CSV format for further analysis
- **Goal Setting**: Set and adjust your daily calorie and protein targets

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt` or using Poetry
3. Run the application: `streamlit run main.py`

## Usage

1. **Set Goals**: Use the sidebar to configure your daily calorie and protein goals
2. **Log Meals**: Navigate to the "Log Entry" tab to record your food intake
3. **Track Progress**: Check your daily progress on the "Dashboard" tab
4. **View History**: Analyze your nutrition trends and export data from the "History" tab

## Technologies Used

- **Streamlit**: For the web interface
- **Pandas**: For data manipulation
- **Plotly**: For interactive visualizations

## File Structure

- `main.py`: The main application file
- `utils.py`: Utility functions for data loading and processing
- `styles.css`: Custom CSS styles
- `data/`: Directory containing the food log data
