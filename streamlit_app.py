import streamlit as st
import pandas as pd
from collections import defaultdict
import html

favicon = 'https://matrioshka.com.mx/wp-content/uploads/2020/01/cropped-favicon-32x32.png'
st.set_page_config(
    page_title="Matrioshka",
    page_icon=favicon,
    initial_sidebar_state="expanded"
)

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Define a dictionary for category colors
category_colors = {
    'urgencia': 'yellow',
    'dudoso': 'violet',
    'promisión': 'lightgreen',
    'dinero': 'cyan',
    'antinatural': 'orange',
    # Other categories should also be added here
}

# Function to load and cache spam data
@st.cache_data
def load_spam_data(filename):
    df = pd.read_csv(filename)
    df_grouped = df.sort_values('score', ascending=False).drop_duplicates('frase')
    return df_grouped.set_index('frase')[['razón', 'score']].to_dict('index')

spam_data = load_spam_data('spamwords.csv')

# Function to check for spam phrases and categorize them
def check_for_spam(text, spam_data):
    found_spam_phrases = defaultdict(lambda: {'count': 0, 'score': 0, 'phrases': []})
    words = text.split()
    for word in words:
        word_lower = word.lower().strip(".,!")
        if word_lower in spam_data:
            category = spam_data[word_lower]['razón']
            score = spam_data[word_lower]['score']
            found_spam_phrases[category]['count'] += 1
            found_spam_phrases[category]['score'] += score
            found_spam_phrases[category]['phrases'].append(word)
    return found_spam_phrases

# Streamlit user interface
st.title(':nesting_dolls: SPAM WORD CHECKER EN ESPAÑOL')
st.caption(':turtle: V1.01 by Polímata.AI')
email_text = st.text_area("Enter Your Email Below")

if st.button('Check for Spam Words'):
    spam_results = check_for_spam(email_text, spam_data)
    highlighted_text = email_text
    total_score = 0  # Initialize total score

    # Apply color highlighting to the spam phrases in the text by category
    for category, details in spam_results.items():
        color = category_colors.get(category, 'grey')  # Default color if category not found
        category_score = details['score']
        total_score += category_score  # Add to total score
        for phrase in details['phrases']:
            escaped_phrase = html.escape(phrase)
            highlight_style = f"background-color: {color};"
            highlighted_text = highlighted_text.replace(phrase, f'<span style="{highlight_style}">{escaped_phrase}</span>')

    # Use Streamlit's HTML capability to render the highlighted text
    st.markdown(highlighted_text, unsafe_allow_html=True)

    # Display categorized results and total score
    for category, details in spam_results.items():
        st.write(f"{category.capitalize()} ({details['count']} occurrences, Score: {details['score']})")
        # Using a loop to write each phrase with its color
        for phrase in set(details['phrases']):
            # Ensure that the phrase is escaped properly to avoid HTML injection
            escaped_phrase = html.escape(phrase)
            color = category_colors.get(category, 'grey')
            st.markdown(f'<span style="background-color: {color};">{escaped_phrase}</span>', unsafe_allow_html=True)
    st.write(f"Total Score: {total_score}")   # Display the total score
