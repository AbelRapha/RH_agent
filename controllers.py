import pymupdf
import time
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_community.chat_models import ChatMaritalk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain


class ParserContent():
    
    def configs_ai_model(API_KEY:str):

        llm = ChatMaritalk(
    model="sabia-3",  # Available models: sabia-2-small and sabia-2-medium
    api_key=API_KEY,  # Insert your API key here
    temperature=0.5,
    max_tokens=10000
    )
        schema =  """{
        "nome_do_cargo_da_vaga": "Qual o nome da vaga de acordo com a descrição?"},
        "requesitos_da_vaga": "Quais são os requesitos técnicos e não técnicos descritos na vaga?"},
        "qualificacoes_para_a_vaga": "Quais sãos as qualificações exigidas para a vaga?"},
        "tecnologias_necessarias_para_a_vaga": "Quais tecnologias e ferramentas requeridas na vaga?"},
        }""",

        return llm, schema

    def parser_pdf(pdf):
        # opening pdf file 

        doc = pymupdf.open(stream=pdf.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
     
    def parser_web_page(url):
        
        # Loading web page content
        loader = AsyncHtmlLoader(url)

        # data Loaded
        docs = loader.load()

        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["span"]
    )
        
        # Grab the first 1000 tokens of the site
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0, separators=["\n", " ", ""]
        )
        texts = splitter.split_documents(docs_transformed)

        return texts
    
    def create_cv_by_schema(cv_content:str, job_content:str, llm, schema, language_option):
        
        prompt_template_to_get_job_description = ChatPromptTemplate.from_messages(
            [
        ("system", "Você é um assitente de RH, agora colete as informações referente a seguinte descrição de uma vaga de trabalho com base no schema a seguir:"),
         ("human","""Informações da vaga: {job_content},
        schema: 
        "nome do cargo da vaga":"Qual o nome da vaga de acordo com a descrição?",
        "requesitos da vaga":"Quais são os requesitos técnicos e não técnicos descritos na vaga?",
        "qualificacoes para a vaga":"Quais sãos as qualificações exigidas para a vaga?",
        "tecnologias necessarias para a vaga":"Quais tecnologias e ferramentas requeridas na vaga?"
         """),
            ]
        )
        
        prompt_template_to_generate_cv = ChatPromptTemplate.from_messages(
            [
                ("system", """Você agora é um profissional de RH que é responsável por analisar currículos e conseguir fazer o os melhores curriculos com base nos requesitos de uma determinada vaga.
                 Utilize os dados da seguinte vaga para conseguir refazer o currículo de acordo os requesitos da vaga a seguir. 
                 E mantenha o princípio das experiências anteriores e projetos realizados, porém fazendo algumas modificações para que estas experiências e projetos se mostrem importantes de acordo com a descrição da vaga."""),
                 ("human","""
                 Dados da vaga: {context}
                 Dados do currículo do candidato: {cv_content}
                 Por fim, utilize uma estrutura em Markdown para formatar um novo currículo do candidato e traduza para o idioma {language}"""),
            ]
        )
        
        chain_job_description = prompt_template_to_get_job_description | llm | StrOutputParser()

        chain_cv = prompt_template_to_generate_cv | llm | StrOutputParser()

        result_chain_job_description = chain_job_description.invoke({"schema":schema,"job_content":job_content})

        return chain_cv.invoke({"language":language_option,"cv_content":cv_content, "context": result_chain_job_description})
    