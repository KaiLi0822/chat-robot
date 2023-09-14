import os

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

os.environ["OPENAI_API_KEY"] = "***"
class QaDatabase:
    def __init__(self,type):
        """
        initialize search engine
        :param type: the category of input
        """
        # create vector path
        dataFile = os.path.dirname(__file__) + "/data/"+type+".csv"
        vectorPath = dataFile.rsplit("/", 1)[0] + "/" + dataFile.rsplit("/", 1)[1].split(".")[0]
        if os.path.exists(vectorPath):
            self.vectorPath = vectorPath
        else:
            self.vectorPath = self.__generate_qa_vector(dataFile)

    def __generate_qa_vector(self,dataFile):
        """
        vectorize context
        :param dataFile: context
        :return: vectorPath
        """
        # new folder to store vector
        vectorPath = dataFile.rsplit("/", 1)[0] + "/" + dataFile.rsplit("/", 1)[1].split(".")[0]
        # Load source data
        loader = CSVLoader(file_path=dataFile,
                           csv_args={'fieldnames': ['question','answer'],'delimiter': "\t"},
                           )
        # Change these data into documents
        documents = loader.load()
        # # Initialize openai's embeddings object
        embeddings = OpenAIEmbeddings()
        # Calculate the embedding vector from the document using openai's embeddings object and store it in the vector store.
        Chroma.from_documents(documents, embeddings, persist_directory=vectorPath).persist()
        return vectorPath

    def search_docs(self, question: str, top=1, threshold_score=0.2) -> str:
        """
        get the most similar QA according to the user' question
        :param top: the number of similar QA which will be returned
        :param question: question from user
        :return: the most similar QA
        """
        embeddings = OpenAIEmbeddings()
        vector_database = Chroma(persist_directory=self.vectorPath, embedding_function=embeddings)
        match_answer = vector_database.similarity_search_with_score(question, k=top)
        if len(match_answer) == 0:
            return ""
        match_score = match_answer[0][1]
        print("###score of relevant QA： "+str(match_score))
        if match_score <= threshold_score:
            return ""
        return match_answer[0][0].page_content



if __name__ == '__main__':
    qaDataBase = QaDatabase("BonusPackage")
    print(qaDataBase.search_docs("vip礼包"))