import nltk
import re
from pycorenlp import *
from nltk.tree import *
nlp=StanfordCoreNLP("http://localhost:9000/")

# get verb phrases
# if one "VP" node has 2 or more "VP" children then
# all child "VP" while be used as verb phrases
# since a clause may have more than one verb phrases
# ex:- he plays cricket but does not play hockey
# here two verb phrases are "plays cricket" and "does not play hockey"
#                       ROOT
#                        |
#                        S
#   _____________________|____
#  |                          VP
#  |          ________________|____
#  |         |           |         VP
#  |         |           |     ____|________
#  |         VP          |    |    |        VP
#  |     ____|_____      |    |    |    ____|____
#  NP   |          NP    |    |    |   |         NP
#  |    |          |     |    |    |   |         |
# PRP  VBZ         NN    CC  VBZ   RB  VB        NN
#  |    |          |     |    |    |   |         |
#  he plays     cricket but  does not play     hockey



AddString=""
NewStringLevel=0
CurrentTreeLevel=0
def get_verb_phrases(t):
    global AddString
    global NewStringLevel
    global CurrentTreeLevel
    verb_phrases = []
    num_children = len(t)







    num_VP = sum(1 if (t[i].label() == "VP" ) else 0 for i in range(0, num_children))


    #print(t.label(),t.leaves(),num_VP,t.height())

    # if(t.label() == "NP"):
    #     verb_phrases.extend(' '.join(t.leaves()))


    if t.label() =="VP":
        if(AddString==""):

            word_tree = ParentedTree.convert(t.left_sibling())
            if (word_tree.label() == "NP"):
                NewString = ""
                for i in word_tree.leaves():
                    AddString = AddString + " " + i
                    NewStringLevel=CurrentTreeLevel



    if t.label() != "VP" :
        for i in range(0, num_children):
            if t[i].height() > 2:
                CurrentTreeLevel+=1
                verb_phrases.extend(get_verb_phrases(t[i])) ##########3 Recurssion
                CurrentTreeLevel -= 1

            if(NewStringLevel>CurrentTreeLevel):
                AddString=""


    elif t.label() == "VP" and num_VP > 1:
        for i in range(0, num_children):
            if t[i].label() == "VP":
                if t[i].height() > 2:
                    CurrentTreeLevel += 1
                    verb_phrases.extend(get_verb_phrases(t[i]))   ##########3 Recurssion
                    CurrentTreeLevel -= 1
                if (NewStringLevel > CurrentTreeLevel):
                    AddString = ""
    else: #


        done=False
        if(AddString!=""): #######If direct sibling is NP

                    SplittedString = AddString
                    for i in t.leaves():

                        SplittedString = SplittedString + " " + i

                    verb_phrases.append(SplittedString)


                    done=True


        if(not done):
            verb_phrases.append(' '.join(t.leaves()))
            # print(verb_phrases)

    # print(verb_phrases)

    return verb_phrases



# get all clauses
def get_clause_list(sent):
    parser = nlp.annotate(sent, properties={"annotators":"parse","outputFormat": "json"})
    sent_tree = nltk.tree.ParentedTree.fromstring(parser["sentences"][0]["parse"])
    # sent_tree.draw()
    clause_level_list = ["S","SBAR","SBARQ","SINV","SQ"]
    clause_list = []
    sub_trees = []
    # sent_tree.pretty_print()

    # break the tree into subtrees of clauses using
    # clause levels "S","SBAR","SBARQ","SINV","SQ"
    for sub_tree in reversed(list(sent_tree.subtrees())):
        if sub_tree.label() in clause_level_list:
            if sub_tree.parent().label() in clause_level_list:
                continue

            if (len(sub_tree) == 1 and sub_tree.label() == "S" and sub_tree[0].label() == "VP"
                and not sub_tree.parent().label() in clause_level_list):

                continue

            sub_trees.append(sub_tree)
            del sent_tree[sub_tree.treeposition()]

    # for each clause level subtree, extract relevant simple sentence



    for t in sub_trees:
        # print(t)
        # get verb phrases from the new modified tree , Actions that are happening in the sentences

        t.draw()
        # exit()

        verb_phrases = get_verb_phrases(t)


        # update the clause_list
        for i in verb_phrases:
            clause_list.append(i)

    return clause_list

if __name__ == "__main__":
    # sent = "he plays cricket but does not play hockey"
    # sent = re.sub(r"(\.|,|\?|\(|\)|\[|\])"," ",sent)
    # clause_list = get_clause_list(sent)
    # print(clause_list)
    while (True):
        sent = input("sentence : \n ")
        sent = re.sub(r"(\.|,|\?|\(|\)|\[|\])", " ", sent)
        print(get_clause_list(sent))