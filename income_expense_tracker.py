import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# File to store data
DATA_FILE = "financial_data.csv"

# Initialize the data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Description", "Amount", "Type", "Category"]).to_csv(DATA_FILE, index=False)

# Helper functions
def add_record(date, description, amount, record_type, category):
    new_record = pd.DataFrame([[date, description, amount, record_type, category]], columns=["Date", "Description", "Amount", "Type", "Category"])
    new_record.to_csv(DATA_FILE, mode='a', header=False, index=False)

def get_records():
    try:
        return pd.read_csv(DATA_FILE)
    except pd.errors.ParserError:
        st.error("Error reading data. The file may be corrupted. Please check the CSV format.")
        # Optionally recreate the file
        pd.DataFrame(columns=["Date", "Description", "Amount", "Type", "Category"]).to_csv(DATA_FILE, index=False)
        return pd.DataFrame(columns=["Date", "Description", "Amount", "Type", "Category"])

def calculate_balance(records):
    income = records[records["Type"] == "Income"]["Amount"].sum()
    expenses = records[records["Type"] == "Expense"]["Amount"].sum()
    return income - expenses, income, expenses

def create_charts(records):
    income_data = records[records["Type"] == "Income"].groupby("Date")["Amount"].sum()
    expense_data = records[records["Type"] == "Expense"].groupby("Date")["Amount"].sum()

    if income_data.empty and expense_data.empty:
        st.info("No income or expense data available for plotting.")
        return
    
    # Bar chart
    fig, ax = plt.subplots()
    if not income_data.empty:
        income_data.plot(kind='bar', color='green', ax=ax, label='Income')
    if not expense_data.empty:
        expense_data.plot(kind='bar', color='red', ax=ax, label='Expense')
    
    ax.set_title('Income vs Expenses')
    ax.set_ylabel('Amount')
    ax.set_xlabel('Date')
    ax.legend()
    st.pyplot(fig)

    # Pie chart
    if not income_data.empty or not expense_data.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie([income_data.sum(), expense_data.sum()], 
                 labels=['Total Income', 'Total Expenses'], 
                 autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)

# Streamlit app starts here
st.title("💰 Income and Expense Tracker")

menu = ["Add Income", "Add Expense", "View Report", "Analyze", "Exit"]
choice = st.sidebar.selectbox("Select an option", menu)

if choice == "Add Income":
    st.subheader("Add Income")
    date = st.date_input("Date")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.text_input("Category")

    if st.button("Add Income"):
        if description and amount and category:
            add_record(date, description, amount, "Income", category)
            st.success(f"Income of {amount} added successfully!")
        else:
            st.error("Please provide description, amount, and category.")

elif choice == "Add Expense":
    st.subheader("Add Expense")
    date = st.date_input("Date")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.text_input("Category")

    if st.button("Add Expense"):
        if description and amount and category:
            add_record(date, description, amount, "Expense", category)
            st.success(f"Expense of {amount} added successfully!")
        else:
            st.error("Please provide description, amount, and category.")

elif choice == "View Report":
    st.subheader("Financial Report")
    records = get_records()

    if records.empty:
        st.info("No records found.")
    else:
        income, expenses, balance = calculate_balance(records)
        st.write(f"**Balance:** {income:.2f}")
        st.write(f"**Total Income:** {expenses:.2f}")
        st.write(f"**Total Expenses:** {balance:.2f}")

        st.write("### All Records")
        st.table(records)

elif choice == "Analyze":
    st.subheader("Data Analysis")
    records = get_records()

    if records.empty:
        st.info("No records found for analysis.")
    else:
        start_date = pd.to_datetime(st.date_input("Start Date", value=pd.to_datetime('2023-01-01')))
        end_date = pd.to_datetime(st.date_input("End Date", value=pd.to_datetime('2023-12-31')))

        filtered_records = records[(pd.to_datetime(records['Date']) >= start_date) & (pd.to_datetime(records['Date']) <= end_date)]

        if filtered_records.empty:
            st.info("No records found for the selected date range.")
        else:
            create_charts(filtered_records)

elif choice == "Exit":
    st.write("Thank you for using the Income and Expense Tracker!")
    st.stop()
