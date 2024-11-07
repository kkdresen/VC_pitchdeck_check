import json
import os
import streamlit as st
import PyPDF2
import plotly.graph_objects as go
from orq_ai_sdk import OrqAI

from typing import Optional

# Initialize the client
client = OrqAI(
    api_key=os.environ.get("ORQ_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3Jrc3BhY2VJZCI6IjQ2NjJlMzQyLTEyODktNGZmNS04YjUwLWI1YWQ5MzExMzNkOCIsImlhdCI6MTcyOTY5MzY5NDgwMX0.UK8t7G0ntm__supebieS8lkktgn82txf9nBAtZnj-JQ"),
    environment="production"
)

client.set_user(id=2024)

APP_TITLE = 'VC Pitchdeck Checker'

# Set up page config
st.set_page_config(APP_TITLE, page_icon="📊", layout="wide")
st.title(APP_TITLE)

# Display the image in the top-left corner of the sidebar with a custom width
st.sidebar.image("/Users/kyradresen/streamlit-map-dashboard/orq.ai_logo.png", width=150)

# Sidebar title and captions
st.sidebar.title("🎯 VC Pitchdeck Checker")
st.sidebar.caption("Made by [Orq.ai](https://orq.ai/)")

# Sidebar content for "How to Use This VC Pitchdeck Checker"
with st.sidebar.expander("**📖 How to Use This VC Pitchdeck Checker**"):
    st.markdown("""
    ### Welcome to the **VC Pitch Deck Analyzer**! 🤝

    Whether you're a first-time investor or a seasoned venture capitalist, this tool helps you evaluate pitch decks by extracting crucial information like business model, market size, and competition.

    Here's how you can use it:

    1. **Configure the Fund** – Select the fund’s focus, preferred investment stage, ticket size, sectors, and location. This helps the analyzer tailor its recommendations to align with your specific investment criteria.
    2. **Upload the Pitch Deck PDF** – Just drag and drop the pitch deck document.
    3. **Ask Your Questions** – Want to understand the market opportunity, revenue model, or team background? Type your questions below, and our AI will analyze the document and provide insights.
    4. **Review the Results** – After the analysis, get a detailed summary and responses to your questions from the model.

    We’ve designed this tool to save you time by quickly pulling key insights from lengthy pitch decks, so you can focus on making decisions.

    **Tips:** Don't hesitate to ask specific questions to dig deeper into the business and its potential. You can inquire about market trends, revenue growth, competition, and more.
    """)

    st.info("""
        This tool complements the comprehensive research and evaluation process that VCs undertake when considering investments. 
        For more detailed insights, always refer to the official documents and reports provided by startups.
    """)

    st.markdown("""
        Have suggestions or feedback? Feel free to reach out directly on [LinkedIn](https://www.linkedin.com/in/kyra-dresen-65a3191a5/)
        Your feedback is essential to keep improving the tool!

        Happy investing! 🚀
    """)

# Sidebar section for additional apps by Orq.ai
with st.sidebar.expander("**See Orq.ai's other Apps**"):
    st.caption("Pitch Deck Analysis: [App](https://sophisticated-palette.streamlit.app/) 🎈,  [Blog Post](https://blog.streamlit.io/create-a-color-palette-from-any-image/) 📝")
    st.caption("Market Research: [App](https://wordler.streamlit.app/) 🎈,  [Blog Post](https://blog.streamlit.io/the-ultimate-wordle-cheat-sheet/) 📝")
    st.caption("Investment Insights: [App](https://koffee.streamlit.app/) 🎈")

# Sidebar section for latest Snowflake release notes
with st.sidebar.expander("ℹ️ **Latest Orq.ai Release Notes**"):
    st.markdown("""Stay up to date with the latest updates and features in LLM Ops by checking out the release notes on our website [here](https://docs.orq.ai/changelog).""")
    

