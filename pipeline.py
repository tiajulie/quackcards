import streamlit as st
import google.generativeai as genai
import json
import random
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyD-habfB4IVEaFZQ1hcJfa5wFB-z1ulotw")

# Load your data
@st.cache_data
def load_data():
    with open('motherduck_docs.json', 'r') as f:
        docs = json.load(f)
    return docs

# Generate questions using Gemini AI
def generate_question(content):
    prompt = f"""
    Based on this MotherDuck documentation:
    {content[:1000]}
    
    Create a technical support question that a customer might ask, with:
    1. The question
    2. 3 multiple choice answers (A, B, C)
    3. The correct answer (A, B, or C)
    4. Brief explanation
    
    Format the response as valid JSON with this structure:
    {{
        "question": "Your question here",
        "options": {{
            "A": "First option",
            "B": "Second option", 
            "C": "Third option"
        }},
        "correct_answer": randomly choose from ["A", "B", "C"], must be formatted as a single letter corresponding to the correct option, e.g., "A"
        "explanation": "Brief explanation of why this is correct"
    }}
    """

    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Generate content
            response = model.generate_content(prompt)
            raw_text = response.text
            print(f"Gemini raw response (attempt {attempt+1}):", raw_text)

            # Validate JSON before parsing
            if raw_text.strip().startswith('{') and raw_text.strip().endswith('}'):
                question_data = json.loads(raw_text)
                return question_data
            else:
                # Try to extract JSON substring if possible
                import re
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if match:
                    try:
                        question_data = json.loads(match.group(0))
                        return question_data
                    except Exception:
                        pass
            # If not valid, continue to next attempt
        except Exception as e:
            print(f"Error generating question (attempt {attempt+1}): {str(e)}")
            continue
    # Fallback if all attempts fail
    return {
        "question": "Error generating question. Please try again.",
        "options": {"A": "Option A", "B": "Option B", "C": "Option C"},
        "correct_answer": "A",
        "explanation": "Please generate a new question."
    }

# Streamlit UI
st.title("🦆 MotherDuck Support Training")
st.write("Generate practice questions from MotherDuck documentation to improve your technical support skills!")

# API Key input
# if 'api_key_set' not in st.session_state:
#     st.session_state.api_key_set = False

# if not st.session_state.api_key_set:
#     st.warning("Please enter your Gemini API key to get started.")
#     api_key = st.text_input("Gemini API Key:", type="password")
#     if st.button("Set API Key"):
#         if api_key:
#             genai.configure(api_key=api_key)
#             st.session_state.api_key_set = True
#             st.success("API Key set successfully!")
#             st.rerun()
#         else:
#             st.error("Please enter a valid API key.")
st.session_state.api_key_set = True

if st.session_state.api_key_set:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎲 Generate New Question", type="primary"):
            with st.spinner("Generating question..."):
                try:
                    docs = load_data()
                    random_doc = random.choice(docs)
                    question_data = generate_question(random_doc['content'])
                    
                    if question_data:
                        st.session_state['current_question'] = question_data
                        st.session_state['user_answer'] = None
                        st.session_state['show_answer'] = False
                        st.rerun()
                except FileNotFoundError:
                    st.error("Could not find 'motherduck_docs.json' file. Please make sure it exists in the same directory.")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
    
    with col2:
        if st.button("🔄 Reset"):
            for key in ['current_question', 'user_answer', 'show_answer']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Display current question
    if 'current_question' in st.session_state and st.session_state['current_question']:
        question_data = st.session_state['current_question']
        
        st.markdown("---")
        st.markdown("### Question:")
        st.write(question_data['question'])
        
        # Multiple choice options
        st.markdown("### Choose your answer:")
        options = question_data['options']
        
        # Radio buttons for answer selection
        user_answer = st.radio(
            "Select an option:",
            options=['A', 'B', 'C'],
            format_func=lambda x: f"{x}: {options[x]}",
            key="answer_radio"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Submit Answer"):
                st.session_state['user_answer'] = user_answer
                st.session_state['show_answer'] = True
                st.rerun()
        
        with col2:
            if st.button("💡 Show Answer"):
                st.session_state['show_answer'] = True
                st.rerun()
        
        # Show results
        if st.session_state.get('show_answer', False):
            correct_answer = question_data['correct_answer']
            
            if 'user_answer' in st.session_state and st.session_state['user_answer']:
                if st.session_state['user_answer'] == correct_answer:
                    st.success("🎉 Correct! Well done!")
                else:
                    st.error(f"❌ Incorrect. You selected {st.session_state['user_answer']}")
            
            st.info(f"**Correct Answer:** {correct_answer}: {options[correct_answer]}")
            
            with st.expander("📚 Explanation", expanded=True):
                st.write(question_data['explanation'])

# Instructions
with st.sidebar:
    st.markdown("## 📖 Instructions")
    st.markdown("""
    1. Make sure you have `motherduck_docs.json` in your project directory
    2. Enter your Gemini API key 
    3. Click "Generate New Question" to create a practice question
    4. Select your answer and submit
    5. Review the explanation to learn more
    
    """)
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Gemini API")