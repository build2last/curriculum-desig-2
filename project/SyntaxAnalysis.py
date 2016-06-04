# -*- coding: utf-8 -*-
# LL(1) analyse 预测表分析法，课程设计答辩过了，好好写下注释和文档，算是初次接触自动机
# 暂未处理字符串中包含空格的情况
import lexical_analysis

# 文法中的分隔符
sp_char = '-*-'
# 空表示
null_char = "#"

token_table = []
# 需要手动设定的终结符(保留字)集合
vt_table = lexical_analysis.get_reserved_dict()
vt_table += ["id", "(", ")", "integer", "string", "MOP", "LOP"]
first_dict = dict()
follow_dict = dict()
for out_vt in vt_table:
    first_dict[out_vt] = [out_vt]
select_dict = dict()
empty_table = set()
ll1_grammars = []


# table
def token_check(words):
    for i in token_table:
        if i[1] == words:
            return i[0]
    return words


# 产生式右部处理为字符列表
def get_elements_of_right_part(pro):
    right_part = pro.split(sp_char)[1]
    if "," in right_part:
        return right_part.split(",")
    return [right_part]


# 制作可以退出空的非终结符表格
def set_empty_table(out_grammars):
    grammars = list(out_grammars)
    while True:
        is_add_new = False
        try:
            for i in grammars:
                sp_words = i.split(sp_char)
                if sp_words[1] == null_char:
                    empty_table.add(sp_words[0])
                    grammars.remove(i)
                elif sp_words[1].replace("#", "").replace(",", "") == "":
                    grammars.remove(i)
            temp_grammar = list(grammars)
            for i in temp_grammar:
                temp_i = i
                new_i = ""
                for em in empty_table:
                    new_i = i.split(sp_char)[0] + sp_char + i.split(sp_char)[1].replace(em, "#")
                    i = new_i
                grammars.remove(temp_i)
                grammars.append(new_i)
                sp_words = new_i.split(sp_char)
                empty_replaced_grammar = sp_words[1].replace("#", "").replace(",", "")
                if empty_replaced_grammar == "":
                    is_add_new = True
                    empty_table.add(sp_words[0])
            # print(grammars)
            if not is_add_new:
                return
        except IndexError as e:
            print("Set empty table Exception" + str(sp_words) + str(e))


# the_token_table is Terminal set
def find_first_set(obj_char, grammars, the_token_table):
    first_set = set()
    # print("debug: obj char is " + obj_char)
    # 左部为vt
    if obj_char in the_token_table:
        return obj_char
    for i in grammars:
        sp_words = i.split(sp_char)
        if sp_words[0] != obj_char:
            continue
        # 右部有多个字符
        if "," in sp_words[1]:
            right_words = sp_words[1].split(",")
            v = sp_words[1].split(",")[0]
            # v in vt
            if v in the_token_table:
                first_set.add(v)
            # v is VN
            elif v in empty_table:
                first_set = find_first_set(v, grammars, the_token_table).remove("#")
                for next_v in right_words[1:]:
                    if next_v in empty_table:
                        first_set += find_first_set(next_v, grammars, the_token_table).remove("#")
                    else:
                        first_set += find_first_set(next_v, grammars, the_token_table)
                        break
            else:
                # V 推不出空
                first_set = find_first_set(v, grammars, the_token_table)
        # 右部只有一个字符
        else:
            v = sp_words[1]
            # v in vt
            if v in the_token_table:
                first_set.add(v)
            # v is VN
            else:
                first_set = find_first_set(v, grammars, the_token_table)
    return first_set


# follow集
def find_follow_set(obj_char, grammars, the_token_table=vt_table):
    vn = obj_char
    follow_set = []
    for pro in grammars:
        sp_words = pro.split(sp_char)
        elements = get_elements_of_right_part(pro)
        # S A #
        if vn in elements:
            if vn == elements[-1]:
                # S->A
                follow_set += follow_dict.get(sp_words[0], "")
            else:
                next_char = elements[elements.index(vn)+1]
                # S A b
                if next_char in vt_table:
                    follow_set.append(next_char)
                # S A B
                elif next_char in first_dict:
                    follow_set += (first_dict[next_char])
                # S A B C D
                for i in elements[elements.index(vn)+1:]:
                    if i in empty_table:
                        if "#" in first_dict[i]:
                            follow_set += first_dict[i]
                            follow_set.remove("#")
                    else:
                        follow_set += first_dict[i]
                        break
                    if i == elements[-1]:
                        # BCD -> #
                        if sp_words[0] == "S":
                            follow_set.append("#")
                        follow_set += find_follow_set(sp_words[0], grammars)
        else:
            continue
    if obj_char == grammars[0].split(sp_char)[0]:
        follow_set.append("#")
    if vn in follow_dict:
        follow_dict[vn] += follow_set
    else:
        follow_dict[vn] = follow_set
    return follow_set


