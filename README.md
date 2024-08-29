# Compare Data Application for Sybase and PostgreSQL

## Overview

This application is designed to facilitate the comparison of data between Sybase and PostgreSQL databases. It aims to help users identify differences in data across these two database systems efficiently. The application provides a graphical user interface for selecting databases and tables to compare, and it outputs the results in both a visual format within the application and as an Excel file for further analysis.

## Features

- **Database Connection Configuration**: Users can configure the connection details for both Sybase and PostgreSQL databases through a GUI configuration file.
- **Schema Selection**: The application allows users to select specific schemas for comparison.
- **Table Selection**: Users can choose to compare all tables within the selected schemas or specify individual tables.
- **Data Comparison**: The application compares data row by row and highlights differences.
- **Output Generation**: Generates detailed reports of the comparison in Excel format, including unique and differing rows.
- **Error Logging**: Errors encountered during the comparison process are logged for troubleshooting.

## Requirements

Before running the application, ensure you have the following installed:
- Python 3.6 or higher
- Required Python packages as listed in `requirements.txt`
- Java Development Kit (JDK) 8 or higher
- driver.jar in current file location, it is a JDBC drive for Sybase and Postgresql

## Installation

Install the required Python packages by running `pip install -r requirements.txt` in the terminal. 

## Usage

Run [`main.py`] to start the application. Follow the graphical user interface prompts to select the databases, schemas, and tables you wish to compare.

## Screenshot
![image](https://github.com/user-attachments/assets/3dd9f784-3272-46fa-b3bb-1b07e4baec0a)
![image](https://github.com/user-attachments/assets/b931ca81-ac37-4787-b05f-714bbdfc7e76)

