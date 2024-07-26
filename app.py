import streamlit as st
import time
import controllers as ct

# Page Config

st.set_page_config(page_title='RH Agent', page_icon=':robot_face:')

# Sidebar

API_KEY = st.sidebar.text_input(label="API KEY MARITRACA", type='password')

save_api_key_button = st.sidebar.button('Save')

if save_api_key_button:
    st.session_state['API_KEY'] = API_KEY
    mensage_sucecess_save_api_key = st.sidebar.success('API KEY SAVED!!', icon='✅')
    time.sleep(5)
    mensage_sucecess_save_api_key.empty()

# Header

st.session_state['url_job'] = None
st.session_state['text_cv'] = None
st.session_state['raw_text_job_description'] = None

st.header('RH Agent 🦜', divider='rainbow')

# Upload File CV

st.info(icon='ℹ️', body="The data of your CV don't will be saved in one database. Your data will stay just in a cache while you use the application.")

pdf = st.file_uploader('Upload your CV in PDF Format', type=['pdf'])

if pdf:
    text_cv = ct.ParserContent.parser_pdf(pdf)
    text_editted = st.text_area(label= 'Edit the extracted text',value=text_cv)

    url = st.checkbox(label="Link of website")
    text_of_job_description = st.checkbox('Raw Text of Job Description')
    if url:
        url_job = st.text_input(label='Link of the job description', type='default')
    if text_of_job_description:
        text_raw_job_description = st.text_area(label="Paste the job description")

    language_option = st.selectbox("Select the language to translate your CV", options=['English 🇺🇸','Spanish 🇪🇸','Portuguese 🇧🇷'])

if st.button('Load'):
    with st.spinner('Wait for it...'):
        st.session_state['url_job'] = url_job if url != False else None
        st.session_state['text_cv'] = text_editted
        st.session_state['raw_text_job_description'] = text_raw_job_description if text_of_job_description != False else None
    
        if st.session_state['url_job'] or st.session_state['raw_text_job_description'] and st.session_state['text_cv'] is not None:
            
            # Get the configs
            llm,schema = ct.ParserContent.configs_ai_model(st.session_state['API_KEY'])
            # Get the infos of the description job

            # For URL
            if st.session_state['url_job'] is not None:
                texts_web_content = ct.ParserContent.parser_web_page(st.session_state['url_job']) 
                # return cv formatted
                extracted_content = ct.ParserContent.create_cv_by_schema(cv_content= st.session_state['text_cv'],job_content= texts_web_content[0].page_content, llm=llm, schema=schema, language_option=language_option)
            # For pasted job description
            if st.session_state['raw_text_job_description'] is not None:
                # return cv formatted
                extracted_content = ct.ParserContent.create_cv_by_schema(cv_content= st.session_state['text_cv'],job_content= st.session_state['raw_text_job_description'], llm=llm, schema=schema, language_option=language_option)

            success_message = st.success(icon="✅", body="DONE!")

            st.write(extracted_content)

            time.sleep(5)
            success_message.empty()