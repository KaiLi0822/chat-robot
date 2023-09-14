import os
class SensitiveCheck:
    def __init__(self):
        self.stop_word_set = [line.split('\n')[0] for line in open(os.path.dirname(__file__) + "/data/stopWords.txt").readlines()]
        self.sensitive_word_set = [line.split("\n")[0].split("\t") for line in open(os.path.dirname(__file__) + "/data/sensitiveWords.txt").readlines()]


    def __init_sensitive_word_map(self):
        """
        initialize the sensitive word database, build the DFA model
        :return: DFA word map
        """
        sensitiveWordMap = dict()
        for category, key in self.sensitive_word_set:
            if not isinstance(key, str) or not isinstance(category, str):
                key = str(key)
                category = str(category)

            nowMap = sensitiveWordMap
            for i in range(len(key)):
                keyChar = key[i]
                wordMap = nowMap.get(keyChar)
                if wordMap is not None:
                    nowMap = wordMap
                else:
                    newWordMap = dict()
                    newWordMap["isEnd"] = "0"
                    nowMap[keyChar] = newWordMap
                    nowMap = newWordMap
                if i == len(key) - 1:
                    nowMap["isEnd"] = "1"
                    nowMap["category"] = category
        return sensitiveWordMap

    def contain_sensitive_words(self, txt):
        """
        judge whether the txt contains sensitive word
        :param txt: input word which will be checked
        :return: contains sensitive word:true，otherwise:false
        """
        for i in range(len(txt)):
            matchFlag = self.__check_sensitive_word(txt, i)
            if matchFlag > 0:
                break
        return matchFlag > 0


    def __check_sensitive_word(self, txt,beginIndex):
        """
        judge whether the txt contains sensitive word
        :param txt:input word which will be checked
        :param beginIndex: the upper bound of the word
        :return: the length of the sensitive word, otherwise return 0
        """
        flag=False
        category=""
        matchFlag=0
        nowMap=self.__init_sensitive_word_map()
        tmpFlag=0

        for i in range(beginIndex,len(txt)):
            word = txt[i]
            if (word in self.stop_word_set or word.isspace()) and len(nowMap)<100:
                tmpFlag += 1
                continue
            nowMap=nowMap.get(word)
            if nowMap !=None:
                matchFlag+=1
                tmpFlag+=1
                if nowMap.get("isEnd")=="1":
                    flag=True
                    category=nowMap.get("category")
                    break
            else:
                break
        if matchFlag<2 or not flag:
            tmpFlag=0
        return tmpFlag