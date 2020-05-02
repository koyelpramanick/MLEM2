"""
Created By: Koyel Pramanick
Date: 04/01/2020
"""

# Importing libraries
from os import path
from pandas import DataFrame


class LERS:

    def __init__(self):
        self.res_name = ""
        self.goal_col = "goal"
        self.outputFilename = ""
        self.rule = list()
        self.A_star = list()
        self.res_values = list()
        self.main_goal = None
        self.max_value = None
        self.output_file = None
        self.la_ua_option = None
        self.lowest_value = None
        self.goal_fulfilment = None
        self.integerFlag = False
        self.symbolsFlag = False
        self.K = dict()
        self.D_star = dict()
        self.uniNumberElm = dict()
        self.low_max_dict = dict()
        self.df = DataFrame()
        self.TG = DataFrame(columns=['index', 'a_v'])

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will read LERS format file and convert the data into Pandas Dataframe.
    """

    def createDF(self, file):
        LERS_file = open(file, 'r')
        col_len = None
        COL = False
        columns = []
        rows = []

        try:
            for line in LERS_file.readlines():
                if line[0] == '[':
                    if not COL:
                        line = line[line.index('[ ') + len('[ '):line.index(' ]')]
                        columns = line.strip().split(' ')
                        col_len = len(columns)
                        COL = True
                    else:
                        raise Exception('Multiple Columns Present')
                elif line[0] != '<' and line[0] != '!':
                    line = line.strip()
                    rows.append(line.split(' ')[0:col_len])
        except Exception as e:
            print('Error : ', e)
            quit()

        if columns and rows:
            self.df = DataFrame(rows, columns=columns)
        print(self.df)
        LERS_file.close()

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will find the Result Column Name and Distinct Result (e.g. Trip: [Yes, No, Maybe])
    """

    def result_column(self):
        res_col = self.df[self.df.columns[-1:]].copy()
        self.res_name = res_col.columns[0]
        self.res_values = list(res_col[res_col.columns[0]].unique())
        print('\nResult Column : ', self.res_name)
        print('Distinct Result:  : ', self.res_values)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will find Lower Approximation and Upper Approximation.
    """

    def lower_upper_approximation_with_symbols(self, value):
        ldf = self.df.index[self.df[self.res_name] == value].tolist()
        la = None
        ua = None

        tmp1 = []
        tmp2 = []
        for idx in ldf:
            item_set = self.K[idx]
            if item_set.issubset(set(ldf)):
                tmp1.append(item_set)
            tmp2.append(item_set)

        if tmp1:
            la = set.union(*tmp1)
        if tmp2:
            ua = set.union(*tmp2)
        print('Lower Approximation: ', la)
        print('Upper Approximation: ', ua)

        return la, ua

    # ------------------------------------------------------------------------------------------------------------------

    """
    This function will find Lower Approximation and Upper Approximation.
    """

    def lower_upper_approximation(self, value):
        ldf = self.df[self.df[self.res_name] == value].copy()
        ldf = ldf[ldf.columns[:-1]]
        rest_df = self.df[self.df[self.res_name] != value].copy()
        rest_df = rest_df[rest_df.columns[:-1]]
        la = []
        ua = []
        for i1, r1 in ldf.iterrows():
            found = False
            for i2, r2 in rest_df.iterrows():
                if list(r1) == list(r2):
                    ua.append(i2)
                    found = True
            if not found:
                la.append(i1)
            ua.append(i1)

        la = set(la)
        ua = set(ua)
        print('Lower Approximation: ', la)
        print('Upper Approximation: ', ua)
        return la, ua

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to check whether the passed argument is zero or int or float or string.
    """

    @staticmethod
    def check_float_int_str(item):
        try:
            item = float(item)
            if item == 0:
                return '0'
            if item.is_integer():
                return int(item)
            else:
                return item
        except ValueError:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will check whether a number or symbols are present in the dataframe.
    """

    def check_for_integer_and_symbols_in_dataframe(self):
        number_count = set()
        for column in self.df[self.df.columns[:-1]]:
            for item in self.df[column]:
                res = self.check_float_int_str(item)
                if res:
                    if res == '0':
                        number_count.add(0)
                    else:
                        number_count.add(res)
                elif (item[0] == '*') or (item[0] == '?') or (item[0] == '-'):
                    self.symbolsFlag = True

        if len(number_count) > 2:
            self.integerFlag = True

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will check whether a number or symbols are present in the dataframe column.
    """

    def check_for_integer_and_symbols(self, column):
        number_count = set()
        for item in self.df[column]:
            res = self.check_float_int_str(item)
            if res:
                if res == '0':
                    number_count.add(0)
                else:
                    number_count.add(res)
            elif (item[0] == '*') or (item[0] == '?') or (item[0] == '-'):
                self.symbolsFlag = True

        if len(number_count) > 2:
            return True
        else:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will take the average of unique consecutive numbers in ascending order in a column and string value.
    """

    def avg_numbers_and_uniqueString_list(self, column):
        unique_number = []
        number_list = set()
        strings_list = set()

        for idx, item in enumerate(self.df[column]):
            res = self.check_float_int_str(item)
            if res:
                if res == '0':
                    number_list.add(0)
                else:
                    number_list.add(res)
            elif type(item) == str and (item[0] != '*' and item[0] != '?' and item[0] != '-'):
                strings_list.add(item)

        strings_list = list(strings_list)

        if number_list:
            number_list = list(sorted(number_list))
            self.lowest_value, self.max_value = str(number_list[0]), str(number_list[-1])

            unique_number = list()
            for i, j in zip(number_list[:-1], number_list[1:]):
                un = round(self.check_float_int_str((i + j) / 2), 2)
                unique_number.append(str(number_list[0]) + '..' + str(un))
                unique_number.append(str(un) + '..' + str(number_list[-1]))

        return unique_number, strings_list

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will check for dash value and replace the dash to corresponded value.
    """

    def check_for_dash(self):
        all_columns = self.df.columns.tolist()[0:-1]

        for col in all_columns:

            df1 = self.df.loc[self.df[col].str.contains('-')].copy()
            if not df1.empty:
                temp_res = df1[self.res_name].unique().tolist()
                value = set()
                for each_res in temp_res:
                    value.update(set(self.df[self.df[self.res_name] == each_res][col]))
                    value.discard('*')
                    value.discard('?')
                    value.discard('-')
                    dash_rep_value = '_'.join(value)
                    if not dash_rep_value:
                        dash_rep_value = None
                    self.df[col] = self.df[col].replace("-", dash_rep_value)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will create T(G) - Set of relevant attribute value pair.
    """

    def createTG(self):
        TG = dict()

        for col in self.df[self.df.columns[:-1]]:

            if self.check_for_integer_and_symbols(col):
                unique_number, strings_list = self.avg_numbers_and_uniqueString_list(col)

                if unique_number:
                    self.uniNumberElm[col] = unique_number
                    for elm in unique_number:
                        i, j = elm.split('..')
                        i, j = float(i), float(j)

                        index = list()
                        for idx, item in enumerate(self.df[col]):
                            res = self.check_float_int_str(item)
                            if res == '0':
                                if i <= 0 <= j:
                                    index.append(idx)
                            elif (res and (i <= res <= j)) or (item[0] == '*'):
                                index.append(idx)
                        TG[col + ',' + elm] = set(index)

                if strings_list:
                    for elm in strings_list:
                        ind = self.df.index[self.df[col].str.contains(elm + '|\\*')].tolist()
                        TG[col + ',' + elm] = set(ind)

            else:
                uniq_elm = self.df[col].unique()
                for elm in uniq_elm:
                    ind = self.df.index[self.df[col] == elm].tolist()
                    TG[col + ',' + elm] = set(ind)

        self.TG['index'] = TG.keys()
        self.TG['a_v'] = TG.values()
        print('\nT{G} :')
        print(self.TG)
        print("#" * 100)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will create T(G) - Set of relevant attribute value pair when symbols are present in data-sets.
    """

    def createTG_withSymbols(self):
        TG = dict()
        for col in self.df[self.df.columns[:-1]]:

            uniq_elm = self.df[col].unique().tolist()
            if "*" in uniq_elm:
                uniq_elm.remove('*')
            if "?" in uniq_elm:
                uniq_elm.remove('?')
            if "-" in uniq_elm:
                uniq_elm.remove('-')

            for elm in uniq_elm:
                ind = self.df.index[self.df[col].str.contains(elm + '|\\*')].tolist()
                TG[col + ',' + elm] = set(ind)

        self.TG['index'] = TG.keys()
        self.TG['a_v'] = TG.values()
        print('\nT{G} :')
        print(self.TG)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will recreate TG dataframe if both numbers and symbols are present in the data-sets.
    """

    def reCreateTG(self):
        index = self.TG['index'].tolist()
        val_dict = dict()
        str_list = dict()
        for i, idx in enumerate(index):
            v, num = idx.split(",")
            res = self.check_float_int_str(num)
            if res:
                if res == '0':
                    res = 0
                if v in val_dict:
                    val_dict[v].append(res)
                else:
                    val_dict[v] = [res]
            else:
                str_list[idx] = self.TG.loc[i]["a_v"]

        unique_number = dict()

        for key, value in val_dict.items():
            value = sorted(value)
            self.low_max_dict[key] = [str(value[0]), str(value[-1])]

            for i, j in zip(value[:-1], value[1:]):
                un = round(self.check_float_int_str((i + j) / 2), 2)
                x, y, z = value[0], un, value[-1]
                indices_xy = []
                indices_yz = []
                for idx, item in enumerate(self.df[key]):
                    res = self.check_float_int_str(item)
                    if res == '0':
                        if x <= 0 <= y:
                            indices_xy.append(idx)
                        if y <= 0 <= z:
                            indices_yz.append(idx)
                    else:
                        if (res and (x <= res <= y)) or (item[0] == '*'):
                            indices_xy.append(idx)
                        if (res and (y <= res <= z)) or (item[0] == '*'):
                            indices_yz.append(idx)
                unique_number[key + "," + str(x) + ".." + str(y)] = set(indices_xy)
                unique_number[key + "," + str(y) + ".." + str(z)] = set(indices_yz)

        unique_number.update(str_list)
        self.TG = self.TG.iloc[0:0]

        self.TG['index'] = unique_number.keys()
        self.TG['a_v'] = unique_number.values()
        print('\nT{G} :')
        print(self.TG)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will find characteristic sets.
    """

    def characteristic_sets(self):
        df = self.df[self.df.columns[:-1]].copy()
        cols = self.df.columns[:-1].tolist()

        for idx, row in df.iterrows():
            row = list(row)
            temp = []
            for item, col in zip(row, cols):
                if "_" not in item:
                    if ("*" not in item) and ("?" not in item) and ("-" not in item):
                        index = col + ',' + item
                        t = self.TG.loc[self.TG['index'] == index]['a_v'].item()
                        temp.append(t)
                else:
                    item = item.split("_")
                    tmp = []
                    for i in item:
                        if ("*" not in i) and ("?" not in i) and ("-" not in i):
                            index = col + ',' + i
                            t = self.TG.loc[self.TG['index'] == index]['a_v'].item()
                            tmp.append(t)
                    temp.append(set.union(*tmp))

            self.K[idx] = set.intersection(*temp)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will find A*.
    """

    def finding_A_star(self):

        A_df = self.df[self.df.columns[:-1]].copy()
        temp = []

        for index, row in A_df.iterrows():
            row = list(row)
            add = True

            if row in temp:
                self.A_star[temp.index(row)].add(index)
                add = False

            if add:
                self.A_star.append({index})
                temp.append(row)

        print('\nA* : ', self.A_star)
        print("#" * 100)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function will find d*.
    """

    def finding_D_Star(self):

        for r_value in self.res_values:
            lst = set(self.df[self.df[self.res_name] == r_value].index)
            self.D_star[r_value] = lst

        print('d* : ', self.D_star)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to check whether the goal column is blank or not.
    """

    def goal_column_empty_orNot(self):
        for s in self.TG["goal"]:
            if s:
                return True
        return False

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to do intersection of column with lower/Upper Approximation.
    """

    def intersection(self, goal):
        set3 = []
        for value in self.TG['a_v']:
            set3.append(value & goal)
        self.TG.insert(2, self.goal_col, set3, True)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to find the largest subset, parent set and its index from current goal column
    """

    def largest_subset(self):

        largest_subset = {}
        parent_set = None
        largest_subset_index = None
        parent_set_len = 0

        for idx, value in enumerate(self.TG[self.goal_col]):
            if (len(value) > len(largest_subset)) or (
                    (len(value) == len(largest_subset)) and (len(self.TG.loc[idx]['a_v']) < parent_set_len)):
                largest_subset = value
                largest_subset_index = idx
                parent_set = self.TG.loc[idx]['a_v']
                parent_set_len = len(parent_set)

        return largest_subset, parent_set, largest_subset_index

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to make a superset value blank in goal column.
    """

    def make_superset_blank(self, parent_set):
        for ind, column_set in enumerate(self.TG['a_v']):
            if column_set.issuperset(parent_set):
                self.TG.loc[ind][self.goal_col] = set()

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to make a superset value blank in goal column.
    """

    def make_contradict_result_blank(self, subset_index):
        index = self.TG.loc[subset_index]['index'].split(',')
        index_value, index_range = index[0], index[1]

        if ".." in index_range:
            x, y = index_range.split("..")
            if self.check_float_int_str(x) and self.integerFlag:
                if not self.lowest_value and self.low_max_dict and self.integerFlag:
                    self.lowest_value = self.low_max_dict[index_value][0]

                if not self.max_value and self.low_max_dict and self.integerFlag:
                    self.max_value = self.low_max_dict[index_value][1]
                if self.lowest_value in index_range:
                    index_name = index_value + ',' + y + '..' + self.max_value
                else:
                    index_name = index_value + ',' + self.lowest_value + '..' + x

                self.TG.loc[self.TG['index'].str.contains(index_name), self.goal_col] = set()
            else:
                index_name = index_value + ','
                self.TG.loc[self.TG['index'].str.contains(index_name), self.goal_col] = set()
        else:
            index_name = index_value + ','
            self.TG.loc[self.TG['index'].str.contains(index_name), self.goal_col] = set()

    # ------------------------------------------------------------------------------------------------------------------
    """
    This is an important function all validation and rule creation happens in the function.
    """

    def check(self, goal):
        intersection_indices = []
        self.intersection(goal)
        firstFlag = True

        largest_subset, parent_set, largest_subset_index = self.largest_subset()
        while goal and self.goal_column_empty_orNot():

            if parent_set.issubset(self.main_goal):
                if parent_set == self.main_goal:
                    intersection_indices.append(largest_subset_index)
                    break
                if firstFlag:
                    intersection_indices.append(largest_subset_index)
                goal = goal - parent_set
                self.goal_fulfilment = self.goal_fulfilment - parent_set

                del self.TG[self.goal_col]
                self.check(goal)
                if self.goal_fulfilment:
                    del self.TG[self.goal_col]
                    self.check(self.goal_fulfilment)

            else:
                firstFlag = False
                old_goal = goal
                goal = goal & parent_set
                self.goal_fulfilment = self.goal_fulfilment - goal
                if not goal:
                    goal = old_goal

                intersection_indices.append(largest_subset_index)

                self.TG.loc[largest_subset_index][self.goal_col] = set()
                self.make_superset_blank(parent_set)

                self.make_contradict_result_blank(largest_subset_index)

                largest_subset, parent_set, largest_subset_index = self.largest_subset()

                parent_set = self.intersection_of_List_items(intersection_indices)

                if not parent_set:
                    intersection_indices.clear()

        if not self.check_list_presence(intersection_indices):
            self.rule.append(intersection_indices)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to check whether a particular list present inside other list
    """

    def check_list_presence(self, list_search):
        if any(lst == list_search for lst in self.rule):
            return True
        else:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to do rule shortening during the fulfilment of goal.
    """

    def check_left_right(self, s, goal):
        # print('set and goal', s, goal)
        for i in s[:-1]:
            for j in s[1:]:
                # print(self.TG.loc[i]['a_v'], '&', self.TG.loc[j]['a_v'])
                if (self.TG.loc[i]['a_v'] & self.TG.loc[j]['a_v']) == goal:
                    # print('i and j  - > ', i, j)
                    return [i, j]
        return s

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function return intersection of all list element.
    """

    def intersection_of_List_items(self, indices):
        set_list = []
        for idx in indices:
            set_list.append(self.TG.loc[idx]['a_v'])
        return set.intersection(*set_list)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is for rule shortening.
    """

    def rule_shortening_forSymbols(self, rule_set):
        ind_set = []
        if len(rule_set) > 1:
            for idx in rule_set:
                temp = rule_set.copy()
                temp.remove(idx)
                t = []
                for i in temp:
                    z = self.TG.loc[i]['a_v']
                    t.append(z)

                if self.TG.loc[idx]['a_v'].issubset(self.main_goal):
                    return [self.TG.loc[idx]['index']]

                s = set.intersection(*t)
                if s.issubset(self.main_goal):
                    item = []
                    for i in temp:
                        item.append(self.TG.loc[i]['index'])
                    return item

        if not ind_set:
            ind_set = self.rule_shortening(rule_set)
        return ind_set

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is for rule shortening.
    """

    def rule_shortening(self, rule_set):
        rule_dict = dict()
        ind_set = []

        for idx in rule_set:
            item = self.TG.loc[idx]['index']
            value, ranges = item.split(',')
            try:
                r1, r2 = ranges.split('..')
                if value in rule_dict:
                    x, y = rule_dict[value][0], rule_dict[value][1]
                    if float(x) > float(r1):
                        r1 = x
                    if float(y) < float(r2):
                        r2 = y
                rule_dict[value] = [r1, r2]
            except ValueError:
                ind_set.append(self.TG.loc[idx]['index'])
                continue

        if rule_dict:
            for k, v in rule_dict.items():
                ind_set.append(k + "," + v[0] + ".." + v[1])

        return ind_set

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to print rule-set.
    """

    def print_rule(self, value, result):
        for res in self.rule:
            c_inter = self.intersection_of_List_items(res)
            b = len(c_inter & self.D_star[result])
            c = len(c_inter)

            if self.symbolsFlag:
                res = self.rule_shortening_forSymbols(res)
            else:
                res = self.rule_shortening(res)

            a = len(res)
            rule = "(" + ") & (".join(res) + ") -> (" + self.res_name + "," + value + ")"
            header = str(a) + ',' + str(b) + ',' + str(c)
            print(header)
            print(rule)

            self.output_file.writelines(str(header) + '\n')
            self.output_file.writelines(str(rule) + '\n')

        print("#" * 100)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function is to find the rule from the lower/upper approximation.
    """

    def run_approximations(self, app, r_value):
        self.main_goal = app
        self.goal_fulfilment = app
        self.check(app)
        self.rule = [x for x in self.rule if x]
        print('Rule Indices: ', self.rule)
        self.print_rule(r_value, r_value)
        self.rule.clear()
        del self.TG[self.goal_col]

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function call run approximation based on lower and upper approximation value.
    """

    def calculation(self, SymFlag=False):
        for r_value in self.res_values:
            print('\nResult:', r_value, self.D_star[r_value])

            if not SymFlag:
                la, ua = self.lower_upper_approximation(r_value)
            else:
                la, ua = self.lower_upper_approximation_with_symbols(r_value)

            # Lower Approximation
            if self.la_ua_option == 1 and la:
                self.run_approximations(la, r_value)

            # Upper Approximation
            elif self.la_ua_option == 2 and ua:
                self.run_approximations(ua, r_value)

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function takes result output_file name and check the extension
    """

    def outputFile_Name(self):
        self.outputFilename = str(input("Enter Output Filename: "))
        if '.' not in self.outputFilename:
            self.outputFilename += '.txt'
            self.output_file = open(self.outputFilename, 'w')

    # ------------------------------------------------------------------------------------------------------------------
    """
    This function takes the file as input and calls all necessary functions to find out the rules.
    """

    def main(self):
        try:
            while True:
                file_name = input("Please Enter the File Name (From Current Directory): ")
                if path.exists(file_name):
                    self.outputFile_Name()
                    self.la_ua_option = int(input("1.Lower Approximation\n2.Upper Approximation\nEnter Your Choice:"))

                    self.createDF(file_name)
                    self.result_column()
                    self.check_for_integer_and_symbols_in_dataframe()
                    self.check_for_dash()
                    self.finding_D_Star()

                    if self.symbolsFlag:
                        self.createTG_withSymbols()
                        self.characteristic_sets()
                        if self.integerFlag:
                            self.reCreateTG()
                        self.calculation(SymFlag=True)

                    else:
                        self.finding_A_star()
                        self.createTG()
                        self.calculation()

                    self.output_file.close()
                    break
                else:
                    print("No Such File Found:")

        except Exception as e:
            print('Exception: ', e)
            print('Exception: ', e.with_traceback())
    # ------------------------------------------------------------------------------------------------------------------


# Crating object from Class
ler = LERS()
ler.main()
