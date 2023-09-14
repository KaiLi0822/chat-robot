from tools.sensitiveCheck.sensitiveCheck import SensitiveCheck
from tools.qaDatabase.qaDatabase_v2 import QaDatabase
from answerQuestion import AnswerQuestion
from tools.classify.classify import Classify
import os

# if the answer doesn't pass the check, the times the generator can retry
RETRY_TIMES = 3
# massage: not pass check
REAL_PERSON = "###not pass the check, transfer to real-person services."
# message: quit dialog
QUIT = "###finish the conversation."
# API_KEY
os.environ["OPENAI_API_KEY"] = "***"
os.environ["PROMPTLAYER_API_KEY"] = "***"

def input_check(input_str: str) -> bool:
    """
    check the input from users
    :param input_str: the input from users
    :return: if pass the check，1-pass，0-not pass
    """
    sensitiveCheck = SensitiveCheck()
    return not sensitiveCheck.contain_sensitive_words(input_str)


def out_check(input_str: str) -> bool:
    """
    check the output from the model, now only include SensitiveCheck, can be added
    :param input_str: the output from the model
    :return: if pass the check，1-pass，0-not pass
    """
    sensitiveCheck = SensitiveCheck()
    return not sensitiveCheck.contain_sensitive_words(input_str)

def generator(question):
    """
    get the answer from robot
    :param question: the input from users
    :return: the answer from robot
    """
    # categorize the input question
    classify = Classify()
    type,score = classify.get_type(question)

    # get the most similar QA according to the category and users' question
    qaDataBase = QaDatabase(type)
    relevant_qa = qaDataBase.search_docs(question)

    # generate answer, using promptLayer note prompt
    answerQuestion = AnswerQuestion(tags=[type],relevant_qa=relevant_qa)
    return answerQuestion.get_answer(question)


def main():
    # initialize classify model
    classify = Classify()
    # the category of conversions
    type_old = ""
    # check times remained
    times = 1

    answerQuestion = None
    question = input("您好，我是***客服，请问您有什么需要帮助的吗？\n")
    while question != 'quit' and input_check(question):
        type, score = classify.get_type(question)
        print("###type： " + type)
        qaDataBase = QaDatabase(type)
        relevant_qa = qaDataBase.search_docs(question)
        print("###relevant_qa： " + relevant_qa)
        # if the type chenged, start a new conversion
        if type_old != type or answerQuestion is None:
            answerQuestion = AnswerQuestion(tags=[type])
            response = answerQuestion.get_answer(question,relevant_qa)
            type_old = type
        else:
            response = answerQuestion.get_answer(question,"")

        # check the output
        while not out_check(response) and times < RETRY_TIMES:
            print("###not pass the check，regenerate answer")
            answerQuestion = AnswerQuestion(tags=[type])
            response = answerQuestion.get_answer(question,relevant_qa)
            times += 1
        if times >= RETRY_TIMES:
            print(REAL_PERSON)
        else:
            print(response)
        question = input()
    if question == 'quit':
        print(QUIT)
    else:
        print(REAL_PERSON)


if __name__ == '__main__':
    main()




