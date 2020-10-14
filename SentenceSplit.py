import nltk
import re
from pycorenlp import *
from nltk.tree import *
import copy
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
StringWithSandNPandVP=""
def get_verb_phrases(t):
    global AddString
    global NewStringLevel
    global CurrentTreeLevel
    global StringWithSandNPandVP
    verb_phrases = []
    num_children = len(t)

    # if(t.label() == "VP" and t[1].label() == "S"):
    #     print("SETTTING")
    #     t[1].set_label("VP")
    #     t.draw()




    num_VP = sum(1 if (t[i].label() == "VP" ) else 0 for i in range(0, num_children))



    #print(t.label(),t.leaves(),num_VP,t.height())

    # if(t.label() == "NP"):
    #     verb_phrases.extend(' '.join(t.leaves()))










    if t.label() =="VP":


        if(AddString==""):

            if(t.left_sibling()!=None):
                word_tree = ParentedTree.convert(t.left_sibling())
                if (word_tree.label() == "NP"):
                    NewString = ""
                    for i in word_tree.leaves():
                        AddString = AddString + " " + i
                        NewStringLevel=CurrentTreeLevel


                #### Handling the cases where we Find PRP , NP , VP (If you are one of the first ten people you will receive a gift card)

                    parent_index = t.parent_index()
                    newPP=""
                    if t._parent and parent_index > 1:
                        word_tree=ParentedTree.convert(t._parent[parent_index - 2])
                        # if(word_tree.label())
                        for i in word_tree.leaves():
                            newPP=newPP + " " + i

                        print(newPP)
                        AddString=newPP+AddString





    if t.label() != "VP" :






        for i in range(0, num_children):
            if t[i].height() > 2:
                CurrentTreeLevel+=1




                Result=get_verb_phrases(t[i])


                ###################
                if(t.label()=="S"):
                    if(i+1<num_children):
                        NextSibling=t[i+1]
                        if(NextSibling.label()=="NP"):
                            Leaves=NextSibling.leaves()
                            StringWithSandNPandVP=' '.join(Leaves)

                            if (i + 2 < num_children):
                                NextSibling = t[i + 2]
                                if (NextSibling.label() == "VP"):
                                    Leaves = NextSibling.leaves()
                                    StringWithSandNPandVP = StringWithSandNPandVP+" "+ ' '.join(Leaves)
                            StringWithSandNPandVP=" "+StringWithSandNPandVP



                    leftSibling=ParentedTree.convert(t.left_sibling())  ### Fixing the 'BY" problem by clicking on the button and accepting the terms and condition you provide your personal information to u
                    if(leftSibling !=None and leftSibling.label()=="IN"):
                        AddIN=""
                        for i in leftSibling.leaves():
                            AddIN=AddIN+i

                        Result[0]=AddIN+" "+Result[0]





                if(len(Result)>0):
                    Result[-1]=Result[-1] + StringWithSandNPandVP
                StringWithSandNPandVP=""




                ####################3





                #########################


                verb_phrases.extend(Result) ##########3 Recurssion
                CurrentTreeLevel -= 1

            if(NewStringLevel>CurrentTreeLevel):
                AddString=""



    ############33 MAJOR CHANGE , when VP dosnt have more VP , but deep inside there are structure that can be broken down.






    elif (t.label() == "VP" and num_VP > 1)   : #or (t.label()=="VP" and t[1].label()=="S")

        for i in range(0, num_children):
            if t[i].label() == "VP" : #or (len(t[i])==1 and t[i].label()=="S" and t.label()=="VP")

                if t[i].height() > 2:
                    CurrentTreeLevel += 1
                    verb_phrases.extend(get_verb_phrases(t[i]))   ##########3 Recurssion
                    CurrentTreeLevel -= 1
                if (NewStringLevel > CurrentTreeLevel):
                    AddString = ""
    else: #
        # print(t.label(), "CHECKING")
        # print(num_VP)
        #     t.draw()

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


############################ Cleaning / Postprocessing Results



    UniquePhrases=[]

    for i in range(len(verb_phrases)):  ### Handing the cases where NP has has another NP and VP (Duplicates if not cleansed). [ Since the work done by Erwin was excellent]
        flag=False
        for j in range(len(verb_phrases)):
            if(i==j): ### Ofcourse the string will match itself
                continue
            if(verb_phrases[i] in verb_phrases[j]): ### if String is being a SubString of another string , Dont add into finalList , its a duplicate/substring of another
                flag=True
                break
        if(not flag):
            UniquePhrases.append(verb_phrases[i])


    return UniquePhrases



# get all clauses
def get_clause_list(sent):
    parser = nlp.annotate(sent, properties={"annotators":"parse","outputFormat": "json"})
    sent_tree = nltk.tree.ParentedTree.fromstring(parser["sentences"][0]["parse"])
    sent_tree.draw()
    clause_level_list = ["S","SBAR","SBARQ","SINV","SQ"] #

    clause_list = []
    sub_trees = []
    ContinueAgain=False
    # sent_tree.pretty_print()

    # break the tree into subtrees of clauses using
    # clause levels "S","SBAR","SBARQ","SINV","SQ"
    for sub_tree in reversed(list(sent_tree.subtrees())):
        if(ContinueAgain and sub_tree.label()=="SBAR"):
            print(sub_tree.label(),"Continue")

            ContinueAgain=False
            continue


        if sub_tree.label() in clause_level_list:
            if sub_tree.parent().label() in clause_level_list and sub_tree.parent().label() == "S":

                continue

            if (len(sub_tree) == 1 and sub_tree.label() == "S" and sub_tree[0].label() == "VP" and sub_tree[0][0].label()!="VBZ" ### 'lets meet at 8:00'
                and not sub_tree.parent().label() in clause_level_list):
                continue





            LeftSibling=ParentedTree.convert(sub_tree.left_sibling())

            if(LeftSibling!=None and LeftSibling.label()=="IN"):

                RemoveIndex=sub_tree.parent().treeposition() + (sub_tree.parent_index()-1,)
                del sent_tree[RemoveIndex]


                sub_tree.insert(0, LeftSibling)





            ################Fixing the Case of Gabriele and Zubair are talking about the problem which they found and they are thinking of solution

            ParentNode=ParentedTree.convert(sub_tree.parent())
            if (len(sub_tree) > 1):

                if (sub_tree.label() == "S" and ParentNode.label()=="SBAR" and sub_tree[0].label()=="S"):  # and t[1].label()=="S" and t[1][0].label()=="S"

                    sub_trees.append(sub_tree[2])
                    del sent_tree[sub_tree[1].treeposition()]
                    del sent_tree[sub_tree[1].treeposition()]
                    ContinueAgain=True
                    continue



                    # RemoveIndex = sub_tree[1].parent().treeposition() + (sub_tree[1].parent_index(),)
                    # AddBranch = sub_tree[1][0]
                    # del sub_tree[RemoveIndex]
                    #
                    # print("CAme here")
                    # sub_tree.insert(0, AddBranch)
                    # sub_tree.draw()
                    # exit()

            sub_trees.append(sub_tree)
            del sent_tree[sub_tree.treeposition()]
    sub_trees.append(sent_tree) ############TESTING THIS ON




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