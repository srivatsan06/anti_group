"""
Test database connection - helps diagnose connection issues
"""
import streamlit as st

st.title("Database Connection Test")

# Check if secrets exist
if 'mysql' in st.secrets:
    st.success("✓ Secrets found!")
    st.write("**Configuration:**")
    st.write(f"- Host: {st.secrets['mysql']['host']}")
    st.write(f"- Database: {st.secrets['mysql']['database']}")
    st.write(f"- User: {st.secrets['mysql']['user']}")
    st.write(f"- Port: {st.secrets['mysql'].get('port', 3306)}")
    
    # Try to connect
    if st.button("Test Connection"):
        try:
            import mysql.connector
            
            with st.spinner("Connecting..."):
                conn = mysql.connector.connect(
                    host=st.secrets['mysql']['host'],
                    user=st.secrets['mysql']['user'],
                    password=st.secrets['mysql']['password'],
                    database=st.secrets['mysql']['database'],
                    port=st.secrets['mysql'].get('port', 3306),
                    connect_timeout=10
                )
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                
                st.success(f"✅ Connected successfully!")
                st.write(f"MySQL Version: {version[0]}")
                
                cursor.close()
                conn.close()
                
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
            st.write("**Possible issues:**")
            st.write("- FreeSQLDatabase might have connection limits")
            st.write("- Check if credentials are correct")
            st.write("- Try accessing from a different IP")
else:
    st.error("❌ No secrets configured!")
    st.write("**To fix:**")
    st.write("1. Go to your app settings")
    st.write("2. Click 'Secrets'")
    st.write("3. Add:")
    st.code("""[mysql]
host = "sql8.freesqldatabase.com"
user = "sql8810071"
password = "QTS5mGlaDF"
database = "sql8810071"
port = 3306""")
