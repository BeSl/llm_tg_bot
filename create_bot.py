import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import aiosqlite  
from decouple import config
from loguru import logger

from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage


logger.add(f"{config('LOG_DIR')}chat.log", format="{time} {level} {message}", level="DEBUG", rotation="100 KB", compression="zip")

# настраиваем логирование и выводим в переменную для отдельного использования в нужных местах
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=f'{config('LOG_DIR')}chat.log')
logger = logging.getLogger(__name__)

def get_index_db():
    """
    Функция для получения или создания векторной Базы-Знаний.
    Если база уже существует, она загружается из файла,
    иначе происходит чтение PDF-документов и создание новой базы.
    """
    logger.debug('...get_index_db')
    # Создание векторных представлений (Embeddings)
    logger.debug('Embeddings')
    from langchain_huggingface import HuggingFaceEmbeddings
    model_id = 'intfloat/multilingual-e5-large'
    model_kwargs = {'device': 'cpu'} # Настройка для использования CPU (можно переключить на GPU)
    # model_kwargs = {'device': 'cuda'}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs=model_kwargs
    )

    db_file_name = f'{config('RAG_DB_DIR')}/db_internal'
    
    # Загрузка векторной Базы-Знаний из файла
    logger.debug('Загрузка векторной Базы-Знаний из файла')
    file_path = db_file_name + "/index.faiss"
    import os.path
    # Проверка наличия файла с векторной Базой-Знаний
    if os.path.exists(file_path):
        logger.debug('Уже существует векторная База-знаний')
        # Загрузка существующей Базы-Знаний
        db = FAISS.load_local(db_file_name, embeddings, allow_dangerous_deserialization=True)

    return db

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_text_response(question, history):
    logger.debug('RAG generation')
    
    message_content = get_message_content(question, index_db, NUMBER_RELEVANT_CHUNKS)
    model_response = get_model_response(question, message_content, history)
    
    return model_response

def get_message_content(topic, index_db, NUMBER_RELEVANT_CHUNKS):
    """
        Функция для извлечения релевантных кусочков текста из Базы-Знаний.
        Выполняется поиск по схожести, извлекаются top-N релевантных частей.
    """
    # Similarity search
    import re
    logger.debug('...get_message_content: Similarity search')
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)
    # Форматирование извлеченных данных
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n#### {i+1} Relevant chunk ####\n' + str(doc.metadata) + '\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    logger.debug(message_content)
    return message_content


def get_model_response(topic, message_content, dialog):
    """
        Функция для генерации ответа модели на основе переданного контекста и вопроса.
        Используется LLM для создания ответа, используя переданный контекст.
    """
    logger.debug('...get_model_response')

    # Загрузка модели для обработки языка (LLM)
    logger.debug('LLM')

    # Промпт
    # rag_prompt = """Ты являешься помощником для выполнения заданий по ответам на вопросы. 
    # Вот контекст, который нужно использовать для ответа на вопрос:
    # {context} 
    # Внимательно подумайте над приведенным контекстом. 
    # Теперь просмотрите вопрос пользователя:
    # {question}
    # По указанному контексту сформулируй подробный ответ на запрос. 
    # Добавь названия файлов, по которым сформирован ответ
    # Ответ:"""

    rag_prompt = """Ты помощник программиста, помогаешь писать код.
    Вот контекст, который нужно использовать для ответа на вопрос:
    {context}    
    Вот история вашего общения:
    {hystory}
    Посмотрите вопрос пользователя и учитывая историю сформулируй ответ на вопрос:
    {question}
    По указанному контексту сформулируй подробный ответ на запрос, напиши пример программы.
    Если пишешь пример выделяй его ``` ```. Все пояснения должны быть на русском языке. 
    Ответ:"""

    # Формирование запроса для LLM
    rag_prompt_formatted = rag_prompt.format(context=message_content, question=topic, hystory=dialog)
    generation = llm.invoke([HumanMessage(content=rag_prompt_formatted)])
    model_response = generation.content
    logger.debug(model_response)
    return model_response

# model_name = "llama3.2:3b"
model_name = "qwen2.5-coder:1.5b"

NUMBER_RELEVANT_CHUNKS = 5# Количество релевантных кусков для извлечения

llm = ChatOllama(model=model_name, temperature=0.5)
llm_json_mode = ChatOllama(model=model_name, temperature=0.4, format="json")

logger.debug(msg="init complete")
# получаем список администраторов из .env
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

# инициируем объект, который будет отвечать за взаимодействие с базой данных
db_path = 'my_database.db'  # Путь к файлу базы данных SQLite
db_manager = aiosqlite.connect(db_path)

# инициируем объект бота, передавая ему parse_mode=ParseMode.HTML по умолчанию
bot = Bot(token=config('BOT_API_KEY'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# инициируем объект бота
dp = Dispatcher()
index_db = get_index_db()