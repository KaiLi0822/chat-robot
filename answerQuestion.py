import os
import sys
import faiss
import langchain
from langchain.llms import PromptLayerOpenAI, PromptLayerOpenAIChat

from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain import PromptTemplate
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import get_openai_callback
from langchain.cache import InMemoryCache
from tools.qaDatabase.qaDatabase import QaDatabase
import promptlayer
from langchain.callbacks import PromptLayerCallbackHandler

os.environ["OPENAI_API_KEY"] = "***"
promptlayer.api_key = "***"
# Set memory cache
langchain.llm_cache = InMemoryCache()

INPUT_TEMPLATE = '''
You are a Customer Support Officer of a game called "***".
context:
'{history}'
relevant questions and answers:
'{relevant_qa}'
And current question is: '{input}'
If current question includes a question of consultation time, please answer as soon as possible.
Please answer the question in Chinese taking the relevant questions and answers and the context into consideration.
'''

class AnswerQuestion:

    def __init__(self,tags=[], temperature=0.2, threshold=0.6, k=3):
        # Define the large language model we need.
        self.llm = PromptLayerOpenAIChat(model="gpt-3.5-turbo",pl_tags=tags, return_pl_id=True,temperature=temperature)
        # Define the memory pack as VectorStoreMemory
        # Initialize faiss
        # set the dimensions of the embeddings
        vectorstore = FAISS(OpenAIEmbeddings().embed_query, faiss.IndexFlatL2(1536), InMemoryDocstore({}), {})
        # Set the similarity score threshold and top k QA.
        retriever = vectorstore.as_retriever(search_type="similarity_score_threshold",
                                             search_kwargs={"score_threshold": threshold, 'k': k})
        self.memory_pack = VectorStoreRetrieverMemory(retriever=retriever)

    def __get_format(self,relevant_qa):
        """
        create format based on relevant QA
        :param relevant_qa: found from history data
        :return: prompt used by ChatGPT to generate answer
        """
        # Change our format string according to sample answer
        input_template = INPUT_TEMPLATE.replace('{relevant_qa}', relevant_qa)
        input_format = PromptTemplate(
            input_variables=['history', 'input'],
            template=input_template,
        )
        return input_format


    def get_answer(self, question,relevant_qa) -> str:
        # Thus, we have a conversation chain to integrate all these functions and parameters!
        """

        :param question: the question from users
        :param relevant_qa: history QA relevant with question
        :return: response from robot
        """
        conversation_chain = ConversationChain(
            llm=self.llm,
            memory=self.memory_pack,
            prompt=self.__get_format(relevant_qa),
            verbose=True
        )

        response = conversation_chain.predict(input=question)
        return response

if __name__ == '__main__':
    relevant_qa = "question:vip礼包 answer:您好，福利是不定期发放的呢，目前暂时没有收到福利活动通知哦"
    answerQuestion = AnswerQuestion(["BonusPackage"])
    print(answerQuestion.get_answer("月礼包",relevant_qa=relevant_qa))