# select集
def find_select_set(pro, the_token_table):
    select_set = []
    right_part = get_elements_of_right_part(pro)
    # E -> #
    if "#" == right_part[0]:
        select_set += follow_dict[pro.split(sp_char)[0]]
    else:
        for i in right_part:
            if i not in empty_table:
                select_set += first_dict[i]
                break
            else:
                select_set += first_dict[i]
                select_set.remove("#")
            if i == right_part[-1]:
                select_set += follow_dict[pro.split[sp_char][0]]
    if pro not in select_dict:
        select_dict[pro] = select_set


def set_first_table(words, its_first_set):
    if words not in first_dict:
        first_dict[words] = its_first_set
    else:
        return


def set_follow_table(words, its_follow_set):
    if words not in follow_dict:
        follow_dict[words] = its_follow_set
    else:
        return


# 对于需要用到的的表进行初始化
def init_table():
    global token_table
    global ll1_grammars
    token_table = lexical_analysis.get_token_table()
    grammar = []
    with open("syntax.txt") as f:
        for ir in f.readlines():
            grammar.append(ir.replace("\n", ""))
    set_empty_table(grammar)
    ll1_grammars = grammar
    with open("source.txt")as f:
        for line in f.readlines():
            sentence = []
            for words in line.replace("\n", "").split(" "):
                token = token_check(words)
                if token is None:
                    print(words)
                    print("Lexical error!")
                    return
                else:
                    sentence.append(token)
    for i in grammar:
        sp_words = i.split(sp_char)
        if sp_words[0] not in first_dict:
            set_first_table(sp_words[0], find_first_set(sp_words[0], grammar, vt_table))
    for i in grammar:
        sp_words = i.split(sp_char)
        find_follow_set(sp_words[0], grammar)
    for i in follow_dict.items():
        follow_dict[i[0]] = set(i[1])
    for gra in grammar:
        find_select_set(gra, token_table)
    # --- test for lexical
    # for i in token_table:
    #    print(i)
    #       End ---------


def show_tables(v=""):
    if v == "":
        print("----------first set--------")
        for i in first_dict.items():
            print(i)
        print("-----------follow set------")
        for i in follow_dict.items():
            print(i[0],i[1])
        print("--------select set---------")
        for i in select_dict.items():
            print(i)


# 查询select set
def select_table_find(vn, vt):
    right_part = []
    for i in select_dict.items():
        if vn == i[0].split(sp_char)[0] and vt in i[1]:
            right_part = get_elements_of_right_part(i[0])
            break
    return right_part


# 将列表倒序输出
def reverse(li):
    l = []
    for i in range(len(li)):
        l.append(li.pop())
    return l


class LL1Analyse:
    def __init__(self, grammar, sentence):
        # sentence token list
        self.left_sentence = sentence
        self.left_sentence.append("#")
        self.grammar = grammar
        self.is_accept = False
        self.used_pro = []
        # 初始状态
        self.origin_state = grammar[0].split(sp_char)[0]
        self.origin_sentence = sentence
        self.current_state = self.origin_state
        self.analyse_stack = ["#", self.origin_state]

    def analyse(self):
            # 接受！
            if self.left_sentence[0] == "#" and self.analyse_stack[-1] == "#":
                self.is_accept = True
                print("========================================")
                print("Yes!")
                print(self.origin_sentence)
                print("==============================================")
                return
            vt = self.left_sentence[0]
            right_part = select_table_find(self.current_state, vt)

            # ----show message
            print(u"语法分析栈:", self.analyse_stack)
            print(u"剩余字符串:", self.left_sentence)
            print(u"产生式右部:", right_part)
            print("---------")
            # end-------

            # loss
            if not right_part and not (self.analyse_stack[-1] == vt):
                print("==================")
                print(u"匹配失败! Fail to match", self.current_state, vt)
                print(self.origin_sentence)
                print("========================")
                return
            # 匹配
            if self.analyse_stack[-1] == vt:
                self.left_sentence = self.left_sentence[1:]
                self.current_state = self.analyse_stack[-2]
                self.analyse_stack.pop()
            else:
                if right_part[0] == "#":
                    self.analyse_stack.pop()
                    self.current_state = self.analyse_stack[-1]
                else:
                    self.current_state = right_part[0]
                    self.analyse_stack.pop()
                    self.analyse_stack += reverse(list(right_part))
            self.used_pro.append((vt, right_part))
            self.analyse()


def source_analyse():
    with open("source.txt")as f:
        for line in f.readlines():
            sentence = []
            for words in line.replace("\n", "").split(" "):
                token = token_check(words)
                if token is None:
                    print("Lexical error! unknown words", words)
                    return
                else:
                    sentence.append(token)
            ana = LL1Analyse(ll1_grammars, sentence)
            ana.analyse()


def test():
    source_analyse()

if __name__ == "__main__":
    init_table()
    # for i in ["*", "+", "(", ")"]:
    #    print(lexical_analysis.look_dictionary(i))
    # print(empty_table)
    # show_tables()
    # source_analyse()
    # show_tables()
    test()