# Function to extract text from the uploaded PDF
def extract_pdf_text(pdf_file: Optional[bytes]) -> Optional[str]:
    if pdf_file is None:
        return None
    
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def main():

    # Create two columns: one for the file upload and chat, and another for the results
    col1, col2 = st.columns([1, 2])  # [2, 1] means 2/3 for col1 and 1/3 for col2

    with col1:
        # Left block with light purple background
        st.markdown('<div class="left-block">', unsafe_allow_html=True)

        # File uploader for the pitch deck PDF
        uploaded_file = st.file_uploader("Upload Pitch Deck (PDF)", type="pdf")
        chat_input = st.text_input("Ask a question about the pitch deck:")
        
		# Top 5 LLM models dropdown
        selected_model = st.selectbox("Top LLM Models", options=[
            "azure/llama-3.1-70B-Instruct", "azure/mistral-large", "chatgpt4o",
            "claude3.5sonnet", "gemini1.5pro"
        ])

        # Add the dropdowns for VC fund configuration
        vc_focus = st.selectbox("VC Focus", options=["B2B", "B2C", "B2G"])
        stage = st.selectbox("Stage", options=["Early-stage", "Growth"])
        ticket_size = st.selectbox("Ticket Size", options=["Up to 1M", "1M-5M"])
        sectors = st.selectbox("Sectors", options=["Enterprise Software", "AI"])
        location = st.selectbox("Location focus", options=["EU", "US"])

        st.markdown('</div>', unsafe_allow_html=True)  # Close the left block div

    # Process the uploaded file and show results in the right block
    if uploaded_file:
        st.success("PDF file uploaded successfully!")
        pdf_text = extract_pdf_text(uploaded_file)

        if pdf_text:
            # Right block for displaying Pitch Deck Analysis and chat responses
            with col2:
                st.subheader("Pitch Deck Analysis")  # Display Pitch Deck Analysis title

                # Integrate the generation API call for pitch deck analysis
                generation_analysis = client.deployments.invoke(
                    key="Pitchdeck_InfoExtraction_VCs",  # Correct model key for info extraction
                    context={"environments": []},
                    inputs={"pdf": pdf_text},
                    metadata={"custom-field-name": "custom-metadata-value"}
                )

                # Display pitch deck analysis content
                st.write(generation_analysis.choices[0].message.content)

                # Integrate generation API call for pitch deck scoring
                generation_scoring = client.deployments.invoke(
                    key="VC_pitchdeck_scoring",  # Correct model key for pitch deck scoring
                    context={
                        "environments": [],
                        "VC_model": [selected_model]  # Pass selected model in context
                    },
                    inputs={
                        "pitchdeck": pdf_text,
                        "vc_focus": vc_focus,
                        "stage": stage,
                        "location": location, 
                        "ticket_size": ticket_size,
                        "sectors": sectors
                    },
                    metadata={"custom-field-name": "custom-metadata-value"}
                )

                # Determine if model supports tool calls
                if selected_model in ["chatgpt4o", "claude3.5sonnet", "gemini1.5pro"]:
                    # Parse JSON data from tool calls
                    try:
                        scoring_data = json.loads(generation_scoring.choices[0].message.tool_calls[0].function.arguments)
                        score = scoring_data.get("score", 0)
                        explanation = scoring_data.get("explanation", "Explanation not available.")
                    except (json.JSONDecodeError, KeyError, TypeError):
                        st.error("Error parsing scoring response with tool call.")
                        score = 0
                        explanation = "Explanation not available."
                else:
                    # Parse JSON data from general content output
                    try:
                        scoring_data = json.loads(generation_scoring.choices[0].message.content)
                        score = scoring_data.get("score", 0)
                        explanation = scoring_data.get("explanation", "Explanation not available.")
                    except (json.JSONDecodeError, KeyError, TypeError):
                        st.error("Error parsing scoring response from content output.")
                        score = 0
                        explanation = "Explanation not available."

                # Gauge chart for the score
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=float(score),  # Convert score to float if needed
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}
                        ],
                    },
                    title={'text': "Pitch Deck Match Score"}
                ))

                # Display gauge chart and explanation text
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Explanation of Score:")
                st.write(explanation)

                # **Question Output Block**: Always visible, directly below the question input
                response_text = "Model's response will appear here once you ask a question."

                # Chat option response section
                if chat_input:
                    with st.spinner('Generating response...'):
                        chat_response = client.deployments.invoke(
                            key="VC_deck_chat",
                            context={"environments": []},
                            inputs={"pdf": pdf_text, "question": chat_input},
                            metadata={"custom-field-name": "custom-metadata-value"}
                        )

                    # Update the text area with the response from the model
                    response_text = chat_response.choices[0].message.content
                    st.text_area("Model's Response:", value=response_text, height=200, max_chars=None, key="chat_response_box", disabled=True)

        else:
            st.error("Could not extract text from the uploaded PDF. Please upload a different file.")
    else:
        st.info("Please upload a PDF pitch deck to get started.")

if __name__ == "__main__":
    main()