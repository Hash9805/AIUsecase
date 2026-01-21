import streamlit as st
import pandas as pd
from models import Booking, Customer, get_session
from sqlalchemy import or_

def show_admin_dashboard():
    """Display admin dashboard for viewing bookings"""
    
    st.title("🔐 Admin Dashboard")
    st.markdown("---")
    
    # Get session
    session = get_session()
    
    try:
        # Fetch all bookings with customer info
        bookings = session.query(
            Booking.id,
            Customer.name,
            Customer.email,
            Customer.phone,
            Booking.booking_type,
            Booking.date,
            Booking.time,
            Booking.status,
            Booking.created_at
        ).join(Customer).order_by(Booking.created_at.desc()).all()
        
        if not bookings:
            st.info("📭 No bookings found in the system yet.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(bookings, columns=[
            'Booking ID', 'Customer Name', 'Email', 'Phone',
            'Service Type', 'Date', 'Time', 'Status', 'Created At'
        ])
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Bookings", len(df))
        
        with col2:
            confirmed = len(df[df['Status'] == 'confirmed'])
            st.metric("Confirmed", confirmed)
        
        with col3:
            unique_customers = df['Email'].nunique()
            st.metric("Unique Customers", unique_customers)
        
        with col4:
            today_bookings = df[df['Date'] == pd.Timestamp.now().strftime('%Y-%m-%d')]
            st.metric("Today's Bookings", len(today_bookings))
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_name = st.text_input("Search by Name", "")
        
        with col2:
            search_email = st.text_input("Search by Email", "")
        
        with col3:
            search_date = st.text_input("Search by Date (YYYY-MM-DD)", "")
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_name:
            filtered_df = filtered_df[filtered_df['Customer Name'].str.contains(search_name, case=False, na=False)]
        
        if search_email:
            filtered_df = filtered_df[filtered_df['Email'].str.contains(search_email, case=False, na=False)]
        
        if search_date:
            filtered_df = filtered_df[filtered_df['Date'].str.contains(search_date, na=False)]
        
        st.markdown("---")
        
        # Display bookings
        st.subheader(f"📋 Bookings ({len(filtered_df)} records)")
        
        # Style the dataframe
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Booking ID": st.column_config.NumberColumn("ID", format="%d"),
                "Status": st.column_config.TextColumn(
                    "Status",
                ),
                "Created At": st.column_config.DatetimeColumn(
                    "Created",
                    format="DD/MM/YYYY HH:mm"
                )
            }
        )
        
        # Export option
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="bookings_export.csv",
            mime="text/csv"
        )
        
        # Service-wise statistics
        st.markdown("---")
        st.subheader("📊 Service Statistics")
        
        service_counts = df['Service Type'].value_counts()
        st.bar_chart(service_counts)
        
    except Exception as e:
        st.error(f"Error loading bookings: {str(e)}")
    
    finally:
        session.close()

def show_booking_details(booking_id: int):
    """Show detailed view of a specific booking"""
    session = get_session()
    
    try:
        booking = session.query(Booking).filter_by(id=booking_id).first()
        
        if booking:
            customer = booking.customer
            
            st.subheader(f"Booking #{booking.id} Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Customer Information:**")
                st.write(f"Name: {customer.name}")
                st.write(f"Email: {customer.email}")
                st.write(f"Phone: {customer.phone}")
            
            with col2:
                st.write("**Booking Information:**")
                st.write(f"Service: {booking.booking_type}")
                st.write(f"Date: {booking.date}")
                st.write(f"Time: {booking.time}")
                st.write(f"Status: {booking.status}")
        else:
            st.warning(f"Booking #{booking_id} not found")
    
    finally:
        session.close()