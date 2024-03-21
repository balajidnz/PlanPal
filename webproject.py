import streamlit as st
import pandas as pd
import sqlite3
from sqlite3 import Error


def apply_styles(css):
    return f'<style>{css}</style>'
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('events.db')
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            event_name TEXT NOT NULL,
            event_date DATE NOT NULL
        )
    ''')
    conn.commit()

def create_event(conn, event_name, event_date):
    """Adds a new event entry to the database."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (event_name, event_date) values (?, ?)', (event_name, event_date))
    conn.commit()

def read_events(conn, filter_date=None):
    """Reads event entries from the database and returns a pandas DataFrame."""
    if filter_date:
        event_data = pd.read_sql_query(f"SELECT * FROM events WHERE event_date = '{filter_date}'", conn)
    else:
        event_data = pd.read_sql_query('SELECT * FROM events', conn)
    return event_data

def update_event(conn, event_id, new_event_name, new_event_date):
    """Updates the details of an event in the database."""
    cursor = conn.cursor()
    cursor.execute('UPDATE events SET event_name=?, event_date=? WHERE id=?', (new_event_name, new_event_date, event_id))
    conn.commit()

def delete_event(conn, event_id):
    """Deletes an event entry from the database."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id=?', (event_id,))
    conn.commit()

def main():

    conn = create_connection()
    if conn is not None:
        create_table(conn)  
    else:
        st.write("Error! Cannot create the database connection.")

    st.set_page_config(page_title="Plan Pal", page_icon="‍📅")

    st.sidebar.title("Plan Pal - Event Planner")

    st.title("Welcome to Plan Pal - Your Event Planner")
    st.write("Plan and manage your events easily!")

    if st.button("Light"):
        with open("./light_style.css", "r") as file:
            css = file.read()
            st.markdown(apply_styles(css), unsafe_allow_html=True)

    if st.button("Dark"):
        with open("./dark_style.css", "r") as file:
            css = file.read()
            st.markdown(apply_styles(css), unsafe_allow_html=True)

    crud_operation = st.sidebar.selectbox("Select operation", ["Create", "Read", "Update", "Delete"])

    if crud_operation == "Create":
        st.sidebar.header("Add Event")
        new_event_name = st.sidebar.text_input("Event Name")
        new_event_date = st.sidebar.date_input("Event Date")
        if st.sidebar.button("Add Event"):
            create_event(conn, new_event_name, new_event_date)
            st.sidebar.success(f"Event '{new_event_name}' created successfully")

    elif crud_operation == "Read":
        st.sidebar.header("View Events")
        filter_date = st.sidebar.date_input("Filter by Date")
        event_data = read_events(conn, filter_date)
        st.dataframe(event_data)

    elif crud_operation == "Update":
        st.sidebar.header("Update Event")
        event_id = st.sidebar.number_input("Enter Event ID to Update", min_value=1)
        new_event_name = st.sidebar.text_input("New Event Name")
        new_event_date = st.sidebar.date_input("New Event Date")
        if st.sidebar.button("Update Event"):
            update_event(conn, event_id, new_event_name, new_event_date)
            st.sidebar.success(f"Event with ID {event_id} has been updated")

    elif crud_operation == "Delete":
        st.sidebar.header("Delete Event")
        event_id = st.sidebar.number_input("Enter Event ID to Delete", min_value=1)
        if st.sidebar.button("Delete Event"):
            delete_event(conn, event_id)
            st.sidebar.success(f"Event with ID {event_id} has been deleted successfully")

    else:
        st.write("Invalid operation selected.")

    conn.close()

if __name__ == '__main__':
    main()
