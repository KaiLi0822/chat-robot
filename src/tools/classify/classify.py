import spacy
import os


class Classify:
    def __init__(self):
        self.model = spacy.load(os.path.dirname(__file__) + "/models/model-last")

    def __highscore_key(self, dic):
        """
        in descending order of score, get the highest key and value
        :param dic: the result of classification model
        :return: the key with the highest score
        """
        lis = list(dic.items())
        lis.sort(key=lambda x: x[1],reverse=True)
        return lis[0][0],lis[0][1]


    def get_type(self, txt) -> (list,float):
        result_dic = self.model(txt).cats
        return self.__highscore_key(result_dic)


if __name__ == "__main__":
    classify = Classify()
    print(classify.get_type("***"))

    # nlp = spacy.load(r'C:\Users\asus\Desktop\data\output\model-last')
    # doc = nlp(text)
    # print(doc)
    # print(doc.cats)