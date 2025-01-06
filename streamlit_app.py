import streamlit as st

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Simple credentials (replace with secure authentication in production)
USERNAME = "admin"
PASSWORD = "password"

def login_page():
    st.title("Login")
    
    # Create a clean login form
    with st.container():
        st.markdown("### Please login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == USERNAME and password == PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        # Display credentials for testing
        st.markdown("---")
        st.markdown("#### Test Credentials:")
        st.markdown(f"Username: `{USERNAME}`")
        st.markdown(f"Password: `{PASSWORD}`")


def main():
    st.write('Hello world!')
if __name__ == "__main__":
    main()
