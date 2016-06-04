# -*- coding:utf-8 -*-
# Author: 刘坤   最后修改时间：2016-06-04
# lexical analyse with NFA

import re

grammar_split_char = '-*-'
key_words_list = ["if", "then", "else", "elif", "for", "while", "do", "="]
math_operator = ["+", "-", "*", "/", "%"]
logical_operator = [">", "<", "=="]
limiter_list = ['\"', ';', '(', ')']
number = [str(x) for x in range(10)]
letter_list = [chr(i) for i in range(97, 123)]
key_words_dict = dict()
for index, value in enumerate(key_words_list):
    key_words_dict[value] = value # index
operator_dict = dict()
for index, value in enumerate(math_operator):
    operator_dict[value] = "MOP" # value # index + len(key_words_dict)
limiter_dict = dict()
for index, value in enumerate(logical_operator):
    limiter_dict[value] = "LOP" # value # index + len(key_words_dict) + len(operator_dict)
for index, value in enumerate(limiter_list):
    limiter_dict[value] = value # index + len(key_words_dict) + len(operator_dict)
merge_dict = dict(key_words_dict)
merge_dict.update(operator_dict)
merge_dict.update(limiter_dict)
token_table = []
reserved_table = key_words_list + logical_operator + math_operator + limiter_list
reserved_table.append("#")


# 对输入的字串进行相应归类到文法中对应的符号
def vt_symbol(char):
    if char.isdigit():
        return 'd'
    elif char.isalpha():
        return 'c'
    elif char == "#":
        return "#"
    else:
        return char


# 为每一种别的单词构造一个DFA
# 文法描述格式   A a B   三元式用空格隔开  分别为current——state  input  next  p为大写
class NFA:
    # 首条grammar表示出初态符
    def __init__(self, re_grammar, obj_string="#"):
        self.re_grammar = re_grammar
        sp_words = re_grammar[0].split(grammar_split_char)
        self.origin_state = sp_words[0]
        self.current_state = self.origin_state
        # 状态转移路径
        self.state_path = []
        self.kind = ""
        self.type = ""
        # 目标匹配的单词字串
        self.obj_string = obj_string
        self.input_index = 0
        self.is_accept = False

    def set_current_state(self, char):
        self.current_state = char
        self.input_index += 1

    # 当前输入错误，回溯
    def input_back_trace(self):
        if self.input_index >= 1:
            self.input_index -= 1

    def add_state(self, state):
        self.current_state = state
        self.state_path.append(state)

    # 状态回溯
    def state_back_trace(self):
        if len(self.state_path) > 0:
            self.state_path.pop()
            if len(self.state_path) > 0:
                self.current_state = self.state_path[-1]
        else:
            self.current_state = self.origin_state

    # 获取当前输入符号
    def get_current_input(self):
        self.input_index += 1
        return self.obj_string[self.input_index-1]

    # 分析并进行状态转移,选择合适的产生式
    def analyse(self, input_string):
        # 终结符对应
        current_input = self.get_current_input()
        temp_vt = vt_symbol(current_input)
        if temp_vt == '#':  # accept
            # token_table.append((self.kind, self.type, input_string))
            token_table.append((self.kind, input_string))
            self.is_accept = True
            return
        # 寻找可能对应的产生式,可能到达的新状态
        possible_production = []
        for i in self.re_grammar:
            sp_words = i.split(grammar_split_char)
            if sp_words[0] == self.current_state and sp_words[1] == temp_vt:
                possible_production.append(i)
        # 查找失败，当前状态错误，跳过
        if len(possible_production) == 0:
            self.state_back_trace()
            return
        # 状态转移深度优先遍历与递归、回溯
        # 下一状态输入终结符对应
        for prod in possible_production:
            # 当前状态入列,需要回溯处理
            self.state_path.append(self.current_state)
            sp_words = prod.split(grammar_split_char)
            # 非终结符对应
            vn = sp_words[2]
            self.current_state = vn
            self.analyse(input_string)
            if self.is_accept:
                return
            self.state_back_trace()
        # 当前可能状态集不符合要求，输入要回溯
        self.input_back_trace()

    def start(self, text_string):
        start_char = text_string[0]
        if vt_symbol(start_char) == 'd':
            # self.kind = "const"
            self.kind = "integer"
            self.type = "integer"
        elif vt_symbol(start_char) == '"':
            # self.kind = "const"
            self.kind = "string"
            self.type = "string"
        elif vt_symbol(start_char) == "c":
            self.kind = "id"
        self.analyse(text_string)
        if not self.is_accept:
            print(self.obj_string + " is not accepted!")


def lex_analyse(string):
    if string in key_words_dict:
        token_table.append((key_words_dict[string], string))
    elif string in operator_dict:
        token_table.append((operator_dict[string], string))
    elif string in limiter_dict:
        token_table.append((limiter_dict[string], string))


# 处理字符串中的空格
def deal_the_space_in_source(string):
    string = string.replace("\n", "")
    start_index = string.find("\"")
    next_index = string.find("\"", start_index + 1)
    string = string[0:start_index] + string[start_index:next_index].replace(" ", "空格") + string[next_index:]
    if string.find("\"", next_index+1) != -1:
        string = deal_the_space_in_source(string)
    return string


def lex_test():
    grammar = []
    words_list = []
    with open("grammar.txt") as f:
        for i in f.readlines():
            grammar.append(i.replace("\n", ""))
    with open("source.txt") as f:
        # 对输入整理，将多个连续空格整合为一个
        for i in f.readlines():
            i = i.replace("\n", "")
            i = re.sub("\s+", " ", i)
            words_list += deal_the_space_in_source(i).split(" ")
    for test_string in words_list:
        # test_string = re.sub("空格", " ",test_string)
        test_string = test_string.replace("空格", " ")
        if test_string in merge_dict:
            lex_analyse(test_string)
            continue
        test_nfa = NFA(grammar, test_string+"#")
        test_nfa.start(test_string)


#  返回词法分析的结果token表
def get_token_table():
    lex_test()
    return token_table


# 外部接口
def look_dictionary(words):
    return merge_dict.get(words, "Not found")


def get_reserved_dict():
    return reserved_table


if __name__ == "__main__":
    print(get_token_table())
    # for i in token_table:
    #    print(i)
    # print(deal_the_space_in_source("\"  \""))

