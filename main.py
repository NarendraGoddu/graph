import base64
from neo4j import GraphDatabase
import streamlit as st

url = "neo4j://localhost:7687"
username = "neo4j"
password = "data0408"

queries = {
    "How many dropouts?":
        "MATCH ()-[r:DROPS_OUT]->()"
        "RETURN count(r) AS Dropout_Count",
    "How many takes?":
        "MATCH ()-[r:TAKES]->()"
        "RETURN count(r) AS Takes_Count",
    "How many actions did a particular user do?":
        "MATCH (User:USER {ID: $userId})-[r]->() "
        "RETURN User.ID, count(r) AS User_Action_Count",
    "How many distinct target action did a particular user do?":
        "MATCH (User:USER {ID: $userId})-[r]->(t:TARGET) "
        "RETURN User.ID, count(DISTINCT t) AS Distinct_Target_Actions",
    "Time stamp when a user last did an action?":
        "MATCH (User:USER {ID: $userId})-[r]->() "
        "RETURN User.ID, max(toFloat(r.tim)) AS Last_Action_Timestamp",
    "Time stamp when a user first did an action?":
        "MATCH (User:USER {ID: $userId})-[r]->() "
        "RETURN User.ID, min(toFloat(r.tim)) AS First_Action_Timestamp",
    "Which target performed maximum times?":
        "MATCH ()-[r]->(t:TARGET) "
        "RETURN t.ID AS Target_ID, count(r) AS Action_Count "
        "ORDER BY Action_Count DESC LIMIT 1",
    "Which target performed minimum times?":
        "MATCH ()-[r]->(t:TARGET) "
        "RETURN t.ID AS Target_ID, count(r) AS Action_Count "
        "ORDER BY Action_Count ASC LIMIT 1",
    "What is minimum timestamp?":
        "MATCH ()-[r]->() "
        "RETURN min(toFloat(r.tim)) AS Minimum_Timestamp",
    "What is maximum timestamp?":
        "MATCH ()-[r]->() "
        "RETURN max(toFloat(r.tim)) AS Maximum_Timestamp",
    "Number of distinct actions between timestamp t1,t2?":
        "MATCH ()-[r]->() "
        "WHERE toFloat(r.tim) >= toFloat($t1) AND toFloat(r.tim) <= toFloat($t2) "
        "RETURN count(DISTINCT r.ID) AS Distinct_Actions",
    "Number of distinct users between timestamp t1,t2?":
        "MATCH (u:USER)-[r]->() "
        "WHERE toFloat(r.tim) >= toFloat($t1) AND toFloat(r.tim) <= toFloat($t2) "
        "RETURN count(DISTINCT u.ID) AS Distinct_Users",
    "Number of distinct targets between timestamp t1,t2?":
        "MATCH ()-[r]->(t:TARGET) "
        "WHERE toFloat(r.tim) >= toFloat($t1) AND toFloat(r.tim) <= toFloat($t2) "
        "RETURN count(DISTINCT t.ID) AS Distinct_Targets",
    "Which user did the maximum number of actions ?":
        "MATCH (User:USER)-[r]->() "
        "WITH User, count(r) AS Number_Of_Actions "
        "RETURN User.ID, Number_Of_Actions "
        "ORDER BY Number_Of_Actions DESC "
        "LIMIT 1",
    "Which user did the minimum number of actions?":
        "MATCH (User:USER)-[r]->() "
        "WITH User, count(r) AS Number_Of_Actions "
        "RETURN User.ID, Number_Of_Actions "
        "ORDER BY Number_Of_Actions ASC "
        "LIMIT 1",
    }

driver = GraphDatabase.driver(url, auth=(username, password))


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

imgm = get_img_as_base64("backm.jpg")
imgn = get_img_as_base64("backn.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64, {imgm}");
    background-size: cover;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}

[data-testid="stSidebar"] > div:first-child {{ 
    position: relative;
    overflow: hidden;
    height: 100vh; /* Set the sidebar height to the full viewport height */
}}

[data-testid="stSidebar"] > div:first-child::before {{ 
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("data:image/png;base64, {imgn}");
    background-size: cover;
    z-index: -1; /* Ensure the image is behind the sidebar content */
}}
</style>
"""


st.markdown(page_bg_img, unsafe_allow_html=True)

nav_choice = st.sidebar.radio("Navigation", ["Home", "Queries"])

if nav_choice == "Home":
    st.title("Graph Query Interface")
    st.subheader("Dataset information")
    st.write("""
    The MOOC user action dataset represents the actions taken by users on a popular MOOC platform.
    The actions are represented as a directed, temporal network. The nodes represent users and course activities (targets),
    and edges represent the actions by users on the targets. The actions have attributes and timestamps.
    To protect user privacy, we anonymize the users and timestamps are standardized to start from timestamp 0.
    Each action has a binary label, representing whether the user dropped-out of the course after this action,
    i.e., whether the student drops-out after the action. The value is 1 for drop-out actions, 0 otherwise.
    """)

elif nav_choice == "Queries":
    query_selection = st.selectbox("Select query", list(queries.keys()))
    if query_selection in ["How many actions did a particular user do?",
                           "How many distinct target action did a particular user do?",
                           "Time stamp when a user last did an action?",
                           "Time stamp when a user first did an action?"
                           ]:
        user_id = st.text_input("User ID")
    else:
        user_id = None

    if query_selection in ["Number of distinct actions between timestamp t1,t2?",
                           "Number of distinct users between timestamp t1,t2?",
                           "Number of distinct targets between timestamp t1,t2?",
                           "How many actions did a user do between timestamp t1,t2 ?",
                           "How many distinct target action did a particular user do between timestamp t1,t2 ?"]:
        t1 = st.text_input("Timestamp t1")
        t2 = st.text_input("Timestamp t2")
    else:
        t1, t2 = None, None

    if st.button("Run Query"):
        with driver.session() as session:
            if user_id is not None:
                parameters = {"userId": user_id, "t1": t1, "t2": t2}
            else:
                parameters = {"t1": t1, "t2": t2}

            query = queries[query_selection]
            result = session.run(query, **parameters).single()

        st.subheader("Result")
        if result is not None:
            st.write()
            for key, value in result.items():
                st.write(f"- {key}: {value}")
        else:
            st.write("No results found.")
