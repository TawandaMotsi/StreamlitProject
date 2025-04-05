import streamlit as st

def main():
    st.title("Dropdown Content Example")

    # Create a dropdown (selectbox)
    option = st.selectbox(
        "Select an option", 
        ["Option 1", "Option 2", "Option 3"]
    )

    # Display content based on selected option
    if option == "Option 1":
        st.subheader("You selected Option 1")
        st.write("Here is more content related to Option 1.")
        # Add more content like images, charts, etc.
        st.image("https://via.placeholder.com/150", caption="Example Image")
    elif option == "Option 2":
        st.subheader("You selected Option 2")
        st.write("Here is more content related to Option 2.")
        # Add more content for Option 2
        st.write("You could display tables, data, etc.")
    elif option == "Option 3":
        st.subheader("You selected Option 3")
        st.write("Here is more content related to Option 3.")
        # Add more content for Option 3
        st.write("This could be charts, graphs, or any other data.")
        
if __name__ == "__main__":
    main()
