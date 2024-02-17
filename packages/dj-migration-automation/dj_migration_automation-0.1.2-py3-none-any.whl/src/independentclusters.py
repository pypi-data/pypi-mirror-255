import heapq
import json
import math
import os
import random
import sys
import time
from operator import or_
from functools import reduce  # python3 required
from collections import OrderedDict, defaultdict,deque
# from turtle import up,write,down,goto
from copy import deepcopy
from itertools import permutations

from src.dao.canister_recommendation_configuration_dao import get_configuration_for_recommendation, \
    get_total_column_and_row_from_pack_grid
from src.optimised_drops_v3 import RecommendDrops

import settings
import more_itertools
import settings
import numpy as np
import pandas as pd
import logging
from itertools import permutations

logger = logging.getLogger("root")


def date_handler(obj):
    """
        @function: date_handler
        @createdBy: Manish Agarwal
        @createdDate: 7/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: date
        @purpose - Parse the date object to isoformat so that it
                    can be handled by json
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    else:
        return str(obj)

def append_dictionary_to_json_file(dict, dict_name, save_json=False, json_name=None):
    """
    This method will save(append) passed dictionary to json
    :return:
    """
    dict_to_store = {dict_name: deepcopy(dict)}
    print ("dict to store", dict_to_store)
    if save_json:
        # a = json.dumps(dict_to_store, default=date_handler)
        with open(json_name, 'a+') as fp:
            json.dump(dict_to_store, fp, default=date_handler)
    pass


class DataFrameUtil:
    """
    This class will be providing all required utilities to process our dataframe.
    """

    def __init__(self, file_name=None, df=None, debug_mode=False, columns_to_delete = None, rows_to_delete = None):
        self.file_name = file_name
        self.columns_to_delete = columns_to_delete
        self.rows_to_delete = rows_to_delete
        self.df = df
        self.is_excel_or_csv = True
        self.debug_mode = debug_mode
        self.processes_on_df()
        pass

    def read_data(self, is_excel_or_csv, file_name):
        """
        This method will read file. It will read excel if flag is 1, or it will read csv
        :param is_excel_or_csv:
        :return: df
        """
        if is_excel_or_csv:
            df = pd.read_excel(str(file_name))
        else:
            df = pd.read_csv(str(file_name))
        return  df

    def convert_dataframe_to_binaryform(self, df):
        """
        this is gonna convert dataframe into the binary format
        :return:
        """
        return df.astype(bool).astype(int)

    def converting_data_frame_to_dict_form(self, df):
        """
        This method will convert data frame into dictionary form.
        :return: dict_df
        """
        df_dict = {}
        for i in range(len(df)):
            df_dict[i] = []
            df_dict[i].append(df.iloc[i].to_dict())
        return df_dict
        pass

    def get_row_element_of_data_frame(self, df):
        """
        This method will return row elements of data frame in the form of list.
        :param df:
        :return: row_element_list
        """
        row_element_list = list(df.index.values)
        return row_element_list
        pass

    def get_column_element_of_data_frame(self, df):
        """
        This method will return colum element of data frame in the form of list.
        :param df:
        :return: colum_element_list
        """
        column_element_list = list(df)
        return column_element_list
        pass

    def get_numpy_mat_of_data_frame(self, df):
        """
        Method will return data frame in numpy form.
        :param df:
        :return: numpy_mat
        """
        return df.as_matrix()
        pass

    def get_nonzero_colum_elements_for_given_row_element_from_data_frame(self, row_element):
        """
        For given row element this method will extract list of column elements which have non zero values.
        :param row_element:
        :return: column_elements_list
        """
        return self.row_element_info_dict[row_element]
        pass

    def get_nonzero_row_elements_for_given_column_element_from_data_frame(self, column_element):
        """
        For given co
        :param df:
        :return: row_elements_list
        """
        return self.column_element_info_dict[column_element]
        pass

    def get_column_elements_info_dict(self, df_mat, row_element_list, column_element_list):
        """
        It will generate a dictionary and return it which will be in the mentioned form.
        column_info_dict = {
        column_element_0 : [list of row elements present in given column element]
        column_element_1 : [list of row elements present in given column element]
        }
        :param df_mat:
        :return: column_elements_info_dict
        """
        column_elements_info_dict = {}
        row_element_list = np.array(row_element_list)
        for num in range(df_mat.shape[1]):
            i = df_mat[:,num]
            column_elements_info_dict[column_element_list[num]] = row_element_list[np.nonzero(i)]
        return column_elements_info_dict

    def get_row_elements_info_dict(self, df_mat, row_element_list, column_element_list):
        """
        It will generate a dictionary and return it which will be in the mentioned form.
        row_info_dict = {
        row_element_0 : [list of column elements present in given row element]
        row_element_1 : [list of column elements present in given row element]
        }
        :param df_mat:
        :param row_element_list:
        :param column_elementlist:
        :return:
        """
        row_elements_info_dict = {}
        column_element_list = np.array(column_element_list)
        for num in range(df_mat.shape[0]):
            i = df_mat[num,:]
            row_elements_info_dict[row_element_list[num]] = column_element_list[np.nonzero(i)]
        return row_elements_info_dict

    def delete_list_of_columns_from_data_frame(self, df, column_list):
        """
        This method will delete list of columns from the data frame.
        :param df:
        :param column_list:
        :return: deleted_data_frame
        """
        return df.drop(column_list, axis = 1)
        pass

    def delete_list_of_rows_from_data_frame(self, df, row_list):
        """
        This method will delete list of rows from the data frame.
        :param df:
        :param row_list:
        :return: daleted_data_frame
        """
        return df.drop(row_list, axis = 0)
        pass

    def processes_on_df(self, debug_mode = True):
        """
        This method we will use to perform list of processes on dataframe
        :return:
        """
        if self.file_name:
            self.df = self.read_data(self.is_excel_or_csv, self.file_name)
        if debug_mode and self.debug_mode and True:
            print (self.df, "dataframe")
            input("enter")

        if self.columns_to_delete is not None:
            self.df = self.delete_list_of_columns_from_data_frame(self.df, self.columns_to_delete)
        if debug_mode and self.debug_mode and True:
                print ("columns to delete", self.rows_to_delete)
                print ("deleted dataframe", self.df)
                input("enter")

        if self.rows_to_delete is not None:
            self.df = self.delete_list_of_rows_from_data_frame(self.df, self.rows_to_delete)
        if debug_mode and self.debug_mode and True:
                print ("rows to delete", self.rows_to_delete)
                print ("deleted df", self.df)
                input("enter")

        self.df_binary = self.convert_dataframe_to_binaryform(self.df)
        if debug_mode and self.debug_mode and True:
            print (self.df_binary, "binary dataframe")
            input("enter")

        self.column_element_list = self.get_column_element_of_data_frame(self.df)
        if debug_mode and self.debug_mode and True:
            print ("column elements", self.column_element_list)
            print ("column_elements_shape", np.shape(self.column_element_list))
            input("clumn elements list")

        self.row_element_list = self.get_row_element_of_data_frame(self.df)
        if debug_mode and self.debug_mode and True:
            print ("row elements", self.row_element_list)
            print ("row_elements_shape", np.shape(self.row_element_list))
            input("row elements list")

        self.df_dict = self.converting_data_frame_to_dict_form(self.df)
        if debug_mode and self.debug_mode and True:
            print ("df in dict form", self.df_dict)
            print ("number of keys", len(self.df_dict.keys()))
            for i in self.df_dict.keys():
                print (i, "key of dict")
                print (self.df_dict[i], "value of dict")
            input("enter")

        self.df_binary_dict = self.converting_data_frame_to_dict_form(self.df_binary)
        if debug_mode and self.debug_mode and True:
            print ("df in dict form", self.df_binary_dict)
            print ("number of keys", len(self.df_binary_dict.keys()))
            for i in self.df_binary_dict.keys():
                print (i, "key of dict")
                print (self.df_binary_dict[i], "value of dict")
            input("enter")

        self.df_mat = self.get_numpy_mat_of_data_frame(self.df)
        if debug_mode and self.debug_mode and True:
            print ("df as numpy mat", self.df_mat)
            print ("shape", self.df_mat.shape)
            input("enter")
        pass

        self.row_element_info_dict = self.get_row_elements_info_dict(self.df_mat, self.row_element_list, self.column_element_list)
        if debug_mode and self.debug_mode and True:
            print ("row element info dict", self.row_element_info_dict)
            print ("shape", self.row_element_info_dict.keys())
            input("enter")

        self.column_element_info_dict = self.get_column_elements_info_dict(self.df_mat, self.row_element_list, self.column_element_list)
        if debug_mode and self.debug_mode and True:
            print ("column element info dict", self.column_element_info_dict)
            print ("shape", self.column_element_info_dict.keys())
            input("enter")

        pass


class RecommendCanisterToAdd(DataFrameUtil):

    def __init__(self, file_name=None, df=None, drug_canister_info_dict=None, robot_list=None):
        DataFrameUtil.__init__(self, file_name=file_name, df=df, debug_mode=False)
        self.debug_mode = False
        self.save_json = True
        self.json_name = "register.json"
        self.robot_list = robot_list
        if os.path.exists(os.getcwd()+'/'+self.json_name):
            os.remove(os.getcwd()+'/'+self.json_name)
        self.drug_canister_info_dict = drug_canister_info_dict
        append_dictionary_to_json_file(self.drug_canister_info_dict, "drug_canister_info_dict", save_json=self.save_json, json_name=self.json_name)
        self.algo_preprocess(True)

    # need to generate seperate df for each robot's distribution
    # If overall recommendation is only needed, then passing the main df would be fine and if we want to give recommendation per robot then need to be changed.
    def generate_common_packs_confusion_matrix(self):
        """
        It generates common_packs_confusion_matrix. In common pack confusion matrix each location [ci, cj] of confusion
        matrix has value of number of common packs between drug ci and cj.
        :return: common_packs_confusion_matrix
        """
        common_packs_confusion_matrix = np.zeros((len(self.column_element_list), len(self.column_element_list)))
        for i in range(len(common_packs_confusion_matrix)):
            for j in range(len(common_packs_confusion_matrix)):
                packs_a = self.get_nonzero_row_elements_for_given_column_element_from_data_frame(self.column_element_list[i])
                packs_b = self.get_nonzero_row_elements_for_given_column_element_from_data_frame(self.column_element_list[j])
                common_packs_confusion_matrix[i, j] = len(set(packs_a).intersection(set(packs_b)))
        np.fill_diagonal(common_packs_confusion_matrix, 0)
        return  common_packs_confusion_matrix

    def generate_common_drugs_confusion_matrix(self):
        """
        It generates common_drugs_confusion_matrix. In common drug confusion matrix each location [ci, cj] of confusion
        matrix has value of number of common drugs between drug ci and cj.
        :return: common_drugs_confusion_matrix
        """
        common_drugs_confusion_matrix = np.zeros((len(self.row_element_list), len(self.row_element_list)))
        print(np.shape(common_drugs_confusion_matrix))
        for i in range(len(common_drugs_confusion_matrix)):
            for j in range(len(common_drugs_confusion_matrix)):
                drugs_a = self.get_nonzero_colum_elements_for_given_row_element_from_data_frame(
                    self.row_element_list[i])
                drugs_b = self.get_nonzero_colum_elements_for_given_row_element_from_data_frame(
                    self.row_element_list[j])
                common_drugs_confusion_matrix[i, j] = len(set(drugs_a).intersection(set(drugs_b)))
        np.fill_diagonal(common_drugs_confusion_matrix, 0)
        return common_drugs_confusion_matrix
        pass

    def ordered_dict_to_recommend_canister_to_add_method0(self, common_packs_confusion_matrix):
        """
        TODO: Check code
        Recommend based on the drug with most dependent packs.
        :param common_drugs_confusion_matrix:
        :return:
        """
        dependent_packs_sum = np.sum(common_packs_confusion_matrix, axis=0)
        total_drug_quantity = np.sum(self.df, axis=0)
        total_drug_quantity_dict = dict(zip(self.column_element_list, total_drug_quantity))
        drug_dependent_packs_sum_dict = dict(zip(self.column_element_list, dependent_packs_sum))

        same_priority_value_quantity_dict = {}  # key = priority number & value = num of times same priority number occured.
        temp_rep_drug_priority_dict = {}  # key  = drug , value = priority number --->This dictionary contain those drus info which has same priority.
        required_drug_quantity_dict = {}  # key = drug , value = quantity  ---> This dictionary contains those drugs quantity info which has same priority with some drug.
        """
        Fill same_priority_value_quantity_dict
        """
        for drug, priority in drug_dependent_packs_sum_dict.items():
            if priority not in same_priority_value_quantity_dict:
                same_priority_value_quantity_dict[priority] = 0
            same_priority_value_quantity_dict[priority] += 1
        """
        Modify same_priority_value_quantity_dict & Fill temp_rep_drug_priority_dict
        """
        for drug, priority in drug_dependent_packs_sum_dict.items():
            if same_priority_value_quantity_dict[priority] < 2:
                del same_priority_value_quantity_dict[priority]
            else:
                temp_rep_drug_priority_dict[drug] = priority

        for drug, priority in temp_rep_drug_priority_dict.items():
            count = 0
            if priority in same_priority_value_quantity_dict.keys():
                prior_val = priority
                # while same_priority_value_quantity_dict[priority] != 0:
                for drug_1, priority_1 in temp_rep_drug_priority_dict.items():
                    if priority_1 == priority:
                        count = count + 1
                        required_drug_quantity_dict[drug_1] = total_drug_quantity_dict[drug_1]
                        # del temp_rep_drug_priority_dict[drug_1]
                        if count == same_priority_value_quantity_dict[priority]:
                            break
                while len(required_drug_quantity_dict) != 0:
                    min_quan = min(required_drug_quantity_dict.values())
                    for drug_id, quantity in required_drug_quantity_dict.items():
                        if quantity == min_quan:
                            drug_dependent_packs_sum_dict[drug_id] = prior_val + 0.001
                            prior_val = drug_dependent_packs_sum_dict[drug_id]
                            del required_drug_quantity_dict[drug_id]
                            break

        orderd_dict_to_recommend_canisters = OrderedDict(
            sorted(drug_dependent_packs_sum_dict.items(), key=lambda x: x[1], reverse=True))
        return orderd_dict_to_recommend_canisters
        pass

    def get_recommendation_to_add_canisters(self,ordered_dict_to_recommend_canisters=None, drug_count = -1):
        """

        :param ordered_dict_to_recommend_canisters:
        :param drug_count:
        :return:
        """
        if ordered_dict_to_recommend_canisters == None:
            ordered_dict_to_recommend_canisters = self.ordered_dict_to_recommend_canister
        drug_list = []
        for num,i in enumerate(ordered_dict_to_recommend_canisters):
            if num == drug_count:
                break
            drug_list.append(i)
        drug_list_of_tuple = []
        if self.drug_canister_info_dict:
            for drug in drug_list:
                if len(self.drug_canister_info_dict[drug]) < 2:
                    drug_list_of_tuple.append((drug, 2 - len(self.drug_canister_info_dict[drug])))
        else:
            drug_list_of_tuple = None
        append_dictionary_to_json_file(drug_list, "drug_list",
                                       save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(drug_list_of_tuple, "drug_list_of_tuple",
                                       save_json=self.save_json, json_name=self.json_name)
        return drug_list, drug_list_of_tuple
        pass

    def get_recommendation_to_add_canisters_new(self, ordered_dict_to_recommend_canisters=None, drug_count=-1,
                                                use_drug_canister_info=True):
        """

        :param ordered_dict_to_recommend_canisters:
        :param drug_count:
        :return:
        """
        if ordered_dict_to_recommend_canisters == None:
            ordered_dict_to_recommend_canisters = self.ordered_dict_to_recommend_canister
        drug_list = []
        for num,drug_id in enumerate(ordered_dict_to_recommend_canisters):
            if num == drug_count:
                break
            drug_list.append(drug_id)
        return drug_list
        pass

    ## TODO: Change this function that can work for multiple systems
    def generate_drug_list_of_tuple(self, drug_list):
        """
        Generate (drug, no of required canisters to register) tuple on daily basis looking at daily dataframe
        :param drug_list:
        :return:
        """
        drug_list_of_tuple = []
        for drug in drug_list:
            if drug not in self.drug_canister_info_dict.keys():
                # drug_list_of_tuple.append((drug, 2*len(system_id_list))
                drug_list_of_tuple.append((drug, 2))
                continue
            if len(self.drug_canister_info_dict[drug]) < 2:
                drug_list_of_tuple.append((drug, 2 - len(self.drug_canister_info_dict[drug])))
                continue
        return drug_list_of_tuple

    def generate_drug_list_of_tuple_multisystem(self, drug_required_canister_list, drug_canister_info_dict):
        """
        Generates (drug, number of required canister to register) tuple with having multiple batch data (around 15 days). It is used to recommend canister registration after every 15 days.
        :param drug_list:
        :param system_batchwise_df:
        :return:
        """
        batchwise_drug_list_of_tuple = []
        drug_canister_to_add_canister = deepcopy(drug_canister_info_dict)

        for drug_tuple in drug_required_canister_list:
            drug = drug_tuple[0]
            required_canister = drug_tuple[1]

            if drug not in drug_canister_to_add_canister:
                batchwise_drug_list_of_tuple.append((drug, required_canister))
            else:
                num_of_canisters = len(drug_canister_to_add_canister[drug])
                if(required_canister <= num_of_canisters):
                    for i in range(required_canister):
                        drug_canister_to_add_canister[drug].pop()
                else:
                    for i in range(num_of_canisters):
                        drug_canister_to_add_canister[drug].pop()
                    batchwise_drug_list_of_tuple.append((drug, required_canister - num_of_canisters))

        return batchwise_drug_list_of_tuple

    # Todo: change this function N- system
    # Instead of passing one df, we can pass multiple splitted dfs(robot-wise) and compute the samething multiple times.
    # Or give one main df, then from Result of algo, we get N-clusters for N-robots
    # todo: change this for N-robots
    def get_recommendation_to_add_canisters_truncated(self, min_percentage=5, max_percentage = 45, division=5, tolerance = 1, manual_drug_list = None, debug_mode = False):
        """
        In this method it will only show canisters which are needed to register for equal split.
        :return:
        """
        drug_list = self.get_recommendation_to_add_canisters_new()
        no_of_robots = len(self.robot_list)
        drug_list_new, canister_added_drug_id = self.get_required_drug_list(no_of_robots, drug_list)
        if debug_mode:
            print ("drug list", drug_list)
            input("enter")
            print ("manual drug list", manual_drug_list)
            input("enter")
        for percentage in range(min_percentage, max_percentage):
            if (percentage - min_percentage) % division == 0:
                print ("percentage", percentage)
                upper_boundary = int(math.floor((float(len(drug_list_new))*percentage)/100))
                # canister_added_drug_id = deepcopy(drug_list_new[0:upper_boundary])
                canister_added_drug_id.extend(drug_list_new[0:upper_boundary])
                if debug_mode:
                    print("canister added drug id", canister_added_drug_id)
                if manual_drug_list:
                    canister_added_drug_id += manual_drug_list

                # c = IndependentClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
                #                                maximum_independence_factor=3,num_of_robots=len(self.robot_list))
                #result_of_algo, loss = c.run_algorithm()

                mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id, drug_canister_info_dict=self.drug_canister_info_dict, robot_list=self.robot_list)
                result_of_algo = mria.fill_robot_distribution_info_dict()

                packs_in_cluster = []
                for cluster in result_of_algo.values():
                    packs_in_cluster.append(len(cluster['packs']))

                # packs_in_cluster = []
                # for cluster in result_of_algo:
                #     packs_in_cluster.append(len(cluster["packs"]))

                difference = abs(packs_in_cluster[0] - packs_in_cluster[1])
                print("difference", difference)
                if difference <= tolerance:
                    non_priority_drugs_list = []
                    for drug_id in drug_list_new[upper_boundary:]:
                        if drug_id in self.drug_canister_info_dict.keys():
                            if len(self.drug_canister_info_dict[drug_id]) == 0:
                                non_priority_drugs_list.append(drug_id)
                        else:
                            non_priority_drugs_list.append(drug_id)

                    priority_drug_list = drug_list_new[0:upper_boundary]
                    priority_drug_dict = OrderedDict()
                    for i in drug_list_new[0:upper_boundary]:
                        priority_drug_dict[i] = 1
                    for i in non_priority_drugs_list:
                        priority_drug_dict[i] = 0
                    drug_list_with_priority = []
                    for i,j in enumerate(drug_list_new[0:upper_boundary]):
                        drug_list_with_priority.append((j,i))
                    drug_list_with_priority.extend(non_priority_drugs_list)
                    return drug_list_new[0:upper_boundary],priority_drug_dict,self.generate_drug_list_of_tuple(deepcopy(drug_list_new[0:upper_boundary]))

                # todo: Check this strategy which is commented
                """
                Think of the proper evaluation metric to check if all clusters packs lenghts are balanced
                """
                # difference_packs_sum = 0
                # total_robots = len(self.robot_list)
                # total_packs = self.df.shape[0]
                # req_robot_packs = math.ceil(total_packs/total_robots)
                # for packlen in packs_in_cluster:
                #     difference_packs_sum =no_of_robots = len(self.robot_list) difference_packs_sum + abs(req_robot_packs - packlen)

            if debug_mode:
                input("enter")
        return drug_list[0:upper_boundary], self.generate_drug_list_of_tuple(deepcopy(drug_list[0:upper_boundary]))



    def get_recommendation_to_add_canisters_truncated_optimised(self, number_of_drugs_needed,drugs_to_register):
        """
        In this method it will only show canisters which are needed to register for equal split.
        :return:
        """
        drug_list = self.get_recommendation_to_add_canisters_new()
        drug_dict = OrderedDict()
        priority_drug_list = []
        default_split = {}
        new_split = {}
        dl = []
        no_of_robots = len(self.robot_list)

        drug_list_new,canister_added_list = self.get_required_drug_list(no_of_robots,drug_list)
        canister_added_drug_id = deepcopy(canister_added_list)

        mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
                                         drug_canister_info_dict=self.drug_canister_info_dict,
                                         robot_list=self.robot_list)
        result_of_algo = mria.fill_robot_distribution_info_dict()
        default_split['default_split'] = {'Robot-1 Pack_length': result_of_algo[0]['pack_length'],
                                          'Robot-2 pack_length': result_of_algo[1]['pack_length'],
                                          'Common packs': len(result_of_algo[0]['packs'] & result_of_algo[1]['packs'])}


        if len(drugs_to_register) > 0:
            canister_added_list.extend(drugs_to_register)
            canister_added_list = list(set(canister_added_list))
            canister_added_drug_id = deepcopy(canister_added_list)

            mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
                                             drug_canister_info_dict=self.drug_canister_info_dict,
                                             robot_list=self.robot_list)
            result_of_algo = mria.fill_robot_distribution_info_dict()

            new_split['new_split'] = {'Robot-1 Pack_length': result_of_algo[0]['pack_length'],
                                          'Robot-2 pack_length': result_of_algo[1]['pack_length'],
                                          'Common packs': len(result_of_algo[0]['packs'] & result_of_algo[1]['packs'])}
            return default_split,new_split,priority_drug_list

        elif number_of_drugs_needed is not None:
            for drug in drug_list_new[0:int(number_of_drugs_needed)]:
                if drug not in canister_added_drug_id:
                    canister_added_drug_id.append(drug)

                mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
                                                 drug_canister_info_dict=self.drug_canister_info_dict,
                                                 robot_list=self.robot_list)
                result_of_algo = mria.fill_robot_distribution_info_dict()

                packs_in_cluster = []
                for cluster in result_of_algo.values():
                    packs_in_cluster.append(len(cluster['packs']))

                # difference = abs(packs_in_cluster[0] - packs_in_cluster[1])
                drug_dict[drug] = {'Robot-1 Pack_length': result_of_algo[0]['pack_length'],
                                   'Robot-2 pack_length': result_of_algo[1]['pack_length'],
                                   'Common packs': len(result_of_algo[0]['packs'] & result_of_algo[1]['packs'])}
                priority_drug_list.append(drug)
            return default_split,drug_dict,priority_drug_list



        # if int(number_of_drugs_needed) == 0 :
        #     mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
        #                                      drug_canister_info_dict=self.drug_canister_info_dict,
        #                                      robot_list=self.robot_list)
        #     result_of_algo = mria.fill_robot_distribution_info_dict()
        #     default_split['default_split'] = {'Robot-1 Pack_length': result_of_algo[0]['pack_length'],'Robot-2 pack_length': result_of_algo[1]['pack_length'],'Common packs':len(result_of_algo[0]['packs'] & result_of_algo[1]['packs'])}
        #
        #     return default_split,priority_drug_list


        # else:
        #     for drug in drug_list_new[0:int(number_of_drugs_needed)]:
        #         if drug not in canister_added_drug_id:
        #             canister_added_drug_id.append(drug)
        #
        #         mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
        #                                          drug_canister_info_dict=self.drug_canister_info_dict,
        #                                          robot_list=self.robot_list)
        #         result_of_algo = mria.fill_robot_distribution_info_dict()
        #
        #         packs_in_cluster = []
        #         for cluster in result_of_algo.values():
        #             packs_in_cluster.append(len(cluster['packs']))
        #
        #         # difference = abs(packs_in_cluster[0] - packs_in_cluster[1])
        #         drug_dict[drug] = {'Robot-1 Pack_length': result_of_algo[0]['pack_length'],'Robot-2 pack_length': result_of_algo[1]['pack_length'],'Common packs':len(result_of_algo[0]['packs'] & result_of_algo[1]['packs'])}
        #         priority_drug_list.append(drug)
        #
        #     return drug_dict,priority_drug_list


        # for percentage in range(min_percentage, max_percentage):
        #     if (percentage - min_percentage) % division == 0:
        #         print ("percentage", percentage)
        #         upper_boundary = int(math.floor((float(len(drug_list))*percentage)/100))
        #         canister_added_drug_id = deepcopy(drug_list[0:upper_boundary])
        #         if debug_mode:
        #             print("canister added drug id", canister_added_drug_id)
        #         if manual_drug_list:
        #             canister_added_drug_id += manual_drug_list
        #
        #         # c = IndependentClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
        #         #                                maximum_independence_factor=3,num_of_robots=len(self.robot_list))
        #         #result_of_algo, loss = c.run_algorithm()
        #
        #         mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id, drug_canister_info_dict=self.drug_canister_info_dict, robot_list=self.robot_list)
        #         result_of_algo = mria.fill_robot_distribution_info_dict()
        #
        #         packs_in_cluster = []
        #         for cluster in result_of_algo.values():
        #             packs_in_cluster.append(len(cluster['packs']))
        #
        #         # packs_in_cluster = []
        #         # for cluster in result_of_algo:
        #         #     packs_in_cluster.append(len(cluster["packs"]))
        #
        #         difference = abs(packs_in_cluster[0] - packs_in_cluster[1])
        #         print("difference", difference)
        #         if difference <= tolerance:
        #             return drug_list[0:upper_boundary], self.generate_drug_list_of_tuple(deepcopy(drug_list[0:upper_boundary]))
        #
        #         # todo: Check this strategy which is commented
        #         """
        #         Think of the proper evaluation metric to check if all clusters packs lenghts are balanced
        #         """
        #         # difference_packs_sum = 0
        #         # total_robots = len(self.robot_list)
        #         # total_packs = self.df.shape[0]
        #         # req_robot_packs = math.ceil(total_packs/total_robots)
        #         # for packlen in packs_in_cluster:
        #         #     difference_packs_sum = difference_packs_sum + abs(req_robot_packs - packlen)
        #
        #     if debug_mode:
        #         input("enter")
        # return drug_list[0:upper_boundary], self.generate_drug_list_of_tuple(deepcopy(drug_list[0:upper_boundary]))


    def get_recommendation_to_add_canisters_truncated_with_priority(self, min_percentage=5, max_percentage = 45, division=5, tolerance = 5, manual_drug_list = None, debug_mode = False):
        """
        In this method it will only show canisters which are needed to register for equal split.
        :return:
        """
        drug_list = self.get_recommendation_to_add_canisters_new()
        no_of_robots = len(self.robot_list)
        drug_list_new, canister_added_drug_id = self.get_required_drug_list(no_of_robots, drug_list)
        if debug_mode:
            print ("drug list", drug_list)
            input("enter")
            print ("manual drug list", manual_drug_list)
            input("enter")
        priority_drug_dict = OrderedDict()
        for percentage in range(min_percentage, max_percentage):
            if (percentage - min_percentage) % division == 0:
                print ("percentage", percentage)
                upper_boundary = int(math.floor((float(len(drug_list_new))*percentage)/100))
                # canister_added_drug_id = deepcopy(drug_list_new[0:upper_boundary])
                canister_added_drug_id.extend(drug_list_new[0:upper_boundary])
                if debug_mode:
                    print("canister added drug id", canister_added_drug_id)
                if manual_drug_list:
                    canister_added_drug_id += manual_drug_list

                # c = IndependentClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id,
                #                                maximum_independence_factor=3,num_of_robots=len(self.robot_list))
                #result_of_algo, loss = c.run_algorithm()

                mria = MultiRobotClusterAnalysis(df=self.df, added_canister_drug_id_list=canister_added_drug_id, drug_canister_info_dict=self.drug_canister_info_dict, robot_list=self.robot_list)
                result_of_algo = mria.fill_robot_distribution_info_dict()

                packs_in_cluster = []
                for cluster in result_of_algo.values():
                    packs_in_cluster.append(len(cluster['packs']))

                common_packs_length = len(result_of_algo[0]["packs"] & result_of_algo[1]["packs"])

                # packs_in_cluster = []
                # for cluster in result_of_algo:
                #     packs_in_cluster.append(len(cluster["packs"]))

                difference = abs(packs_in_cluster[0] - packs_in_cluster[1])
                print("difference", difference)
                if difference <= tolerance and common_packs_length < tolerance:
                    non_priority_drugs_list = []
                    for drug_id in drug_list_new[upper_boundary:]:
                        if drug_id in self.drug_canister_info_dict.keys():
                            if len(self.drug_canister_info_dict[drug_id]) == 0:
                                non_priority_drugs_list.append(drug_id)
                        else:
                            non_priority_drugs_list.append(drug_id)

                    # priority_drug_list = drug_list_new[0:upper_boundary]

                    for i in drug_list_new[0:upper_boundary]:
                        priority_drug_dict[i] = 1
                    for i in non_priority_drugs_list:
                        priority_drug_dict[i] = 0
                    # drug_list_with_priority = []
                    # for i,j in enumerate(drug_list_new[0:upper_boundary]):
                    #     drug_list_with_priority.append((j,i))
                    # drug_list_with_priority.extend(non_priority_drugs_list)
                    return drug_list_new[0:upper_boundary],priority_drug_dict,self.generate_drug_list_of_tuple(deepcopy(drug_list_new[0:upper_boundary]))

                # todo: Check this strategy which is commented
                """
                Think of the proper evaluation metric to check if all clusters packs lenghts are balanced
                """
                # difference_packs_sum = 0
                # total_robots = len(self.robot_list)
                # total_packs = self.df.shape[0]
                # req_robot_packs = math.ceil(total_packs/total_robots)
                # for packlen in packs_in_cluster:
                #     difference_packs_sum =no_of_robots = len(self.robot_list) difference_packs_sum + abs(req_robot_packs - packlen)

            if debug_mode:
                input("enter")
        return drug_list[0:upper_boundary],priority_drug_dict, self.generate_drug_list_of_tuple(deepcopy(drug_list[0:upper_boundary]))



    def get_required_drug_list(self,no_of_robots,drug_list):
        if (no_of_robots != 1):
            manual_drugs_list = []
            for drug_id in drug_list:
                if drug_id in self.drug_canister_info_dict.keys():
                    if len(self.drug_canister_info_dict[drug_id]) == 0:
                        manual_drugs_list.append(drug_id)
                else:
                    manual_drugs_list.append(drug_id)

            multiple_canister_drug = []
            one_canister_list = []
            for drug_id in drug_list:
                if drug_id in self.drug_canister_info_dict.keys():
                    if len(self.drug_canister_info_dict[drug_id]) >= no_of_robots:
                        multiple_canister_drug.append(drug_id)
                    elif len(self.drug_canister_info_dict[drug_id]) < no_of_robots and len(self.drug_canister_info_dict[drug_id]) > 0:
                        one_canister_list.append(drug_id)
        else:
            manual_drugs_list = []
            multiple_canister_drug = []
        drug_list_new = deepcopy(drug_list)
        for drug in drug_list:
            if drug in multiple_canister_drug:
                drug_list_new.remove(drug)

        canister_added_list = []
        canister_added_list = multiple_canister_drug + manual_drugs_list
        # canister_added_list.extend(multiple_canister_drug)
        return drug_list_new,canister_added_list


    def fill_batch_system_drug_info_dict(self, system_batchwise_df):
        batch_system_drug_info_dict = {}
        for system_id, list_df in system_batchwise_df.items():
            batch_system_drug_info_dict[str(system_id)] = set()
            for i in range(len(system_batchwise_df[system_id])):
                batch_system_drug_info_dict[str(system_id)].update(list(system_batchwise_df[system_id][i]))

        return batch_system_drug_info_dict

    def fill_drug_system_info_dict(self, batch_system_drug_info_dict):
        batch_all_drugs = set()
        drug_system_info_dict = {}

        for system_id, drug_list in batch_system_drug_info_dict.items():
            batch_all_drugs.update(drug_list)

        for drug in batch_all_drugs:
            drug_system_info_dict[drug] = []
            for system_id, drug_list in batch_system_drug_info_dict.items():
                if(drug in drug_list):
                    drug_system_info_dict[drug].append(system_id)

        return batch_all_drugs, drug_system_info_dict

    # change this according to N- systems
    def process_system_priority_druglist_info_dict(self,system_priority_druglist_info_dict, batch_system_drug_info_dict):
        """
        To merge all 15 days priority drug lists(one priority list per system, i.e. 2 if there are 2 systems) into one single priority list
        :param system_priority_druglist_info_dict:
        :return:
        """

        # fill_system_priority_drugs_info_dict
        system_priority_drugs_info_dict = {}
        temp_system_drug_priority_dict = deepcopy(system_priority_druglist_info_dict)
        for system_id in system_priority_druglist_info_dict.keys():
            system_priority_drugs_info_dict[system_id] = []
            while(True):
                if not (all(len(temp_list) is 0 for temp_list in temp_system_drug_priority_dict[system_id])):
                    for list in temp_system_drug_priority_dict[system_id]:
                        if(len(list)!=0):
                            temp_drug = list.pop(0)
                            system_priority_drugs_info_dict[system_id].append(temp_drug)
                else:
                    break


        # remove repetition of drugs within one system (keep repetion among the different systems)
        system_final_priority_info_dict = {}
        for system_id in system_priority_druglist_info_dict:
            system_final_priority_info_dict[system_id] = []

        for system_id in system_priority_druglist_info_dict:
            [system_final_priority_info_dict[system_id].append(drug) for drug in system_priority_drugs_info_dict[system_id] if not system_final_priority_info_dict[system_id].count(drug)]

        # merge all dataframes priority list into one list
        system_priority_merged_list = []
        system_list = sorted(system_final_priority_info_dict)
        for system_id in system_list:
            system_priority_merged_list.append(system_final_priority_info_dict[system_id])

        temp_system_priority_merged_list = deepcopy(system_priority_merged_list)
        final_priority_list = []

        # Create final priority list, which contains prioritywise drugs throughout all systems.
        # Take first elements of each priority list, then take second elements of each priority list and store them to one final priority list
        while True:
            if not(all(len(temp_list) is 0 for temp_list in temp_system_priority_merged_list)):
                for list in temp_system_priority_merged_list:
                    if(len(list)!=0):
                        temp_drug = list.pop(0)
                        final_priority_list.append((temp_drug, 2))
            else:
                break

        # fill_system_drug_non_priority_info_dict
        system_drug_non_priority_info_dict = {}
        for system_id in system_list:
            system_drug_non_priority_info_dict[system_id] = []

        for system_id in system_list:
            system_drug_non_priority_info_dict[system_id].extend((set(batch_system_drug_info_dict[str(system_id)])-set(system_priority_drugs_info_dict[system_id])))

        # merge all dataframes non priority list into one list
        system_non_priority_merged_list = []
        for system_id in system_list:
            system_non_priority_merged_list.append(system_drug_non_priority_info_dict[system_id])

        temp_system_non_priority_merged_list = deepcopy(system_non_priority_merged_list)
        final_non_priority_list = []

        # create final non priority list (all drugs - priority list for each df)
        while True:
            if not(all(len(temp_list) is 0 for temp_list in temp_system_non_priority_merged_list)):
                for list in temp_system_non_priority_merged_list:
                    if(len(list)!=0):
                        temp_drug = list.pop(0)
                        final_non_priority_list.append((temp_drug, 1))
            else:
                break

        drug_required_canister_list = []
        drug_required_canister_list = final_priority_list + final_non_priority_list

        return drug_required_canister_list

    def get_manual_drug_ids(self, maximum_pack_count = 5):
        """
        Gets list of those drugs whose pack counts are less than or equals to 5.
        :param maximum_pack_count:
        :return:
        """
        manual_drug_list = []
        for drug_id in self.column_element_info_dict.keys():
            if len (self.column_element_info_dict[drug_id]) <= maximum_pack_count:
                manual_drug_list.append(drug_id)
        return manual_drug_list
        pass

    def algo_preprocess(self, debug_mode=False):
        """
        This method will perform set of pre processing for algorith,
        :return:
        """
        self.common_packs_confusion_matrix = self.generate_common_packs_confusion_matrix()
        if debug_mode and self.debug_mode and True:
            print (self.common_packs_confusion_matrix)
            input("enter")
        self.common_drugs_confusion_matrix = self.generate_common_drugs_confusion_matrix()
        if debug_mode and self.debug_mode and True:
            print (self.common_drugs_confusion_matrix)
            input("enter")
        self.ordered_dict_to_recommend_canister = self.ordered_dict_to_recommend_canister_to_add_method0(self.common_packs_confusion_matrix)
        if debug_mode and self.debug_mode and True:
            print ("ordered dict to recommend canisters", self.ordered_dict_to_recommend_canister)
            input("enter")
        pass


class RecommendCanistersToRemove:

    def __init__(self, file_name=None, df=None, robot_capacity_info_dict=None, drug_canister_info_dict=None,
                 canister_location_info_dict=None, testing_mode=False, manual_drugs_list=None, multiple_canister_drug_list=None):
        self.file_name = file_name
        self.testing_mode = testing_mode
        if not self.testing_mode:
            self.df = df
            self.dfu = DataFrameUtil(df=deepcopy(df))
        self.debug_mode = False
        self.robot_capacity_info_dict = robot_capacity_info_dict
        self.drug_canister_info_dict = drug_canister_info_dict
        self.canister_location_info_dict = canister_location_info_dict
        self.manual_drugs_list = manual_drugs_list
        self.multiple_canister_drug_list = multiple_canister_drug_list
        self.robot_id_list = None
        self.robot_canister_info_dict = None
        self.robot_drug_info_dict = None
        self.robot_cluster_info_dict = None
        self.robot_remove_drugs_dict = None
        self.canister_drug_info_dict = None
        self.robot_cluster_drug_info_dict = None
        self.robot_cluster_canister_info_dict = None
        self.save_json = True
        self.json_name = "remove.json"
        self.assert_output = False
        if os.path.exists(os.getcwd()+'/'+self.json_name):
            os.remove(os.getcwd()+'/'+self.json_name)
        # Saving data
        append_dictionary_to_json_file(self.drug_canister_info_dict, "drug_canister_info_dict", save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.robot_capacity_info_dict, "robot_capacity_info_dict", save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.canister_location_info_dict, "canister_location_info_dict", save_json=self.save_json, json_name=self.json_name)
        self.preprocess_input()
        # self.ica = IndependentClusterAnalysis(df=df, file_name=file_name, added_canister_drug_id_list=canister_added_drug_id, maximum_independence_factor=3)
        pass

    def preprocess_input(self):
        """
        This method will preprocess the input and convert it into suitable from which  can be used by the algorithms.
        It will be achieving following tasks.
        1)
        :return:
        """
        if self.manual_drugs_list is None:
            self.manual_drugs_list = self.decide_manual_fill_drug()
        append_dictionary_to_json_file(self.manual_drugs_list, "manual_drug_list", save_json=self.save_json,
                                       json_name=self.json_name)
        if self.multiple_canister_drug_list is None:
            self.multiple_canister_drug_list = self.decide_multiple_canister_drug(self.robot_capacity_info_dict)
        append_dictionary_to_json_file(self.multiple_canister_drug_list, "multiple_canister_drug_list", save_json=self.save_json, json_name=self.json_name)
        self.drugs_to_remove = self.manual_drugs_list + self.multiple_canister_drug_list
        self.robot_id_list = []
        for robot_id in self.robot_capacity_info_dict.keys():
            self.robot_id_list.append(robot_id)
        self.robot_canister_info_dict = self.fill_robot_canister_info_dict(self.robot_id_list, self.canister_location_info_dict)
        append_dictionary_to_json_file(self.robot_canister_info_dict, "robot_canister_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        self.robot_drug_info_dict = self.fill_robot_drug_info_dict(robot_canister_info_dict=self.robot_canister_info_dict,
                                                                   drug_canister_info_dict=self.drug_canister_info_dict)
        append_dictionary_to_json_file(self.robot_drug_info_dict, "robot_drug_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        self.canister_drug_info_dict = self.fill_canister_drug_info_dict()
        append_dictionary_to_json_file(self.canister_drug_info_dict, "canister_drug_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        pass

    def decide_manual_fill_drug(self):
        """

        :return:
        """
        manual_drugs_list = []
        for drug_id in self.dfu.column_element_list:
            if drug_id in self.drug_canister_info_dict.keys():
                if len(self.drug_canister_info_dict[drug_id]) == 0:
                    manual_drugs_list.append(drug_id)
            else:
                manual_drugs_list.append(drug_id)
        return manual_drugs_list
        pass

    def decide_multiple_canister_drug(self, robot_capacity_info_dict):
        """

        :return:
        """
        robot_len = len(robot_capacity_info_dict)
        multiple_canister_drug = []
        for drug_id in self.dfu.column_element_list:
            if drug_id in self.drug_canister_info_dict.keys():
                if len(self.drug_canister_info_dict[drug_id]) >= robot_len:
                    multiple_canister_drug.append(drug_id)
        return multiple_canister_drug

    def fill_robot_canister_info_dict(self, robot_id_list, canister_location_info_dict):
        """

        :return:
        """
        robot_canister_info_dict = {}
        for robot_id in robot_id_list:
            robot_canister_info_dict[robot_id] = []
            for canister_id in canister_location_info_dict.keys():
                if canister_location_info_dict[canister_id][0] == robot_id:
                    robot_canister_info_dict[robot_id].append(canister_id)
        return robot_canister_info_dict

    def fill_robot_drug_info_dict(self, robot_canister_info_dict, drug_canister_info_dict):
        """

        :return:
        """
        robot_drug_info_dict = {}
        for robot_id in robot_canister_info_dict.keys():
            robot_drug_info_dict[robot_id] = []
            for canister_id in robot_canister_info_dict[robot_id]:
                for drug_id in drug_canister_info_dict.keys():
                    if canister_id in drug_canister_info_dict[drug_id]:
                        robot_drug_info_dict[robot_id].append(drug_id)
        return robot_drug_info_dict

    def fill_canister_drug_info_dict(self):
        """

        :return:
        """
        canister_drug_info_dict = {}
        for drug in self.drug_canister_info_dict.keys():
            if len(self.drug_canister_info_dict[drug]) == 0:
                continue
            for canister_id in self.drug_canister_info_dict[drug]:
                canister_drug_info_dict[canister_id] = drug
        return canister_drug_info_dict
        pass

    def check_which_cluster_is_similar_to_which_robot(self, result_of_algorithm, robot_drug_info_dict, drug_canister_info_dict):
        """
        #TODO: This method is written in a temporary way, you need to rewrite this method.-Yash
        :param result_of_algorithm: list of clusters made by independent_tree_analysis_algo.
        :param robot_drug_info_dict: dictionary containing robot_id as key, list of drugs which contains as value.
        :return: robot_cluster_drug_info_dict: dict containing robot_id as key, list of drugs which is needed by that robot for next batch as value.
        """
        robot_cluster_info_dict = {}
        robot_cluster_drug_info_dict = {}
        robot_cluster_canister_info_dict = {}
        # self.robot_cluster_info_dict = {}
        cluster_0_drug = set(result_of_algorithm[0]["drugs"])
        cluster_1_drug = set(result_of_algorithm[1]["drugs"])
        for num, robot_id in enumerate(robot_drug_info_dict.keys()):
            robot_cluster_drug_info_dict[robot_id] = None
            if num == 0:
                cluster_0_robot_id_first_similarity = cluster_0_drug.intersection(set(robot_drug_info_dict[robot_id]))
                cluster_1_robot_id_first_similarity = cluster_1_drug.intersection(set(robot_drug_info_dict[robot_id]))
            if len(cluster_0_robot_id_first_similarity) >= len(cluster_1_robot_id_first_similarity) and num == 0:
                robot_cluster_drug_info_dict[robot_id] = deepcopy(result_of_algorithm[0]["drugs"])
                robot_cluster_info_dict[robot_id] = deepcopy(result_of_algorithm[0])
                result_of_algorithm.remove(result_of_algorithm[0])
            elif len(cluster_0_robot_id_first_similarity) < len(cluster_1_robot_id_first_similarity) and num == 0:
                robot_cluster_drug_info_dict[robot_id] = deepcopy(result_of_algorithm[1]["drugs"])
                robot_cluster_info_dict[robot_id] = deepcopy(result_of_algorithm[1])
                result_of_algorithm.remove(result_of_algorithm[1])
            else:
                robot_cluster_drug_info_dict[robot_id] = deepcopy(result_of_algorithm[0]["drugs"])
                robot_cluster_info_dict[robot_id] = deepcopy(result_of_algorithm[0])

        for robot_id in robot_cluster_drug_info_dict.keys():
            robot_cluster_canister_info_dict[robot_id] = []
            for drug_id in robot_cluster_drug_info_dict[robot_id]:
                if drug_id not in drug_canister_info_dict.keys():
                    continue
                if len(drug_canister_info_dict[drug_id]) == 0:
                    # Manual Drug
                    continue
                robot_cluster_canister_info_dict[robot_id].append(drug_canister_info_dict[drug_id].pop())
        # TODO: Check condition where same drug's canister is needed in different robot and assigned to different robot.

        return robot_cluster_info_dict, robot_cluster_drug_info_dict, robot_cluster_canister_info_dict
        pass


    def recommend_canisters_to_remove(self, result_of_algorithm = None, robot_cluster_info_dict = None, hybrid_method=True):
        """

        :return:
        """
        if result_of_algorithm is None:
            self.ica = IndependentClusterAnalysis(df= self.df, file_name=self.file_name, added_canister_drug_id_list=self.drugs_to_remove, maximum_independence_factor=3)
            result_of_algorithm, minimum_loss_function = self.ica.run_algorithm()
        self.result_of_algorithm = deepcopy(result_of_algorithm)

        """
        checking which cluster is similar to which robot.
        """
        self.robot_cluster_drug_info_dict = {}
        self.robot_cluster_info_dict, self.robot_cluster_drug_info_dict, self.robot_cluster_canister_info_dict = self.check_which_cluster_is_similar_to_which_robot(deepcopy(result_of_algorithm), deepcopy(self.robot_drug_info_dict), deepcopy(self.drug_canister_info_dict))
        append_dictionary_to_json_file(self.robot_cluster_info_dict, "robot_cluster_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.robot_cluster_canister_info_dict, "robot_cluster_canister_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)

        """
        Finding how many drugs are needed to be removed. This includes following steps.
        1) 
        """



        self.robot_remove_drugs_dict = {}
        self.robot_remove_canisters_dict = {}

        # Represents those canisters which are not at all needed for that robot in that batch.
        self.robot_absolute_remove_canisters_dict = {}
        self.second_robot_canister_from_remove_canister_dict = {}

        # Represents those canister  which will not be used in any robot for this batch.
        self.robot_absolute_remove_canisters_for_batch_dict = {}

        #Represents those canisters which are not needed in our robot but needed in other robots.
        self.robot_second_remove_canisters_dict = {}

        # Dictionary of open space in any robot. # TODO: Explain more
        self.robot_open_space_dict = {}

        # Represents those canisters of clusters which are not present in assigned robot
        self.robot_extra_cluster_canister_info_dict = {}

        # Only difference remove dict for hybrid approach.
        self.insufficient_space_canister_remove_dict = {}
        for robot_id in self.robot_cluster_canister_info_dict.keys():
            self.insufficient_space_canister_remove_dict[robot_id] = set([])
            self.robot_extra_cluster_canister_info_dict[robot_id] = set([])
            self.robot_second_remove_canisters_dict[robot_id] = set([])
            self.robot_absolute_remove_canisters_for_batch_dict[robot_id] = set([])




        for robot_id in self.robot_cluster_canister_info_dict.keys():
            self.robot_absolute_remove_canisters_dict[robot_id] = set(self.robot_canister_info_dict[robot_id]) - set(self.robot_cluster_canister_info_dict[robot_id])
            dummy_0 = set(self.robot_canister_info_dict[robot_id]).intersection(set(self.robot_cluster_canister_info_dict[robot_id]))
            self.robot_extra_cluster_canister_info_dict[robot_id] = set(self.robot_cluster_canister_info_dict[robot_id]) - set(self.robot_canister_info_dict[robot_id])
            for robot_id_second in self.robot_cluster_canister_info_dict.keys():
                if robot_id == robot_id_second:
                    continue
                second_robot_canister = self.robot_absolute_remove_canisters_dict[robot_id].intersection(self.robot_cluster_canister_info_dict[robot_id_second])
                self.robot_second_remove_canisters_dict[robot_id].update(second_robot_canister)
            self.robot_absolute_remove_canisters_for_batch_dict[robot_id] = set(self.robot_absolute_remove_canisters_dict[robot_id]) - set(self.robot_second_remove_canisters_dict[robot_id])
            self.robot_open_space_dict[robot_id] = self.robot_capacity_info_dict[robot_id] - len(self.robot_canister_info_dict[robot_id]) + len(self.robot_second_remove_canisters_dict[robot_id])
            self.robot_remove_canisters_dict[robot_id] = set([])
            if self.robot_open_space_dict[robot_id] > len(self.robot_extra_cluster_canister_info_dict[robot_id]):
                self.robot_remove_canisters_dict[robot_id] = set(deepcopy(self.robot_second_remove_canisters_dict[robot_id]))
            else:
                difference = len(self.robot_extra_cluster_canister_info_dict[robot_id]) - self.robot_open_space_dict[robot_id]
                for i in range(difference):
                    canister_set = set([self.robot_absolute_remove_canisters_for_batch_dict[robot_id].pop()])
                    self.robot_remove_canisters_dict[robot_id].update(canister_set)
                    self.insufficient_space_canister_remove_dict[robot_id].update(canister_set)

        """
        Asserting end output for remove suggestion. We will assert following points.
        1) No canister should be needed in both robot
        2) No canister should be in both robot.
        3) Cannister needed in one robot available in another must be removed.
        4) pass
        """
        if self.assert_output:
            """
            Gathering needed variables for assertions
            """
            robot_0_key = list(self.robot_cluster_info_dict.keys())[0]
            robot_1_key = list(self.robot_cluster_info_dict.keys())[1]
            canister_needed_in_robot_0 = deepcopy(set(self.robot_cluster_canister_info_dict[robot_0_key]))
            canister_needed_in_robot_1 = deepcopy(set(self.robot_cluster_canister_info_dict[robot_1_key]))
            canister_available_in_robot_0 = deepcopy(set(self.robot_canister_info_dict[robot_0_key]))
            canister_available_in_robot_1 = deepcopy(set(self.robot_canister_info_dict[robot_1_key]))
            canister_removing_from_robot_0 = deepcopy(set(self.robot_remove_canisters_dict[robot_0_key]))
            canister_removing_from_robot_1 = deepcopy(set(self.robot_remove_canisters_dict[robot_1_key]))
            """
            1
            """
            assert len(canister_needed_in_robot_0.intersection(canister_needed_in_robot_1)) == 0
            """
            2
            """
            assert len(canister_available_in_robot_0.intersection(canister_available_in_robot_1)) == 0
            """
            3
            """
            can_needed_in_0_available_in_1 = canister_needed_in_robot_0.intersection(canister_available_in_robot_1)
            assert can_needed_in_0_available_in_1.issubset(canister_removing_from_robot_1)
            can_needed_in_1_available_in_0 = canister_needed_in_robot_1.intersection(canister_available_in_robot_0)
            assert can_needed_in_1_available_in_0.issubset(canister_removing_from_robot_0)
            """
            """
            pass
        """
        Make it in a list
        """
        self.remove_canister_list = []
        for robot_id in self.robot_remove_canisters_dict:
            self.remove_canister_list.extend(list(self.robot_remove_canisters_dict[robot_id]))
        append_dictionary_to_json_file(self.remove_canister_list, "remove_canister_list",
                                       save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.insufficient_space_canister_remove_dict, "insufficient_space_canister_remove_dict",
                                       save_json=self.save_json, json_name=self.json_name)

        if hybrid_method:
            return deepcopy(self.insufficient_space_canister_remove_dict)
        return self.remove_canister_list
        pass


class RecommendCanistersToTransfer:

    def __init__(self, file_name=None, df=None, robot_capacity_info_dict=None, drug_canister_info_dict=None,
                 canister_location_info_dict=None, canister_expiry_status_dict=None, robot_free_location_info_dict=None,
                 testing_mode=False, robot_list=None, pack_drug_manual_dict=None, pack_half_pill_drug_dict=None,
                 split_function_id=None, total_packs=None, pack_slot_drug_dict=None, pack_slot_detail_drug_dict=None,
                 pack_drug_slot_number_slot_id_dict=None, pack_drug_slot_id_dict=None, total_robots=None,
                 pack_drug_half_pill_slots_dict=None, drug_quantity_dict=None, canister_qty_dict=None,
                 drug_canister_usage=None, pack_delivery_date=None, robot_quadrant_enable_locations=None):
        self.file_name = file_name
        self.testing_mode = testing_mode
        self.total_packs = total_packs
        self.total_robots = total_robots
        self.pack_slot_drug_dict = pack_slot_drug_dict
        self.pack_slot_detail_drug_dict = pack_slot_detail_drug_dict
        self.pack_drug_slot_number_slot_id_dict = pack_drug_slot_number_slot_id_dict
        self.drug_quantity_dict = drug_quantity_dict
        self.canister_qty_dict = canister_qty_dict
        if not self.testing_mode:
            self.df = df
            self.dfu = DataFrameUtil(df=deepcopy(df))
        self.robot_list = robot_list
        self.debug_mode = False
        self.split_function_id = split_function_id
        self.pack_drug_slot_id_dict = pack_drug_slot_id_dict
        self.robot_capacity_info_dict = robot_capacity_info_dict
        self.drug_canister_info_dict = drug_canister_info_dict
        self.drug_canister_usage = drug_canister_usage
        self.robot_quadrant_enable_locations = robot_quadrant_enable_locations
        self.assert_output = False
        self.canister_location_info_dict = canister_location_info_dict
        self.canister_expiry_status_dict = canister_expiry_status_dict
        #self.external_manual_drug_list = list(external_manual_drug_list)
        self.pack_drug_manual_dict = pack_drug_manual_dict
        self.pack_half_pill_drug_dict = pack_half_pill_drug_dict
        self.pack_drug_half_pill_slots_dict = pack_drug_half_pill_slots_dict
        self.pack_delivery_date = pack_delivery_date
        self.save_json = True
        self.json_name = "transfer.json"
        if os.path.exists(os.getcwd()+'/'+self.json_name):
            os.remove(os.getcwd()+'/'+self.json_name)
        self.robot_free_location_info_dict = robot_free_location_info_dict
        append_dictionary_to_json_file(self.drug_canister_info_dict, "drug_canister_info_dict", save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.robot_capacity_info_dict, "robot_capacity_info_dict", save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.canister_location_info_dict, "canister_location_info_dict", save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.robot_free_location_info_dict, "robot_free_location_info_dict",save_json=self.save_json, json_name=self.json_name)
        self.preprocess_input()

    def preprocess_input(self):
        """
        This method will preprocess the input and convert it into suitable from which  can be used by the algorithms.
        It will be achieving following tasks.
        1)
        :return:
        """

        """
        Currently allocated canisters in the robot
        """
        self.robot_canister_info_dict = self.fill_robot_canister_info_dict(self.robot_list, self.canister_location_info_dict)
        append_dictionary_to_json_file(self.robot_canister_info_dict, "robot_canister_info_dict",save_json=self.save_json, json_name=self.json_name)

        """
        Currently allocated drugs in the robot
        """
        self.robot_drug_info_dict = self.fill_robot_drug_info_dict(robot_canister_info_dict=self.robot_canister_info_dict,
                                                                   drug_canister_info_dict=self.drug_canister_info_dict)

        append_dictionary_to_json_file(self.robot_drug_info_dict, "robot_drug_info_dict",save_json=self.save_json, json_name=self.json_name)

        self.canister_drug_info_dict = self.fill_canister_drug_info_dict()
        append_dictionary_to_json_file(self.canister_drug_info_dict, "canister_drug_info_dict", save_json=self.save_json, json_name=self.json_name)

        # try:
        #     self.canister_recommendation_credibility_analysis(manual_drug_list=deepcopy(self.manual_drugs_list),
        #                                                       multiple_canister_drug_list=deepcopy(self.multiple_canister_drug_list),
        #                                                       pack_drug_info_dict=self.dfu.row_element_info_dict,
        #                                                       all_pack_list=deepcopy(self.dfu.row_element_list))
        # except:
        #     print("credibility_analysis_dict : Failed")
        # pass

    def fill_robot_canister_info_dict(self, robot_list, canister_location_info_dict):
        """
        Canister location is the dictionary which stores the current location of each canister. The current location may be in any of the robots or on shelf
        We filter those canisters which are already present in robots that we are using currently.
        Therefore, It shows the robot and canisters placed inside the robot
        :return: dict: robot and currently placed canisters inside the same robot
        """
        robot_canister_info_dict = {}
        for robot_id in robot_list:
            robot_canister_info_dict[robot_id] = []
            for canister_id in canister_location_info_dict.keys():
                if canister_location_info_dict[canister_id][0] == robot_id:
                    robot_canister_info_dict[robot_id].append(canister_id)
        return robot_canister_info_dict

    def fill_robot_drug_info_dict(self, robot_canister_info_dict, drug_canister_info_dict):
        """

        :return:
        """
        robot_drug_info_dict = {}
        for robot_id in robot_canister_info_dict.keys():
            robot_drug_info_dict[robot_id] = []
            for canister_id in robot_canister_info_dict[robot_id]:
                for drug_id in drug_canister_info_dict.keys():
                    if canister_id in drug_canister_info_dict[drug_id]:
                        robot_drug_info_dict[robot_id].append(drug_id)
        return robot_drug_info_dict

    def fill_canister_drug_info_dict(self):
        """

        :return:
        """
        canister_drug_info_dict = {}
        for drug in self.drug_canister_info_dict.keys():
            if len(self.drug_canister_info_dict[drug]) == 0:
                continue
            for canister_id in self.drug_canister_info_dict[drug]:
                canister_drug_info_dict[canister_id] = drug
        return canister_drug_info_dict

    def canister_recommendation_credibility_analysis(self, manual_drug_list, multiple_canister_drug_list, pack_drug_info_dict, all_pack_list):
        """

        :return:
        """
        all_double_drugs = set(manual_drug_list + multiple_canister_drug_list)
        manual_drug_list = set(manual_drug_list)
        multiple_canister_drug_list = set(multiple_canister_drug_list)
        credibility_analysis_dict = {"packs_filled_by_manual_drugs": set([]),
                                     "packs_filled_by_multiple_canister_drugs": set([]), "all_packs_list": set([]),
                                     "manual_length": -1, "multiple_length": -1, "all_length": -1}
        for pack_id in all_pack_list:
            drugs_of_given_pack_id = set(pack_drug_info_dict[pack_id])
            if drugs_of_given_pack_id.issubset(manual_drug_list):
                credibility_analysis_dict["packs_filled_by_manual_drugs"].update([pack_id])
            if drugs_of_given_pack_id.issubset(multiple_canister_drug_list):
                credibility_analysis_dict["packs_filled_by_multiple_canister_drugs"].update([pack_id])
            if drugs_of_given_pack_id.issubset(all_double_drugs):
                credibility_analysis_dict["all_packs_list"].update([pack_id])
        credibility_analysis_dict["manual_length"] = len(credibility_analysis_dict["packs_filled_by_manual_drugs"])
        credibility_analysis_dict["multiple_length"] = len(credibility_analysis_dict["packs_filled_by_multiple_canister_drugs"])
        credibility_analysis_dict["all_length"] = len(credibility_analysis_dict["all_packs_list"])
        append_dictionary_to_json_file(credibility_analysis_dict, "credibility_analysis_dict", False, "NA")
        pass


    """
    1.
    """
    def multi_robot_check_cluster_similarity_which_robot(self, result_of_algo, robot_drug_info_dict, robot_list):
        """
        Check similarity of all clusters with robots and assign clusters to robots accordingly.
        :param result_of_algo: result containing number of clusters as per number of robots
        :param robot_drug_info_dict: robot containing drugs initially
        :param robot_list: list of robots
        :return: robot_cluster_dict: robot mapping with cluster
                 robot_cluster_drug_dict: robot mapping with drugs
        """

        """
        Assign cluster-id to each result of algo's cluster
        """
        cluster_drugs_dict = {}
        for cluster_id in result_of_algo:
            cluster_drugs_dict[cluster_id] = result_of_algo[cluster_id]['drugs']

        """
        For all combinations of clusters and robots, check drug similarity with each clusters.
        """
        robot_cluster_common_drugs = {}
        for robot_id in robot_list:
            for cluster_id in cluster_drugs_dict:
                common_drugs = set(robot_drug_info_dict[robot_id]) & set(cluster_drugs_dict[cluster_id])
                robot_cluster_common_drugs[(robot_id, cluster_id)] = len(common_drugs)

        """
        Sort the cluster-id: robot pair based on number of common drugs(high to low)
        """
        sorted_robot_cluster_common_drugs = sorted(robot_cluster_common_drugs, key=lambda x: robot_cluster_common_drugs[x], reverse=True)

        """
        Assign cluster-id to each robot
        """
        robot_assigned_cluster_list = []
        robot_assigned = set()
        cluster_assigned = set()
        temp_robot_cluster_common_drugs = deepcopy(sorted_robot_cluster_common_drugs)
        while (temp_robot_cluster_common_drugs):
            robot_id, cluster_id = temp_robot_cluster_common_drugs.pop(0)
            if robot_id not in robot_assigned:
                if cluster_id not in cluster_assigned:
                    robot_assigned_cluster_list.append((robot_id, cluster_id))
                    cluster_assigned.add(cluster_id)
                    robot_assigned.add(robot_id)

        """
        Assign clusters to each robot and drugs to each robot according to distribution
        """
        robot_cluster_dict = {}
        robot_cluster_drug_dict = {}
        for robot_id in robot_list:
            for robot_cluster_id_tuple in robot_assigned_cluster_list:
                robot = robot_cluster_id_tuple[0]
                cluster_id = robot_cluster_id_tuple[1]
                if robot_id is robot:
                    robot_cluster_dict[robot_id] = result_of_algo[cluster_id]
                    robot_cluster_drug_dict[robot_id] = result_of_algo[cluster_id]['drugs']

        return robot_cluster_dict, robot_cluster_drug_dict

    """
    2. 
    """
    def fill_robot_manual_drugs(self, robot_cluster_dict, pack_drug_manual_dict):
        """

        :param robot_cluster_dict:
        :param external_manual_drugs:
        :param pack_drug_manual_dict:
        :return:
        """
        robot_manual_drugs_dict = {}
        for robot_id, cluster in robot_cluster_dict.items():
            robot_manual_drugs_dict[robot_id] = set()

            for pack in cluster['packs']:
                for drug in pack_drug_manual_dict[pack]:
                    if pack_drug_manual_dict[pack][drug]:
                        robot_manual_drugs_dict[robot_id].update({drug})

        return robot_manual_drugs_dict

    """
    3. 
    """
    # def fill_robot_pack_drug_manual_dict(self, pack_drug_manual_dict, robot_cluster_dict):
    #     robot_pack_drug_manual_dict = {}
    #
    #     for robot_id, cluster in robot_cluster_dict.items():
    #         robot_pack_drug_manual_dict[robot_id] = {}
    #         robot_packs = cluster['packs']
    #         for pack in robot_packs:
    #             robot_pack_drug_manual_dict[robot_id][pack] = pack_drug_manual_dict[pack]
    #     return robot_pack_drug_manual_dict

    def fill_robot_pack_half_pill_drug_dict(self, pack_half_pill_drug_dict, robot_cluster_dict):
        """

        :param pack_half_pill_drug_dict:
        :param robot_list:
        :return:
        """
        robot_manual_drugs_dict = {}
        robot_pack_half_pill_drug_dict = {}
        for robot_id, cluster in robot_cluster_dict.items():
            robot_pack_half_pill_drug_dict[robot_id] = {}
            robot_manual_drugs_dict[robot_id] = set()
            robot_allocated_packs = cluster['packs']
            half_pill_packs = list(pack_half_pill_drug_dict.keys())
            for pack in robot_allocated_packs:
                if pack in half_pill_packs:
                    robot_pack_half_pill_drug_dict[robot_id][pack] = pack_half_pill_drug_dict[pack]

        robot_half_pill_drug_pack_dict = {}
        for robot_id in robot_pack_half_pill_drug_dict:
            robot_half_pill_drug_pack_dict[robot_id] = {}
            for pack, drug_list in robot_pack_half_pill_drug_dict[robot_id].items():
                for drug in drug_list:
                    robot_half_pill_drug_pack_dict[robot_id].setdefault(drug, set()).add(pack)

        return robot_pack_half_pill_drug_dict, robot_half_pill_drug_pack_dict
    """
    4. 
    """

    def fill_robot_cluster_canister_dict(self, robot_cluster_dict, robot_cluster_drug_dict, drug_canister_info_dict,
                                         canister_location_info_dict, robot_half_pill_drug_pack_dict):
        """
        Store required canisters for each robots
        :param robot_cluster_dict: cluster(packs and drugs distribution) for each robot
        :param robot_cluster_drug_dict: drugs for each robot
        :param drug_canister_info_dict: present canisters for the drug which are not being used anywhere
        :param canister_location_info_dict: each canister's current location dictionary
        :return:
        """

        # temp_half_pill_packs = deepcopy(self.half_pill_manual_drug_packs)
        # robot_half_pill_drug_pack = []
        # temp_robot_pack_half_pill_drug_dict = deepcopy(robot_pack_half_pill_drug_dict)

        robot_list = []
        for robot in robot_cluster_dict:
            robot_list.append(robot)


        updated_drug_canister_info_dict = dict()
        for drug, canister_set in drug_canister_info_dict.items():
            updated_drug_canister_info_dict[drug] = list(sorted(canister_set))

        temp1_drug_canister_info_dict = deepcopy(updated_drug_canister_info_dict)
        """
        temp_drug_canister_info_dict:
        Original copy of drug_canister_info_dict for de-allocate the canister in the case of half-pill drug in all the packs of the same robot
        """
        temp_drug_canister_info_dict = deepcopy(drug_canister_info_dict)
        not_allocated_canister_drugs = []

        robot_cluster_canister_dict = {}
        robot_inspection_cnt = 0
        other_robot = None
        robot_list  = list(robot_cluster_dict.keys())
        try:
            for robot_id in robot_cluster_dict:
                robot_inspection_cnt+=1
                temp_robot_list = deepcopy(robot_list)
                temp_robot_list.remove(robot_id)
                if robot_inspection_cnt != len(robot_list):
                    other_robot = temp_robot_list.pop()
                robot_cluster_canister_dict[robot_id] = []
                for drug_id in robot_cluster_drug_dict[robot_id]:
                    available_csr_list = []
                    alloted = False
                    print("before")
                    """
                    After each time we allocate the canister, we pop the canister from that drug, 
                    So, if there are 3 canister for the particular robot and there is a drug which is present in all 4 robots, then the last robot will not get any canister.
                    """
                    if drug_id not in updated_drug_canister_info_dict or len(updated_drug_canister_info_dict[drug_id]) is 0:
                        # Manual drug
                        continue

                    # """
                    # Half pill drug
                    # """
                    # if drug_id in robot_manual_drugs_dict[robot_id]:
                    #     if len(robot_half_pill_drug_pack_dict[robot_id][drug_id]) == robot_cluster_dict[robot_id]['pack_length']:
                    #         not_allocated_canister_drugs.append(drug_id)
                    #         continue
                    """
                    If canister of any drug already exists in the robot, assign that canister
                    to the robot else, assign any canister to robot.
                    """
                    canister_locations = []
                    canister_list = []
                    for canister in updated_drug_canister_info_dict[drug_id]:
                        canister_locations.append(canister_location_info_dict[canister])
                        canister_list.append(canister)
                    print("step 2")
                    canister_locations_robot = []
                    for location_tuple in canister_locations:
                        canister_locations_robot.append(location_tuple[0])

                    # canister_locations_robot = [3,3,3]
                    for robot in canister_locations_robot:
                        if robot not in robot_list and robot is not None:
                            if robot not in available_csr_list:
                                available_csr_list.append(robot)
                    # available_csr_list = ['CSR 1-B']
                    if robot_id in canister_locations_robot:
                        print("step 4")
                        index = canister_locations_robot.index(robot_id)
                        canister_id = canister_list[index]
                        # NOTE: .remove() will not throw exception because we have skipped this code section if len(drug_canister_info_dict[drug_id]) is 0. SEE ABOVE at line 1229-1231
                        updated_drug_canister_info_dict[drug_id].remove(canister_id)
                        robot_cluster_canister_dict[robot_id].append(canister_id)
                        print("step 5")
                    else:
                        cnt = 0
                        count_csr = 0
                        canister_id = None
                        if robot_inspection_cnt != len(robot_list):
                            # robot = temp_robot_list.pop()
                            if other_robot in canister_locations_robot:
                                if drug_id not in robot_cluster_drug_dict[other_robot]:
                                    index = canister_locations_robot.index(other_robot)
                                    canister_id = canister_list[index]
                                    print("step 6")
                                    updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                    robot_cluster_canister_dict[robot_id].append(canister_id)

                                elif len(canister_locations_robot) > 1:
                                    for elem in canister_locations_robot:
                                        if elem == other_robot:
                                            cnt+=1
                                    if cnt > len(robot_list)-1:
                                        index = canister_locations_robot.index(other_robot)
                                        canister_id = canister_list[index]
                                        updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                        robot_cluster_canister_dict[robot_id].append(canister_id)
                                    else:
                                        for csr in available_csr_list:
                                            if csr in canister_locations_robot:
                                                index = canister_locations_robot.index(csr)
                                                canister_id = canister_list[index]
                                                updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                                robot_cluster_canister_dict[robot_id].append(canister_id)
                                                alloted = True
                                        if not alloted:
                                            robot_cluster_canister_dict[robot_id].append(updated_drug_canister_info_dict[drug_id].pop())
                                        # if len(available_csr_list) == 0:
                                        #     index = canister_locations_robot.index(other_robot)
                                        #     canister_id = canister_list[index]
                                        #     updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                        #     robot_cluster_canister_dict[robot_id].append(canister_id)

                            else:
                                print("step 3")
                                for csr in available_csr_list:
                                    if csr in canister_locations_robot:
                                        index = canister_locations_robot.index(csr)
                                        canister_id = canister_list[index]
                                        updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                        robot_cluster_canister_dict[robot_id].append(canister_id)
                                        alloted = True
                                        break
                                if not alloted:
                                    robot_cluster_canister_dict[robot_id].append(
                                        updated_drug_canister_info_dict[drug_id].pop())

                        else:
                            if len(temp_robot_list) != 0:
                                if temp_robot_list[0] in canister_locations_robot:
                                    index = canister_locations_robot.index(temp_robot_list[0])
                                    canister_id = canister_list[index]
                                    updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                    robot_cluster_canister_dict[robot_id].append(canister_id)
                                else:
                                    for csr in available_csr_list:
                                        if csr in canister_locations_robot:
                                            index = canister_locations_robot.index(csr)
                                            canister_id = canister_list[index]
                                            updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                            robot_cluster_canister_dict[robot_id].append(canister_id)
                                            alloted = True
                                            break
                                    if not alloted:
                                        robot_cluster_canister_dict[robot_id].append(
                                            updated_drug_canister_info_dict[drug_id].pop())

                            else:
                                for csr in available_csr_list:
                                    if csr in canister_locations_robot:
                                        index = canister_locations_robot.index(csr)
                                        canister_id = canister_list[index]
                                        updated_drug_canister_info_dict[drug_id].remove(canister_id)
                                        robot_cluster_canister_dict[robot_id].append(canister_id)
                                        alloted = True
                                        break
                                #     else:
                                #         count_csr += 1
                                # if count_csr > 0:
                                #     robot_cluster_canister_dict[robot_id].append(
                                #         updated_drug_canister_info_dict[drug_id].pop())
                                if not alloted:
                                    robot_cluster_canister_dict[robot_id].append(
                                        updated_drug_canister_info_dict[drug_id].pop())
                            # else:
                            #     if temp_robot_list[0] in canister_locations_robot:
                            #         index = canister_locations_robot.index(temp_robot_list[0])
                            #         canister_id = canister_list[index]
                            #         updated_drug_canister_info_dict[drug_id].remove(canister_id)
                            #         robot_cluster_canister_dict[robot_id].append(canister_id)
                            #     else:
                            #         if len(updated_drug_canister_info_dict[drug_id]) != 0 and not alloted:
                            #             robot_cluster_canister_dict[robot_id].append(
                            #                 updated_drug_canister_info_dict[drug_id].pop())

                        # NOTE: .pop() will not throw exception because we have skipped this code section if len(drug_canister_info_dict[drug_id]) is 0. SEE ABOVE at line 1229-1231
                        # robot_cluster_canister_dict[robot_id].append(updated_drug_canister_info_dict[drug_id].pop())
        except Exception as e:
            logger.error(e)
        """
        Half pill drug:
        When the drug is 0.5 in amount in all the packs of the robot, then we don't want to assign canister to the robot, else the canister is assigned.
        Check if the drug is used in all of the packs of the robot, then we don't want the canister of the drug in that robot.
        """
        for robot_id in robot_cluster_dict:
            for drug_id, half_pill_packs in robot_half_pill_drug_pack_dict[robot_id].items():
                if drug_id in temp1_drug_canister_info_dict:
                    if len(temp1_drug_canister_info_dict[drug_id]) is not 0:
                        if len(half_pill_packs) == robot_cluster_dict[robot_id]['pack_length']:
                            not_allocated_canister_drugs.append(drug_id)
                            canister_list = temp1_drug_canister_info_dict[drug_id]
                            for canister in canister_list:
                                if canister in robot_cluster_canister_dict[robot_id]:
                                    robot_cluster_canister_dict[robot_id].remove(canister)
        logger.debug("Half pill drugs that are not allocated to any packs: {}-->{}".format(len(not_allocated_canister_drugs), not_allocated_canister_drugs))
        return robot_cluster_canister_dict

    """
    5.
    """

    def fill_canister_transfer_dict(self, robot_cluster_canister_dict, robot_free_location_info_dict,
                                    canister_location_info_dict):
        """
        Canister Transfer from source robot(location info) to destination robot if that canister is already not present in the current robot
        :param robot_cluster_canister_dict:
        :param robot_free_location_info_dict:
        :param canister_location_info_dict:
        :return:
        """

        canister_transfer_info_dict = {}
        extended_canister_transfer_info_dict = {}

        on_shelf_canisters_dict = OrderedDict()
        robot_canister_dict = OrderedDict()

        for canister_id, location_tuple in canister_location_info_dict.items():
            if location_tuple[0] == None:
                on_shelf_canisters_dict[canister_id] = location_tuple
            else:
                robot_canister_dict[canister_id] = location_tuple

        robot_canister_dict.update(on_shelf_canisters_dict)
        canister_location_info_dict = robot_canister_dict

        for dest_robot_id in robot_cluster_canister_dict.keys():
            # required canisters for the robot
            for canister_id in robot_cluster_canister_dict[dest_robot_id]:
                # access the current location of the canisters(which robot and which location)
                src_robot_id = canister_location_info_dict[canister_id][0]
                src_location_id = canister_location_info_dict[canister_id][1]
                # Transfer is only possible if there is any free space in robots
                if robot_free_location_info_dict is not None:
                    # if canister is already present in the same robot, then you don't want to transfer it within
                    if src_robot_id == dest_robot_id:
                        dest_location_id = src_location_id
                    # if canister is not there in current robot, then borrow it from another robot/shelf and that assigned places will not be free space now
                    # remove the free space which is allocated now
                    else:
                        if len(robot_free_location_info_dict[dest_robot_id]) > 0:
                            dest_location_id = robot_free_location_info_dict[dest_robot_id].pop()
                        else:
                            dest_location_id = None
                    extended_canister_transfer_info_dict[canister_id] = (
                    src_robot_id, dest_robot_id, src_location_id, dest_location_id)
                canister_transfer_info_dict[canister_id] = (src_robot_id, dest_robot_id)

        return canister_transfer_info_dict, extended_canister_transfer_info_dict

    def fill_canister_transfer_dictV3(self, robot_quadrant_canister_info_dict, robot_free_location_info_dict, canister_location_info_dict):
        """

        :return:
        """
        try:
            canister_transfer_info_dict = {}
            extended_canister_transfer_info_dict = {}

            on_shelf_canisters_dict = OrderedDict()
            robot_canister_dict = OrderedDict()

            for canister_id, location_tuple in canister_location_info_dict.items():
                if location_tuple[0] == None:
                    on_shelf_canisters_dict[canister_id] = location_tuple
                else:
                    robot_canister_dict[canister_id] = location_tuple

            robot_canister_dict.update(on_shelf_canisters_dict)
            canister_location_info_dict = robot_canister_dict

            # for dest_robot_id in robot_quadrant_canister_info_dict.keys():
            #     # required canisters for the robot
            #     for canister_id in robot_quadrant_canister_info_dict[dest_robot_id]:
            #         # access the current location of the canisters(which robot and which location)
            #         src_robot_id = canister_location_info_dict[canister_id][0]
            #         src_location_id = canister_location_info_dict[canister_id][1]
            #         # Transfer is only possible if there is any free space in robots
            #         if robot_free_location_info_dict is not None:
            #             # if canister is already present in the same robot, then you don't want to transfer it within
            #             if src_robot_id == dest_robot_id:
            #                 dest_location_id = src_location_id
            #             # if canister is not there in current robot, then borrow it from another robot/shelf and that assigned places will not be free space now
            #             # remove the free space which is allocated now
            #             else:
            #                 if len(robot_free_location_info_dict[dest_robot_id]) > 0:
            #                     dest_location_id = robot_free_location_info_dict[dest_robot_id].pop()
            #                 else:
            #                     dest_location_id = None
            #             extended_canister_transfer_info_dict[canister_id] = (src_robot_id, dest_robot_id, src_location_id, dest_location_id)
            #         canister_transfer_info_dict[canister_id] = (src_robot_id, dest_robot_id)

            for robot_id in robot_quadrant_canister_info_dict.keys():
                for quadrant, canisters in robot_quadrant_canister_info_dict[robot_id].items():
                    remaining_canisters = []
                    for each_canister in canisters:
                        src_canister_location = canister_location_info_dict[each_canister]
                        src_robot_id = canister_location_info_dict[each_canister][0]
                        src_location_id = canister_location_info_dict[each_canister][1]
                        if src_robot_id == robot_id and src_canister_location[2] == quadrant:
                            dest_canister_location_id = canister_location_info_dict[each_canister][1]
                            if dest_canister_location_id in robot_free_location_info_dict[robot_id][quadrant]:
                                robot_free_location_info_dict[robot_id][quadrant].remove(dest_canister_location_id)
                            else:
                                logger.info("Canister placed at disable location {}".format(each_canister))

                            extended_canister_transfer_info_dict[each_canister] = (
                                src_robot_id, robot_id, src_location_id, dest_canister_location_id, quadrant)
                            canister_transfer_info_dict[each_canister] = (src_robot_id, robot_id, quadrant)
                        else:
                            remaining_canisters.append(each_canister)

                    if len(remaining_canisters)> 0:
                        for every_canister in remaining_canisters:
                            src_canister_location = canister_location_info_dict[every_canister]
                            src_robot_id = canister_location_info_dict[every_canister][0]
                            src_location_id = canister_location_info_dict[every_canister][1]

                            if len(robot_free_location_info_dict[robot_id][quadrant]) > 0:
                                dest_canister_location_id = robot_free_location_info_dict[robot_id][quadrant].pop()
                            else:
                                dest_canister_location_id = None
                            extended_canister_transfer_info_dict[every_canister] = (
                                src_robot_id, robot_id, src_location_id, dest_canister_location_id, quadrant)
                            canister_transfer_info_dict[every_canister] = (src_robot_id, robot_id, quadrant)

            return canister_transfer_info_dict, extended_canister_transfer_info_dict

        except Exception as e:
            logger.info(e)
            return e

    """
    6.
    """
    def fill_pack_drug_canister_robot_dict(self, df, robot_cluster_dict, robot_cluster_drug_dict, robot_cluster_canister_dict, drug_canister_info_dict, robot_half_pill_drug_pack_dict,pack_drug_slot_id_dict):
        """

        :param df:
        :param robot_cluster_drug_dict:
        :param drug_canister_info_dict:
        :return:
        """
        dfu = DataFrameUtil(df=df)
        pack_drug_canister_robot_dict = {}
        for pack in dfu.row_element_info_dict.keys():
            pack_drug_canister_robot_dict[pack] = []
            for drug_id in dfu.row_element_info_dict[pack]:
                for slot_id in pack_drug_slot_id_dict[pack][drug_id]:
                    """
                    Manual drug condition
                    """
                    # [drug_id,canister_id,robot_id,quadrant,slot_id,drop,configuration]
                    if drug_id not in drug_canister_info_dict.keys():
                        pack_drug_canister_robot_dict[pack].append([drug_id, None, None,None,slot_id,None,None])
                        continue
                    if len(drug_canister_info_dict[drug_id]) == 0:
                        pack_drug_canister_robot_dict[pack].append([drug_id, None, None,None,slot_id,None,None])
                        continue

                    drug_used = False
                    for robot_id in robot_cluster_drug_dict.keys():
                        # if pack is present in current robot
                        if pack in robot_cluster_dict[robot_id]["packs"]:
                            # if (drug of the current pack: drug_id) is present in current robot
                            if drug_id in robot_cluster_drug_dict[robot_id]:
                                '''
                                In the situation, where the pack is common in both robot and the certain drug is also common in both robot.
                                This will recommend us to fill the drug from both robots, which is not correct.
                                Therefore used a flag drug_used to avoid these cases.
                                '''
                                if(drug_used is True):
                                    break
                                canister_ids = drug_canister_info_dict[drug_id]
                                for canister_id in canister_ids:
                                    if canister_id in robot_cluster_canister_dict[robot_id]:
                                        pack_drug_canister_robot_dict[pack].append([drug_id, canister_id, robot_id,None,slot_id,None,None])
                                        drug_used = True
                                        break

        """
        Half pill drug
        """
        for robot_id, drug_packs in robot_half_pill_drug_pack_dict.items():
            for drug, pack_list in drug_packs.items():
                for pack in pack_list:
                    for slot_id in pack_drug_slot_id_dict[pack][drug]:
                        pack_drug_canister_robot_dict[pack].append([drug, None, None,None,slot_id,None,None])
                    logger.debug("pack ---> half pill drug info {}::{}".format(pack, [drug, None, None,None,slot_id,None,None]))

        return pack_drug_canister_robot_dict

    def fill_pack_drug_canister_robot_dictV3(self, df, pack_slot_drop_info_dict, robot_quadrant_drug_distribution_dict,
                                             robot_quadrant_canister_info_dict, robot_drug_canister_info_dict,
                                             robot_half_pill_drug_pack_dict, pack_drug_slot_number_slot_id_dict,
                                             pack_slot_drug_config_id_dict, pack_slot_drug_quad_id_dict,
                                             pack_drug_half_pill_slots_dict):
        """
        :param df:
        :param robot_cluster_drug_dict:
        :param drug_canister_info_dict:
        :return:
        """
        try:
            drug_canister_skipped = dict()
            self.used_canisters = set()
            self.pack_drug_slot_number_slot_id_dict = pack_drug_slot_number_slot_id_dict
            self.pack_slot_drop_info_dict = pack_slot_drop_info_dict
            pack_drug_canister_robot_dict = {}

            for pack, slot_details in self.pack_slot_drug_dict.items():
                pack_drug_canister_robot_dict[pack] = []
                for slot, drugs in slot_details.items():
                    # slot_id = self.pack_slot_detail_drug_dict[pack][slot]
                    # drug_used = False
                    for robot in robot_quadrant_drug_distribution_dict:
                        if pack not in self.robot_cluster_dict[robot]["packs"]:
                            continue
                        for drug in drugs:
                            """
                            Manual drug condition
                            """
                            if drug in robot_half_pill_drug_pack_dict[robot]:
                                if pack in robot_half_pill_drug_pack_dict[robot][drug]:
                                    continue
                            slot_id = self.pack_drug_slot_number_slot_id_dict[pack][drug][slot]
                            if drug not in robot_drug_canister_info_dict[robot].keys():
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                                continue
                            if robot_drug_canister_info_dict[robot][drug] == 0:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                                continue
                            if slot not in self.pack_slot_drop_info_dict[pack]:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                                continue
                            quadrant_details = self.pack_slot_drop_info_dict[pack][slot]
                            drug_used = False

                            if 'drop_number' in quadrant_details and quadrant_details['drop_number'] is None:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                                continue

                            if type(quadrant_details['quadrant']) == tuple or type(quadrant_details['quadrant']) == set:
                                quadrants = list(quadrant_details['quadrant'])
                            else:
                                quadrants = list(map(int, list(str(quadrant_details['quadrant']))))

                            if len(quadrant_details['configuration_id']) > 1:
                                quad = pack_slot_drug_quad_id_dict[pack][slot][drug]
                                conf_id = pack_slot_drug_config_id_dict[pack][slot][drug]
                                drop_id = pack_slot_drop_info_dict[pack][slot]['drop_number']
                                if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
                                    if (drug_used is True):
                                        break
                                    if drug in self.robot_quadrant_drug_canister_info_dict[robot][quad]:
                                        canister_id = self.robot_quadrant_drug_canister_info_dict[robot][quad][drug]
                                        pack_drug_canister_robot_dict[pack].append(
                                            [drug, canister_id, robot, quad, slot_id, drop_id,
                                             {conf_id}])
                                        self.used_canisters.add(canister_id)
                                    else:
                                        pack_drug_canister_robot_dict[pack].append(
                                            [drug, None, None, None, slot_id, None, None])
                                    drug_used = True
                                continue

                            for quad in quadrants:
                                if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
                                    if (drug_used is True):
                                        break
                                    if drug in self.robot_quadrant_drug_canister_info_dict[robot][quad]:
                                        canister_id = self.robot_quadrant_drug_canister_info_dict[robot][quad][drug]

                                        pack_drug_canister_robot_dict[pack].append(
                                            [drug, canister_id, robot, quad, slot_id, quadrant_details['drop_number'],
                                             quadrant_details['configuration_id']])

                                        self.used_canisters.add(canister_id)

                                    else:
                                        pack_drug_canister_robot_dict[pack].append(
                                            [drug, None, None, None, slot_id, None, None])
                                    drug_used = True

            extended_canister_transfer_info_dict = deepcopy(self.extended_canister_transfer_info_dict)
            for canister, transfer in extended_canister_transfer_info_dict.items():
                if canister in self.used_canisters:
                    continue
                del self.extended_canister_transfer_info_dict[canister]

            # for pack, quadrant_details in self.pack_slot_drop_info_dict.items():
            #     pack_drug_canister_robot_dict[pack] = []
            #     for slot, quadrant_details in quadrant_details.items():
            #         slot_id = self.pack_slot_detail_drug_dict[pack][slot]
            #         # drug_used = False
            #         for robot in robot_quadrant_drug_distribution_dict:
            #             if pack not in self.robot_cluster_dict[robot]["packs"]:
            #                 continue
            #             for drug in self.pack_slot_drug_dict[pack][slot]:
            #                 """
            #                 Manual drug condition
            #                 """
            #                 if drug not in robot_drug_canister_info_dict[robot].keys():
            #                     pack_drug_canister_robot_dict[pack].append([drug, None, None, None, slot_id, None, None])
            #                     continue
            #                 if len(robot_drug_canister_info_dict[robot][drug]) == 0:
            #                     pack_drug_canister_robot_dict[pack].append([drug, None, None, None, slot_id, None, None])
            #                     continue
            #
            #                 drug_used = False
            #                 if type(quadrant_details['quadrant']) == tuple:
            #                     quadrants = list(quadrant_details['quadrant'])
            #                 else:
            #                     quadrants = list(map(int, list(str(quadrant_details['quadrant']))))
            #
            #                 if len(quadrant_details['configuration_id']) > 1:
            #                     quad = pack_slot_drug_quad_id_dict[pack][slot][drug]
            #                     conf_id = pack_slot_drug_config_id_dict[pack][slot][drug]
            #                     if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
            #                         if (drug_used is True):
            #                             break
            #                         if drug in self.robot_quadrant_drug_canister_info_dict[robot][quad]:
            #                             canister_id = self.robot_quadrant_drug_canister_info_dict[robot][quad][drug]
            #                             pack_drug_canister_robot_dict[pack].append(
            #                                 [drug, canister_id, robot, quad, slot_id, quad,
            #                                  {conf_id}])
            #                         drug_used = True
            #                     continue
            #
            #
            #                 for quad in quadrants:
            #                     if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
            #                         if (drug_used is True):
            #                             break
            #                         if drug in self.robot_quadrant_drug_canister_info_dict[robot][quad]:
            #                             canister_id = self.robot_quadrant_drug_canister_info_dict[robot][quad][drug]
            #                             pack_drug_canister_robot_dict[pack].append(
            #                                 [drug, canister_id, robot, quad, slot_id, quadrant_details['drop_number'],
            #                                  quadrant_details['configuration_id']])
            #                         else:
            #                             pack_drug_canister_robot_dict[pack].append(
            #                                 [drug, None, None, None, slot_id, None, None])
            #                         drug_used = True
            """
            Half pill drug
            """
            for robot_id, drug_packs in robot_half_pill_drug_pack_dict.items():
                for drug, pack_list in drug_packs.items():
                    for pack in pack_list:
                        for slot in pack_drug_half_pill_slots_dict[pack][drug]:
                            slot_id = self.pack_drug_slot_number_slot_id_dict[pack][drug][slot]
                            pack_drug_canister_robot_dict[pack].append([drug, None, None, None, slot_id, None, None])
                            logger.debug("pack ---> half pill drug info {}::{}".format(pack,
                                                                                       [drug, None, None, None, slot_id,
                                                                                        None, None]))

            return pack_drug_canister_robot_dict

        except KeyError as e:
            logger.info("Error in fill_pack_drug_canister_robot_dictV3: {}".format(e))
            print("Error in fill_pack_drug_canister_robot_dictV3: {}".format(e))
            print(pack)
            raise
        except Exception as e:
            logger.info("Error in fill_pack_drug_canister_robot_dictV3: {}".format(e))
            print("Error in fill_pack_drug_canister_robot_dictV3: {}".format(e))
            print(pack)
            raise

    def check_assertion(self, robot_cluster_dict, robot_cluster_canister_dict, robot_canister_info_dict, canister_transfer_info_dict, extended_canister_transfer_info_dict, pack_drug_canister_robot_dict):

        """
        Gathering needed variables for assertions
        """
        robot_0_key = list(robot_cluster_dict.keys())[0]
        robot_1_key = list(robot_cluster_dict.keys())[1]
        canister_needed_in_robot_0 = deepcopy(set(robot_cluster_canister_dict[robot_0_key]))
        canister_needed_in_robot_1 = deepcopy(set(robot_cluster_canister_dict[robot_1_key]))
        canister_available_in_robot_0 = deepcopy(set(robot_canister_info_dict[robot_0_key]))
        canister_available_in_robot_1 = deepcopy(set(robot_canister_info_dict[robot_1_key]))
        canister_transfer_info_dict = deepcopy(canister_transfer_info_dict)
        extended_canister_transfer_info_dict = deepcopy(extended_canister_transfer_info_dict)
        #pack_drug_canister_robot_dict = deepcopy(pack_drug_canister_robot_dict)
        # canister_removing_from_robot_1 = deepcopy(set(self.robot_remove_canisters_dict[robot_1_key]))
        """
        1
        """
        for canister in canister_transfer_info_dict.keys():
            src_robot_id = canister_transfer_info_dict[canister][0]
            dest_robot_id = canister_transfer_info_dict[canister][1]
            if src_robot_id == None:
                continue
            assert canister in self.robot_cluster_canister_info_dict[dest_robot_id]
            assert canister in self.robot_canister_info_dict[src_robot_id]
        """
        2
        """
        for canister in extended_canister_transfer_info_dict.keys():
            src_robot_id = extended_canister_transfer_info_dict[canister][0]
            dest_robot_id = extended_canister_transfer_info_dict[canister][1]
            src_location_id = extended_canister_transfer_info_dict[canister][2]
            dest_location_id = extended_canister_transfer_info_dict[canister][3]
            assert canister in self.robot_cluster_canister_info_dict[dest_robot_id]
            assert canister in self.robot_canister_info_dict[src_robot_id]
            assert dest_location_id in self.robot_free_location_info_dict[dest_robot_id]
            assert src_location_id == self.canister_location_info_dict[canister][1]
        """
        3
        """
        assert len(pack_drug_canister_robot_dict.keys()) == len(self.dfu.row_element_info_dict.keys())
        robot_packs_for_assertion = {robot_0_key: set([]), robot_1_key: set([])}
        for pack in pack_drug_canister_robot_dict.keys():
            print(len(pack_drug_canister_robot_dict[pack]), len(self.dfu.row_element_info_dict[pack]))
            print(pack_drug_canister_robot_dict[pack])
            print(self.dfu.row_element_info_dict[pack])
            assert len(pack_drug_canister_robot_dict[pack]) == len(self.dfu.row_element_info_dict[pack])
            for drug, canister, robot in pack_drug_canister_robot_dict[pack]:
                if robot == None or canister == None or drug == None:
                    continue
                robot_packs_for_assertion[robot].update(set([pack]))
                assert drug in self.robot_cluster_drug_info_dict[robot]
                assert canister in self.robot_cluster_canister_info_dict[robot]
                assert drug in self.dfu.row_element_info_dict[pack]
                if drug in self.drug_canister_info_dict.keys():
                    assert canister in self.drug_canister_info_dict[drug]

        assert len(robot_packs_for_assertion[robot_0_key]) == len(self.robot_cluster_info_dict[robot_0_key]["packs"])
        assert len(robot_packs_for_assertion[robot_1_key]) == len(self.robot_cluster_info_dict[robot_1_key]["packs"])
        pass

    def common_packs_drugs_diagnostics(self, robot_cluster_info_dict, robot_cluster_canister_info_dict):
        """

        :param robot_cluster_info_dict:
        :return:
        """
        common_pack_drug_dict = {"packs":[], "drugs":[], "pack_length":-1, "drug_length":-1}
        robot_id_0 = robot_cluster_canister_info_dict.keys()[0]
        robot_id_1 = robot_cluster_canister_info_dict.keys()[1]
        packs_0 = set(robot_cluster_canister_info_dict[robot_id_0]["packs"])
        packs_1 = set(robot_cluster_canister_info_dict[robot_id_1]["packs"])
        common_pack_drug_dict["packs"] = packs_0.intersection(packs_1)
        common_pack_drug_dict["pack_length"] = len(common_pack_drug_dict["packs"])
        drugs_0 = set(robot_cluster_canister_info_dict[robot_id_0]["drugs"])
        drugs_1 = set(robot_cluster_canister_info_dict[robot_id_1]["drugs"])
        common_pack_drug_dict["drugs"] = drugs_0.intersection(drugs_1)
        common_pack_drug_dict["drug_length"] = len(common_pack_drug_dict["drugs"])
        append_dictionary_to_json_file(robot_cluster_info_dict, "common_pack_drug_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        pass

    def recommend_multiple_split(self,batch_formation=False):
        self.mria = MultiRobotClusterAnalysis(df=self.df, drug_canister_info_dict=self.drug_canister_info_dict,
                                              robot_list=self.robot_list,is_multi_split=True,total_packs=self.total_packs,batch_formation=batch_formation,total_robots=self.total_robots, pack_delivery_date=self.pack_delivery_date)
        return self.mria.multiple_split_info

    def recommend_canisters_to_transfer(self):
        """
        Gives information about which canisters need to be transferred from source robot to destination robot
        :return:
        """

        """
        Get the cluster(packs and drugs) distribution for further processing 
        """
        logger.info('split function id: {}'.format(self.split_function_id))
        self.mria = MultiRobotClusterAnalysis(df=self.df, drug_canister_info_dict=self.drug_canister_info_dict, robot_list=self.robot_list,split_function_id=self.split_function_id,total_packs=self.total_packs,total_robots=self.total_robots)
        result_of_algo = self.mria.fill_robot_distribution_info_dict()
        self.multi_robot_result = deepcopy(result_of_algo)

        """
        1. checking which cluster is similar to which robot.
        """
        self.robot_cluster_dict, self.robot_cluster_drug_dict = self.multi_robot_check_cluster_similarity_which_robot(result_of_algo=deepcopy(self.multi_robot_result),
                                                                                                                       robot_drug_info_dict=deepcopy(self.robot_drug_info_dict),
                                                                                                                        robot_list=deepcopy(self.robot_list))

        """
        Consider the 1/2 pill drugs in canister requirement
        """
        #self.robot_manual_drugs_dict = self.fill_robot_manual_drugs(self.robot_cluster_dict, self.pack_drug_manual_dict)
        #
        # self.robot_pack_drug_manual_dict = self.fill_robot_pack_drug_manual_dict(self.pack_drug_manual_dict, self.robot_cluster_dict)

        self.robot_pack_half_pill_drug_dict, self.robot_half_pill_drug_pack_dict = self.fill_robot_pack_half_pill_drug_dict(self.pack_half_pill_drug_dict, self.robot_cluster_dict)
        """
        robot-wise required canister list
        """
        self.robot_cluster_canister_dict = self.fill_robot_cluster_canister_dict(robot_cluster_dict=deepcopy(self.robot_cluster_dict),
                                                                                 robot_cluster_drug_dict=deepcopy(self.robot_cluster_drug_dict),
                                                                                 drug_canister_info_dict=deepcopy(self.drug_canister_info_dict),
                                                                                 canister_location_info_dict=deepcopy(self.canister_location_info_dict),
                                                                                 robot_half_pill_drug_pack_dict=deepcopy(self.robot_half_pill_drug_pack_dict))
        """
        Canister Transfer data according to its source and destination location
        """
        self.canister_transfer_info_dict, self.extended_canister_transfer_info_dict = self.fill_canister_transfer_dict(robot_cluster_canister_dict=deepcopy(self.robot_cluster_canister_dict),
                                                                            robot_free_location_info_dict=deepcopy(self.robot_free_location_info_dict),
                                                                            canister_location_info_dict=deepcopy(self.canister_location_info_dict))

        """
        Analysis data: pack as a key, [drug_id, canister_id, robot_id] as value
        """
        self.pack_drug_canister_robot_dict = self.fill_pack_drug_canister_robot_dict(df=deepcopy(self.df),
                                                                                     robot_cluster_dict=deepcopy(
                                                                                         self.robot_cluster_dict),
                                                                                     robot_cluster_drug_dict=deepcopy(
                                                                                         self.robot_cluster_drug_dict),
                                                                                     robot_cluster_canister_dict=deepcopy(
                                                                                         self.robot_cluster_canister_dict),
                                                                                     drug_canister_info_dict=deepcopy(
                                                                                         self.drug_canister_info_dict),
                                                                                     robot_half_pill_drug_pack_dict=deepcopy(
                                                                                         self.robot_half_pill_drug_pack_dict),
                                                                                     pack_drug_slot_id_dict=deepcopy(self.pack_drug_slot_id_dict))
        """
        Save appropriate data in a dictionary
        """
        append_dictionary_to_json_file(self.robot_cluster_dict, "robot_cluster_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(self.robot_cluster_canister_dict, "robot_cluster_canister_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)

        append_dictionary_to_json_file(self.canister_transfer_info_dict, "canister_transfer_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        append_dictionary_to_json_file(str(self.pack_drug_canister_robot_dict), "pack_robot_drug_info_dict",
                                       save_json=self.save_json, json_name=self.json_name)
        """
        To check the correctness of algorithm
        """
        if self.assert_output:
            """
            Asserting end output for remove suggestion. We will assert following points.
            1) For every canister in canister transfer_info_dict source_robot and dest_robot are relevant.
            2) Same check for extended canister transfer_info_dict.
            3) Check total number of packs in data_frame and pack_robot_drug_info_dict are same.
            4) 
            """
            self.check_assertion(deepcopy(self.robot_cluster_dict), deepcopy(self.robot_cluster_canister_dict),
                                 deepcopy(self.robot_canister_info_dict),
                                 deepcopy(self.canister_transfer_info_dict),
                                 deepcopy(self.extended_canister_transfer_info_dict),
                                 deepcopy(self.pack_drug_canister_robot_dict))

        if self.robot_free_location_info_dict is not None:
            return self.extended_canister_transfer_info_dict, self.pack_drug_canister_robot_dict

        return self.canister_transfer_info_dict, self.pack_drug_canister_robot_dict

    def recommend_pack_distribution_in_robots_v3(self):

        """
               Gives information about which canisters need to be transferred from source robot to destination robot
               :return:
               """

        """
        Get the cluster(packs and drugs) distribution for further processing 
        """
        self.drug_canister_info_dict_updated = deepcopy(self.drug_canister_info_dict)
        self.mria = MultiRobotClusterAnalysis(df=self.df, drug_canister_info_dict=self.drug_canister_info_dict,
                                              robot_list=self.robot_list, split_function_id=self.split_function_id,
                                              total_packs=self.total_packs, total_robots=self.total_robots,
                                              pack_delivery_date=self.pack_delivery_date)
        result_of_algo = self.mria.fill_robot_distribution_info_dict()
        self.multi_robot_result = deepcopy(result_of_algo)

        """
        1. checking which cluster is similar to which robot.
        
        """
        self.robot_cluster_dict, self.robot_cluster_drug_dict = self.multi_robot_check_cluster_similarity_which_robot(
            result_of_algo=deepcopy(self.multi_robot_result),
            robot_drug_info_dict=deepcopy(self.robot_drug_info_dict),
            robot_list=deepcopy(self.robot_list))

        """
        Consider the 1/2 pill drugs in canister requirement
        """

        self.robot_pack_half_pill_drug_dict, self.robot_half_pill_drug_pack_dict = self.fill_robot_pack_half_pill_drug_dict(
            self.pack_half_pill_drug_dict, self.robot_cluster_dict)
        """
        robot-wise required canister list
        """
        self.robot_cluster_canister_dict = self.fill_robot_cluster_canister_dict(
            robot_cluster_dict=deepcopy(self.robot_cluster_dict),
            robot_cluster_drug_dict=deepcopy(self.robot_cluster_drug_dict),
            drug_canister_info_dict=deepcopy(self.drug_canister_info_dict),
            canister_location_info_dict=deepcopy(self.canister_location_info_dict),
            robot_half_pill_drug_pack_dict=deepcopy(self.robot_half_pill_drug_pack_dict))

        return self.robot_cluster_dict


    def get_robot_common_drugs(self, robot_cluster_dict):
        # TODO : temp function to get the common packs of both the robot for testing
        robots = list(robot_cluster_dict.keys())
        common_drugs = set()
        if len(robots) > 1:
            robot_1_drugs = robot_cluster_dict[robots[0]]['drugs']
            robot_2_drugs = robot_cluster_dict[robots[1]]['drugs']
            common_drugs = robot_1_drugs.intersection(robot_2_drugs)
        return common_drugs, robots

    def get_permutation_list(self):
        reserved_value = []
        permutation_list = []
        permutation_count = 0
        response_value_list = []
        for id,data in self.quadrant_distribution_data.items():
            response_value_list.append(data['drugs'])
        # response_value_list = list(self.quadrant_distribution_data.values())
        for value in response_value_list:
            if value in reserved_value:
                indx = response_value_list.index(value)
                per_cnt = permutation_list[indx]
                permutation_list.append(per_cnt)
                continue
            permutation_count += 1
            reserved_value.append(value)
            permutation_list.append(permutation_count)
        return permutation_list


    def get_calculated_permutation(self,permutation):
        res = []
        permutation = list(permutation)
        # permutation = [1,1,2,3]
        while len(set(permutation)) < 4:
            remaining_quads = {1, 2, 3, 4} - set(permutation)
            if len(remaining_quads) == 2:
                quad_rep = dict(zip(sorted(list(set(permutation))), sorted(list(set(remaining_quads)))))
                for idx, ele in enumerate(permutation):
                    if ele in res:
                        permutation[idx] = quad_rep[ele]
                    else:
                        res.append(ele)
            else:
                permutation = [next(iter(remaining_quads)) if (ele in permutation[:idx]) else ele
                               for idx, ele in enumerate(permutation)]
        return permutation

    def canister_recommendation_for_quadrants_v3(self):
        total_drop_count = 0
        robot_drop_count_dict = {}
        robot_cluster_dict =self.robot_cluster_dict
        robot_quadrant_drug_distribution_dict = {}
        drop_count_list = []
        self.pack_slot_drop_info_dict = {}
        self.pack_slot_drug_quad_id_dict = {}
        self.pack_slot_drug_config_id_dict = {}
        time_count_list = []
        drop_count_list_v2 = []
        time_count_list_v2 = []
        pack_slot_drop_info_dict = {}
        pack_slot_drop_info_dict_robotwise = {}
        pack_list = []
        pack_wise_time = {}
        quadrant_distribution_data = {}
        analysis_dict = {}
        self.fully_manual_drugs = list()
        self.robot_drug_canister_info_dict = {}

        print("21")

        # Code part temporary to handle canister distribution evenly in both the robots
        robot_common_drugs, robots = self.get_robot_common_drugs(robot_cluster_dict)
        for each_robot in robots:
            self.robot_drug_canister_info_dict[each_robot] = dict()

        '''
        This below code is used to define number of canisters to be used in quadrant distribution.
        When we set system to run on 1x, SYSTEM_SPEED is defined as 1 so that the drug_canister dict is set to have 1 
        canister per drug,
        For rest of the settings, we keep all the canisters for that drug, and to run the quadrant distribution on Nx, we 
        modify this list as per canister usage in Fn "modify_drug_canister_info_dict()"
        '''
        if settings.SYSTEM_SPEED < 4:
            if len(robots) > 1:
                for each_drug, canister in self.drug_canister_info_dict_updated.items():
                    self.robot_drug_canister_info_dict[robots[0]][each_drug] = settings.SYSTEM_SPEED
                    self.robot_drug_canister_info_dict[robots[1]][each_drug] = settings.SYSTEM_SPEED
            else:
                for each_drug, canister in self.drug_canister_info_dict_updated.items():
                    self.robot_drug_canister_info_dict[robots[0]][each_drug] = settings.SYSTEM_SPEED

        else:
            frozen_as_1x = False
            if len(robots) > 1:
                '''
                For Nx canister recommendation,
                    if are going to be using 8 canisters for drug d1.
                    In case that it is going to be used in both robot then we will assign 4 canister to r1 and 4 to r2
                    If we have only 5 canister available, we will use 3 for r1 and 2 for r2.
                    For those drugs which we have to treat as single canister drug then we have to set its max canister usage to 2, (one for each)
                '''
                if not frozen_as_1x:
                    for each_drug, canister in self.drug_canister_info_dict_updated.items():
                        canister_len = len(canister)
                        max_usable_canister = math.ceil(self.drug_canister_usage[each_drug]['max']/2)
                        max_usable_canister1 = self.drug_canister_usage[each_drug]['max'] - max_usable_canister
                        if each_drug in robot_common_drugs:
                            if canister_len > 1:
                                robot0_canister_length = math.ceil(canister_len / 2)
                                self.robot_drug_canister_info_dict[robots[0]][
                                    each_drug] = max_usable_canister if max_usable_canister <= robot0_canister_length else robot0_canister_length
                                robot1_canister_length = canister_len - robot0_canister_length
                                self.robot_drug_canister_info_dict[robots[1]][
                                    each_drug] = max_usable_canister1 if max_usable_canister1 <= robot1_canister_length else robot1_canister_length
                            else:
                                self.robot_drug_canister_info_dict[robots[0]][
                                    each_drug] = max_usable_canister if max_usable_canister <= canister_len else canister_len
                                self.robot_drug_canister_info_dict[robots[1]][each_drug] = 0

                        else:
                            self.robot_drug_canister_info_dict[robots[0]][
                                each_drug] = max_usable_canister if max_usable_canister <= canister_len else canister_len
                            self.robot_drug_canister_info_dict[robots[1]][
                                each_drug] = max_usable_canister1 if max_usable_canister1 <= canister_len else canister_len
                else:
                    for each_drug, canister in self.drug_canister_info_dict_updated.items():
                        canister_len = len(canister)
                        if canister_len > 1:
                            self.robot_drug_canister_info_dict[robots[0]][each_drug] = 1
                            self.robot_drug_canister_info_dict[robots[1]][each_drug] = 1
                        else:
                            self.robot_drug_canister_info_dict[robots[0]][each_drug] = 1
                            self.robot_drug_canister_info_dict[robots[1]][each_drug] = 0

            else:
                if not frozen_as_1x:
                    for each_drug, canister in self.drug_canister_info_dict_updated.items():
                        canister_len = len(canister)
                        max_usable_canister = math.ceil(self.drug_canister_usage[each_drug]['max'] / 2)
                        self.robot_drug_canister_info_dict[robots[0]][
                            each_drug] = max_usable_canister if max_usable_canister <= canister_len else canister_len
                else:
                    for each_drug, canister in self.drug_canister_info_dict_updated.items():
                        canister_len = len(canister)
                        if canister_len > 0:
                            self.robot_drug_canister_info_dict[robots[0]][each_drug] = 1
                # self.robot_drug_canister_info_dict[robots[0]] = {key: len(value) for key, value in
                #                                                  self.drug_canister_info_dict_updated.items()}
            # self.robot_drug_canister_info_dict[robots[0]] = deepcopy(self.drug_canister_info_dict_updated)
        # temp code ends

        unique_matrix_list = []
        unique_matrix_data_list = []

        for robot in robot_cluster_dict.keys():
            robot_drop_count_dict[robot] = 0
            #  temp code to handle canister distribution in both the robots
            robot_quadrant_drug_distribution_dict[robot] = dict()
            self.drug_canister_info_dict_updated = deepcopy(self.robot_drug_canister_info_dict[robot])
            for each_drug, canister in self.drug_canister_info_dict_updated.items():
                if canister == 0:
                    self.fully_manual_drugs.append(each_drug)

            pack_set = robot_cluster_dict[robot]["packs"]
            pack_slot_drug_dict_robotwise = {}
            for pack in pack_set:
                pack_slot_drug_dict_robotwise[pack] = self.pack_slot_drug_dict[pack]

            self.num_of_quadrants = 4
            print("2121")
            '''
            Here we try to keep those drugs which are already in robot to that place so that we can reduce transfers in 1x.
            For Nx we need to run quadrant distribution algo.
            '''
            if settings.CR_STRATEGY == 1:
                quadrant_drug_len = {}
                quadrant_drug_dict = {}
                temp_quadrant_drug_len = {}
                temp_quadrant_drug_dict = {}
                drug_set = robot_cluster_dict[robot]["drugs"]
                for i in range(1,5):
                    quadrant_drug_len[i] = 0
                    quadrant_drug_dict[i] = set()
                    temp_quadrant_drug_len[i] = 0
                    temp_quadrant_drug_dict[i] = set()
                unique = set()

                qty_canister_location_info_dict = dict()
                for can, location_tuple in self.canister_location_info_dict.items():
                    qty_canister_location_info_dict[can] = (location_tuple[0],location_tuple[1],location_tuple[2],int(self.canister_qty_dict[can]), self.canister_expiry_status_dict[can])

                # sorting based on expiry status and qty
                # priority : expires soon, expired, normal expiry
                sorted_qty_canister_location_info_dict = OrderedDict(sorted(qty_canister_location_info_dict.items(), key=lambda x: (-(x[1][4]==1),-(x[1][4]==0),-(x[1][4]==2), -x[1][3])))

                for can,location_tuple in sorted_qty_canister_location_info_dict.items():
                    if location_tuple[0] == robot:
                        if location_tuple[2]:
                            if location_tuple[2] not in quadrant_drug_dict:
                                quadrant_drug_dict[location_tuple[2]] = set()
                            if self.canister_drug_info_dict[can] in drug_set and self.canister_drug_info_dict[can] not in unique:
                                quadrant_drug_dict[location_tuple[2]].add(self.canister_drug_info_dict[can])
                                unique.add(self.canister_drug_info_dict[can])
                # self.canister_drug_info_dict
                # quadrant_drug_dict = {1:{'1'},2:{'2'},3:{'3'},4:{'4'}}
                if not quadrant_drug_dict.values():
                    in_drug = set()
                else:
                    in_drug = reduce(or_, list(quadrant_drug_dict.values()))#quadrant_drug_dict.values()
                rem_drug_set = drug_set - in_drug
                split = math.ceil(len(rem_drug_set) / 4)
                for qd,drug in quadrant_drug_dict.items():
                    quadrant_drug_len[qd] = len(drug)
                quadrant_drug_len = OrderedDict(sorted(quadrant_drug_len.items(),key=lambda k:k[1],reverse=False))
                qd = list(quadrant_drug_len.keys())[0]
                drug_list = list(sorted(rem_drug_set))
                while len(drug_list):
                    drug = drug_list.pop(0)
                    if 1 <= split - len(temp_quadrant_drug_dict[qd]):
                        temp_quadrant_drug_dict[qd].add(drug)
                        temp_quadrant_drug_len[qd] += 1
                        temp_quadrant_drug_len = OrderedDict(
                            sorted(temp_quadrant_drug_len.items(), key=lambda k: k[1], reverse=False))
                        qd = list(temp_quadrant_drug_len.keys())[0]
                for q in range(1,5):
                    quadrant_drug_dict[q].update(temp_quadrant_drug_dict[q])

                self.quadrant_distribution_data = {}
                for qdt,drugs in quadrant_drug_dict.items():
                    if qdt not in self.quadrant_distribution_data:
                        self.quadrant_distribution_data[qdt] = {}
                    self.quadrant_distribution_data[qdt]['drugs'] = sorted(list(drugs))

                self.temp_pack_slot_drug_dict = {}
                for pack, slots in pack_slot_drug_dict_robotwise.items():
                    self.temp_pack_slot_drug_dict[pack] = dict()
                    for each_slot, drug_set in slots.items():
                        self.temp_pack_slot_drug_dict[pack][each_slot] = set()
                        for each_drug in drug_set:
                            if each_drug not in self.fully_manual_drugs:
                                self.temp_pack_slot_drug_dict[pack][each_slot].add(each_drug)
                        if len(self.temp_pack_slot_drug_dict[pack][each_slot]) == 0:
                            self.temp_pack_slot_drug_dict[pack].pop(each_slot)
                    if len(self.temp_pack_slot_drug_dict[pack]) == 0:
                        self.temp_pack_slot_drug_dict.pop(pack)
                self.updated_pack_slot_drug_dict = self.temp_pack_slot_drug_dict

            else:
                self.sort_drug_canister_dict_by_min_usage()
                """
                When we want to use Nx strategy but also minimise canister transfers. So here is the freeze canister logic
                """
                if settings.FREEZE_CANISTER:
                    """Creating data structures to know combinations of drugs so that we can distribute them on base of most common combination quadrant
                        This function can be also found inside RecommendCanisterDistributionInQuadrants class
                    """
                    self.create_data_structure_for_processing()
                    self.quadrant_distribution_data, self.updated_pack_slot_drug_dict = self.frozen_canister_algo(robot_cluster_dict, robot, pack_slot_drug_dict_robotwise)
                else:
                    self.rcdiq = RecommendCanisterDistributionInQuadrants(
                        pack_slot_drug_dict=pack_slot_drug_dict_robotwise,
                        drug_canister_info_dict=self.drug_canister_info_dict_updated,
                        num_of_quadrants=self.num_of_quadrants, fully_manual_drugs=self.fully_manual_drugs)


                    # TODO: No of quadrants will not be passed from here.It should be passed at the time of instantation
                    print("this")
                    self.quadrant_distribution_data, self.updated_pack_slot_drug_dict = self.rcdiq.run_algo()
            print("this one")
            logger.info("Permutation starts for robot {}".format(robot))
            permutation_list = self.get_permutation_list()
            total_permutations = list(map(list, set(permutations(permutation_list))))
            min_time = 10000000000000000000000000000
            # if (settings.CR_STRATEGY == 1) or (settings.FREEZE_CANISTER == 1 and settings.SYSTEM_SPEED == 4):
            #     total_permutations = [[1, 2, 3, 4]]
            response_value_list = list(self.quadrant_distribution_data.values())
            for permutation in total_permutations:
                if (settings.CR_STRATEGY == 1) or (settings.FREEZE_CANISTER == 1 and settings.SYSTEM_SPEED_MODE == 2):
                    permutation = [1,2,3,4]
                logger.info("Permutation {}".format(permutation))
                permutation = self.get_calculated_permutation(permutation)
                possible_response = OrderedDict(sorted(dict(list(zip(permutation,response_value_list))).items()))
                response = {"quadrant_drugs": possible_response,
                            "pack_slot_drug_dict": self.updated_pack_slot_drug_dict}
                rd = RecommendDrops(distribution_response=response,unique_matrix_list=unique_matrix_list,unique_matrix_data_list=unique_matrix_data_list)
                pack_wise_detailed_time,total_time,pack_slot_drop_info_dict,pack_slot_drug_config_id_dict,pack_slot_drug_quad_id_dict,unique_matrix_list,unique_matrix_data_list = rd.get_pack_fill_analysis()
                print("iteration")
                # pack_wise_detailed_time,total_time = self.get_pack_fill_analysis(response)
                if total_time < min_time:
                    self.quadrant_distribution_data = possible_response
                    self.pack_slot_drop_info_dict.update(pack_slot_drop_info_dict)
                    self.pack_slot_drug_config_id_dict.update(pack_slot_drug_config_id_dict)
                    self.pack_slot_drug_quad_id_dict.update(pack_slot_drug_quad_id_dict)
                    min_time = total_time
                    pack_wise_time[robot] = {'total_packs':len(robot_cluster_dict[robot]["packs"]),'pack_wise_time':pack_wise_detailed_time,'total_seconds':total_time,'total_minutes':total_time/60,'total_drops':total_time/10}
                if (settings.CR_STRATEGY == 1) or (settings.FREEZE_CANISTER == 1 and settings.SYSTEM_SPEED_MODE == 2):
                    break
                # if self.quadrant_distribution_data[0]['drugs'] == self.quadrant_distribution_data[1]['drugs'] == self.quadrant_distribution_data[2]['drugs'] == self.quadrant_distribution_data[3]['drugs']:
                # break
            print("that one")
            for pack,data in pack_wise_time[robot]['pack_wise_time'].items():
                robot_drop_count_dict[robot] += len(data['drops'])
                total_drop_count += len(data['drops'])
                drop_count_list.append(len(data['drops']))
                time_count_list.append(data['time_in_sec.'])
                pack_list.append(pack)
                slots = len(self.updated_pack_slot_drug_dict[pack])
                time_v2 = len(list(self.pack_slot_drug_dict[pack].keys()))*10
                analysis_dict[pack] = {'pack':pack,'drop_V3':len(data['drops']),'slots':slots}

            print("that these")
            # TODO : Changing Temporarily
            # robot_quadrant_drug_distribution_dict[robot] = {1: {'drugs': {'763850104##4590', '458020650##18698', '009046751##16995', '678770248##60293', '683820080##3974', '678770223##21414', '710930132##13318', '763850105##4591', '317220537##44633', '627560798##4540', '009046457##3009', '005361064##3011', '009047591##1645', '683820116##21156', '005363790##64176', '005364046##2532', '435980166##27960', '683820114##21154'}, 'combinations': [['005361064##3011'], ['710930132##13318'], ['009047591##1645'], ['435980166##27960'], ['683820116##21156'], ['115340165##2366', '005363790##64176'], ['683820080##3974', '458020650##18698'], ['317220537##44633'], ['678770248##60293', '683820079##3977'], ['009046751##16995'], ['005364046##2532'], ['763850105##4591', '683820114##21154', '683820116##21156'], ['009046457##3009', '678770223##21414'], ['678770223##21414'], ['627560798##4540'], ['005364046##2532', '435980166##27960'], ['763850104##4590', '009046751##16995']], 'slots': 0}, 2: {'drugs': {'435980166##27960', '009046751##16995'}, 'combinations': [['763850104##4590', '009046751##16995'], ['009046751##16995'], ['005364046##2532', '435980166##27960'], ['435980166##27960']], 'slots': 0}, 3: {'drugs': {'763850104##4590', '458020650##18698', '009046751##16995', '683820114##21154', '678770248##60293', '683820080##3974', '710930132##13318', '763850105##4591', '678770223##21414', '009046457##3009', '627560798##4540', '009047591##1645', '005361064##3011', '683820116##21156', '435980166##27960', '005364046##2532', '005363790##64176', '317220537##44633'}, 'combinations': [['009047591##1645'], ['005361064##3011'], ['435980166##27960'], ['683820116##21156'], ['115340165##2366', '005363790##64176'], ['683820080##3974', '458020650##18698'], ['317220537##44633'], ['678770223##21414'], ['678770248##60293', '683820079##3977'], ['009046751##16995'], ['005364046##2532'], ['763850105##4591', '683820114##21154', '683820116##21156'], ['009046457##3009', '678770223##21414'], ['710930132##13318'], ['627560798##4540'], ['005364046##2532', '435980166##27960'], ['763850104##4590', '009046751##16995']], 'slots': 0}, 4: {'drugs': {'009046751##16995', '678770223##21414', '005361064##3011', '683820116##21156', '005364046##2532', '435980166##27960'}, 'combinations': [['005361064##3011'], ['435980166##27960'], ['683820116##21156'], ['009046751##16995'], ['005364046##2532'], ['763850105##4591', '683820114##21154', '683820116##21156'], ['009046457##3009', '678770223##21414'], ['678770223##21414'], ['005364046##2532', '435980166##27960'], ['763850104##4590', '009046751##16995']], 'slots': 0}}

            robot_quadrant_drug_distribution_dict[robot] = self.quadrant_distribution_data

            # analysis_dict = {'packs':pack_list,'drops_V3':drop_count_list,'drops_V2':drop_count_list_v2,'time_V3':time_count_list,'time_V2':time_count_list_v2}
            print("these")
            logger.info("Permutation ends for robot {}".format(robot))
            # sorted_prioirty_to_reg_df = pd.DataFrame.from_dict(analysis_dict, orient='index', columns=['pack','drop_V3','slots'])
            # p_to_reg_file = sorted_prioirty_to_reg_df.to_csv(
            #     "/home/meditab/Desktop/canister_recommendation_V3_analysis.csv")
        print("Robot drop count dict :- ",robot_drop_count_dict)
        return robot_quadrant_drug_distribution_dict, self.pack_slot_drop_info_dict,self.robot_drug_canister_info_dict,self.pack_slot_drug_config_id_dict,self.pack_slot_drug_quad_id_dict

    def sort_drug_canister_dict_by_min_usage(self):
        """
        In case that if we have some canister which is set to use least 2 cnaister, we will sort the dictionary so that
        we will consider that drug as priority to keep 2 canister in 2 quadrant.
        :return:
        """
        try:
            temp_min_usage_drug = []
            for drug, canister_count in self.drug_canister_info_dict_updated.items():
                if drug in self.drug_canister_usage.keys():
                    temp_min_usage_drug.append(self.drug_canister_usage[drug]['min'])
                else:
                    print("modify_drug_canister_info_dict, unique drug not present with usage : {}".format(drug))
            if temp_min_usage_drug and len(temp_min_usage_drug) == len(self.drug_canister_info_dict_updated.items()):
                temp_drug_canister_info_dict = OrderedDict({x[0]:x[1] for x, _ in
                                                            sorted(zip(self.drug_canister_info_dict_updated.items(), temp_min_usage_drug),
                                                                   key=lambda item: item[1], reverse=True)})
                self.drug_canister_info_dict_updated = temp_drug_canister_info_dict
        except Exception as e:
            logger.info("Error in modify_drug_canister_info_dict {}".format(e))
            raise

    def frozen_canister_algo(self, robot_cluster_dict, robot, pack_slot_drug_dict_robotwise):
        try:
            """Init. Variables"""
            quadrant_drug_len = OrderedDict()
            quadrant_drug_dict = OrderedDict()
            temp_quadrant_drug_len = OrderedDict()
            temp_quadrant_drug_dict = OrderedDict()
            multi_can_drug = set()
            frz_time_quad_dict =  OrderedDict()  # holds batch drugs which are added while freezing so that we won't remove those drugs
            extra_drug_per_quad = OrderedDict()  # Holds drug that is not needed in current batch and is in quad
            drug_count_placed_inside_quad_count =OrderedDict()  # holds which drug is placed for how many times
            drug_to_be_placed_in_quad_after_frzing = OrderedDict()  # Holds drugs that are needed to be places in the quad after freezing
            inside_robot_quad_data = OrderedDict()  # Holds drugs which are in robot per quad
            extra_drug_in_quad_for_batch = {}
            self.single_canister_drug = set()
            self.multi_canister_drug = set()
            drug_set = robot_cluster_dict[robot]["drugs"]  # drugs needs to be inside the robot.
            """
            creating datasets per quadrant
            """
            for i in range(1, 5):
                quadrant_drug_len[i] = 0
                quadrant_drug_dict[i] = set()  # Holds all the drugs which are going to be added in the robot for the batch
                temp_quadrant_drug_len[i] = 0
                temp_quadrant_drug_dict[i] = set() # USe to save data while not adding it to main dict.
                frz_time_quad_dict[i] = set()
                extra_drug_per_quad[i] = set()
                inside_robot_quad_data[i] = list()
                extra_drug_in_quad_for_batch[i] = set()

            drug_canister_info_dict_temp = deepcopy(
                self.drug_canister_info_dict_updated)  # holds drugs and there usable canister
            # unique = set()
            for drug, can in self.drug_canister_info_dict_updated.items():
                if drug in drug_set:
                    if can > 1:
                        self.multi_canister_drug.add(drug)
                    elif can == 1:
                        self.single_canister_drug.add(drug)


            explored_drugs_with_count = {}  # Drug count which where in robot and in drug_set
            extra_canister_dict = {}
            """Sorting canisters on the basis of there quantity so we could use cansiters which have max quantity firdt"""
            qty_canister_location_info_dict = dict()
            for can, location_tuple in self.canister_location_info_dict.items():
                qty_canister_location_info_dict[can] = (
                    location_tuple[0], location_tuple[1], location_tuple[2],
                    location_tuple[3], int(self.canister_qty_dict[can]))

            sorted_qty_canister_location_info_dict = OrderedDict(
                sorted(qty_canister_location_info_dict.items(), key=lambda x: -x[1][4]))

            """
            For each canisters, if the canister is in robot, we put that drug in the quadrant where the canister is in that device
            """

            for can, location_tuple in sorted_qty_canister_location_info_dict.items():
                if location_tuple[0] == robot:
                    if location_tuple[2]:
                        if location_tuple[2] not in quadrant_drug_dict:
                            quadrant_drug_dict[location_tuple[2]] = set()
                        drug = self.canister_drug_info_dict[can]
                        inside_robot_quad_data[location_tuple[2]].append(drug)
                        """
                        
                        Check if drug is needed in batch
                        """

                        if drug in drug_set:
                            if not location_tuple[3]:
                                if drug not in explored_drugs_with_count.keys():
                                    explored_drugs_with_count[drug] = 1
                                else:
                                    explored_drugs_with_count[drug] += 1

                                if drug in drug_canister_info_dict_temp.keys() and drug_canister_info_dict_temp[drug] > 0:
                                    if drug not in quadrant_drug_dict[location_tuple[2]]:
                                        quadrant_drug_dict[location_tuple[2]].add(drug)
                                        drug_canister_info_dict_temp[drug] = drug_canister_info_dict_temp[drug] -1
                                        if drug not in drug_count_placed_inside_quad_count.keys():
                                            drug_count_placed_inside_quad_count[drug] = 1
                                        else:
                                            drug_count_placed_inside_quad_count[drug] += 1

                                        frz_time_quad_dict[location_tuple[2]].add(drug)
                                else:
                                    extra_drug_in_quad_for_batch[location_tuple[2]].add(drug)

                        else:

                            extra_drug_per_quad[location_tuple[2]].add(drug)

                            if drug in drug_canister_info_dict_temp.keys():
                                drug_canister_info_dict_temp.pop(drug)


            # At this point, we have ,ulticanoster drugs that has to be placed in robot/// some are already placed.
            #  Also we are going to use drug_canister_info_dict_temp to use as drugs which we are going to be in batch

            # calculate combination dict
            quadrant_drug_combination = {1: set(), 2: set(), 3:set(), 4:set()}
            for quad in quadrant_drug_dict.keys():
                for drug in quadrant_drug_dict[quad]:
                    if drug in self.drug_combinations_dict.keys():
                        quadrant_drug_combination[quad].update(self.drug_combinations_dict[drug])

            """
            Placing remaning canister which had sngle cnasiter to use and was not already placed
            """
            try:
                for drug in self.single_canister_drug:
                    if drug_canister_info_dict_temp[drug] >0:
                        print("Trying to add drug {} in any quad".format(drug))
                        combination = set(self.drug_combinations_dict[drug])
                        common_combination_list = [0,0,0,0]
                        """
                        First we find out that which quadrant has most of common combinations
                        """
                        common_combination_list[0] = len(list(quadrant_drug_combination[1] & combination))
                        common_combination_list[1] = len(list(quadrant_drug_combination[2] & combination))
                        common_combination_list[2] = len(list(quadrant_drug_combination[3] & combination))
                        common_combination_list[3] = len(list(quadrant_drug_combination[4] & combination))
                        preferd_quad = int(common_combination_list.index(max(common_combination_list))) + 1
                        given_quad = None
                        prefered_quad_len = len(inside_robot_quad_data[preferd_quad])
                        space_found = False

                        """
                        to compare the exact capacity of preferd quadrant
                        """
                        quadrant_capacity = self.robot_quadrant_enable_locations[robot][preferd_quad]

                        if len(inside_robot_quad_data[preferd_quad]) >= quadrant_capacity:
                            # ============================= Try fitting in quad without removing
                            alt_comb_list = deepcopy(common_combination_list)
                            alt_comb_list[preferd_quad - 1] = 0
                            preferd_quad = int(alt_comb_list.index(max(alt_comb_list))) + 1
                            checked_quad = [preferd_quad]
                            """
                            to compare the exact capacity of preferd quadrant
                            """
                            quadrant_capacity = self.robot_quadrant_enable_locations[robot][preferd_quad]
                            for _ in range(0,3):
                                if len(inside_robot_quad_data[preferd_quad]) >= quadrant_capacity:
                                    alt_comb_list[preferd_quad - 1] = 0
                                    checked_quad.append(preferd_quad)
                                    temp_prefred_quad = int(
                                        alt_comb_list.index(max(alt_comb_list))) + 1
                                    if temp_prefred_quad in checked_quad:
                                        # preferd_quad = random.choice([q for q in [1,2,3,4] if q not in checked_quad])
                                        # or optimised way
                                        preferd_quad = min(inside_robot_quad_data, key=lambda k : len(inside_robot_quad_data[k]))

                                    else:
                                        preferd_quad = temp_prefred_quad
                                else:
                                    space_found = True
                                    break

                            # if len(inside_robot_quad_data[preferd_quad]) >= settings.QUAD_CANISTER_CAPACITY:
                            #     alt_comb_list[preferd_quad] = 0
                            #     preferd_quad = int(alt_comb_list.index(max(alt_comb_list))) + 1
                            #     if len(inside_robot_quad_data[preferd_quad]) >= settings.QUAD_CANISTER_CAPACITY:
                            #         alt_comb_list[preferd_quad] = 0
                            #         preferd_quad = int(alt_comb_list.index(max(alt_comb_list))) + 1
                            #         if len(inside_robot_quad_data[preferd_quad]) >= settings.QUAD_CANISTER_CAPACITY:
                            #             alt_comb_list[preferd_quad] = 0
                            #             preferd_quad = int(alt_comb_list.index(max(alt_comb_list))) + 1
                            #         else:
                            #             space_found = True
                            #     else:
                            #         space_found = True
                            # else:
                            #     space_found = True

                            """Try removing drugs from quadrant"""
                            if not space_found:
                                checked_quad = []
                                for _ in range(0,4):
                                    space_found = self.create_space_for_drug_in_quadrant(extra_drug_per_quad,
                                                                                         inside_robot_quad_data,
                                                                                         preferd_quad, space_found,
                                                                                         drug_count_placed_inside_quad_count,
                                                                                         frz_time_quad_dict,
                                                                                         extra_drug_in_quad_for_batch)

                                    if space_found:
                                        given_quad = preferd_quad
                                        break
                                    else:
                                        checked_quad.append(preferd_quad)
                                        common_combination_list[preferd_quad - 1] = 0
                                        temp_prefred_quad = int(common_combination_list.index(max(common_combination_list))) + 1
                                        if temp_prefred_quad in checked_quad:
                                            preferd_quad = random.choice([q for q in [1,2,3,4] if q not in checked_quad])
                                        else:
                                            preferd_quad = temp_prefred_quad


                            if not space_found:
                                print("Error Found in canister recommendation")
                                raise Exception("Unable to add single canister of drug {} in any quadrant".format(drug))

                        else:
                            space_found = True

                        if space_found and given_quad:
                            print("Adding drug {} in quadrant {} ".format(drug, given_quad))

                            quadrant_drug_dict[given_quad].add(drug)
                            inside_robot_quad_data[given_quad].append(drug)
                            if drug not in drug_count_placed_inside_quad_count.keys():
                                drug_count_placed_inside_quad_count[drug] = 1
                            else:
                                drug_count_placed_inside_quad_count[drug] += 1
                            quadrant_drug_combination[given_quad].update(self.drug_combinations_dict[drug])

                        elif space_found and preferd_quad:
                            print("Adding drug {} in quadrant {} ".format(drug, preferd_quad))

                            quadrant_drug_dict[preferd_quad].add(drug)
                            quadrant_drug_combination[preferd_quad].update(self.drug_combinations_dict[drug])
                            inside_robot_quad_data[preferd_quad].append(drug)
                            if drug not in drug_count_placed_inside_quad_count.keys():
                                drug_count_placed_inside_quad_count[drug] = 1
                            else:
                                drug_count_placed_inside_quad_count[drug] += 1
            except(KeyError, IndexError) as e:
                logger.error("Error in forzen singlecanister : {}".format(e))
                raise e
            except Exception as e:
                logger.error("Error in forzen singlecanister : {}".format(e))
                raise e

            try:
                for drug in self.multi_canister_drug:
                    required_can_count = self.drug_canister_info_dict_updated[drug]
                    placed_count = drug_count_placed_inside_quad_count[drug] if drug in drug_count_placed_inside_quad_count.keys() else 0
                    if required_can_count > placed_count:
                        print("Trying to add drug {} in any quad".format(drug))
                        quadrant = {1,2,3,4}
                        for quad, quad_drug in quadrant_drug_dict.items():
                            if drug in quad_drug:
                                quadrant.remove(quad)
                        for i in range(required_can_count - placed_count):
                            if drug_canister_info_dict_temp[drug] > 0:
                                combination = set(self.drug_combinations_dict[drug])
                                common_combination_dict = {}
                                quadrant = {1, 2, 3, 4}
                                for quad, quad_drug in quadrant_drug_dict.items():
                                    if drug in quad_drug:
                                        quadrant.remove(quad)
                                for quad in quadrant:
                                    common_combination_dict[quad] = len(list(quadrant_drug_combination[quad] & combination))

                                preferd_quad = max(common_combination_dict, key = common_combination_dict.get)
                                given_quad = None
                                prefered_quad_len = len(inside_robot_quad_data[preferd_quad])
                                space_found = False
                                """
                                to compare the exact capacity of preferd quadrant
                                """
                                quadrant_capacity = self.robot_quadrant_enable_locations[robot][preferd_quad]
                                if len(inside_robot_quad_data[preferd_quad]) >= quadrant_capacity:
                                    alt_comb_list = deepcopy(common_combination_dict)
                                    del alt_comb_list[preferd_quad]
                                    l = len(alt_comb_list.keys())

                                    for _ in range(l):
                                        preferd_quad = max(alt_comb_list, key = alt_comb_list.get)
                                        """
                                        to compare the exact capacity of preferd quadrant
                                        """
                                        quadrant_capacity = self.robot_quadrant_enable_locations[robot][preferd_quad]
                                        if len(inside_robot_quad_data[preferd_quad]) >= quadrant_capacity:
                                            del alt_comb_list[preferd_quad]
                                        else:
                                            space_found = True
                                            break

                                    # Remove drug that is not in use from inside robot quad data3
                                    if not space_found:
                                        for _ in range(len(common_combination_dict.keys())):
                                            space_found = self.create_space_for_drug_in_quadrant(extra_drug_per_quad,
                                                                                                 inside_robot_quad_data,
                                                                                                 preferd_quad, space_found,
                                                                                                 drug_count_placed_inside_quad_count,
                                                                                                 frz_time_quad_dict,
                                                                                                 extra_drug_in_quad_for_batch
                                                                                                 )

                                            if space_found:
                                                given_quad = preferd_quad
                                                break
                                            else:
                                                del common_combination_dict[preferd_quad]
                                                if len(common_combination_dict.keys()):
                                                    preferd_quad = max(common_combination_dict, key = common_combination_dict.get)


                                    if not space_found:
                                        print("Error Found in canister recommendation")
                                        # raise Exception

                                else:
                                    space_found = True

                                if space_found and given_quad:
                                    print("Adding drug {} in quadrant {} ".format(drug, given_quad))
                                    quadrant_drug_dict[given_quad].add(drug)
                                    inside_robot_quad_data[given_quad].append(drug)
                                    if drug not in drug_count_placed_inside_quad_count.keys():
                                        drug_count_placed_inside_quad_count[drug] = 1
                                    else:
                                        drug_count_placed_inside_quad_count[drug] += 1
                                    quadrant_drug_combination[given_quad].update(self.drug_combinations_dict[drug])

                                elif space_found and preferd_quad:
                                    print("Adding drug {} in quadrant {} ".format(drug, preferd_quad))
                                    quadrant_drug_dict[preferd_quad].add(drug)
                                    quadrant_drug_combination[preferd_quad].update(self.drug_combinations_dict[drug])
                                    inside_robot_quad_data[preferd_quad].append(drug)
                                    if drug not in drug_count_placed_inside_quad_count.keys():
                                        drug_count_placed_inside_quad_count[drug] = 1
                                    else:
                                        drug_count_placed_inside_quad_count[drug] += 1
                            placed_count = drug_count_placed_inside_quad_count.get(drug, 0)

                    if not drug_count_placed_inside_quad_count.get(drug, 0):
                        raise Exception("Unable to place multicanister drug {} in any quadrant".format(drug))
            except(KeyError, IndexError) as e:
                logger.error("Error in forzen multicanister : {}".format(e))
                raise e
            except Exception as e:
                logger.error("Error in forzen multicanister : {}".format(e))
                raise e


            # =====================================================================================
            quadrant_distribution_data = {}
            for qdt, drugs in quadrant_drug_dict.items():
                if qdt not in quadrant_distribution_data:
                    quadrant_distribution_data[qdt] = {}
                quadrant_distribution_data[qdt]['drugs'] = sorted(list(drugs))

            temp_pack_slot_drug_dict = {}
            for pack, slots in pack_slot_drug_dict_robotwise.items():
                temp_pack_slot_drug_dict[pack] = dict()
                for each_slot, drug_set in slots.items():
                    temp_pack_slot_drug_dict[pack][each_slot] = set()
                    for each_drug in drug_set:
                        if each_drug not in self.fully_manual_drugs:
                            temp_pack_slot_drug_dict[pack][each_slot].add(each_drug)
                    if len(temp_pack_slot_drug_dict[pack][each_slot]) == 0:
                        temp_pack_slot_drug_dict[pack].pop(each_slot)
                if len(temp_pack_slot_drug_dict[pack]) == 0:
                    temp_pack_slot_drug_dict.pop(pack)
            updated_pack_slot_drug_dict = temp_pack_slot_drug_dict

            return quadrant_distribution_data, updated_pack_slot_drug_dict

        except (KeyError, ValueError, IndexError) as e:
            logger.error("Error in Frozen Canister: {}".format(e))
            print(e)
            raise e

        except Exception as e:
            logger.error("Error in Frozen Canister: {}".format(e))
            print(e)
            raise e

    def create_space_for_drug_in_quadrant(self, extra_drug_per_quad, inside_robot_quad_data, preferd_quad, space_found,
                                          drug_count_placed_inside_quad_count, frz_time_quad_dict,
                                          extra_drug_in_quad_for_batch):
        # remove not required batch drug
        if not space_found:
            if len(extra_drug_per_quad[preferd_quad]) > 0:
                poped_drug = extra_drug_per_quad[preferd_quad].pop()
                inside_robot_quad_data[preferd_quad].remove(poped_drug)
                space_found = True

        # remove required batch drug which have already enough required canister in the robot
        if not space_found:
            if len(extra_drug_in_quad_for_batch[preferd_quad]) > 0:
                poped_drug = extra_drug_in_quad_for_batch[preferd_quad].pop()
                inside_robot_quad_data[preferd_quad].remove(poped_drug)
                space_found = True

        # Remove multiple canister of same drug placed in robot in preferred quadrant.
        if not space_found:
            for drug in self.multi_canister_drug:
                if drug_count_placed_inside_quad_count.get(drug, 0) > settings.ALT_MAX_CANISTER_COUNT and drug not in frz_time_quad_dict[preferd_quad]:
                    try:
                        inside_robot_quad_data[preferd_quad].remove(drug)
                    except (ValueError, KeyError) as e:
                        logger.debug(
                            "In create_space_for_drug_in_quadrant cannot remove drug {} from quad {}".format(drug,
                                                                                                             preferd_quad))
                        continue
                    drug_count_placed_inside_quad_count[drug] -= 1
                    space_found = True
        return space_found


    def create_data_structure_for_processing(self):
        self.drugs_combination_list = []
        self.drug_combination_frequency_dict = {}
        self.combination_slot_dict = {}
        self.canister_drugs_in_packs = set()
        self.drug_combinations_dict = {}
        self.combinations_dict = {}
        self.drug_set = set()
        self.total_number_of_slots = 0

        number_of_slots = 0
        for pack, slot_drugs in self.pack_slot_drug_dict.items():
            for slots, drug in slot_drugs.items():

                drugs = list(drug)
                if len(drugs) == 0:  # i.e 0 canister drug
                    continue
                self.canister_drugs_in_packs.update(set(drugs))

                if drugs not in self.drugs_combination_list:
                    self.drugs_combination_list.append(drugs)
                    combination_index = self.drugs_combination_list.index(drugs)
                    self.combinations_dict[combination_index] = drugs
                    self.combination_slot_dict[combination_index] = []
                    self.drug_combination_frequency_dict[combination_index] = 0
                else:
                    combination_index = self.drugs_combination_list.index(drugs)

                self.drug_combination_frequency_dict[combination_index] += 1
                self.combination_slot_dict[combination_index].append(str(pack) + '_' + str(slots))
                self.drug_set.update(drugs)
                for each_drug in drug:
                    if each_drug not in self.drug_combinations_dict.keys():
                        self.drug_combinations_dict[each_drug] = []
                    if combination_index not in self.drug_combinations_dict[each_drug]:
                        self.drug_combinations_dict[each_drug].append(combination_index)
                number_of_slots += 1

        self.total_number_of_slots = number_of_slots if self.total_number_of_slots == 0 else self.total_number_of_slots


    def get_quadrant_wise_canister_data(self):
        """
        canister_quadrant_robot: dict which stores canister_id as a key and list
                                of [quadrant , robot_id, canister_id] as value
        @return:
        """
        self.canister_quadrant_robot = dict()
        self.robot_quad_drug_canister_dict = dict()

        for canister, location_tuple in self.canister_location_info_dict.items():
            self.canister_quadrant_robot[canister] = (location_tuple[2], location_tuple[0], canister,int(self.canister_qty_dict[canister]))

        # prepare dict to get drugs are distributed in which device and quad
        drug_distribution_dict = {}
        for robot, quadrant_drug in self.robot_quadrant_drug_distribution_dict.items():
            for quadrant, drugs in quadrant_drug.items():
                for drug in drugs['drugs']:
                    if not drug_distribution_dict.get(drug):
                        drug_distribution_dict[drug] = set()
                    drug_distribution_dict[drug].add((robot, quadrant))

        self.drug_canister_info_dict_robot = deepcopy(self.drug_canister_info_dict)
        for robot, quad_drugs in self.robot_quadrant_drug_distribution_dict.items():
            self.robot_quad_drug_canister_dict[robot] = dict()
            for quad, drugs in quad_drugs.items():
                self.robot_quad_drug_canister_dict[robot][quad] = dict()
                for each_drug in drugs['drugs']:
                    canister_found = False
                    canister_list = self.drug_canister_info_dict_robot[each_drug]
                    canister_expiry_dict = {0: [], 1:[], 2:[]}
                    canister_location_tuple = [self.canister_location_info_dict[canister]+(self.canister_expiry_status_dict[canister],) for canister in canister_list]

                    for can in canister_list:
                        canister_expiry_dict[self.canister_expiry_status_dict[can]].append(can)

                    # priority : expire soon, expired, normal canister
                    if len(drug_distribution_dict[each_drug]) <= len(canister_expiry_dict[1]):
                        canister_list_optim = canister_expiry_dict[1]
                    elif len(drug_distribution_dict[each_drug]) <= len(canister_expiry_dict[1])+len(canister_expiry_dict[0]):
                        canister_list_optim = canister_expiry_dict[1]+canister_expiry_dict[0]
                    else:
                        canister_list_optim = canister_expiry_dict[1] + canister_expiry_dict[0] + canister_expiry_dict[2]
                    for each_can in canister_list_optim:
                        location_tup = self.canister_location_info_dict[each_can]
                        if location_tup[0] == robot and location_tup[2] == quad:
                            self.robot_quad_drug_canister_dict[robot][quad][each_drug] = each_can
                            self.drug_canister_info_dict_robot[each_drug].discard(each_can)
                            drug_distribution_dict[each_drug].discard((robot, quad))
                            canister_found = True
                            break
                    if not canister_found:
                        self.robot_quad_drug_canister_dict[robot][quad][each_drug] = None
        logger.info("robot_quad_drug_canister_dict created to freeze canister in same quad {}".format(self.robot_quad_drug_canister_dict))

    def get_suitable_canister(self, drug, robot):
        """
        canister_location : list of tuples where each tuple has (quadrant, robot_id, canister_id)
        drug_info_list : it gives list of quad and robot in which this drug is required
        @param canister_set:
        @param quadrant:
        @param robot:
        @return: Returns suitable canister which fits best for transfer
        """
        logger.info("data")
        canister_location = list()
        canister_found = False
        canister_set = self.drug_canister_info_dict_robot[drug]
        canister_list = list(canister_set)
        if len(canister_list) > 0:
            for can in canister_list:
                canister_location.append(self.canister_quadrant_robot[can].__add__((self.canister_expiry_status_dict[can], )))

            new_cl = []
            for c in canister_location:
                # c : (quadrant, device_id, canister_id, qty)
                #TODO: Need to fetch [1,2,3] from database by device_type_id CSR and ROBOT.
                if not c[0] and not c[1] or c[1] not in [1,2,3]:
                    new_cl.append((1000, 1000,c[2], c[3], c[4]))
                else:
                    new_cl.append((c[0] or -1,c[1] or -1,c[2],c[3], c[4]))
                # else:
                #     new_cl.append(c)

            # get available canister and sort according to qty.  >> need to change: sort according to expiry_status
            # expiry priority: expire soon, expired, normal expiry
            new_cl = sorted(new_cl, key=lambda L: (-(L[4]==1), -(L[4]==0), -(L[4]==2) ,L[0], -L[3]))

            # for each_location in new_cl:
            #         if each_location[1] == robot and each_location[4] in [0,1]:
            #             canister_found = True
            #             self.drug_canister_info_dict_robot[drug].discard(each_location[2])
            #             return each_location[2]
            if canister_found == False:
                logger.info(new_cl[0][2])
                self.drug_canister_info_dict_robot[drug].discard(new_cl[0][2])
                return new_cl[0][2]
        else:
            logger.info("canister not found for drug {} and robot {}".format(drug, robot))
            return None

    def get_quantity_sorted_drug_list(self,drug_quantity_dict, drug_list, robot_drugs_):
        """

        @param drug_quantity_dict:
        @param drug_list:
        @return:
        """
        robot_drugs = deepcopy(list(robot_drugs_.keys()))
        non_robot_drugs = list()
        drug_quant_dict = dict()
        for drug in drug_list:
            if drug not in robot_drugs:
                non_robot_drugs.append(non_robot_drugs)
                continue
            drug_quant_dict[drug] = drug_quantity_dict[drug]

        sorted_drug_quant_dict = {k: v for k, v in sorted(drug_quant_dict.items(), key=lambda item: item[1], reverse=True)}
        sorted_drugs = list(sorted_drug_quant_dict.keys())
        sorted_drugs.extend(list(non_robot_drugs))

        return sorted_drugs

    def recommend_canisters_to_transfer_v3(self):

        try:
            '''
            Below class function divides packs among robots in the system.
            While dividing packs to robot, we try to make sure that there are near to 0 common packs among robots.
            We create tree which holds nodes where there are common packs.
            '''
            self.recommend_pack_distribution_in_robots_v3()
            print("step 1")
            print('Robot pack distributed')

            '''
            Below function will call class "RecommendCanisterDistributionInQuadrants" and "Recommend Drops"
            For each robot we will run first -- > RecommendCanisterDistributionInQuadrants
                which will give us 4 clusters for drugs that are going to be placed in 4 quadrant
                This will create 24 combinations of cluster and quadrant on which we will run RecommendDrops.
                 By this we will get combination in which the drop time is fastest
            '''
            logger.info("Quadrant Distribution started")
            self.robot_quadrant_drug_distribution_dict, pack_slot_drop_info_dict,robot_drug_canister_info_dict,pack_slot_drug_config_id_dict,pack_slot_drug_quad_id_dict = self.canister_recommendation_for_quadrants_v3()
            self.robotwise_drug_canister_info_dict = deepcopy(robot_drug_canister_info_dict)
            # Function added to get quad and robot of each canister separately.
            logger.info("Quadrant Distribution Ends")
            self.get_quadrant_wise_canister_data()
            self.robot_quadrant_canister_info_dict = {}
            self.robot_quadrant_free_location_info_dict = {}
            self.robot_quadrant_drug_canister_info_dict = {}
            canister_needed_in_quadrants = {}

            for robot, quadrant_drug in self.robot_quadrant_drug_distribution_dict.items():
                self.robot_quadrant_canister_info_dict[robot] = {}
                self.robot_quadrant_drug_canister_info_dict[robot] = {}
                for quadrant, drug in quadrant_drug.items():
                    if quadrant not in self.robot_quadrant_canister_info_dict[robot].keys():
                        self.robot_quadrant_canister_info_dict[robot][quadrant] = []
                    if quadrant not in self.robot_quadrant_drug_canister_info_dict[robot].keys():
                        self.robot_quadrant_drug_canister_info_dict[robot][quadrant] = {}

                    # if self.drug_quantity_dict:
                    #     sorted_drug_list = self.get_quantity_sorted_drug_list(self.drug_quantity_dict, drug['drugs'],
                    #                                                           self.robotwise_drug_canister_info_dict[robot])
                    #     if len(sorted_drug_list) > settings.QUAD_CANISTER_CAPACITY:
                    #         sorted_drug_list = sorted_drug_list[0:settings.QUAD_CANISTER_CAPACITY]
                    # else:
                    sorted_drug_list = drug['drugs']

                    for each_drug in sorted_drug_list:
                        if each_drug in self.robotwise_drug_canister_info_dict[robot]:
                            if self.robotwise_drug_canister_info_dict[robot][each_drug] > 0:
                                if self.robot_quad_drug_canister_dict[robot][quadrant][each_drug] is not None:
                                    canister = self.robot_quad_drug_canister_dict[robot][quadrant][each_drug]
                                else:
                                    canister = self.get_suitable_canister(each_drug,  robot)
                                # canister = robotwise_drug_canister_info_dict[robot][each_drug].pop()
                                if canister:
                                    canister_needed_in_quadrants[canister] = quadrant
                                    self.robot_quadrant_drug_canister_info_dict[robot][quadrant][each_drug] = canister
                                    self.robot_quadrant_canister_info_dict[robot][quadrant].append(canister)

            print("Dicts for canister transfer created")
            """
            Canister Transfer data according to its source and destination location
            """
            self.canister_transfer_info_dict, self.extended_canister_transfer_info_dict = self.fill_canister_transfer_dictV3(
                robot_quadrant_canister_info_dict=deepcopy(self.robot_quadrant_canister_info_dict),
                robot_free_location_info_dict=deepcopy(self.robot_free_location_info_dict),
                canister_location_info_dict=deepcopy(self.canister_location_info_dict))

            print("step 5")

            """
            Analysis data: pack as a key, [drug_id, canister_id, robot_id] as value
            """
            self.pack_drug_canister_robot_dict = self.fill_pack_drug_canister_robot_dictV3(df=deepcopy(self.df),
                                                                                         pack_slot_drop_info_dict=deepcopy(
                                                                                             pack_slot_drop_info_dict),
                                                                                         robot_quadrant_drug_distribution_dict=deepcopy(
                                                                                             self.robot_quadrant_drug_distribution_dict),
                                                                                         robot_quadrant_canister_info_dict=deepcopy(
                                                                                             self.robot_quadrant_canister_info_dict),
                                                                                         robot_drug_canister_info_dict=deepcopy(
                                                                                             robot_drug_canister_info_dict),
                                                                                         robot_half_pill_drug_pack_dict=deepcopy(
                                                                                             self.robot_half_pill_drug_pack_dict),
                                                                                           pack_drug_slot_number_slot_id_dict = deepcopy(
                                                                                               self.pack_drug_slot_number_slot_id_dict),
                                                                                           pack_slot_drug_quad_id_dict = deepcopy(pack_slot_drug_quad_id_dict),
                                                                                           pack_slot_drug_config_id_dict = deepcopy(pack_slot_drug_config_id_dict),
                                                                                           pack_drug_half_pill_slots_dict = self.pack_drug_half_pill_slots_dict)
            print("step 6")
            """
            Save appropriate data in a dictionary
            """
            # logger.info('robot_quadrant_canister_info_dict: {}'.format(self.robot_quadrant_canister_info_dict))
            # logger.info('robot_quadrant_drug_canister_info_dict: {}'.format(self.robot_quadrant_drug_canister_info_dict))
            # logger.info('robot_quadrant_drug_distribution_dict: {}'.format(self.robot_quadrant_drug_distribution_dict))
            # logger.info('pack_robot_drug_info_dict: {}'.format(self.pack_drug_canister_robot_dict))
            # append_dictionary_to_json_file(self.robot_cluster_dict, "robot_cluster_info_dict",
            #                                save_json=self.save_json, json_name=self.json_name)
            # append_dictionary_to_json_file(self.robot_cluster_canister_dict, "robot_cluster_canister_info_dict",
            #                                save_json=self.save_json, json_name=self.json_name)
            #
            # append_dictionary_to_json_file(self.canister_transfer_info_dict, "canister_transfer_info_dict",
            #                                save_json=self.save_json, json_name=self.json_name)
            # append_dictionary_to_json_file(str(self.pack_drug_canister_robot_dict), "pack_robot_drug_info_dict",
            #                                save_json=self.save_json, json_name=self.json_name)
            """
            To check the correctness of algorithm
            """
            if self.assert_output:
                """
                Asserting end output for remove suggestion. We will assert following points.
                1) For every canister in canister transfer_info_dict source_robot and dest_robot are relevant.
                2) Same check for extended canister transfer_info_dict.
                3) Check total number of packs in data_frame and pack_robot_drug_info_dict are same.
                4) 
                """
                self.check_assertion(deepcopy(self.robot_cluster_dict), deepcopy(self.robot_cluster_canister_dict), deepcopy(self.robot_canister_info_dict),
                                deepcopy(self.canister_transfer_info_dict), deepcopy(self.extended_canister_transfer_info_dict), deepcopy(self.pack_drug_canister_robot_dict))

            if self.robot_free_location_info_dict is not None:
                return self.extended_canister_transfer_info_dict, self.pack_drug_canister_robot_dict

            return self.canister_transfer_info_dict, self.pack_drug_canister_robot_dict

        except Exception as e:
            logger.info("Error in recommend_canisters_to_transfer_v3 {}".format(e))
            raise


    def get_pack_fill_analysis(self,response):

        try:
            input_data = response
            configuration_details = {1:{(1,1),(2,2),(3,3),(4,4)},2:{(1,2),(4,3)},3:{(1,4),(2,3)},4:{(2,1),(3,4)},5:{(4,1),(3,2)},6:{(1,3)},7:{(2,4)},8:{(3,1)},9:{(4,2)}}
            self.conf_to_id_dict = {}

            for con_id,details in configuration_details.items():
                for conf in details:
                    self.conf_to_id_dict[conf] = con_id

            arr = np.zeros([4, 7])
            pack_slot_drug = response['pack_slot_drug_dict']
            self.quadrant_drugs = response['quadrant_drugs']

            # pack_slot_id = [[22, 23, 24, 25, 26, 27, 28], [15, 16, 17, 18, 19, 20, 21],
            #                 [8, 9, 10, 11, 12, 13, 14], [1, 2, 3, 4, 5, 6, 7]]
            # pack_slot_id = [[25, 26, 27, 28, 29, 30, 31, 32], [17, 18, 19, 20, 21, 22, 23, 24],
            #                 [9, 10, 11, 12, 13, 14, 15, 16], [1, 2, 3, 4, 5, 6, 7, 8]]

            # TODO : pack_slot_id can get from database
            pack_slot_id = get_configuration_for_recommendation(pack_slot_id=True)
            # column = PackGrid.select(fn.MAX(PackGrid.slot_column)).scalar()
            # row = PackGrid.select(fn.MAX(PackGrid.slot_row)).scalar()
            # pack_slot_id = []
            # for i in range(column, 0, -1):
            #     x = [m for m in range((row * i) - (row - 1), (row * i) + 1)]
            #     pack_slot_id.append(x)

            self.pack_slot_id_mat = np.array(pack_slot_id)
            self.pack_slot_id_mat = np.transpose(self.pack_slot_id_mat)
            id_slot = {}
            column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
            # for i in range(7):
            for i in range(row):
                for j in range(column):
                    id_slot[(i, j)] = self.pack_slot_id_mat[i][j]
            # neighbour_dct,neighbour_tuple,neighbour_tuple_in = get_neighbour_slots(arr,id_slot)

            drug_set_qua_dict = dict()
            quad_wise_drug = defaultdict(set)
            total_combinations = list()
            for quad, drug_set in input_data['quadrant_drugs'].items():
                for comb in drug_set['combinations']:
                    # comb = set(comb)
                    comb.sort()
                    total_combinations.append(set(comb))
                    quad_wise_drug[quad].update(comb)
                    drug_set_qua_dict[tuple(comb)] = quad

            drug_qua_dict = dict()
            for quad, drugs in quad_wise_drug.items():
                for drug in drugs:
                    drug_qua_dict[drug] = quad

            # self.valid_slot_quadrant = {1:{2,3},2:{2,3},3:{2,3},4:{2,3},5:{2,3},6:{2,3},7:{3},8:{1,2,3,4},9:{1,2,3,4},10:{1,2,3,4},11:{1,2,3,4},12:{1,2,3,4},13:{1,2,3,4},14:{3,4},15:{1,2,3,4},16:{1,2,3,4},17:{1,2,3,4},18:{1,2,3,4},19:{1,2,3,4},20:{1,2,3,4},21:{3,4},22:{1,4},23:{1,4},24:{1,4},25:{1,4},26:{1,4},27:{1,4},28:{4}}
            # self.valid_slot_quadrant = {1:{2},2:{2,3},3:{2,3},4:{2,3},5:{2,3},6:{2,3},7:{2,3},8:{3},9:{1,2},10:{1,2,3,4},11:{1,2,3,4},12:{1,2,3,4},13:{1,2,3,4},14:{1,2,3,4},15:{1,2,3,4},16:{3,4},17:{1,2},18:{1,2,3,4},19:{1,2,3,4},20:{1,2,3,4},21:{1,2,3,4},22:{1,2,3,4},23:{1,2,3,4},24:{3,4},25:{1},26:{1,4},27:{1,4},28:{1,4},29:{1,4},30:{1,4},31:{1,4},32:{4}}

            # TODO: self.valid_slot_quadrant can get from database
            self.valid_slot_quadrant = get_configuration_for_recommendation(valid_slot_quadrant=True)
            # self.valid_slot_quadrant = {}
            # query = EdgeSlotMapping.select().dicts()
            # for data in query:
            #     for slot in data["slots"]:
            #         self.valid_slot_quadrant[slot] = data["quadrant"]
            # max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).sclar()
            # for slot in range(1,max_slot+1):
            #     if slot not in self.valid_slot_quadrant:
            #         self.valid_slot_quadrant[slot] = {1,2,3,4}

            total_qua = [1, 2, 3, 4]
            pack_wise_time = {}
            patterns = [(1, 2, 3, 4), (1, 2), (3, 4), (1, 4), (2, 3), (1, 3), (2, 4), (1,), (2,), (3,), (4,)]
            total_time = 0
            self.pack_slot_drop_info_dict = {}
            column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
            for pack, slot_drugs in pack_slot_drug.items():
                self.drop_slots_dict = {}
                self.slot_drop_id_dict = {}
                self.final_drops = []
                self.pack_slot_drop_info_dict[pack] = {}
                self.total_slots = list(slot_drugs.keys())

                # self.pack_mat = np.empty((7, 4), dtype=object)
                self.pack_mat = np.empty((row, column), dtype=object)
                for slot, drugs in slot_drugs.items():
                    try:
                        present_quad = set()
                        '''
                        Function To get slot to quadrant mapping
                        '''
                        quadrant,slot_quadrant = self.get_slot_to_quad_mapping(slot,drugs)
                        self.pack_mat[self.pack_slot_id_mat == slot] = quadrant
                    except Exception as e:
                        print(e)
                    # '''
                    # Temporarily Commented
                    # '''
                    # cnt = 1
                    # if drugs not in total_combinations:
                    #     for drug in drugs:
                    #         present_quad.add(drug_qua_dict[drug])
                    #     mat[self.pack_slot_id_mat == slot] = tuple(present_quad)
                    # else:
                    #     for i in total_qua:
                    #         drugs = list(drugs)
                    #         drugs.sort()
                    #         drugs = tuple(drugs)
                    #         present_quad.add(drug_set_qua_dict[drugs])
                    #     mat[self.pack_slot_id_mat == slot] = tuple(present_quad)
                    # cnt += 1

                '''
                static testing
                '''
                if settings.STATIC_V3:
                    self.pack_mat = [['q1','q1','q4','q1','q1','q2','q4'],['q4','q2','q1','q4','q2','q1','q3'],['q1','q2','q2','q3','q1','q4','q3'],['q2','q3','q2','q3','q2','q3','q3']]
                    self.pack_mat = [[1, 1, 4, 4, 1, 2, 4], [4, 2, 1, 3, 2, 1, 3],
                                [1, 2, 2, 3, 1, 4, 3], [2, 3, 2, 3, 2, 3, 3]]
                    self.pack_mat = [[{1},{(2,3)},{1},{4},{2},{4},{3}],[{(1,2)},{(2,3,4)},{(1,3)},{2},{(1,4)},{3},{1}],[{1},{(2,4)},{3},{4},{(2,3,4)},{(1,2,3,4)},{2}],[{(2,4)},{(2,3)},{2},{2},{2},{3},{1}]]
                    self.pack_mat = np.array(self.pack_mat)
                    self.pack_mat = np.transpose(self.pack_mat)
                    # self.total_slots = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
                    # self.total_slots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                    #                     23, 24, 25,26, 27, 28, 29, 30, 31, 32]

                    # TODO : self.total_slots can get from databse
                    self.total_slots = get_configuration_for_recommendation(total_slots=True)
                    # max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).sclar()
                    # self.total_slots = [i for i in range(1,max_slot+1)]

                self.pack_mat_final,self.selected_slot_quadrant = self.get_slot_wise_selected_quadrants()
                slot_gruop_defined,slot_group_address,address_to_slots,self.reserved_slots = self.find_possible_patterns_for_indepandent_quadrants(patterns)
                self.final_slot_group_independent_quad_slots = self.get_drop_data_for_independent_quad_slots(slot_gruop_defined,slot_group_address,address_to_slots)
                self.final_slot_group_multiple_quad_slots = self.get_drop_data_for_multiple_quad_slots()
                self.edge_slots = self.get_edge_slot_drops()
                self.drop_slots_dict,self.slot_drop_id_dict,self.drops = self.get_final_drop_details()
                self.slot_conf_id_dict = self.get_configuration_id_for_edge_slots()
                for slot in self.total_slots:
                    self.pack_slot_drop_info_dict[pack][slot] = {'drop_number':self.slot_drop_id_dict[slot],'configuration_id':self.slot_conf_id_dict[slot],"quadrant":self.selected_slot_quadrant[slot]}

                pack_wise_time[pack] = {'drops': self.drops, 'time_in_sec.': len(self.drops) * 10}
                total_time += pack_wise_time[pack]['time_in_sec.']
            return pack_wise_time,total_time,self.pack_slot_drop_info_dict
        except Exception as e:
            print(e)

    def get_drop_data_for_independent_quad_slots(self,slot_gruop_defined,slot_group_address,address_to_slots):
        """
        This function will give us drop slot groups for independent quad slots.
        :param slot_gruop_defined:
        :param slot_group_address:
        :param address_to_slots:
        :param reserved_slots:
        :return:
        """
        try:
            final_slot_group = []
            final_slot_group.extend(slot_gruop_defined[(1, 2, 3, 4)])
            del slot_group_address[(1, 2, 3, 4)]

            """
            This wil help in generating groups
            """
            for pattern in slot_group_address.keys():
                pattern_set = set(pattern)
                """
                Initialise quadrant array
                """
                quadrant_array = set([1, 2, 3, 4])

                pattern_slot_groups = deepcopy(slot_group_address[pattern])

                # while len(slot_group_address[pattern]) > 0:
                for add in pattern_slot_groups:
                    addition = set()
                    set_to_remove = deepcopy(pattern_set)
                    group_set = set()
                    group_set.update(address_to_slots[add])

                    for pattern2 in slot_group_address.keys():
                        pattern2_slot_groups = deepcopy(slot_group_address[pattern2])
                        set_to_remove.update(addition)
                        remaining_pattern = quadrant_array - set_to_remove

                        if type(pattern2) == int:
                            pattern2_set = set()
                            pattern2_set.add(pattern2)
                            pattern2_array = pattern2_set
                        else:
                            pattern2_array = set(pattern2)

                        """
                        Skip if not slot group available for given pattern
                        """
                        if len(pattern2_slot_groups) == 0:
                            continue
                        """
                        Pattern2 should be subset of remaining quadrants
                        """
                        if not pattern2_array.issubset(remaining_pattern):
                            continue
                        min_distance = 1000
                        min_distance_slot = None
                        for slot_address in pattern2_slot_groups:
                            distance = self.find_distance_between_two_slot_group(add, slot_address)
                            if distance < min_distance:
                                min_distance = distance
                                min_distance_slot = slot_address
                        slot_group_address[pattern2].remove(min_distance_slot)
                        if add in slot_group_address[pattern]:
                            slot_group_address[pattern].remove(add)
                        group_set.update(set(address_to_slots[min_distance_slot]))
                        group_set.update(set(address_to_slots[add]))
                        addition.update(set(pattern2))
                    final_slot_group.append(group_set)
            return final_slot_group
        except Exception as e:
            print("Error in get_drop_data_for_independent_quad_slots" + e)

    def get_drop_data_for_multiple_quad_slots(self):
        """
        This function find pairs of slots for which drugs are to be dropped from multiple quadrant
        Here We are skipping edge slots for which quad are not lying in specific quads
        :return:
        """

        total_quadrants = {1,2,3,4}
        self.quad_slots = defaultdict(set)
        self.slot_quads = {}
        group_set = set()
        all_slot_quadrants = []
        not_consider_in_drop = []
        final_slot_group_multiple_quad_slots = []
        column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
        try:
            for i in range(row):
                for j in range(column):
                    self.slot_quads[self.pack_slot_id_mat[i][j]] = self.pack_mat_final[i][j]
                    if type(self.pack_mat_final[i][j]) == set:
                        self.quad_slots[tuple(self.pack_mat_final[i][j])].add(self.pack_slot_id_mat[i][j])
                    else:
                        self.quad_slots[self.pack_mat_final[i][j]].add(self.pack_slot_id_mat[i][j])
                    if self.pack_mat_final[i][j] is not None and type(self.pack_mat_final[i][j]) == set:
                        all_slot_quadrants.append(tuple(self.pack_mat_final[i][j]))

            for slot,quads in self.slot_quads.items():
                group_set = set()
                if type(quads) == int or quads is None:
                    continue
                edge_slot = get_configuration_for_recommendation(edge_slot=True)
                if slot in edge_slot:
                    if quads != self.valid_slot_quadrant[slot]:
                        not_consider_in_drop.append(slot)
                        continue
                rem_quad = tuple(total_quadrants - set(quads))
                if slot in self.reserved_slots:
                    continue
                group_set.add(slot)
                self.reserved_slots.add(slot)
                if rem_quad in all_slot_quadrants:
                    for slt in self.quad_slots[rem_quad]:
                        if slt in not_consider_in_drop and slt in self.reserved_slots:
                            continue
                        group_set.add(slt)
                        self.reserved_slots.add(slt)
                        break
                final_slot_group_multiple_quad_slots.append(group_set)
            return final_slot_group_multiple_quad_slots
        except Exception as e:
            print("Error in get_drop_data_for_multiple_quad_slots" + e)

    def get_final_drop_details(self):
        final_drops = []
        drop_slots_dict= {}
        slot_drop_id_dict = {}

        final_drops.extend(self.final_slot_group_independent_quad_slots)
        final_drops.extend(self.final_slot_group_multiple_quad_slots)
        final_drops.extend(self.edge_slots)

        try:
            for id, drops in enumerate(final_drops):
                drop_slots_dict[id + 1] = drops

            for id, drop_slots in drop_slots_dict.items():
                for slot in drop_slots:
                    slot_drop_id_dict[slot] = id

            return drop_slots_dict,slot_drop_id_dict,final_drops
        except Exception as e:
            print("Error in get_final_drop_details")
            print(e)


    def get_edge_slot_drops(self):
        """
        This function returns slot group for edge slots.
        :return:
        """
        edge_slot_drops_temp = set(self.total_slots) - self.reserved_slots
        edge_slot_drops_updated = list()
        drop_set = set()
        for slot in edge_slot_drops_temp:
            drop_set = set()
            drop_set.add(slot)
            edge_slot_drops_updated.append(drop_set)
        return edge_slot_drops_updated

    def get_configuration_id_for_edge_slots(self):
        """
        This function provide us configuration id based on quadrants
        :return:
        """
        # group_slot_dict = {1:{1,2,3,4,5,6},2:{7},3:{14,21},4:{22,23,24,25,26,27},5:{28}}
        # group_slot_dict = {1: {1}, 2: {2, 3, 4, 5, 6, 7}, 3: {8}, 4: {9, 17}, 5: {16, 24}, 6: {25},
        #                    7: {26, 27, 28, 29, 30, 31}, 8: {32}}

        # TODO : group_slot_dict can get from database
        group_slot_dict = get_configuration_for_recommendation(group_slot_dict=True)
        # group_slot_dict = {}
        # query  = EdgeSlotMapping.select().dicts()
        # for data in query:
        #     group_slot_dict[data["group_no"]] = eval(data["slots"])

        slot_group_map = {}

        try:
            for group_id,slots in group_slot_dict.items():
                for slot in slots:
                    slot_group_map[slot] = group_id

            # slot_quads = {}
            # quad_slots = {}
            config_id = []
            slot_conf_details_dict = {}
            slot_conf_id_dict = {}

            # edge_slot_group_wise_conf_mapping = {1:{1:2,4:3},2:{1:3,2:3,4:3},3:{1:3,2:4},4:{2:1,3:4},5:{1:4,2:4,3:4}}
            # edge_slot_group_wise_conf_mapping = {1: {1: 2, 3: 2, 4: 2}, 2: {1: 2, 4: 3}, 3: {1: 3, 2: 3, 4: 3},
            #                                      4: {4: 1, 3: 2}, 5: {1: 4, 2: 3}, 6: {2: 1, 3: 1, 4: 1},
            #                                      7: {2: 1, 3: 4}, 8: {1: 4, 2: 4, 3: 4}}

            # TODO : edge_slot_group_wise_conf_mapping can get from database
            edge_slot_group_wise_conf_mapping = get_configuration_for_recommendation(
                edge_slot_group_wise_conf_mapping=True)
            # edge_slot_group_wise_conf_mapping = {}
            # query = EDGE_SLOT_MAPPING.select().dicts()
            # for data in query:
            #     edge_slot_group_wise_conf_mapping[data["group_no"]] = eval(data["edge_slot_group_wise_conf_mapping"])

            # for i in range(7):
            #     for j in range(4):
            #         slot_quads[self.pack_slot_id_mat[i][j]] = self.pack_mat_final[i][j]
            #         quad_slots[self.pack_mat_final[i][j]] = self.pack_slot_id_mat[i][j]

            for slot in self.edge_slots:
                slot = next(iter(slot))
                quads = self.slot_quads[slot]
                slot_conf_details_dict[slot] = list()
                if type(quads) != int:
                    for quad in quads:
                        if quad not in edge_slot_group_wise_conf_mapping[slot_group_map[slot]]:
                            slot_conf_details_dict[slot].append((quad,quad))
                            # config_id.append(1)
                            continue
                        # slot_conf_details_dict[slot][quad] = 0
                        # slot_conf_details_dict[slot].update({quad:edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quad]})
                        slot_conf_details_dict[slot].append((quad, edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quad]))
                else:
                    # slot_conf_details_dict[slot][quads] = 0
                    # slot_conf_details_dict[slot].update(
                    #     {quads: edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quads]})
                    slot_conf_details_dict[slot].append((quads, edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quads]))

            for slot in self.slot_quads:
                slot_conf_id_dict[slot] = set()
                if {slot} not in self.edge_slots:
                    slot_conf_id_dict[slot].add(1)
                    continue
                for conf in slot_conf_details_dict[slot]:
                    slot_conf_id_dict[slot].add(self.conf_to_id_dict[conf])

            return slot_conf_id_dict
        except Exception as e:
            print("Error in get_configuration_id_for_edge_slots")
            print(e)

    def get_slot_wise_selected_quadrants(self):
        """
        We are selecting particular quadrant for particular slot.
        Whole quadrant selection logic is inside this function.
        :return:
        """
        try:
            selected_slot_quadrant = {}
            pack_mat_final = self.pack_mat.copy()

            for i in range(len(self.pack_mat)):
                for j in range(len(self.pack_mat[i])):
                    selected_quadrant = self.pop_quadrant_for_slot(i,j)
                    if selected_quadrant == 0:
                        continue
                    selected_slot_quadrant[self.pack_slot_id_mat[i][j]] = selected_quadrant
                    if type(selected_quadrant) == int:
                        pack_mat_final[self.pack_slot_id_mat == self.pack_slot_id_mat[i][j]] = selected_quadrant
                    else:
                        pack_mat_final[self.pack_slot_id_mat == self.pack_slot_id_mat[i][j]] = set(selected_quadrant)
            return pack_mat_final,selected_slot_quadrant
        except Exception as e:
            print("Error in get_slot_wise_selected_quadrants" + e)

    def pop_quadrant_for_slot(self,row,column):
        """
        Particular quadrant selection logic will be inside this function
        :param row:
        :param column:
        :return:
        """
        if self.pack_mat[row][column] is not None:
            return self.pack_mat[row][column].pop()
        else:
            return 0

    def find_possible_patterns_for_indepandent_quadrants(self,patterns):
        """
        Here We are finding possible patterns for independent quad slots and we are skipping Edge slots if their quad are not lying in particular quad set.

        :param patterns: possible defined patterns
        :return: pattern details
        """

        reserved_slots = set()
        slots_group = []
        quad_slots = {}
        column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
        for i in range(row):
            for j in range(column):
                quad_slots[self.pack_slot_id_mat[i][j]] = self.pack_mat_final[i][j]

        slot_gruop_defined = OrderedDict()
        slot_group_address = OrderedDict()
        single_slot_gruop_defined = OrderedDict()
        single_slot_group_address = OrderedDict()
        address_to_slots = dict()
        for pt in patterns:
            slot_gruop_defined[pt] = []
            slot_group_address[pt] = []
            single_slot_gruop_defined[pt] = []
            single_slot_group_address[pt] = []
        pattern_cnt = 0
        for pattern in patterns:
            try:
                for i in range(row):
                    for j in range(column):
                        slots = set()
                        if self.pack_slot_id_mat[i][j] in reserved_slots:
                            continue
                        if pattern_cnt == 0:
                            if self.pack_slot_id_mat[i][j] - 7 <= 0 or self.pack_slot_id_mat[i][j] - 6 <= 0 or \
                                    self.pack_slot_id_mat[i][j] + 1 > 28:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] - 7] == 2 and 2 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] - 7]:  # 'q2':
                                    if quad_slots[self.pack_slot_id_mat[i][j] - 6] == 3 and 3 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] - 6]:  # 'q3':
                                        if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 4 and 4 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 1]:  # 'q4':
                                            if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                                j] - 7 in reserved_slots or self.pack_slot_id_mat[i][
                                                j] - 6 in reserved_slots or self.pack_slot_id_mat[i][
                                                j] + 1 in reserved_slots:
                                                continue
                                            slots.add(self.pack_slot_id_mat[i][j])
                                            slots.add(self.pack_slot_id_mat[i][j] - 7)
                                            slots.add(self.pack_slot_id_mat[i][j] - 6)
                                            slots.add(self.pack_slot_id_mat[i][j] + 1)
                                            reserved_slots = reserved_slots | slots
                                            slots_group.append(slots)
                                            slot_gruop_defined[pattern].append(slots)
                        elif pattern_cnt == 1:
                            if self.pack_slot_id_mat[i][j] - 7 <= 0:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] - 7] == 2 and 2 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] - 7]:  # 'q2':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] - 7 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] - 7)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)

                        elif pattern_cnt == 2:
                            if self.pack_slot_id_mat[i][j] + 7 > 28:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 3 and 3 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q3':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 7] == 4 and 4 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 7]:  # 'q4':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] + 7 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] + 7)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)
                        elif pattern_cnt == 3:
                            if self.pack_slot_id_mat[i][j] + 1 > 28:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 4 and 4 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 1]:  # 'q4':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] + 1 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] + 1)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)
                        elif pattern_cnt == 4:
                            if self.pack_slot_id_mat[i][j] + 1 > 28:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 2 and 2 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q2':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 3 and 3 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 1]:  # 'q3':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] + 1 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] + 1)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)
                        elif pattern_cnt == 5:
                            if self.pack_slot_id_mat[i][j] - 6 <= 0:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] - 6] == 3 and 3 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] - 6]:  # 'q3':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] - 6 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] - 6)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)
                        elif pattern_cnt == 6:
                            if self.pack_slot_id_mat[i][j] + 8 > 28:
                                continue
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 2 and 2 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:  # 'q2':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 8] == 4 and 4 in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 8]:  # 'q4':
                                    if self.pack_slot_id_mat[i][j] in reserved_slots or self.pack_slot_id_mat[i][
                                        j] + 8 in reserved_slots:
                                        continue
                                    slots.add(self.pack_slot_id_mat[i][j])
                                    slots.add(self.pack_slot_id_mat[i][j] + 8)
                                    reserved_slots = reserved_slots | slots
                                    slots_group.append(slots)
                                    slot_gruop_defined[pattern].append(slots)
                                    address = (i, j)
                                    address_to_slots[address] = slots
                                    slot_group_address[pattern].append(address)
                        else:
                            if quad_slots[self.pack_slot_id_mat[i][j]] == pattern[0] and pattern[0] in self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:
                                if self.pack_slot_id_mat[i][j] in reserved_slots:
                                    continue
                                slots.add(self.pack_slot_id_mat[i][j])
                                reserved_slots = reserved_slots | slots
                                slot_gruop_defined[pattern].append(self.pack_slot_id_mat[i][j])
                                address = (i, j)
                                address_to_slots[address] = slots
                                slot_group_address[pattern].append(address)
            except Exception as e:
                print("Error in finding possible combinations" + e)

            pattern_cnt += 1

        return slot_gruop_defined,slot_group_address,address_to_slots,reserved_slots


    def get_slot_to_quad_mapping(self,slot,drugs):
        """
        We will find the slot can be filled from which quadrant
        :param slot_id: slot_id
        :param drugs: drug_set
        :return: quadrant,slot_quadrant_dict
        """
        slot_quadrant = dict()
        independent_quadrant = self.get_indepandent_quads(slot,drugs)
        if len(independent_quadrant) != 0:
            slot_quadrant[slot] = independent_quadrant
            return independent_quadrant,slot_quadrant
        else:
            self.get_quad_to_drugs_dict_for_slot(slot,drugs)
            possible_multi_quadrants = self.get_multiple_quads(slot,drugs)
            slot_quadrant[slot] = possible_multi_quadrants
            return possible_multi_quadrants,slot_quadrant

        pass

    def get_indepandent_quads(self,slot,drugs):
        qd_count = 1
        drug_count = 0
        independant_quadrant = set()
        current_quadrant = 0
        while qd_count != 5:
            for drug in drugs:
                if drug in self.quadrant_drugs[qd_count]['drugs']:
                    drug_count+=1
            if drug_count == len(drugs):
                if qd_count in self.valid_slot_quadrant[slot]:
                    independant_quadrant.add(qd_count)
                    # We are adding this condition for now on temp base
                    break
                else:
                    current_quadrant = qd_count
            qd_count+=1
        if len(independant_quadrant) == 0 and current_quadrant != 0:
            independant_quadrant.add(current_quadrant)
        return independant_quadrant

    def get_quad_to_drugs_dict_for_slot(self,slot,drugs):
        self.quad_to_drugs_dict = defaultdict(set)
        for quad in settings.TOTAL_QUADRANTS:
            self.quad_to_drugs_dict[quad] = set()
            for drug in drugs:
                if drug in self.quadrant_drugs[quad]['drugs']:
                    self.quad_to_drugs_dict[quad].add(drug)
        pass

    def get_multiple_quads(self,slot,drugs):

        quad_list = []
        possible_combinations = set()

        '''
        Check for only if Two quad required
        '''
        for qd in settings.TOTAL_QUADRANTS:
            for qd1 in settings.TOTAL_QUADRANTS:
                if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1]) == len(drugs):
                    quad_list = (qd,qd1)
                    possible_combinations.add(quad_list)
                    '''
                    For now we are putting this for now
                    '''
                    return possible_combinations
        #             break
        #
        #     else:
        #         continue
        #     break
        #
        # if len(possible_combinations) != 0:
        #     return possible_combinations
        '''
        Check for if Three quad required 
        '''
        for qd in settings.TOTAL_QUADRANTS:
            for qd1 in settings.TOTAL_QUADRANTS:
                for qd2 in settings.TOTAL_QUADRANTS:
                    if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1] | self.quad_to_drugs_dict[qd2]) == len(drugs):
                        quad_list = (qd, qd1, qd2)
                        possible_combinations.add(quad_list)
                        '''
                        For now we are putting this for now
                        '''
                        return possible_combinations
            #             break
            #     else:
            #         continue
            #     break
            # else:
            #     continue
            # break

        # if len(possible_combinations) != 0:
        #     return possible_combinations
        '''
        Check for all four quadrant required
        '''
        for qd in settings.TOTAL_QUADRANTS:
            for qd1 in settings.TOTAL_QUADRANTS:
                for qd2 in settings.TOTAL_QUADRANTS:
                    for qd3 in settings.TOTAL_QUADRANTS:
                        if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1] | self.quad_to_drugs_dict[qd2] | self.quad_to_drugs_dict[qd3]) == len(drugs):
                            quad_list = (qd, qd1, qd2,qd3)
                            possible_combinations.add(quad_list)
                            '''
                            For now we are putting this for now
                            '''
                            return possible_combinations
            #                 break
            #         else:
            #             continue
            #         break
            #     else:
            #         continue
            #     break
            # else:
            #     continue
            # break


    def find_distance_between_two_slot_group(self, address, slot_address):
        distance = abs(address[0]-slot_address[0]) + abs(address[1] - address[1])
        return distance


class RecommendCanisterDistributionInQuadrants:

    def __init__(self, pack_slot_drug_dict, drug_canister_info_dict,num_of_quadrants, fully_manual_drugs = list() ):
        """

        @param pack_slot_drug_dict: pack id as main key, slot number as sub key and drug list as value
        @param drug_canister_info_dict: drug id as key and list of canister id as value
        @param num_of_quadrants: int value of number of quadrants per robot as value
        """

        self.total_number_of_slots_test = []
        self.drug_canister_info_dict = drug_canister_info_dict
        self.cluster_config = {}
        self.pending_combinations_dict = {}
        self.pack_slot_drug_dict = pack_slot_drug_dict
        self.temp_pack_slot_drug_dict = {}
        self.explored_multi_canister_drugs = {}
        self.total_number_of_slots = 0
        self.num_of_canister_capacity = settings.QUAD_CANISTER_CAPACITY
        self.num_of_quadrants = num_of_quadrants
        self.create_needed_data_structures()
        self.fully_manual_drugs = fully_manual_drugs
        # TODO: Considered num of canister capacity dynamically. It will be quadrant wise.



    def run_algo(self, num_of_quadrants = None, cluster_drugs = None):
        """
        # TODO: All the methods lack proper commenting.
        # TODO: Doc string is not in pycharm format.

        Main function which is called recursively considering number of quadrants.
        @param num_of_quadrants: int value of number of quadrants
        @return: quadrant wise drugs distribution dict and pack slot drug dict robot wise
        """

        try:
            if num_of_quadrants == 1:
                self.save_cluster_data(cluster_drugs)

                # self.check_output()
                return


            num_of_quadrants = self.num_of_quadrants if num_of_quadrants is None else num_of_quadrants
            self.remaining_pack_slot = {}
            self.save_data_dict = {}
            self.unexplored_drugs_list  = []
            self.remove_multiple_canister_drugs()

            """
            dict to store the drug list, combination list, nodes and slot count of both the clusters
            """
            self.save_data_dict = {0: {"cluster_config": [], "cluster_sum": 0,
                                                    "cluster_combinations": [],
                                                    "cluster_drugs": []},
                                       1: {"cluster_config": [], "cluster_sum": 0,
                                                    "cluster_combinations": [],
                                                    "cluster_drugs": []}}


            """
            if drug set has single canister drugs than we will generate and trace tree to get two clusters
            """
            if len(self.drug_set)> 0:
                self.independent_cluster_tree, self.cluster_info_dict = self.generate_tree_for_combinations()
                self.save_data_dict = self.trace_tree(num_of_quadrants)

            cluster_0_drugs, cluster_1_drugs = self.add_multiple_canister_drugs(num_of_quadrants)
            self.drug_set = cluster_1_drugs
            """
            case when drug set includes all multiple canister drugs i.e canister > 1
            in that case we will not generate tree, and proceeed by adding canister drugs to cluster
            """
            print("length of cluster: {}".format(len(cluster_0_drugs)))
            print("length of cluster: {}".format(len(cluster_1_drugs)))
            num_of_quad = num_of_quadrants - 1

            self.run_algo(1, cluster_0_drugs)
            self.run_algo(num_of_quad, cluster_1_drugs)

            for pack, slots in self.pack_slot_drug_dict.items():
                self.temp_pack_slot_drug_dict[pack] = dict()
                for each_slot, drug_set in slots.items():
                    self.temp_pack_slot_drug_dict[pack][each_slot] = set()
                    for each_drug in drug_set:
                        if each_drug not in self.fully_manual_drugs:
                            self.temp_pack_slot_drug_dict[pack][each_slot].add(each_drug)
                    if len(self.temp_pack_slot_drug_dict[pack][each_slot]) == 0:
                        self.temp_pack_slot_drug_dict[pack].pop(each_slot)
                if len(self.temp_pack_slot_drug_dict[pack]) == 0:
                    self.temp_pack_slot_drug_dict.pop(pack)

            logger.info(self.temp_pack_slot_drug_dict)
            return self.cluster_config, self.temp_pack_slot_drug_dict

        except Exception as e:
            logger.info(e)


    def add_multiple_canister_drugs(self, num_of_quadrants):
        """
        drugs having canister > 1 were stored in drugs to remove list.
        drug_combinations_of_multiple_canister_drug_dict: having drugs of 'drugs to remove' as keys
                            and list of combination of corresponding drug as value.
        @return: two clusters of drugs after adding multiple canister drugs
        """
        try:
            cluster_0_drugs = set(self.save_data_dict[0]["cluster_drugs"])
            cluster_1_drugs = set(self.save_data_dict[1]["cluster_drugs"])
            '''
            Condition where there is only one distinct drug and other drugs have multiple canisters
            '''
            # if  len(self.unexplored_drugs_list) > 0:
            #     for i in self.unexplored_drugs_list:
            #         cluster_0_drugs.add(i)

            """
            When there are multiple canister drugs
            """
            cluster_0_max_len = settings.QUAD_CANISTER_CAPACITY
            cluster_1_max_len = abs((num_of_quadrants * settings.QUAD_CANISTER_CAPACITY) - cluster_0_max_len)

            drug_combinations_of_multiple_canister_drug_dict = {}
            for drug in self.drug_to_remove:
                if drug in self.manual_drugs:
                    continue
                drug_combinations_of_multiple_canister_drug_dict[drug] = self.drug_combinations_dict[drug]

            """
            This adds drug to the cluster which includes any of its combination and if not in any cluster than it adds
            that drug to both the cluster
            """
            for multiple_canister_drug, combinations in drug_combinations_of_multiple_canister_drug_dict.items():
                drug_added_0 = False
                drug_added_1 = False
                for each_combination in combinations:
                    if each_combination in self.save_data_dict[0]["cluster_combinations"]:
                        cluster_0_drugs.add(multiple_canister_drug)
                        if not drug_added_0:
                            self.add_count_to_explored_multi_canister_dict(multiple_canister_drug)
                            drug_added_0 = True
                    if each_combination in self.save_data_dict[1]["cluster_combinations"]:
                        cluster_1_drugs.add(multiple_canister_drug)
                        if num_of_quadrants == 2 and not drug_added_1:
                            self.add_count_to_explored_multi_canister_dict(multiple_canister_drug)
                            drug_added_1 = True
                    if each_combination not in self.save_data_dict[1]["cluster_combinations"] and each_combination not in \
                            self.save_data_dict[0]["cluster_combinations"]:
                        cluster_1_drugs.add(multiple_canister_drug)
                        cluster_0_drugs.add(multiple_canister_drug)
                        if num_of_quadrants == 2 and not drug_added_1:
                            self.add_count_to_explored_multi_canister_dict(multiple_canister_drug)
                            drug_added_1 = True
                        if not drug_added_0:
                            self.add_count_to_explored_multi_canister_dict(multiple_canister_drug)
                            drug_added_0 = True


            ''' Removing drugs that do not have combination in cluster 0 to balance '''
            if len(cluster_1_drugs) > cluster_1_max_len:
                common_drugs = cluster_1_drugs.intersection(cluster_0_drugs)
                for i in common_drugs:
                    combinations = drug_combinations_of_multiple_canister_drug_dict[i]
                    if not set(combinations).intersection(set(self.save_data_dict[1]["cluster_combinations"])):
                        cluster_1_drugs.remove(i)
                        print("Removed multiple drug canister from cluster 1")
                    if len(cluster_1_drugs) < cluster_1_max_len:
                        break
            ''' Removing drugs that do not have combination in cluster 1 to balance '''
            if len(cluster_0_drugs) > cluster_0_max_len:
                common_drugs = cluster_0_drugs.intersection(cluster_1_drugs)
                for i in common_drugs:
                    combinations = drug_combinations_of_multiple_canister_drug_dict[i]
                    if not set(combinations).intersection(set(self.save_data_dict[0]["cluster_combinations"])):
                        cluster_0_drugs.remove(i)
                        print("Removed multiple drug canister from cluster 0")
                    if len(cluster_0_drugs) < cluster_0_max_len:
                        break

            '''Removing drugs that have combinations in cluster 0 but already is in other cluster'''
            if num_of_quadrants < 4:
                if len(cluster_0_drugs) > cluster_0_max_len:
                    for drug in cluster_0_drugs.copy():
                        if drug in self.explored_multi_canister_drugs.keys():
                            if self.explored_multi_canister_drugs[drug] > settings.ALT_MAX_CANISTER_COUNT:
                                cluster_0_drugs.remove(drug)
                        if len(cluster_0_drugs) < cluster_0_max_len:
                            break

            '''Removing drugs that have combinations in cluster 1 but already is in other cluster'''
            if num_of_quadrants < 4:
                if len(cluster_1_drugs) > cluster_1_max_len:
                    for drug in cluster_1_drugs.copy():
                        if drug in self.explored_multi_canister_drugs.keys():
                            if self.explored_multi_canister_drugs[drug] > settings.ALT_MAX_CANISTER_COUNT:
                                cluster_1_drugs.remove(drug)
                        if len(cluster_1_drugs) < cluster_1_max_len:
                            break


            return cluster_0_drugs, cluster_1_drugs
        except Exception as e:
            print("In add_multicanister_durgs: {}".format(e))


    def add_count_to_explored_multi_canister_dict(self, multiple_canister_drug):
        if multiple_canister_drug not in self.explored_multi_canister_drugs.keys():
            self.explored_multi_canister_drugs[multiple_canister_drug] = 1
        else:
            self.explored_multi_canister_drugs[multiple_canister_drug] += 1


    def save_cluster_data(self, cluster_drugs):

        """
        Save drugs and combinations for each quadrant
        @param cluster_drugs: list of drugs for one quadrant
        quadrant : variable to maintain key for cluster config dict (assume it as a quadrant number)
        """
        # self.cluster_drugs = cluster_drugs
        try:
            self.cluster_drugs = set()
            # TODO : remove after testing
            for drug in cluster_drugs:
                if drug is None:
                    continue
                self.cluster_drugs.add(drug)

            if len(self.pending_combinations_dict) > 0:
                logger.info(self.pending_combinations_dict)

            quadrant = len(self.cluster_config)
            self.cluster_config[quadrant] = {"drugs": set(), "combinations": [], "slots": 0}

            """
            """
            cluster_combinations = set()
            for each_drug in set(cluster_drugs):
                if each_drug in self.drug_canister_info_dict:
                    if self.drug_canister_info_dict[each_drug] > 0:
                        self.drug_canister_info_dict[each_drug] -= 1
                    for each_combination in self.drug_combinations_dict[each_drug]:
                        cluster_combinations.add(tuple(self.combinations_dict[each_combination]))

            self.cluster_config[quadrant]["drugs"] = cluster_drugs
            self.cluster_config[quadrant]["combinations"] = list(map(list,list(cluster_combinations)))
        except Exception as e:
            logger.info("In save_cluster_data : e".format(e))


    def remove_multiple_canister_drugs(self):
        """
        Function creates list of drugs having canisters greater than 1 and 0 canister drugs.
        Updates drug set (which is passed to generate tree) by removing multiple and 0 canister drugs.
        @return:
        """

        self.drug_to_remove = []
        self.manual_drugs = set()
        self.multiple_canister_drug = set()
        drugs_to_remove = []
        manual_drugs = set()
        for drug, canister_count in self.drug_canister_info_dict.items():
            if canister_count > 1 or canister_count == 0:
                drugs_to_remove.append(drug)
            if canister_count == 0:
                manual_drugs.add(drug)

        for drug in drugs_to_remove:
            if drug in self.drug_set:
                self.drug_to_remove.append(drug)
                self.drug_set.remove(drug)

        for each_drug in manual_drugs:
            self.manual_drugs.add(each_drug)

        self.multiple_canister_drug = set(self.drug_to_remove).difference(self.manual_drugs)

        # debug string to check all the drugs that are removed and their canister qty : [(drug, self.drug_canister_info_dict[drug]) for drug in self.drug_to_remove]

        print("Multiple canister drugs count: {} . Drugs : {}".format(len(self.drug_to_remove), self.drug_to_remove))




    def check_output(self):
        """
        check the combinations and drugs of four quadrants with the drug_combination_dict to verify that all
        combinations and drugs are present in the quadrant division.
        @return:
        """
        drugs_list_of_all_quadrants = []
        combinations_of_all_quadrants = []
        for quadrant, data in self.cluster_config.items():
            drugs_list_of_all_quadrants.extend(self.cluster_config[quadrant]['drugs'])
            combinations_of_all_quadrants.extend(self.cluster_config[quadrant]['combinations'])

        drug_list_before_division_in_quadrants = []
        combination_list_before_division_in_quadrants = []
        for drug, combination in self.drug_combinations_dict.items():
            drug_list_before_division_in_quadrants.append(drug)
            combination_list_before_division_in_quadrants.extend(combination)

        self.drugs_diff = (list(set(drugs_list_of_all_quadrants) - set(drug_list_before_division_in_quadrants)))
        self.combinations_diff = len(combinations_of_all_quadrants) - len(combination_list_before_division_in_quadrants)


    def add_remaining_slots(self, save_data_list, num_of_quadrants):

        """
        Function to add remaining slots which were removed because of multiple canisters
        @param save_data_list: list containing quadrant wise drug distribution with slot count
        @param num_of_quadrants: int value of number of quadrants for capacity distribution
        @return: added remaining slots in save data list
        """

        updated_data_list=  []
        cluster_0 = save_data_list[0]
        cluster_1 = save_data_list[1]
        cluster_0_capacity = math.ceil(self.total_number_of_slots/num_of_quadrants)
        cluster_1_capacity = self.total_number_of_slots - cluster_0_capacity
        remaining_0_capacity = cluster_0_capacity - cluster_0[1]
        remaining_1_capacity = cluster_1_capacity - cluster_1[1]
        for pack, slots in self.remaining_pack_slot.items():
            for slot in slots:
                if remaining_0_capacity > remaining_1_capacity:
                    cluster_0[1] += 1
                    cluster_0[2].append("{}_{}".format(pack,slot))
                    remaining_0_capacity -= 1
                elif remaining_1_capacity > remaining_0_capacity:
                    cluster_1[1] += 1
                    cluster_1[2].append("{}_{}".format(pack, slot))
                    remaining_1_capacity -= 1
                elif remaining_0_capacity == remaining_1_capacity:
                    cluster_0[1] += 1
                    cluster_0[2].append("{}_{}".format(pack, slot))
                    remaining_0_capacity -= 1
        updated_data_list.append(cluster_0)
        updated_data_list.append(cluster_1)
        return updated_data_list

    # def add_remaining_combinations(self):
    #     sorted_cluster_config = self.cluster_config
    #     for combinations in self.pending_combinations:


    def add_remaining_combinations(self):
        """
        Function to add the pending combinations and balance the drug count for each quadrant
        @return:
        """
        cluster_config = self.cluster_config
        for each_pc, slots in self.pending_combinations_dict.items():
            cluster_config[0]['slots']



    def create_needed_data_structures(self):

        """
        To create dict:
        drugs_combination_list: contains unique drug combinations
        drug_combination_frequency_dict: each drug combination as key and count of slots that combination is used as value
        combination_slot_dict:  combination as key and slot_id(packid_slots) as value
        drug_combinations_dict: drug id as key and list of combinations in which that drug is used as values
        canister_drugs_in_packs: set of drugs having canisters greater than equal to 1
        drug_set: set of drugs that will be used to generate tree on every recursion
        """

        self.drugs_combination_list = []
        self.drug_combination_frequency_dict = {}
        self.combination_slot_dict = {}
        self.canister_drugs_in_packs = set()
        self.drug_combinations_dict = {}
        self.combinations_dict  ={}
        self.drug_set = set()


        number_of_slots = 0
        for pack, slot_drugs in self.pack_slot_drug_dict.items():
            for slots, drug in slot_drugs.items():

                drugs = list(drug)
                if len(drugs) == 0:    #i.e 0 canister drug
                    continue
                self.canister_drugs_in_packs.update(set(drugs))

                if drugs not in self.drugs_combination_list:
                    self.drugs_combination_list.append(drugs)
                    combination_index = self.drugs_combination_list.index(drugs)
                    self.combinations_dict[combination_index] = drugs
                    self.combination_slot_dict[combination_index] = []
                    self.drug_combination_frequency_dict[combination_index] = 0
                else:
                    combination_index = self.drugs_combination_list.index(drugs)

                self.drug_combination_frequency_dict[combination_index] += 1
                self.combination_slot_dict[combination_index].append(str(pack) + '_' + str(slots))
                self.drug_set.update(drugs)
                for each_drug in drug:
                    if each_drug not in self.drug_combinations_dict.keys():
                        self.drug_combinations_dict[each_drug] = []
                    if combination_index not in self.drug_combinations_dict[each_drug]:
                        self.drug_combinations_dict[each_drug].append(combination_index)
                number_of_slots += 1

        self.total_number_of_slots = number_of_slots if self.total_number_of_slots == 0 else self.total_number_of_slots

    def generate_tree_for_combinations(self):
        """
        Function is used to create tree at finite level
        @return: independent_cluster_tree: dict having parent node as key and child nodes as value

        cluster_info_dict: having node as main key and drugs and combinations as subkey and list of drugs of
        that node as value to key drugs and list of combinations as value to key combinations
        """
        try:
            self.cluster_level = 5
            independent_cluster_tree, cluster_info_dict = self.generate_clusters_for_tree(self.cluster_level)

            return independent_cluster_tree, cluster_info_dict

        except Exception as e:
            logger.info("In generate_tree_for_combinations. {}".format(e))

    def generate_clusters_for_tree(self, limit_tree_factor):
        """
        This method will generate tree by tracing on each parent node and generating possible child nodes.
        drugs_list: list of drugs which will be used to create independent clusters
        """
        try:
            independent_cluster_tree = {}
            cluster_info_dict = {}
            last_used_id = 0
            drugs_list = list(self.drug_set)
            self.qu = Queue()
            self.qu.push([drugs_list, -1, last_used_id])
            while not self.qu.isEmpty():
                parent = self.qu.pop()
                parent_drug_list = parent[0]
                parent_independence_degree = parent[1]
                parent_id = parent[2]

                independent_cluster_tree[parent_id, parent_independence_degree] = []
                if parent_independence_degree > limit_tree_factor or len(parent_drug_list) == 1:
                    self.unexplored_drugs_list.extend(parent_drug_list)
                    continue
                # TODO: Name should be proper, here drug_list is not only a list of drugs. It is much more than that.
                cluster_list = self.generate_independent_cluster(parent_drug_list, parent_independence_degree + 1)

                for cluster in cluster_list:
                    child_independence_degree = parent_independence_degree + 1
                    last_used_id += 1
                    child_id = last_used_id
                    child = [cluster["drugs"], child_independence_degree, child_id]

                    self.qu.push(child)
                    independent_cluster_tree[(parent_id, parent_independence_degree)].append(
                        (child_id, child_independence_degree))
                    cluster_info_dict[(child_id, child_independence_degree)] = cluster
            return independent_cluster_tree, cluster_info_dict
            pass
        except Exception as e:
            logger.info("In generate_tree_for_combinations. {}".format(e))

    def generate_independent_cluster(self, drugs_list, degree_of_independence=0):
        """
        Here everytime we will get a parent drug list which will be used to generate independent clusters considering
        common combinations and degree of independence
        :param drugs_list: list of drugs having canister = 1
        :param degree_of_independence: integer value of level of tree
        :return: independent_cluster_list: list of clusters where each element is a dict having drugs, combinations
                                            as key and set of drugs, list of combinations as value
        """
        try:
            independent_cluster_list = []
            for drug in drugs_list:

                cluster_found_flag = False
                # slots_of_given_drug_combination = self.combination_slot_dict[str(drug_combination)]
                found_cluster_list = []
                for num, cluster in enumerate(independent_cluster_list):

                    """
                    list to add combinations which are common between combinations of drug and cluster
                    """
                    common_combinations = list(set(self.drug_combinations_dict[drug]) & set(cluster['combinations']))

                    if len(common_combinations) > degree_of_independence:
                        found_cluster_list.append(num)
                        drug_set = set()
                        drug_set.add(drug)
                        cluster["drugs"].update(drug_set)
                        cluster["combinations"].update(self.drug_combinations_dict[drug])
                        cluster_found_flag = True
                if cluster_found_flag and len(found_cluster_list) > 0:
                    independent_cluster_list = self.merge_clusters(found_cluster_list, independent_cluster_list)
                if not cluster_found_flag:
                    drug_set  =set()
                    drug_set.add(drug)
                    cluster = {"drugs": drug_set ,
                               "combinations": set(self.drug_combinations_dict[drug])}
                    independent_cluster_list.append(cluster)
            for drug_pack_set in independent_cluster_list:
                for key, value in drug_pack_set.items():
                    # if key == "combinations":   # no need to sort combinations
                    #     set_list = set(tuple(row) for row in value)
                    #     value_list = list(map(list, list(set_list)))
                    # else:
                    value_list = list(value)
                    print(value_list)
                    if value_list == None:
                        print("P")
                    value_list.sort()
                    drug_pack_set[key] = value_list
            return independent_cluster_list
        except Exception as e:
            logger.info("In generate_tree_for_combinations. {}".format(e))

    def merge_clusters(self, found_cluster_list, independent_cluster_list):
        """
        Function is used to merge cluster
        :param found_cluster_list:
        :param independent_cluster_list:
        :return: merged independent_cluster_list
        """

        if len(found_cluster_list) == 1:
            return independent_cluster_list
        else:
            new_independent_cluster_dict = {}
            tempdruglist = []
            temppacklist = []
            tempcombinationset = set()
            tempslotcount = 0
            indexlist = []
            for num, value in enumerate(independent_cluster_list):
                if num not in found_cluster_list:
                    continue
                tempdruglist.append(independent_cluster_list[num]["drugs"])
                tempcombinationset.update(set(independent_cluster_list[num]["combinations"]))
                # for combination in independent_cluster_list[num]["combinations"]:
                #     if combination not in tempcombinationlist:
                #         tempcombinationlist.append(combination)
                #         tempslotcount += len(self.combination_slot_dict[combination])
                indexlist.append(num)
            new_independent_cluster_dict["drugs"] = tempdruglist

            new_independent_cluster_dict["combinations"] = tempcombinationset
            new_independent_cluster_dict["drugs"] = set(more_itertools.collapse(new_independent_cluster_dict["drugs"]))
            # new_independent_cluster_dict["combinations"] = new_independent_cluster_dict["combinations"]
            new_independent_cluster_dict = new_independent_cluster_dict
            independent_cluster_list.append(new_independent_cluster_dict)
            templist_indpendent_list = []
            for index in indexlist:
                templist_indpendent_list.append(independent_cluster_list[index])
            for element in templist_indpendent_list:
                independent_cluster_list.remove(element)

            return independent_cluster_list
        pass

    def trace_tree(self, num_of_quadrants):
        """
        Function to trace tree at different levels with all possible combinations
        @param num_of_quadrants:
        @return:
        """
        try:
            self.min_loss  = 10000000000
            trace_array = [(0, -1)]
            degree_of_independence = -1
            drug_combinations_of_multiple_canister_drug_dict = {}
            self.loss_split_dict = {}
            for drug in self.multiple_canister_drug:
                drug_combinations_of_multiple_canister_drug_dict[drug] = self.drug_combinations_dict[drug]

            while degree_of_independence < 5:
                configuration_list = []
                configuration_loss_result = []
                degree_of_independence += 1
                for node in trace_array:
                    if len(self.independent_cluster_tree[node]) == 0:
                        continue

                    temp_trace_array = deepcopy(trace_array)
                    temp_trace_array.remove(node)
                    while len(self.independent_cluster_tree[node]) == 1 and len(
                            self.independent_cluster_tree[self.independent_cluster_tree[node][0]]) != 0:
                        node = self.independent_cluster_tree[node][0]
                    temp_trace_array.extend(self.independent_cluster_tree[node])
                    configuration_list.append(temp_trace_array)
                logger.info("LEVEL: {} ".format(degree_of_independence))
                logger.info(" {} level: {}".format(degree_of_independence, len(configuration_list)))
                # print("Total configurations at this level: ",len(configuration_list))
                if len(configuration_list) == 0:
                    logger.debug("configuration list is empty!")
                    break
                for configuration in configuration_list:
                    configuration_loss_result.append(
                        self.multi_robot_balance_scale_algo(configuration, self.cluster_info_dict, num_of_quadrants, drug_combinations_of_multiple_canister_drug_dict))
                trace_array = configuration_list[np.argmin(configuration_loss_result)]
                # logger.info("configuration_loss_result {}".format(configuration_loss_result))
                # logger.info("save_data_list {}".format(self.save_data_list))
            # sorted_save_data_list = sorted(self.save_data_list, key=lambda x: (x[2]))

            '''
            In case we do not find any split, we will take cluster which had minimum loss from the dict created earlier.
            '''
            if not self.save_data_dict[0]['cluster_config'] and self.loss_split_dict.keys():
                x = min(self.loss_split_dict.keys())
                self.save_data_dict = self.loss_split_dict[x]
                print("Spliting failed. didn't got optimized result")
            return self.save_data_dict
        except Exception as e:
            logger.info("In trace_tree {}".format(e))

    def multi_robot_balance_scale_algo(self, configuration, cluster_info_dict, num_of_quadrants,
                                       drug_combinations_of_multiple_canister_drug_dict):
        """
        Function to add combinations equally maintaining the split in two clusters
        :param drug_combinations_of_multiple_canister_drug_dict: contains drugs combination of multiple canister drugs to measure approx size of cluster before adding it
        :param configuration: list of nodes which are going to be divided in two clusters
        :param cluster_info_dict: dict having nodes (that are in configuration) as main key, drugs and combinations as
                                    sub key, list of drugs and list of combinations as value of sub keys
        :param num_of_quadrants: used to decide the split of slot count and drug split for each cluster
        :return loss_counted: length of common combinations between two clusters
        """
        try:
            total_slots = set()
            total_slots_length = self.total_number_of_slots
            slots_count_cluster0 = math.ceil((1/num_of_quadrants)*total_slots_length)

            total_can_capacity = num_of_quadrants * self.num_of_canister_capacity
            drug_split_cluster0 = self.num_of_canister_capacity
            drug_split_cluster1 = total_can_capacity - drug_split_cluster0

            # required clusters pack counts
            req_min_slots_cluster_count = slots_count_cluster0
            req_max_slots_cluster_count = total_slots_length - slots_count_cluster0
            logger.debug("Required Pack-Distribution {} {}".format(req_min_slots_cluster_count, req_max_slots_cluster_count))

            configwise_slots_len_list = []
            for node in configuration:
                slots_to_fill_by_node = 0
                for combination in cluster_info_dict[node]['combinations']:
                    slots_to_fill_by_node += self.drug_combination_frequency_dict[combination]
                configwise_slots_len_list.append(slots_to_fill_by_node)

            sorted_slotlen_list = sorted(configwise_slots_len_list)[::-1]
            sorted_config_list = [x for _, x in sorted(zip(configwise_slots_len_list, configuration))[::-1]]

            sorted_config_slotlen_list = list(zip(sorted_config_list, sorted_slotlen_list))
            temp_sorted_config_slotlen_list = deepcopy(sorted_config_slotlen_list)

            cluster0_config = []
            cluster1_config = []
            cluster0_sum = 0
            cluster1_sum = 0
            self.cluster_0_drugs = []
            self.cluster_1_drugs = []
            self.cluster_0_combinations = []
            self.cluster_1_combinations = []

            while len(temp_sorted_config_slotlen_list) != 0:
                node_tuple = temp_sorted_config_slotlen_list.pop(0)
                temp_node = node_tuple[0]
                temp_slotlen = node_tuple[1]
                drugs_0 = set(self.cluster_info_dict[temp_node]['drugs']) - set(self.cluster_0_drugs)
                drugs_1 = set(self.cluster_info_dict[temp_node]['drugs']) - set(self.cluster_1_drugs)

                if (cluster0_sum + temp_slotlen <= req_min_slots_cluster_count) and len(set(self.cluster_0_drugs))+ len(drugs_0) <= drug_split_cluster0 :
                    cluster0_config.append(temp_node)
                    self.cluster_0_drugs.extend(drugs_0)
                    cluster0_sum = cluster0_sum + temp_slotlen
                elif (cluster1_sum + temp_slotlen <= req_max_slots_cluster_count) and len(set(self.cluster_1_drugs)) + len(drugs_1) <= drug_split_cluster1:
                    cluster1_config.append(temp_node)
                    self.cluster_1_drugs.extend(drugs_1)
                    cluster1_sum = cluster1_sum + temp_slotlen
                else:
                    if len(set(self.cluster_0_drugs))+ len(drugs_0) <= drug_split_cluster0 and (abs(req_min_slots_cluster_count - (cluster0_sum + temp_slotlen)) <= abs(req_max_slots_cluster_count - (cluster1_sum + temp_slotlen))):
                        cluster0_config.append(temp_node)
                        self.cluster_0_drugs.extend(drugs_0)
                        cluster0_sum = cluster0_sum + temp_slotlen
                    elif len(set(self.cluster_1_drugs)) + len(drugs_1) <= drug_split_cluster1:
                        cluster1_config.append(temp_node)
                        self.cluster_1_drugs.extend(drugs_1)
                        cluster1_sum = cluster1_sum + temp_slotlen
                    else:
                        cluster1_config.append(temp_node)
                        self.cluster_1_drugs.extend(drugs_1)
                        cluster1_sum = cluster1_sum + temp_slotlen

                        # Below line is commented as this is of no use.
                        # self.pending_combinations_dict[self.cluster_info_dict[temp_node]['combinations']] = len(self.cluster_info_dict[temp_node]['slots'])

            for c0_node in cluster0_config:
                # self.cluster_0_drugs.extend(self.cluster_info_dict[c0_node]['drugs'])
                self.cluster_0_combinations.extend(self.cluster_info_dict[c0_node]['combinations'])
            for c1_node in cluster1_config:
                # self.cluster_1_drugs.extend(self.cluster_info_dict[c1_node]['drugs'])
                self.cluster_1_combinations.extend(self.cluster_info_dict[c1_node]['combinations'])

            # loss functions evaluation temp code
            loss_counted = self.get_loss_count_for_cluster()

            '''
            Saving splits in case we do not get split with all the quadrant limitations.
            '''
            if len(self.cluster_0_drugs) < drug_split_cluster0 and len(self.cluster_1_drugs) < drug_split_cluster1:
                self.loss_split_dict[loss_counted] = {
                    0: {"cluster_config": cluster0_config, "cluster_sum": cluster0_sum,
                        "cluster_combinations": self.cluster_0_combinations,
                        "cluster_drugs": self.cluster_0_drugs},
                    1: {"cluster_config": cluster1_config, "cluster_sum": cluster1_sum,
                        "cluster_combinations": self.cluster_1_combinations,
                        "cluster_drugs": self.cluster_1_drugs}}

            # we can try that if there we move any drug which is going to be dropped in less packs to other quadrant from levels less than 1
            # and calculate the loss we are getting on it.
            cluster_0_multi_drug_count = set()
            cluster_1_multi_drug_count = set()
            '''
            Finding that number of multi canister drugs that are going to be added in respective clusters.
            '''
            for multi_can_drug, combinations in drug_combinations_of_multiple_canister_drug_dict.items():
                for each_combination in combinations:
                    if each_combination in self.cluster_0_combinations:
                        cluster_0_multi_drug_count.add(multi_can_drug)
                    if each_combination in self.cluster_1_combinations:
                        cluster_1_multi_drug_count.add(multi_can_drug)
                    if each_combination not in self.cluster_1_combinations and each_combination not in self.cluster_0_combinations:
                        cluster_0_multi_drug_count.add(multi_can_drug)
                        cluster_1_multi_drug_count.add(multi_can_drug)

            '''
            If the split exceeds the quadrant capacity limit, we will add loss so that that splt wont count.
            '''
            if len(set(self.cluster_1_drugs)) > (drug_split_cluster1- len(cluster_1_multi_drug_count) ) or len(set(self.cluster_0_drugs)) > (drug_split_cluster0 - len(cluster_0_multi_drug_count)):
                loss_counted += 10000000000

            if loss_counted < self.min_loss:
                self.save_data_dict = {0: {"cluster_config": cluster0_config, "cluster_sum": cluster0_sum,
                                           "cluster_combinations": self.cluster_0_combinations,
                                           "cluster_drugs": self.cluster_0_drugs},
                                       1: {"cluster_config": cluster1_config, "cluster_sum": cluster1_sum,
                                           "cluster_combinations": self.cluster_1_combinations,
                                           "cluster_drugs": self.cluster_1_drugs}}

                self.min_loss = loss_counted
            return loss_counted
        except Exception as e:
            logger.error("error in multi_robot_balance_scale_algo {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error : exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

    def get_loss_count_for_cluster(self):

        if settings.LOSS_FUNCTION == "common_combination":
            common_combinations = set(self.cluster_0_combinations) & set(self.cluster_1_combinations)
            loss_counted = len(common_combinations)

        elif settings.LOSS_FUNCTION == "slot_count":
            cluster_0_slots = 0
            cluster_1_slots = 0
            for each_comb in self.cluster_0_combinations:
                cluster_0_slots += len(self.combination_slot_dict[each_comb])
            for each_comb in self.cluster_1_combinations:
                cluster_1_slots += len(self.combination_slot_dict[each_comb])
            loss_counted = abs(cluster_0_slots - cluster_1_slots)

        return loss_counted


class RecommendPackDistributionAcrossSystems:

    def __init__(self, df=None, robot_capacity_info_dict=None, drug_canister_info_dict=None,
                 canister_location_info_dict=None, robot_free_location_info_dict=None, facility_pack_info_dict=None,
                 system_robot_info_dict=None):
        """
        The Core idea is to find optimum Facility Distribution across the systems
        :param df: The main dataframe which needed to be split according to number of systems
        :param robot_capacity_info_dict: Capacity of holding number of canisters per robot
        :param drug_canister_info_dict: Available(free, not allocated) to use canisters for each drug
        :param canister_location_info_dict: Location(On shelf OR robot) for each canister
        :param robot_free_location_info_dict: Free locations for each robot
        :param facility_pack_info_dict: Set of packs needed for each facility
        :param system_robot_info_dict: List of robot id's for each system
        """
        """
        The main df, which needed to be split according to number of systems and the split dfs would be used as a separate dfs for individual Multi-Robot Algorithm 
        """
        self.df = df
        """
        To access the dataframe related utility functions
        """
        self.dfu = DataFrameUtil(df=deepcopy(df))
        self.robot_capacity_info_dict = robot_capacity_info_dict
        self.drug_canister_info_dict = drug_canister_info_dict
        self.canister_location_info_dict = canister_location_info_dict
        self.robot_free_location_info_dict = robot_free_location_info_dict
        """
        pack requirement in each facility data
        """
        self.facility_pack_info_dict = facility_pack_info_dict
        self.system_robot_info_dict = system_robot_info_dict
        self.system_drug_info_dict = {}
        self.robot_drug_info_dict = {}
        self.robot_canister_info_dict = {}
        self.robot_id_list = []
        self.facility_drug_info_dict = {}
        self.common_drugs_confusion_matrix = None
        self.system_id_list = []
        self.facility_id_list = []
        self.maximum_similarity_matrix = {}
        self.similarity_based_facility_system_mapping = {}
        self.system_facility_info_dict = {}
        self.system_division_info_dict = {}
        pass

    def recommend_distribution(self):
        """
        Theory :-- Method performs optimisation based on two purposes.
        1) - First it checks for every facility that with which system similarity with its own is higher.
           -  It assigns that facility to the same system.
        2) - After facility assignment, it will check        This step will be completed later.
 balancing is required or not based on pre-defined threshold.
           - if it is required algorithm will transfer facilities of overloaded systems to other systems.
           - Facilities with the least similarity will be selected for the transfer, from the overloaded system.

        ## Steps ##
        a) generate robot_drug_info_dict, contains which robot owns which drugs, and system_drug_info_dict, which is
           the dict which contains the information regarding which drugs are present in particular system
        b) generate facility_drug_info_dict, contains which facility owns which drugs.
        c) generate common drugs confusion matrix, system_id_list, facility_id_list
        d) get similarity_based_facility_system_mapping, which is dictionary facility_id as key and system_id as value,
           system id assigned will be based on the closest match of the drug.
        e) Normalising similarity_based_facility_system_mapping.
        f) converting facility_system_mapping into system_facility_mapping. system facility mapping is a dict, system_id
           as key and list of facility_id as value.
        g) converting system_facility_mapping to system_division_info_dict and return it.
        :return:
        """

        """
        The required data for performing the main algorithm
        """
        """
        Generate dictionary(system_drug_info) which stores the drugs that are already present in the system for later usage.
        """
        self.robot_id_list = self.fill_robot_id_list(system_robot_info_dict=deepcopy(self.system_robot_info_dict))

        self.robot_canister_info_dict = self.fill_robot_canister_info_dict(deepcopy(self.robot_id_list),
                                                                           deepcopy(self.canister_location_info_dict))

        self.robot_drug_info_dict = self.fill_robot_drug_info_dict(robot_canister_info_dict=deepcopy(self.robot_canister_info_dict),
                                                                    drug_canister_info_dict=deepcopy(self.drug_canister_info_dict))

        self.system_drug_info_dict = self.fill_system_drug_info_dict(system_robot_info_dict=deepcopy(self.system_robot_info_dict),
                                                                    robot_drug_info_dict=deepcopy(self.robot_drug_info_dict))
        """
        From Facility-Packs info, extract Facility-drug info from main-df, by collecting the total drugs used for each pack and append it to each facility accordingly. 
        """
        self.facility_drug_info_dict = self.fill_facility_drug_info_dict(facility_pack_info_dict=self.facility_pack_info_dict, dfu=self.dfu)

        """
        Mainly two drugs data available:
        1. facility required drugs available from facility_drug_info
        2. system available drugs from system_drug_info.
        
        Core Idea: Assign facilities to the system where the drug is already present in that system. i.e. Allocate facilities according to drugs similarity between (required drugs and available drugs)
        For this, compute common_drug_confusion_matrix
        """
        self.system_id_list = list(self.system_drug_info_dict.keys())
        self.facility_id_list = list(self.facility_drug_info_dict.keys())
        self.common_drugs_confusion_matrix = self.generate_common_drugs_confusion_matrix(system_id_list=self.system_id_list, facility_id_list=self.facility_id_list)

        """
        Core Algorithm to decide which facility should be assigned to which system
        1. Create priority lists w.r.t to System0 (priority-wise facilities, 
        2. Assign facilities according to pack-length, with considering the priority of the facilities with each system (trade-off between priority of facility in system, and balancing pack-length)
            - Due to trade-off, set the threshold to which extend we want to balance the facilities by balancing pack-length
        """

        if(len(self.system_id_list) > 1):
            # todo: change this for N-systems and N-robots
            self.priority_facilities_list, self.facilitywise_druglen_list, self.facilitywise_packlen_list = self.fill_priority_lists(facility_id_list=deepcopy(self.facility_id_list),
                                                                                                                                     common_drugs_confusion_matrix=deepcopy(self.common_drugs_confusion_matrix),
                                                                                                                                     facility_pack_info_dict=deepcopy(self.facility_pack_info_dict))
            # todo: change this for N-systems and N-robots
            self.system_facility_info_dict = self.facility_packlen_balancing_algorithm(system_id_list=deepcopy(self.system_id_list),
                                                                                       priority_facilities_list=deepcopy(self.priority_facilities_list),
                                                                                       facilitywise_druglen_list=deepcopy(self.facilitywise_druglen_list),
                                                                                       facilitywise_packlen_list=deepcopy(self.facilitywise_packlen_list))

            # self.system_facility_info_dict = self.multi_robot_facility_packlen_balancing_algorithm(system_id_list=deepcopy(self.system_id_list),
            #                                                                                         priority_facilities_list=deepcopy(self.priority_facilities_list),
            #                                                                                         facilitywise_druglen_list=deepcopy(self.facilitywise_druglen_list),
            #                                                                                         facilitywise_packlen_list=deepcopy(self.facilitywise_packlen_list),
            #                                                                                        system_robot_info_dict=deepcopy(self.system_robot_info_dict))

        else:
            self.system_facility_info_dict[self.system_id_list[0]] = self.facility_id_list


        self.system_division_info_dict = self.fill_system_division_info_dict(system_facility_info_dict=deepcopy(self.system_facility_info_dict),
                                                                             facility_pack_info_dict=deepcopy(self.facility_pack_info_dict))

        return self.system_division_info_dict

    def fill_robot_id_list(self, system_robot_info_dict):
        """

        :param system_robot_info_dict:
        :return: robot_id_list
        """
        robot_id_list = []
        for system_id in system_robot_info_dict.keys():
            robot_id_list.extend(system_robot_info_dict[system_id])
        return robot_id_list

    def fill_robot_canister_info_dict(self, robot_id_list, canister_location_info_dict):
        """

        :return:
        """
        robot_canister_info_dict = {}
        for robot_id in robot_id_list:
            robot_canister_info_dict[robot_id] = []
            for canister_id in canister_location_info_dict.keys():
                if canister_location_info_dict[canister_id][0] == robot_id:
                    robot_canister_info_dict[robot_id].append(canister_id)
        return robot_canister_info_dict

    def fill_robot_drug_info_dict(self, robot_canister_info_dict, drug_canister_info_dict):
        """

        :return:
        """
        robot_drug_info_dict = {}
        for robot_id in robot_canister_info_dict.keys():
            robot_drug_info_dict[robot_id] = []
            for canister_id in robot_canister_info_dict[robot_id]:
                for drug_id in drug_canister_info_dict.keys():
                    if canister_id in drug_canister_info_dict[drug_id]:
                        robot_drug_info_dict[robot_id].append(drug_id)
        return robot_drug_info_dict

    def fill_system_drug_info_dict(self, system_robot_info_dict, robot_drug_info_dict):
        """

        :return:
        """
        system_drug_info_dict = {}
        for system_id in system_robot_info_dict.keys():
            system_drug_info_dict[system_id] = set([])
            for robot_id in system_robot_info_dict[system_id]:
                system_drug_info_dict[system_id].update(set(robot_drug_info_dict[robot_id]))
        #print(system_drug_info_dict)
        return system_drug_info_dict


    def fill_facility_drug_info_dict(self, facility_pack_info_dict, dfu):
        """

        :param facility_pack_info_dict:
        :param dfu:
        :return:
        """
        facility_drug_info_dict = {}
        for facility_id in facility_pack_info_dict.keys():
            facility_drug_info_dict[facility_id] = set([])
            pack_list = facility_pack_info_dict[facility_id]
            for pack_id in pack_list:
                drugs_for_given_pack = dfu.row_element_info_dict[pack_id]
                facility_drug_info_dict[facility_id].update(drugs_for_given_pack)
        return facility_drug_info_dict

    def generate_common_drugs_confusion_matrix(self, system_id_list, facility_id_list):
        """
        It generates common_packs_confusion_matrix. In common pack confusion matrix each location [ci, cj] of confusion
        matrix has value of number of common packs between drug ci and cj.
        :return: common_packs_confusion_matrix
        """
        common_drugs_confusion_matrix = np.zeros((len(system_id_list), len(facility_id_list)))
        for row, system_id in enumerate(system_id_list):
            for column, facility_id in enumerate(facility_id_list):
                drugs_system = self.system_drug_info_dict[system_id]
                drugs_facility = self.facility_drug_info_dict[facility_id]

                common_drugs_confusion_matrix[row, column] = len(set(drugs_system).intersection(set(drugs_facility)))
        return common_drugs_confusion_matrix

    def fill_system_status(self, system_id_list, common_drug_confusion_matrix):
        system_status = {}
        for i in range(common_drug_confusion_matrix.shape[0]):
            row = common_drug_confusion_matrix[i,:]
            if(np.all(row == 0)):
                system_status[system_id_list[i]] = False
            else:
                system_status[system_id_list[i]] = True

        return system_status

    def fill_priority_lists(self, facility_id_list, common_drugs_confusion_matrix, facility_pack_info_dict):
        '''
        Generate priority lists with respect to system-0
        :param facility_id_list: list of all facilities
        :param common_drugs_confusion_matrix: common drugs between system and facility matrix
        :param facility_pack_info_dict: facility containing packs information
        :return: prioritywise facility list, prioritywise drug len list, facilitywise packlen list
        '''

        '''
        # These priority lists are considered with respect to system - 0
        # i.e. The left-most element have highest priority to remain in system - 0 rather than system - 1, the right-most element have lowest priority to remain in system 0
        '''

        priority_facilities_list = []
        facilitywise_druglen_list = []
        facilitywise_packlen_list = []
        non_zero_element_count = []
        zero_row_cnt = 0

        '''
        Count number of rows(systems) where there is not a single drug common with any facility
        '''
        for num, i in enumerate(range(common_drugs_confusion_matrix.shape[0])):
            # row: each system --> all facilities common drugs
            row = common_drugs_confusion_matrix[i,:]
            non_zero_element_count.append(np.count_nonzero(row))
            # if system doesn't have any common drugs with any facilities, then the entire row will be 0
            if (np.all(row == 0)):
                zero_row_cnt = zero_row_cnt + 1

        for num, i in enumerate(range(common_drugs_confusion_matrix.shape[0])):
            row = common_drugs_confusion_matrix[i,:].astype(int)
            # Case-1 : When all systems(2 systems) have something common with some/all facilities
            # todo: We are considering taking only one systems point of view, we can change this and assign facilities to the system where the common drug is higher(Only in the case where every system contians facility correlation)
            if(zero_row_cnt == 0):
                if(non_zero_element_count[0] > non_zero_element_count[1]):
                    facilitywise_druglen_list = deepcopy(list(sorted(row)[::-1]))
                    priority_facilities_list = [x for _, x in sorted(zip(row, facility_id_list))[::-1]]
                    break

                elif(non_zero_element_count[0] <= non_zero_element_count[1]):
                    facilitywise_druglen_list = deepcopy(list(sorted(row)[::-1]))
                    priority_facilities_list = [x for _, x in sorted(zip(row, facility_id_list))[::-1]]
                    break
            # Case-2: When one system don't have any drugs common with any facilities and one system have common drugs
            elif(zero_row_cnt == 1):
                if not (np.all(row == 0)):
                    facilitywise_druglen_list = deepcopy(list(sorted(row)[::-1]))
                    priority_facilities_list = [x for _, x in sorted(zip(row, facility_id_list))[::-1]]
                    break
            # Case-3: When both system don't have any common drugs with any facilities
            # In this case, we can just balance the packs, because we don't have any priority based on drugs as there are no common drugs with any facilites
            # todo: here, we can set the threshold to zero, that is we can try to perfectly balance the packs in both facilities
            elif(zero_row_cnt == 2):
                facilitywise_druglen_list = deepcopy(list(sorted(row)[::-1]))
                priority_facilities_list = [x for _, x in sorted(zip(row, facility_id_list))[::-1]]
                break

        for facility in priority_facilities_list:
            facilitywise_packlen_list.append(len(facility_pack_info_dict[facility]))

        return priority_facilities_list, facilitywise_druglen_list, facilitywise_packlen_list


    def facility_packlen_balancing_algorithm(self, system_id_list ,priority_facilities_list, facilitywise_druglen_list, facilitywise_packlen_list):

        system_facility_info_dict = {}
        # system_packlen_count_dict ={}
        system0_facility = []
        system1_facility = []
        system0_packlen_count = 0
        system1_packlen_count = 0
        sum_packlen = sum(facilitywise_packlen_list)

        percentage = 10 if sum_packlen > 20 else 20
        packlen_diff = math.ceil(sum_packlen*(percentage/100))

        pop_element_list = []

        for num, druglen in enumerate(facilitywise_druglen_list):
            if(druglen == 0):
                system1_facility.append(priority_facilities_list[num])
                system1_packlen_count = system1_packlen_count + facilitywise_packlen_list[num]
            else:
                system0_facility.append(priority_facilities_list[num])
                system0_packlen_count = system0_packlen_count + facilitywise_packlen_list[num]

        while(abs(system0_packlen_count - system1_packlen_count) > packlen_diff):
            if(system0_packlen_count > system1_packlen_count):
                if(len(system0_facility) > 1):
                    item = system0_facility.pop()
                    pop_element_list.append(item)
                    if(len(pop_element_list) > len(priority_facilities_list) - 1):
                        system0_facility.append(item)
                        break
                    system1_facility.append(item)
                    system1_packlen_count = system1_packlen_count + facilitywise_packlen_list[priority_facilities_list.index(item)]
                    system0_packlen_count = system0_packlen_count - facilitywise_packlen_list[priority_facilities_list.index(item)]
                else:
                    break
            else:
                if(len(system1_facility) > 1):
                    item = system1_facility.pop(0)
                    pop_element_list.append(item)
                    if (len(pop_element_list) > len(priority_facilities_list) - 1):
                        system1_facility = [item] + system1_facility
                        break
                    system0_facility.append(item)
                    system0_packlen_count = system0_packlen_count + facilitywise_packlen_list[priority_facilities_list.index(item)]
                    system1_packlen_count = system1_packlen_count - facilitywise_packlen_list[priority_facilities_list.index(item)]
                else:
                    break

        for num, system_id in enumerate(system_id_list):
            if(num == 0):
                system_facility_info_dict[system_id] = system0_facility
            else:
                system_facility_info_dict[system_id] = system1_facility

        return system_facility_info_dict

    def multi_robot_facility_packlen_balancing_algorithm(self, system_id_list, priority_facilities_list, facilitywise_druglen_list, facilitywise_packlen_list, system_robot_info_dict):
        """

        :param system_id_list:
        :param priority_facilities_list:
        :param facilitywise_druglen_list:
        :param facilitywise_packlen_list:
        :param system_robot_info_dict:
        :return:
        """
        #system_list = list(system_robot_info_dict.keys())
        #all_robots = [robot_id for robot_list in system_robot_info_dict.values() for robot_id in robot_list]
        #sorted_system_robot_info_dict = {system_id: system_robot_info_dict[system_id] for system_id in sorted(system_robot_info_dict, key=len(system_robot_info_dict.get), reverse=True)}
        sorted_robot_list = sorted(system_robot_info_dict.values(), key=lambda k: len(k), reverse=True)
        system0_robot, system1_robot = sorted_robot_list[0], sorted_robot_list[1]
        len_system0_robot, len_system1_robot = len(system0_robot), len(system1_robot)

        system_facility_info_dict = {}
        # system_packlen_count_dict ={}
        system0_facility = []
        system1_facility = []
        system0_packlen_count = 0
        system1_packlen_count = 0
        sum_packlen = sum(facilitywise_packlen_list)

        percentage = 10 if sum_packlen > 20 else 20
        packlen_diff = math.ceil(sum_packlen*(percentage/100))

        pop_element_list = []

        for num, druglen in enumerate(facilitywise_druglen_list):
            if(druglen == 0):
                system1_facility.append(priority_facilities_list[num])
                system1_packlen_count = system1_packlen_count + facilitywise_packlen_list[num]
            else:
                system0_facility.append(priority_facilities_list[num])
                system0_packlen_count = system0_packlen_count + facilitywise_packlen_list[num]

        req_packlen_system0 = math.ceil((len_system0_robot/(len_system0_robot + len_system1_robot)*sum_packlen))
        #req_packlen_system1 = sum_packlen - req_packlen_system0

        while(system0_packlen_count - req_packlen_system0 > 0):
            if(abs(system0_packlen_count - system1_packlen_count) > packlen_diff):
                if(system0_packlen_count > system1_packlen_count):
                    if(len(system0_facility) > 1):
                        item = system0_facility.pop()
                        pop_element_list.append(item)
                        if(len(pop_element_list) > len(priority_facilities_list) - 1):
                            system0_facility.append(item)
                            break
                        system1_facility.append(item)
                        system1_packlen_count = system1_packlen_count + facilitywise_packlen_list[priority_facilities_list.index(item)]
                        system0_packlen_count = system0_packlen_count - facilitywise_packlen_list[priority_facilities_list.index(item)]
                    else:
                        break
                else:
                    if(len(system1_facility) > 1):
                        item = system1_facility.pop(0)
                        pop_element_list.append(item)
                        if (len(pop_element_list) > len(priority_facilities_list) - 1):
                            system1_facility = [item] + system1_facility
                            break
                        system0_facility.append(item)
                        system0_packlen_count = system0_packlen_count + facilitywise_packlen_list[priority_facilities_list.index(item)]
                        system1_packlen_count = system1_packlen_count - facilitywise_packlen_list[priority_facilities_list.index(item)]
                    else:
                        break

        for num, system_id in enumerate(system_id_list):
            if(num == 0):
                system_facility_info_dict[system_id] = system0_facility
            else:
                system_facility_info_dict[system_id] = system1_facility

        return system_facility_info_dict

    def fill_system_division_info_dict(self, system_facility_info_dict, facility_pack_info_dict):
        system_division_info_dict = {}
        for system_id in system_facility_info_dict.keys():
            system_division_info_dict[system_id] = []
            for facility_id in system_facility_info_dict[system_id]:
                system_division_info_dict[system_id].extend(facility_pack_info_dict[facility_id])
        append_dictionary_to_json_file(deepcopy(system_division_info_dict), "system_division_info_dict",save_json=False)
        return system_division_info_dict


class RecommendCanisterDistributionAcrossSystems:
    def __init__(self, system_df_info_dict=None, drug_canister_info_dict=None, system_robot_info_dict=None, robot_capacity_info_dict=None, pack_drug_manual_dict=None, canister_location_info_dict=None,canister_qty_dict=None):
        self.system_df_info_dict = system_df_info_dict
        self.drug_canister_info_dict = drug_canister_info_dict
        self.system_robot_info_dict = system_robot_info_dict
        self.robot_capacity_info_dict = robot_capacity_info_dict
        self.pack_drug_manual_dict = pack_drug_manual_dict
        self.canister_location_info_dict = canister_location_info_dict
        self.canister_qty_dict = canister_qty_dict

    def recommend_canister_distribution(self):
        """
        This class segregates "drug_caniter_info_dict" according to different systems.
        It divides the canisters in the both systems in a optimal way such that manual drug filling is minimal

        Steps)
        1. Get systemwise drug_info_dict
        2. To distribute drug canisters, first find the common drugs that are required in both systems.
        3. Algorithm uses length of packs used in each drug, therefore, define a dictionary which stores this length as a value and drug being key
        4. Reverse the dictionary from system_drug_packlength to drug_system_packlength
        5. Get common drug_system_packlength dictionary
        6. Get system_list and systemwise_common_canister_list where canister list is the set of canisters which are to put in particular system, which is decided by algorithm.
        7. From previous information, form a systemwise canister_info_dict.
        8. Get systemwise drug_canister_info_dict which is used as a input in various CanisterRecommendation Classes.
        :return: system list(list), systemwise drug_canister_info_dict (dictionary)
        """

        """
        Get system-wise packs and drugs from system_df
        """
        self.system_robot_capacity_info_dict = self.split_robot_capacity_info_dict(system_robot_info_dict=deepcopy(self.system_robot_info_dict),
                                                                                   robot_capacity_info_dict=deepcopy(self.robot_capacity_info_dict))

        self.system_drug_info_dict = self.fill_system_drug_info_dict(system_df_info_dict=deepcopy(self.system_df_info_dict))

        self.system_pack_info_dict = self.fill_system_pack_info_dict(system_df_info_dict=deepcopy(self.system_df_info_dict))

        # self.systemwise_manual_drug_dict = self.fill_systemwise_manual_drug_dict(pack_drug_manual_dict=deepcopy(self.pack_drug_manual_dict),
        #                                                                            system_pack_info_dict=deepcopy(self.system_pack_info_dict))

        self.system_pack_drug_manual_dict = self.fill_system_pack_drug_manual_dict(pack_drug_manual_dict=deepcopy(self.pack_drug_manual_dict),
                                                                                   system_pack_info_dict=deepcopy(self.system_pack_info_dict))

        self.system_pack_half_pill_drug_dict = self.fill_system_pack_half_pill_drug_dict(pack_drug_manual_dict=deepcopy(self.pack_drug_manual_dict),
                                                                                         system_pack_info_dict=deepcopy(self.system_pack_info_dict))
        # """
        # Get Robot-wise drugs and packs --> we need to generate that data from multirobot
        # """
        # for system_id in self.system_df_info_dict:
        #     systemwise_df = self.system_df_info_dict[system_id]
        #     systemwise_robot_list = self.system_robot_info_dict[system_id]
        #
        #     mria = MultiRobotClusterAnalysis(df=systemwise_df, drug_canister_info_dict=self.drug_canister_info_dict, robot_list=systemwise_robot_list)
        #     result_of_algo = mria.fill_robot_distribution_info_dict()
        #
        #     self.system_robot_cluster = {}
        #     self.system_robot_cluster[system_id] = mria.assign_cluster_to_robot(result_of_algo=deepcopy(result_of_algo), canister_location_info_dict=deepcopy(self.canister_location_info_dict),
        #                                                 drug_canister_info_dict=deepcopy(self.drug_canister_info_dict), robot_list=deepcopy(systemwise_robot_list))
        #
        # """
        #
        # """
        # self.system_robot_drug_dict = self.fill_system_robot_drug_dict(system_robot_cluster=deepcopy(self.system_robot_cluster), system_robot_info_dict=deepcopy(self.system_robot_info_dict))
        #
        # self.system_robot_pack_dict = self.fill_system_robot_pack_dict(system_robot_cluster=deepcopy(self.system_robot_cluster))


        """
        Find common drugs between both systems
        """
        # todo: change this for N-systems
        self.systemwise_common_drug_list = self.fill_systemwise_common_drug_info_dict(system_drug_info_dict=
                                                                                      deepcopy(self.system_drug_info_dict))

        # todo: Instead only calculate this dictionary for only common drugs, this will reduce the computation
        """
        Shows the usage of drug in number of different packs (system-wise) 
        """
        self.system_drug_pack_len_dict = self.fill_system_drug_pack_len_dict(system_df_info_dict=
                                                                             deepcopy(self.system_df_info_dict))
        """
        Reverse the dictionary found in previous step to compare the difference between two systems
        """
        self.drug_system_pack_len_dict = self.fill_drug_system_pack_len_dict(system_drug_pack_len_dict=
                                                                             deepcopy(self.system_drug_pack_len_dict))
        """
        Filter-down the common drug system packlen dict where there will be only drugs which are being used in both systems. 
        """
        self.common_drug_system_pack_len_dict = self.fill_common_drug_system_pack_len_dict(drug_system_pack_len_dict=
                                                                                           deepcopy(self.drug_system_pack_len_dict))
        """
        Insert the drugs which are not available in drug_canister_info_dict but actually present in robot (system_robot)
        """
        # todo: check if this function is required
        self.drug_canister_info_dict = self.update_drug_canister_info_dict(system_drug_info_dict=
                                                                           deepcopy(self.system_drug_info_dict),
                                                                           drug_canister_info_dict=
                                                                           deepcopy(self.drug_canister_info_dict))

        """
        Main function for allocation of canisters available in drug_canister dictionary
        """
        # todo: change this for N-systems
        self.system_list, self.systemwise_common_canister_list = self.allocate_canisters_system(common_drug_system_pack_len_dict=
                                                                                     deepcopy(self.common_drug_system_pack_len_dict),
                                                                                     drug_canister_info_dict=
                                                                                     deepcopy(self.drug_canister_info_dict),
                                                                                     system_drug_pack_len_dict=
                                                                                     deepcopy(self.system_drug_pack_len_dict))
        """
        step - 7
        """
        self.system_common_canister_info_dict = self.fill_system_common_canister_info_dict(system_list=
                                                                             deepcopy(self.system_list),
                                                                             systemwise_common_canister_list=
                                                                             deepcopy(self.systemwise_common_canister_list),
                                                                             common_drug_system_pack_len_dict=
                                                                             deepcopy(self.common_drug_system_pack_len_dict))

        """
        Split drug_canister_info_dict according to number of systems
        The canisters will be distributed to the different systems where the drug is common between systems. The drugs that are not common would remain in both drug_canister_info_dict
        """
        # todo: Change this, if we want the only drugs and canisters of the particular system.
        self.system_drug_canister_info_dict = self.split_systemwise_drug_canister_info_dict(system_list=
                                                                                            deepcopy(self.system_list),
                                                                                            drug_canister_info_dict=
                                                                                            deepcopy(self.drug_canister_info_dict),
                                                                                            system_common_canister_info_dict=
                                                                                            deepcopy(self.system_common_canister_info_dict),
                                                                                            common_drug_system_pack_len_dict=
                                                                                            deepcopy(self.common_drug_system_pack_len_dict))



        return self.system_list, self.system_drug_canister_info_dict, self.system_robot_capacity_info_dict, self.system_pack_drug_manual_dict, self.system_pack_half_pill_drug_dict

    # def fill_system_robot_drug_dict(self, system_robot_cluster, system_robot_info_dict):
    #     system_robot_drug_dict = {}
    #
    #     for system_id in system_robot_info_dict:
    #         system_robot_info_dict[system_id] = {}
    #         for robot_id in system_robot_info_dict[system_id]:
    #             system_robot_info_dict[system_id][robot_id] = system_robot_cluster[system_id]
    #

    ## step 1 - get system drug info dict
    def fill_system_drug_info_dict(self, system_df_info_dict):

        system_drug_info_dict = {}
        for system_id, df in system_df_info_dict.items():
            system_drug_info_dict[system_id] = list(df)

        return system_drug_info_dict

    def fill_system_pack_info_dict(self, system_df_info_dict):
        system_pack_info_dict = {}
        for system_id, df in system_df_info_dict.items():
            system_pack_info_dict[system_id] = list(df.index.values)

        return system_pack_info_dict

    # todo: Check if this function works that way we want for actual data
    def fill_systemwise_manual_drug_dict(self, pack_drug_manual_dict, system_pack_info_dict):
        systemwise_manual_drug_dict = {}
        for system_id in system_pack_info_dict.keys():
            systemwise_manual_drug_dict[system_id] = []

        for system_id, pack_list in system_pack_info_dict.items():
            for pack in pack_list:
                for drug in pack_drug_manual_dict[pack]:
                    if(pack_drug_manual_dict[pack][drug]):
                        systemwise_manual_drug_dict[system_id].append(drug)

        for system_id in systemwise_manual_drug_dict:
            systemwise_manual_drug_dict[system_id] = set(systemwise_manual_drug_dict[system_id])

        return systemwise_manual_drug_dict

    def fill_system_pack_drug_manual_dict(self, pack_drug_manual_dict, system_pack_info_dict):
        system_pack_drug_manual_dict = {}

        for system_id, pack_list in system_pack_info_dict.items():
            system_pack_drug_manual_dict[system_id] = {}
            for pack in pack_list:
                system_pack_drug_manual_dict[system_id][pack] = pack_drug_manual_dict[pack]

        return system_pack_drug_manual_dict

    def fill_system_pack_half_pill_drug_dict(self, pack_drug_manual_dict, system_pack_info_dict):

        system_pack_half_pill_drug_dict = {}
        for system_id, pack_list in system_pack_info_dict.items():
            system_pack_half_pill_drug_dict[system_id] = {}
            for pack in pack_list:
                for drug in pack_drug_manual_dict[pack]:
                    if pack_drug_manual_dict[pack][drug]:
                        system_pack_half_pill_drug_dict[system_id][pack] = []
                        system_pack_half_pill_drug_dict[system_id][pack].append(drug)

        return system_pack_half_pill_drug_dict

    ## step 2 - systemwise common drug info dict
    def fill_systemwise_common_drug_info_dict(self, system_drug_info_dict):
        systemwise_common_drug_info_dict = {}
        systemwise_common_drug_list = set()
        if(len(system_drug_info_dict.keys()) > 1):
            for num, system_id in enumerate(system_drug_info_dict.keys()):
                #systemwise_common_drug_info_dict[system_id] = set()
                temp_common = set(system_drug_info_dict[system_id])

                if(num == 0):
                    #systemwise_common_drug_info_dict[system_id] = temp_common
                    systemwise_common_drug_list = temp_common
                else:
                    #systemwise_common_drug_info_dict[system_id] = systemwise_common_drug_info_dict[system_id].intersection(temp_common)
                    systemwise_common_drug_list = systemwise_common_drug_list.intersection(temp_common)

        return systemwise_common_drug_list

    ## step 3 - create system_drug_pack_len_dict
    def fill_system_drug_pack_len_dict(self, system_df_info_dict):

        try:
            system_drug_pack_len_dict = {}

            for system_id, df in system_df_info_dict.items():
                system_drug_pack_len_dict[system_id] = {}

                df_mat = df.as_matrix()
                row_element_list = list(df.index.values)
                col_element_list = list(df)
                row_element_list = np.array(row_element_list)
                for num in range(df_mat.shape[1]):
                    i = df_mat[:, num]
                    system_drug_pack_len_dict[system_id][col_element_list[num]] = len(row_element_list[np.nonzero(i)])
            return system_drug_pack_len_dict

        except Exception as e:
            logger.error(str(e))

    def fill_drug_system_pack_len_dict(self, system_drug_pack_len_dict):
        drug_system_pack_len_dict = {}

        for system_id, drug_pack_len_dict in system_drug_pack_len_dict.items():
            for drug_id in drug_pack_len_dict.keys():
                drug_system_pack_len_dict[drug_id] = {}

        for system_id, drug_pack_len_dict in system_drug_pack_len_dict.items():
            for drug_id in drug_pack_len_dict.keys():
                drug_system_pack_len_dict[drug_id][system_id] = system_drug_pack_len_dict[system_id][drug_id]

        return drug_system_pack_len_dict

    def fill_common_drug_system_pack_len_dict(self, drug_system_pack_len_dict):
        common_drug_system_pack_len_dict = {}
        for drug_id in drug_system_pack_len_dict.keys():
            if(len(drug_system_pack_len_dict[drug_id]) > 1):
                common_drug_system_pack_len_dict[drug_id] = {}
                common_drug_system_pack_len_dict[drug_id] = drug_system_pack_len_dict[drug_id]

        return common_drug_system_pack_len_dict

    def update_drug_canister_info_dict(self, system_drug_info_dict, drug_canister_info_dict):
        # update_drug_canister_info_dict
        all_system_drugs = set()
        drugs_not_in_drug_canister_dict = []
        for system_id in system_drug_info_dict:
            all_system_drugs.update(system_drug_info_dict[system_id])

        drugs = all_system_drugs - set(drug_canister_info_dict.keys())
        if (len(drugs) != 0):
            drugs_not_in_drug_canister_dict.extend(list(drugs))
            for drug in drugs_not_in_drug_canister_dict:
                drug_canister_info_dict[drug] = set()

        return drug_canister_info_dict

    def allocate_canisters_system(self, common_drug_system_pack_len_dict, drug_canister_info_dict, system_drug_pack_len_dict):
        max_diff_threshold = 10
        drug_packlen_diff_dict = {}
        system0_canister_list = []
        system1_canister_list = []
        system_list = []

        for system_id in system_drug_pack_len_dict:
            system_list.append(system_id)

        if (len(common_drug_system_pack_len_dict) > 0 and len(system_list) > 1):
            for drug, sys_dict in common_drug_system_pack_len_dict.items():

                for num, sys_id in enumerate(sys_dict.keys()):

                    if (num == 0):
                        temp_diff = common_drug_system_pack_len_dict[drug][sys_id]
                    elif (num == 1):
                        temp_diff1 = temp_diff - common_drug_system_pack_len_dict[drug][sys_id]
                        drug_packlen_diff_dict[drug] = temp_diff1


            # consider only drugs which are common in both systems
            for drug in drug_packlen_diff_dict:
                temp_drug_canister_list = list(drug_canister_info_dict[drug])

                # if drug has 4 canisters available, then distribute 2, 2 canisters to both systems
                # todo: When there are more than 2 robots, then we have to change this code
                if (len(drug_canister_info_dict[drug]) >= 4):
                    system0_canister_list.extend(temp_drug_canister_list[:2])
                    system1_canister_list.extend(temp_drug_canister_list[2:4])

                # if drug has 3 canisters available, then disbribute canisters according to priority(drug present in no. of packs count)
                elif (len(drug_canister_info_dict[drug]) == 3):
                    if (drug_packlen_diff_dict[drug] >= 0):
                        system0_canister_list.extend(temp_drug_canister_list[:2])
                        system1_canister_list.extend(temp_drug_canister_list[2:])
                    elif (drug_packlen_diff_dict[drug] < 0):
                        system1_canister_list.extend(temp_drug_canister_list[:2])
                        system0_canister_list.extend(temp_drug_canister_list[2:])

                # if drug has 2 canisters available, then disbribute canisters according to priority(drug present in no. of packs count)
                elif (len(drug_canister_info_dict[drug]) == 2):
                    if (drug_packlen_diff_dict[drug] >= 0 and abs(drug_packlen_diff_dict[drug]) > max_diff_threshold):
                        system0_canister_list.extend(temp_drug_canister_list[:2])
                    elif (drug_packlen_diff_dict[drug] < 0 and abs(drug_packlen_diff_dict[drug]) > max_diff_threshold):
                        system1_canister_list.extend(temp_drug_canister_list[:2])
                    elif (drug_packlen_diff_dict[drug] >= 0 and abs(drug_packlen_diff_dict[drug]) < max_diff_threshold):
                        system0_canister_list.extend(temp_drug_canister_list[:1])
                        system1_canister_list.extend(temp_drug_canister_list[1:])
                    elif (drug_packlen_diff_dict[drug] < 0 and abs(drug_packlen_diff_dict[drug]) < max_diff_threshold):
                        system1_canister_list.extend(temp_drug_canister_list[:1])
                        system0_canister_list.extend(temp_drug_canister_list[1:])

                # if drug has 1 canisters available, then disbribute canister to system whose drug has higher no. of packs
                elif (len(drug_canister_info_dict[drug]) == 1):
                    if (drug_packlen_diff_dict[drug] >= 0):
                        system0_canister_list.extend(temp_drug_canister_list)
                    else:
                        system1_canister_list.extend(temp_drug_canister_list)

            systemwise_common_canister_list = [system0_canister_list, system1_canister_list]
        else:
            systemwise_common_canister_list = []
        return system_list, systemwise_common_canister_list

    def multi_robot_allocate_canisters_system(self, common_drug_system_pack_len_dict, drug_canister_info_dict, system_drug_pack_len_dict, system_robot_info_dict):
        """

        :param common_drug_system_pack_len_dict:
        :param drug_canister_info_dict:
        :param system_drug_pack_len_dict:
        :param system_robot_info_dict:
        :return:
        """
        drug_packlen_diff_dict = {}
        system_list = list(system_robot_info_dict.keys())
        total_robots = [robot_id for robot_list in system_robot_info_dict.values() for robot_id in robot_list]

        if(len(common_drug_system_pack_len_dict) > 0 and len(system_list) > 1):
            for drug, sys_dict in common_drug_system_pack_len_dict.items():
                for num, sys_id in enumerate(sys_dict.keys()):
                    if (num == 0):
                        temp_diff = common_drug_system_pack_len_dict[drug][sys_id]
                    elif (num == 1):
                        temp_diff1 = temp_diff - common_drug_system_pack_len_dict[drug][sys_id]
                        drug_packlen_diff_dict[drug] = temp_diff1

            for drug in drug_packlen_diff_dict:
                canisters_of_drug = list(drug_canister_info_dict[drug])
        pass


    ## step 6 - system canisters info dict
    def fill_system_common_canister_info_dict(self, system_list, systemwise_common_canister_list, common_drug_system_pack_len_dict):
        system_common_canister_info_dict = {}
        if(len(system_list) > 1 and len(common_drug_system_pack_len_dict)> 0):
            for system_id in system_list:
                system_common_canister_info_dict[system_id] = set(systemwise_common_canister_list[system_list.index(system_id)])
        return system_common_canister_info_dict

    ## step 7 - seperate drug_canister_info_dict for both systems
    def split_systemwise_drug_canister_info_dict(self, system_list, drug_canister_info_dict, system_common_canister_info_dict, common_drug_system_pack_len_dict):
        """
        Split drug_canister_info_dict into N-numbers for N-systems
        :param system_list:
        :param drug_canister_info_dict:
        :param system_common_canister_info_dict:
        :param common_drug_system_pack_len_dict:
        :return:
        """
        system_drug_canister_info_dict = {}
        for system_id in system_list:
            system_drug_canister_info_dict[system_id] = deepcopy(drug_canister_info_dict)
        if(len(system_list) > 1 and len(common_drug_system_pack_len_dict) > 0):
            for drug in common_drug_system_pack_len_dict.keys():
                for system_id in common_drug_system_pack_len_dict[drug]:
                    for canister in list(system_drug_canister_info_dict[system_id][drug]):
                        if(canister not in (system_common_canister_info_dict[system_id])):
                            system_drug_canister_info_dict[system_id][drug].remove(canister)

        return system_drug_canister_info_dict

    def split_robot_capacity_info_dict(self, system_robot_info_dict, robot_capacity_info_dict):
        system_robot_capacity_info_dict = {}
        for system_id in system_robot_info_dict.keys():
            # system_id = str(system_id)
            system_robot_capacity_info_dict[system_id] = {}

        for system_id, robot_list in system_robot_info_dict.items():
            # system_id = str(system_id)
            for robot_id in robot_list:
                system_robot_capacity_info_dict[system_id][robot_id] = robot_capacity_info_dict[robot_id]

        return system_robot_capacity_info_dict

class MultiRobotClusterAnalysis(DataFrameUtil):

    def __init__(self, df=None, file_name=None, added_canister_drug_id_list=None, drug_canister_info_dict=None,
                 maximum_independence_factor=3, robot_list=None, is_multi_split=False, split_function_id=None,
                 total_packs=None, batch_formation=False, total_robots=None, pack_delivery_date=None):
        #DataFrameUtil.__init__(self, df=df, file_name=file_name, columns_to_delete=added_canister_drug_id_list)
        self.df = df
        self.total_packs= total_packs
        """
        drug_canister info for the particular system
        """
        self.drug_canister_info_dict = drug_canister_info_dict

        """
        Number of robots for the particular system
        """
        self.robot_list = robot_list
        self.total_robots = total_robots
        self.split_function_id = split_function_id
        self.pack_delivery_date = pack_delivery_date

        """
        drugs to remove:
        1. Manual drugs: which is filled manually by worker
        2. Multiple canister drugs: Don't need to compute in the Independent Cluster Analysis, because it will eventually be assigned to all robots
        """
        self.added_canister_drug_id_list = added_canister_drug_id_list
        if self.added_canister_drug_id_list is None:
            self.added_canister_drug_id_list = self.fill_drugs_to_remove(self.df, self.drug_canister_info_dict, len(self.robot_list))
        logger.debug('Common drugs in all robots: {}'.format(len(self.added_canister_drug_id_list)))
        #print("COMMON DRUGS IN ALL ROBOTS: ", len(self.added_canister_drug_id_list))
        logger.debug("Initial Main-df dimension: {}".format(df.shape))
        #print("Initial Main df dimension: ", df.shape)
        """
        - Initially, count, level is set to zero
        - Initially, optimum cluster info is not available, so it is set to empty dictionary
        """
        self.count = 0
        self.level_id = 0
        self.cluster_info = {}
        self.multiple_split_info = {}

        """
        # The main dictionary to store [df, current robot list, cluster info, drugs to remove]
        # It gets updated every time recursion function algorithm() is called
        """
        self.data_dict = {}
        start_time = time.time()
        self.algorithm(self.df, len(self.robot_list), self.added_canister_drug_id_list, self.cluster_info, self.count, self.level_id,is_multi_split,batch_formation)
        logger.debug("multi-robot algorithm time: {}".format(time.time() - start_time))
        #print("multi-robot algorithm time: ", time.time() - start_time)
        self.result_of_algo = {}

    def algorithm(self, df, num_of_robots, added_canister_drug_id_list, cluster_info, count, level_id,is_multi_split,batch_formation):
        """
        A recursion Algorithm, recursively creates result from information of parent node.
        :param df: 1) Main dataframe when algorithm() is called for the first time 2) derived df from result IndependentClusterAnalysis Class
        :param robot_list: 1) Total number robots present 2) Total number of robots available for current node
        :param added_canister_drug_id_list: These are the drugs which we want to remove from main algorithm of IndependentClusterAnalysis Class
        :param cluster_info: 1) It is empty dictionary at root node, because the optimum cluster split is not applied 2) derived cluster info(drugs, packs info) from parent node
        :param count: To assign incremental number to each node
        :param level_id: To store recursion level info for each node
        :return: data_dict which contains df, robot list, cluster info, drugs to remove at each node where key being (level id, nth node count)
        """

        """
        # 1. When the algorithm() function is first time called it will save the main df, total robot list, cluster_info(which is empty at start) and drugs to remove information
        # 2. When the algorithm() function is called after first time, it will dynamically take df, robot list, drugs to remove, cluster info according to split result from parent node

        The keys of data_dict is tuple = (level_id, count), i.e. (0,0) will be root node, further nodes will be like (1,1), (1,2) for level 1; (2,3), (2,4), (2,5), (2,6) for level 2 and so on.
        """
        if self.total_robots > 1:
            self.data_dict[level_id, count] = {
                'df': df,
                'num of robots': num_of_robots,
                'cluster_info': cluster_info,
                'drugs to remove': added_canister_drug_id_list,
            }
            # Base Condition when recursion stops
            if(num_of_robots == 1):
                return

        """
        - Compute result of algorithm using IndependentClusterAnalysis
        - df, added_canister_drug_id_list, num_of_robots will be different at every level of recursion. Same for the same level nodes.
        """
        c = IndependentClusterAnalysis(df=df, added_canister_drug_id_list=added_canister_drug_id_list,
                                       maximum_independence_factor=3, num_of_robots=num_of_robots,
                                       total_robots=self.total_robots, split_function_id=self.split_function_id,
                                       total_packs=self.total_packs,
                                       drug_canister_info_dict=self.drug_canister_info_dict,
                                       pack_delivery_date=self.pack_delivery_date)
        if is_multi_split:
            if batch_formation:
                result_of_algo, loss = c.run_algorithm()
            else:
                result_of_algo, loss = c.run_algorithm_multi_split()
            self.multiple_split_info = result_of_algo
            return self.multiple_split_info
        else:
            result_of_algo, loss = c.run_algorithm()

        #print("RESULT OF ALGO clusters -----> FOR CHILD NODES")
        logger.debug("Cluster-0 :: Packs-length: {}, Drugs-length: {}".format(len(result_of_algo[0]['packs']), len(result_of_algo[0]['drugs'])))
        logger.debug("Cluster-1 :: Packs-length: {}, Drugs-length: {}".format(len(result_of_algo[1]['packs']), len(result_of_algo[1]['drugs'])))
        # print("C0 PackLen:",len(result_of_algo[0]['packs']),"DrugLen:",len(result_of_algo[0]['drugs']))
        # print("C1 PackLen:", len(result_of_algo[1]['packs']), "DrugLen:", len(result_of_algo[1]['drugs']))

        """
        Number of robots division at each recursion.
        - Currently, splits into (1, total robots - 1) manner
        """
        num_robot_cluster0, num_robot_cluster1 = self.num_of_robots_division(num_of_robots)

        """
        - Assign 0 key to smaller cluster and 1 to larger 
        """
        cluster_dict = self.fill_cluster_dict(result_of_algo)

        """
        Generate dfs from parent node optimum result of algorithm(contains packs, drugs distribution)
        """
        df0, df1 = self.generate_dfs_from_parent_result(result_of_algo, df)

        """
        Assign 0, 1 keys to each result clusters according to pack-length
        0 key is assigned to the cluster which is having smaller pack-length
        """
        cluster_df_dict = self.fill_df_dict(df0, df1, cluster_dict)

        """
        drugs to remove at each node will be dependent to the number of robots
        - Iteratively compute manual drugs and multiple canisters drugs each time
        """
        df0_drugs_to_remove = self.fill_drugs_to_remove(cluster_df_dict[0], self.drug_canister_info_dict, num_robot_cluster0)

        df1_drugs_to_remove = self.fill_drugs_to_remove(cluster_df_dict[1], self.drug_canister_info_dict, num_robot_cluster1)

        if self.total_robots == 1:
            self.data_dict[level_id, count] = {
                'df': df,
                'num of robots': num_of_robots,
                'cluster_info': cluster_dict[1],
                'drugs to remove': added_canister_drug_id_list,
            }
            # Base Condition when recursion stops
            if (num_of_robots == 1):
                return

        """
        Recursive call to the main function algorithm
        - Recursively compute result from parent optimum cluster
        """
        self.algorithm(cluster_df_dict[0], num_robot_cluster0, df0_drugs_to_remove, cluster_dict[0], 2 * count + 1, level_id + 1,is_multi_split,batch_formation)
        self.algorithm(cluster_df_dict[1], num_robot_cluster1, df1_drugs_to_remove, cluster_dict[1], 2 * count + 2, level_id + 1,is_multi_split,batch_formation)
        return self.data_dict

    def num_of_robots_division(self, total_robots):
        """
        We split the robots in two clusters: One robot + all other robots
        :param total_robots:
        :return:
        """
        num_robots_cluster0 = 1
        num_robots_cluster1 = total_robots - num_robots_cluster0

        return num_robots_cluster0, num_robots_cluster1

    def fill_cluster_dict(self, result_of_algo):

        sorted_cluster_id = [0, 1]
        sorted_cluster_list = sorted(result_of_algo, key=lambda x: len(x['packs']), reverse=False)
        sorted_cluster_dict = OrderedDict(zip(sorted_cluster_id, sorted_cluster_list))

        return sorted_cluster_dict

    def generate_dfs_from_parent_result(self, result_of_algo, df):
        """

        :param result_of_algo: Optimum cluster info from parent node
        :param df: dataframe derived from parent node
        :param added_canister_drug_id_list: list of drugs that we want to remove from df(remove columns)
        :return: generated dataframes df0, df1
        """
        # Find each cluster's drugs and packs list
        cluster0_drugs = result_of_algo[0]['drugs']
        cluster0_packs = result_of_algo[0]['packs']

        cluster1_drugs = result_of_algo[1]['drugs']
        cluster1_packs = result_of_algo[1]['packs']

        # 1. Keep the columns that are required
        df0 = df[list(cluster0_drugs)]
        df1 = df[list(cluster1_drugs)]

        # 2. keep only rows(packs) that are present in cluster packs
        df0 = df0.loc[cluster0_packs]
        df1 = df1.loc[cluster1_packs]
        # print("After Post-Processing, common drugs are already added")
        # print("IN GENERATE DFs FROM PARENT NODE:")
        logger.info("df dimensions before removing all-empty column")
        logger.debug("df shapes: Parent-node df: {}, Child-node df0: {}, Child-node df1: {}".format(df.shape, df0.shape, df1.shape))
        # print('PARENT df:', df.shape)
        # print("child df0: ", df0.shape, "child df1: ", df1.shape)

        # For debugging purpose
        df0_initial_drugs = set(list(df0))
        df1_initial_drugs = set(list(df1))

        # remove drugs which are being not used
        df0 = df0.loc[:, (df0 != 0).any(axis=0)]
        df1 = df1.loc[:, (df1 != 0).any(axis=0)]
        # print("AFTER EMPTY COLUMN DELETION:---")
        # print("child df0: ", df0.shape, "child df1: ", df1.shape)
        logger.info("df dimensions after removing all-empty column")
        logger.debug("df shapes: Parent-node df: {}, Child-node df0: {}, Child-node df1: {}".format(df.shape, df0.shape, df1.shape))

        # For debugging purpose
        df0_final_drugs = set(list(df0))
        df1_final_drugs = set(list(df1))

        # For debugging purpose
        df0_drugs_remove = df0_initial_drugs - df0_final_drugs
        df1_drugs_remove = df1_initial_drugs - df1_final_drugs

        logger.debug("Drugs removed: df0: {}, df1: {}".format(df0_drugs_remove, df1_drugs_remove))
        # print('df0: drugs removed:- ', df0_drugs_remove)
        # print('df1: drugs removed:- ', df1_drugs_remove)

        return df0, df1

    def fill_df_dict(self, df0, df1, cluster_dict):
        """

        :param df0:
        :param df1:
        :param cluster_dict:
        :return:
        """
        sorted_cluster_id = sorted(list(cluster_dict.keys()))
        df_list = [df0, df1]
        sorted_df_list = sorted(df_list, key=lambda x: x.shape[0])

        df_dict = OrderedDict(zip(sorted_cluster_id, sorted_df_list))
        return df_dict

    def fill_drugs_to_remove(self, df, drug_canister_info_dict, no_of_robots):
        """
        It computes which drugs to remove: manual drug + multiple drug + external manual drug (1/2 pill case)
        :param df: generated dataframe from result of parent node
        :param drug_canister_info_dict: drug as key and number of canisters allocated to that drug as values
        :return: set of drugs to remove at each node (When IndependentClusterAnalysis Class is called)
        """
        drugs_list = list(df)
        if (no_of_robots != 1):
            manual_drugs_list = []
            for drug_id in drugs_list:
                if drug_id in drug_canister_info_dict.keys():
                    if len(drug_canister_info_dict[drug_id]) == 0:
                        manual_drugs_list.append(drug_id)
                else:
                    manual_drugs_list.append(drug_id)

            multiple_canister_drug = []
            for drug_id in drugs_list:
                if drug_id in drug_canister_info_dict.keys():
                    if len(drug_canister_info_dict[drug_id]) >= no_of_robots:
                        multiple_canister_drug.append(drug_id)
        else:
            manual_drugs_list = []
            multiple_canister_drug = []

        # print("Number of robots: ", no_of_robots)
        # print("Number of Manual Drugs: ", len(manual_drugs_list))
        # print("Number of Multiple Drugs: ", len(multiple_canister_drug))
        logger.debug("No of Robots: {}".format(no_of_robots))
        logger.debug("No of Manual Drugs: {}-->{}, ".format(len(manual_drugs_list), manual_drugs_list))
        logger.debug("No of Multiple Canister Drugs: {}-->{}".format(len(multiple_canister_drug), multiple_canister_drug))
        drugs_to_remove = manual_drugs_list + multiple_canister_drug
        return drugs_to_remove

    def fill_robot_distribution_info_dict(self):
        """
        Fill cluster information for each robot which is generated from algorithm
        :return: result of algo: A dictionary where key is robot_id and value being optimum cluster information
        """
        clusters_id_list = list(range((len(self.robot_list))))
        result = []
        for key, data in self.data_dict.items():
            if(data['num of robots'] is 1):
                result.append(data['cluster_info'])

        self.result_of_algo = OrderedDict(zip(clusters_id_list, result))

        return self.result_of_algo

    def assign_cluster_to_robot(self, result_of_algo, canister_location_info_dict, drug_canister_info_dict, robot_list):
        cluster_drugs_dict = {}
        for cluster_id in result_of_algo:
            cluster_drugs_dict[cluster_id] = result_of_algo[cluster_id]['drugs']

        '''
        robot_canister_info_dict: stores information about currently placed canisters in the each robot
        '''
        robot_canister_info_dict = {}
        for robot_id in robot_list:
            robot_canister_info_dict[robot_id] = []
            for canister_id in canister_location_info_dict.keys():
                if canister_location_info_dict[canister_id][0] == robot_id:
                    robot_canister_info_dict[robot_id].append(canister_id)
        """
        robot_drug_info_dict: currently placed drug in each robot information
        """
        robot_drug_info_dict = {}
        for robot_id in robot_canister_info_dict.keys():
            robot_drug_info_dict[robot_id] = []
            for canister_id in robot_canister_info_dict[robot_id]:
                for drug_id in drug_canister_info_dict.keys():
                    if canister_id in drug_canister_info_dict[drug_id]:
                        robot_drug_info_dict[robot_id].append(drug_id)

        """
        Now we check similarity with drugs present in each robot and the algorithm result drugs
        """
        robot_cluster_common_drugs = {}
        for robot_id in robot_list:

            for cluster_id in cluster_drugs_dict:
                common_drugs = set(robot_drug_info_dict[robot_id]) & set(cluster_drugs_dict[cluster_id])
                robot_cluster_common_drugs[(robot_id, cluster_id)] = len(common_drugs)

        sorted_robot_cluster_common_drugs = sorted(robot_cluster_common_drugs, key=lambda x: robot_cluster_common_drugs[x], reverse=True)

        robot_assigned_cluster_list = []
        robot_assigned = set()
        cluster_assigned = set()
        temp_robot_cluster_common_drugs = deepcopy(sorted_robot_cluster_common_drugs)
        while(temp_robot_cluster_common_drugs):
            robot_id, cluster_id = temp_robot_cluster_common_drugs.pop(0)

            if robot_id not in robot_assigned:
                if cluster_id not in cluster_assigned:
                    robot_assigned_cluster_list.append((robot_id, cluster_id))
                    cluster_assigned.add(cluster_id)
                    robot_assigned.add(robot_id)

        robot_cluster_dict = {}
        for robot_id in robot_list:
            for robot_cluster_id_tuple in robot_assigned_cluster_list:
                robot = robot_cluster_id_tuple[0]
                cluster_id = robot_cluster_id_tuple[1]
                if robot_id is robot:
                    robot_cluster_dict[robot_id] = result_of_algo[cluster_id]

        return robot_cluster_dict

class IndependentClusterAnalysis(DataFrameUtil):
    """
    This class will make a tree based on independent cluster analysis. It will be in the following format.
    tree_dict = {
                 a : [(b,0),(c,0),(d,0)] ,
                 b : [(e,1),(f,1)]
                }
    """

    def __init__(self, df=None, file_name=None, added_canister_drug_id_list=None, maximum_independence_factor=3,
                 assert_algo=True, num_of_robots=None, split_function_id=None, total_packs=None, total_robots=None,
                 drug_canister_info_dict={}, pack_delivery_date=None):
        DataFrameUtil.__init__(self, df=df, file_name=file_name, debug_mode=False,
                               columns_to_delete=added_canister_drug_id_list)
        self.df = df
        self.total_packs = total_packs
        self.unexplored_packs_list = self.row_element_list
        self.unexplored_drugs_list = self.column_element_list
        self.drug_canister_info_dict = drug_canister_info_dict
        self.independent_cluster_dict = {}
        self.independent_cluster_list = []
        self.df_binary_0_removed = {}
        self.independent_cluster_tree = None
        self.cluster_info_dict = None
        self.total_robots = total_robots
        self.num_of_robots = num_of_robots
        self.tt = TreeTrace()
        self.debug_mode = False
        self.split_function_id = split_function_id
        self.maximum_independence_factor = maximum_independence_factor
        self.added_canister_drug_id_list = added_canister_drug_id_list
        self.pack_delivery_date = pack_delivery_date
        self.assert_algo = False

    def run_algorithm(self, max_independence_factor=None, debug_mode = False):
        """
        Runs Algorithm
        :return:
        """
        split_function_id = self.split_function_id
        logger.info('passed split function id: {}'.format(split_function_id))
        if max_independence_factor == None:
            max_independence_factor = self.maximum_independence_factor
        total_number_of_packs = len(self.unexplored_packs_list)
        self.independent_cluster_tree, self.cluster_info_dict = self.generate_independent_cluster_tree(max_independence_factor)
        append_dictionary_to_json_file(deepcopy(self.independent_cluster_tree), "independent_cluster_tree",
                                       save_json=False)
        append_dictionary_to_json_file(deepcopy(self.cluster_info_dict), "cluster_info_dict",
                                       save_json=False)

        self.tt.tracing_tree(total_number_of_packs, self.independent_cluster_tree, self.cluster_info_dict, debug_mode, self.num_of_robots,self.row_element_list,self.added_canister_drug_id_list,self.df,self.column_element_list,split_function_id,total_packs=self.total_packs,total_robots=self.total_robots)

        #self.tt.result_with_minimum_loss_function = self.algorithm_post_processing_v2(self.tt.result_with_minimum_loss_function, self.row_element_list, self.added_canister_drug_id_list)
        self.tt.result_with_minimum_loss_function = self.algorithm_post_processing_v3_multi_robot(self.tt.result_with_minimum_loss_function, self.row_element_list, self.added_canister_drug_id_list, self.num_of_robots)
        if self.assert_algo:
            self.assertion_confirming_result_of_algorithm(deepcopy(self.tt.result_with_minimum_loss_function), multiple_drugs_added_canisters=self.added_canister_drug_id_list)
        append_dictionary_to_json_file(deepcopy(self.tt.result_with_minimum_loss_function), "result_of_algorithm",
                                       save_json=False)

        logger.info('final cluster dict: {}'.format(self.tt.result_with_minimum_loss_function))
        return self.tt.result_with_minimum_loss_function, self.tt.minimum_loss_function

    def run_algorithm_multi_split(self, max_independence_factor=None, debug_mode = False):
        """
        Runs Algorithm
        :return:
        """
        if max_independence_factor == None:
            max_independence_factor = self.maximum_independence_factor
        total_number_of_packs = len(self.unexplored_packs_list)
        self.independent_cluster_tree, self.cluster_info_dict = self.generate_independent_cluster_tree(max_independence_factor)
        append_dictionary_to_json_file(deepcopy(self.independent_cluster_tree), "independent_cluster_tree",
                                       save_json=False)
        append_dictionary_to_json_file(deepcopy(self.cluster_info_dict), "cluster_info_dict",
                                       save_json=False)

        split_with_function = {}
        for id in range(1,settings.TOTAL_SPLIT_FUNCTIONS+1):
            self.tt.tracing_tree(total_number_of_packs, self.independent_cluster_tree, self.cluster_info_dict, debug_mode, self.num_of_robots,self.row_element_list,self.added_canister_drug_id_list,self.df,self.column_element_list,split_function_id=id,total_packs=self.total_packs)

            if self.tt.result_with_minimum_loss_function is None:
                if len(self.independent_cluster_tree[(0,-1)]) == 0:
                    self.tt.result_with_minimum_loss_function = self.algorithm_post_processing_v3_multi_robot(
                        self.tt.result_with_minimum_loss_function, self.row_element_list,
                        self.added_canister_drug_id_list, self.num_of_robots)
                print("P")
            #self.tt.result_with_minimum_loss_function = self.algorithm_post_processing_v2(self.tt.result_with_minimum_loss_function, self.row_element_list, self.added_canister_drug_id_list)
            elif self.tt.result_with_minimum_loss_function is not None:
                self.tt.result_with_minimum_loss_function = self.algorithm_post_processing_v3_multi_robot(self.tt.result_with_minimum_loss_function, self.row_element_list, self.added_canister_drug_id_list, self.num_of_robots)
            if self.assert_algo:
                self.assertion_confirming_result_of_algorithm(deepcopy(self.tt.result_with_minimum_loss_function), multiple_drugs_added_canisters=self.added_canister_drug_id_list)
            append_dictionary_to_json_file(deepcopy(self.tt.result_with_minimum_loss_function), "result_of_algorithm",
                                           save_json=False)
            if self.tt.result_with_minimum_loss_function is not None:
                split_with_function[id] = {"Robot-1" : self.tt.result_with_minimum_loss_function[0]['pack_length'] , "Robot-2": self.tt.result_with_minimum_loss_function[1]['pack_length'] , "common_packs": len(self.tt.result_with_minimum_loss_function[0]['packs'] & self.tt.result_with_minimum_loss_function[1]['packs'])}
        split_with_function_optimised = {}
        l = []
        for k,v in split_with_function.items():
            tp = (max(v['Robot-1'],v['Robot-2']),v['common_packs'])
            l.append(tp)

        for i in l:
            for k, v in split_with_function.items():
                if i[0] == max(v['Robot-1'],v['Robot-2']) and i[1] == v['common_packs']:
                    split_with_function_optimised[k] = v
                    break

        return split_with_function_optimised, self.tt.minimum_loss_function

    def assertion_confirming_result_of_algorithm(self, result_of_algorithm, multiple_drugs_added_canisters=[], number_of_robots = 2):
        """
        This method will check following condition.
        1) Type of result_of_algorithm is list.
        2) There are same number of clusters as that of the robot in result_of_algorithm.
        3) Every cluster has the type dictionary.
        4) Pack and Drug data structures are stored in the format of set or list.
        5) Multiple drug_added_canisters do exist in both the cluster.
        6) Only multiple_drugs_added_canisters exist repeated in both the clusters.
        7) Every cluster contains respective packs' drugs.
        8) Total number of packs is equal to set addition(union) of packs of all the clusters.
        9) Total number of drugs is equal to algebric addition of drugs of all the drugs.

        :param result_of_algorithm:
        :param multiple_drugs_added_canisters:
        :param number_of_robots:
        :return:
        """
        """
        1
        """
        assert type(result_of_algorithm) == list
        """
        2
        """
        assert len(result_of_algorithm) == number_of_robots

        total_cluster_packs = set([])
        total_cluster_drugs = []
        for cluster in result_of_algorithm:
            """
            3
            """
            assert type(cluster) ==  dict
            """
            4
            """
            assert (type(cluster["packs"]) == list and type(cluster["drugs"]) == list) or (
                        type(cluster["packs"]) == set and type(cluster["drugs"]) == set)
            """
            5 & 6
            """
            assert len(set(cluster["drugs"]).intersection(set(multiple_drugs_added_canisters))) == len(multiple_drugs_added_canisters)
            """
            7
            """
            for pack in cluster["packs"]:
                for drug in self.get_nonzero_colum_elements_for_given_row_element_from_data_frame(pack):
                    print (pack, drug, cluster["drugs"])
                    assert drug in cluster["drugs"]

            total_cluster_packs.update(deepcopy(cluster["packs"]))
            total_cluster_drugs += list(deepcopy(cluster["drugs"]))
        """
        8
        """
        total_packs = deepcopy(set(self.row_element_list))
        assert len(total_cluster_packs) == len(total_packs)
        """
        9
        """
        assert len(total_cluster_drugs) == len(self.column_element_list) + 2*len(self.added_canister_drug_id_list)
        pass

    def algorithm_post_processing_v1(self, result_of_algo, total_pack_list, added_drug_id_list):
        """

        :param result_of_algo:
        :return:
        """
        total_pack_list = set(total_pack_list)
        remainder_pack_list = total_pack_list

        """
        Condition where we have multiple canisters for all the drugs.
        """
        if result_of_algo == None:
            result_of_algo = []
            for i in range(2):
                cluster = {}
                cluster["packs"] = []
                cluster["drugs"] = []
                result_of_algo.append(cluster)
        for cluster in result_of_algo:
            cluster["packs"] = set(cluster["packs"])
            cluster["drugs"] = set(list(cluster["drugs"]) + added_drug_id_list)
            # print (len(cluster["drugs"]))
            remainder_pack_list = remainder_pack_list - cluster["packs"]
        # print ("remainder pack list", remainder_pack_list, len(remainder_pack_list))
        number_of_remainder_packs = len(remainder_pack_list)
        half_point = number_of_remainder_packs//2
        for num,cluster in enumerate(result_of_algo):
            remainder_pack_list = list(remainder_pack_list)
            if num == 0:
                cluster["packs"] = set(list(cluster["packs"]) + list(remainder_pack_list[0:half_point]))
            if num == 1:
                cluster["packs"] = set(list(cluster["packs"]) + list(remainder_pack_list[half_point:number_of_remainder_packs]))

        for cluster in result_of_algo:
            print ("packs", len(cluster["packs"]))
            print ("drugs", len(cluster["drugs"]))
            cluster["pack_length"] = len(cluster["packs"])
            cluster["drug_length"] = len(cluster["drugs"])
        return result_of_algo
        pass

    def pack_balancing_for_multicanister_drugs(self,num_of_robots,total_pack_length,sorted_result_min_loss):
        """
        This function distributes the multiple canister drugs pack between 2 robots with clustering logic.
        1) Initialize the data utils with all packs and drugs dataframe(df).
        2) Now we will generate cluster of packs where there are no common packs between 2 clusters(level 0 clustering).
        3) We will sort the internal cluster packs by 2 parameter :
            - min no. of total available canister from drugs of packs(Ex. P1 :- d1,d2,d3 and d1 has 2 canisters, d2 has 4 ,d3 has 8 so we take 2 which is min of 2)
            - total no. of unique drugs in pack.
        4) we now sort cluster based on no. of packs in descending order for distribution.
        5) we distribute the cluster between 2 robots and if any cluster which can not be kept in any of the robot then we split it.
        6) Update the final dictionary with cluster packs and drugs.
        """
        split_count = math.ceil((1 / num_of_robots) * total_pack_length)
        req_cluster0_packs = split_count
        req_cluster1_packs = total_pack_length - split_count

        '''
        1) Initializing dataframe in Dataframeutil.
        '''
        DataFrameUtil.__init__(self, df=self.df, file_name=None, debug_mode=False)
        '''
        2) Generate clusters of packs with level 0(common packs between 2 clusters are 0).
        '''
        independent_clusters = self.generate_independent_clusters(sorted(list(self.added_canister_drug_id_list)), 0)

        '''
        3) sort internal cluster packs with parameters
        '''
        total_pack_list = []
        pack_drug_dict = {}
        for cluster in independent_clusters:
            pack_sort_tuple = []
            for pack in cluster['packs']:
                canister_len = []
                drugs_of_given_pack = self.for_given_pack_return_list_of_drugs(pack)
                pack_drug_dict[pack] = drugs_of_given_pack
                for drug in drugs_of_given_pack:
                    if drug in self.drug_canister_info_dict:
                        if len(self.drug_canister_info_dict[drug]) != 0:
                            canister_len.append(len(self.drug_canister_info_dict[drug]))
                if not canister_len:
                    pack_sort_tuple.append((pack, 10, len(drugs_of_given_pack)))
                else:
                    pack_sort_tuple.append((pack, min(canister_len), len(drugs_of_given_pack)))
            pack_sort_tuple = sorted(pack_sort_tuple, key=lambda k: (k[1], -k[2]))
            pack_list = [pack[0] for pack in pack_sort_tuple]
            cluster['packs'] = pack_list
            total_pack_list.extend(pack_list)

        '''
        4) sort clusters in descending order of length of packs in them.
        '''
        clusterwise_packlen_list = []
        configuration = []
        sorted_independent_clusters = []
        for node, cluster_info in enumerate(independent_clusters):
            configuration.append(node)
            clusterwise_packlen_list.append(len(cluster_info['packs']))

        sorted_packlen_list = sorted(clusterwise_packlen_list)[::-1]
        sorted_config_list = [x for _, x in sorted(zip(clusterwise_packlen_list, configuration))[::-1]]

        sorted_config_packlen_list = list(zip(sorted_config_list, sorted_packlen_list))
        temp_sorted_config_packlen_list = deepcopy(sorted_config_packlen_list)

        '''
        5) Distribute clusters between 2 robots .
        '''
        cluster0_config = []
        cluster1_config = []
        cluster0_sum = 0
        cluster1_sum = 0
        cluster0_packs = []
        cluster1_packs = []
        cluster0_drugs = set()
        cluster1_drugs = set()

        pending_clusters = []
        while (len(temp_sorted_config_packlen_list) != 0):
            node_tuple = temp_sorted_config_packlen_list.pop(0)
            temp_node = node_tuple[0]
            temp_packlen = node_tuple[1]

            if (cluster0_sum + temp_packlen <= req_cluster0_packs):
                cluster0_config.append(temp_node)
                cluster0_sum = cluster0_sum + temp_packlen
                cluster0_packs.extend(independent_clusters[temp_node]['packs'])
            elif (cluster1_sum + temp_packlen <= req_cluster1_packs):
                cluster1_config.append(temp_node)
                cluster1_sum = cluster1_sum + temp_packlen
                cluster1_packs.extend(independent_clusters[temp_node]['packs'])
            else:
                pending_clusters.append(temp_node)

        for cluster_id in pending_clusters:
            cluster_packs = independent_clusters[cluster_id]['packs']
            while cluster_packs:
                if cluster0_sum < cluster1_sum:
                    while cluster_packs and cluster0_sum < req_cluster0_packs:
                        cluster0_packs.append(cluster_packs.pop(0))
                        cluster0_sum += 1
                if cluster1_sum < cluster0_sum:
                    while cluster_packs and cluster1_sum < req_cluster1_packs:
                        cluster1_packs.append(cluster_packs.pop(0))
                        cluster1_sum += 1
                if cluster0_sum == cluster1_sum:
                    while cluster_packs:
                        if cluster0_sum < req_cluster0_packs:
                            cluster0_packs.append(cluster_packs.pop(0))
                            cluster0_sum += 1
                        else:
                            cluster1_packs.append(cluster_packs.pop(0))
                            cluster1_sum += 1

        '''
        6) Update the dictionaries.
        '''
        for pack in cluster0_packs:
            cluster0_drugs.update(pack_drug_dict[pack])
        for pack in cluster1_packs:
            cluster1_drugs.update(pack_drug_dict[pack])


        sorted_result_min_loss[0]['packs'].update(set(cluster0_packs))
        sorted_result_min_loss[0]['drugs'].update(cluster0_drugs)

        sorted_result_min_loss[1]['packs'].update(set(cluster1_packs))
        sorted_result_min_loss[1]['drugs'].update(cluster1_drugs)

        for cluster in sorted_result_min_loss:
            cluster['pack_length'] = len(cluster['packs'])
            cluster['drug_length'] = len(cluster['drugs'])

        return sorted_result_min_loss

    def algorithm_post_processing_v2(self, result_of_algo, total_pack_list, added_drug_id_list):
        """

        :param result_of_algo:
        :return:
        """
        # Required if there is only one drug as input in IndependentClusterAnalysis
        dfu = DataFrameUtil(df=deepcopy(self.df))

        total_pack_list = set(total_pack_list)
        remainder_pack_list = deepcopy(total_pack_list)
        """
        Required if there is only one drug as input in IndependentClusterAnalysis
        """
        dfu = DataFrameUtil(df=deepcopy(self.df))

        '''
        Condition where there is only one distinct drug and other drugs have multiple canisters
        '''
        if result_of_algo is None and len(self.unexplored_drugs_list) == 1:
            result_of_algo = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_of_algo.append(cluster)

            result_of_algo[0]['drugs'] = set(self.unexplored_drugs_list)
            result_of_algo[0]['packs'] = list(dfu.column_element_info_dict[self.unexplored_drugs_list[0]])

        '''
        Condition where there is only one distinct drug and other drugs have multiple canisters
        '''
        if result_of_algo is None and len(self.unexplored_drugs_list) == 1:
            result_of_algo = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_of_algo.append(cluster)

            result_of_algo[0]['drugs'] = set(self.unexplored_drugs_list)
            result_of_algo[0]['packs'] = list(dfu.column_element_info_dict[self.unexplored_drugs_list[0]])

        """
        Condition where we have multiple canisters for all the drugs.
        """
        if result_of_algo == None:
            result_of_algo = []
            for i in range(2):
                cluster = {}
                cluster["packs"] = []
                cluster["drugs"] = []
                result_of_algo.append(cluster)
        """
        - Appending added_drug_id_list into both clusters.
        - Generating remainder_pack_list.
        remainder_pack_list is a list of packs which can be fully filled by added_drug_id_lists.
        added_drug_id_list is a list which contains manual_drugs(drugs with no canisters) and multiple_canister_drugs(drugs 
        for which we have mutliple canisters).
        """
        # for cluster in result_of_algo:
        #     cluster["packs"] = set(cluster["packs"])
        #     cluster["drugs"] = set(list(cluster["drugs"]) + added_drug_id_list)
        #     remainder_pack_list = remainder_pack_list - cluster["packs"]

        '''
        - added_drug_id_list will be different for both robots according to drug usage in pack distribution
        '''
        for cluster in result_of_algo:
            cluster["packs"] = set(cluster["packs"])
            cluster["drugs"] = set(list(cluster["drugs"]))
            remainder_pack_list = remainder_pack_list - cluster["packs"]
        """
        - Arranging remainder pack_list into both the clusters. In what follows is a strategy by which we are dividing 
        remainder pack list into both clusters.
        1) Check difference in packs of both clusters.
        2) If #of_remainder_pack_list is lesser than difference of packs, assign all remainder packs to the cluster with 
        lower number of pack counts.
        3) else devide remainder_pack_list into two parts.
            a) difference balance part:- Which will be making difference in #packs in both the clusters zero.
            b) Equal split part:- After making difference zero packs remained will be devided equally into both clusters.
        """
        remainder_pack_list = list(remainder_pack_list)
        difference_in_packs =abs(len(result_of_algo[0]["packs"]) - len(result_of_algo[1]["packs"]))
        if len(remainder_pack_list) > difference_in_packs:
            packs_to_append = remainder_pack_list[0:difference_in_packs]
            remainder_length = len(remainder_pack_list) - difference_in_packs
            remainder_pack_list = remainder_pack_list[-remainder_length:]
            if len(result_of_algo[0]["packs"]) < len(result_of_algo[1]["packs"]):
                result_of_algo[0]["packs"].update(set(packs_to_append))
            else:
                result_of_algo[1]["packs"].update(set(packs_to_append))

            number_of_remainder_packs = len(remainder_pack_list)
            half_point = number_of_remainder_packs//2
            for num,cluster in enumerate(result_of_algo):
                if num == 0:
                    cluster["packs"] = set(list(cluster["packs"]) + list(remainder_pack_list[0:half_point]))
                if num == 1:
                    cluster["packs"] = set(list(cluster["packs"]) + list(remainder_pack_list[half_point:number_of_remainder_packs]))
        else:
            if len(result_of_algo[0]["packs"]) < len(result_of_algo[1]["packs"]):
                result_of_algo[0]["packs"].update(set(remainder_pack_list))
            else:
                result_of_algo[1]["packs"].update(set(remainder_pack_list))

        '''
        remove drugs that are not required for the packs.
        i.e. after splitting into two clusters, if split individual df has a drug which is not used by any packs, then we simply remove drug
        '''

        cluster0_packs = result_of_algo[0]['packs']
        cluster1_packs = result_of_algo[1]['packs']

        # generate dataframes for each cluster result
        # 1. keep the columns that are required
        df0 = self.df[list(added_drug_id_list)]
        df1 = self.df[list(added_drug_id_list)]

        # 2. keep only rows (packs) that are present in cluster packs
        df0 = df0.loc[cluster0_packs]
        df1 = df1.loc[cluster1_packs]

        df0 = df0.loc[:, (df0 != 0).any(axis=0)]
        df1 = df1.loc[:, (df1 != 0).any(axis=0)]

        cluster0_added_drug_id_list = list(df0)
        cluster1_added_drug_id_list = list(df1)

        '''
        add manual drugs and multiple canister drugs to each cluster according to usage of drug in that cluster packs
        i.e. the only drugs will be added which are being used within cluster packs(It will be not added if it is being used in another cluster packs)
        '''
        result_of_algo[0]['drugs'] = set(list(result_of_algo[0]['drugs']) + cluster0_added_drug_id_list)
        result_of_algo[1]['drugs'] = set(list(result_of_algo[1]['drugs']) + cluster1_added_drug_id_list)
        """
        Edge cases, where there are no packs assigned to particular one cluster
        """
        for cluster in result_of_algo:
            if len(cluster['packs']) is 0:
                cluster['drugs'] = set()

        """
        Appending pack and drug length in cluster dictionary.
        """
        for cluster in result_of_algo:
            cluster["pack_length"] = len(cluster["packs"])
            cluster["drug_length"] = len(cluster["drugs"])

        return result_of_algo
        pass

    def get_sorted_pack_list_with_clustering(self):
        """

        """
        sorted_pack_list = []

        DataFrameUtil.__init__(self, df=self.df, file_name=None, debug_mode=False)
        independent_clusters = self.generate_independent_clusters(sorted(list(self.added_canister_drug_id_list)), 0)

        pack_drug_dict = {}
        for cluster in independent_clusters:
            pack_sort_tuple = []
            for pack in cluster['packs']:
                canister_len = []
                drugs_of_given_pack = self.for_given_pack_return_list_of_drugs(pack)
                pack_drug_dict[pack] = drugs_of_given_pack
                for drug in drugs_of_given_pack:
                    if drug in self.drug_canister_info_dict:
                        if len(self.drug_canister_info_dict[drug]) != 0:
                            canister_len.append(len(self.drug_canister_info_dict[drug]))
                if not canister_len:
                    pack_sort_tuple.append((pack, 10, len(drugs_of_given_pack)))
                else:
                    pack_sort_tuple.append((pack, min(canister_len), len(drugs_of_given_pack)))
            pack_sort_tuple = sorted(pack_sort_tuple, key=lambda k: (k[1], -k[2]))
            pack_list = [pack[0] for pack in pack_sort_tuple]
            cluster['packs'] = pack_list
            sorted_pack_list.extend(pack_list)

        return sorted_pack_list

    def algorithm_post_processing_v3_multi_robot(self, result_min_loss, total_pack_list, added_drug_id_list, num_of_robots):
        """
        Fill manual and multiple drugs so as to balance the packs in each node according to number of robots
        :param result_min_loss: Best result returned from the previous
        :param total_pack_list:
        :param added_drug_id_list:
        :param robot_list:
        :return:
        """
        # Required if there is only one drug as input in IndependentClusterAnalysis
        dfu = DataFrameUtil(df=deepcopy(self.df))
        all_multiple = False

        total_pack_list = set(total_pack_list)
        #print("Total Packs in POST PROCESSING", len(total_pack_list))
        remainder_pack_list = deepcopy(total_pack_list)

        # multiple_canister_drugs = set()
        # manual_drugs = set()
        # for drug_id,canisters in self.drug_canister_info_dict.items():
        #     if  drug_id in self.added_canister_drug_id_list:
        #         if len(canisters) >= num_of_robots:
        #             multiple_canister_drugs.add(drug_id)
        #         else:
        #             manual_drugs.add(drug_id)

        '''
        Condition where there is only one distinct drug and other drugs have multiple canisters
        '''
        if result_min_loss is None and len(self.unexplored_drugs_list) == 1:
            result_min_loss = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_min_loss.append(cluster)

            result_min_loss[0]['drugs'] = set(self.unexplored_drugs_list)
            result_min_loss[0]['packs'] = list(dfu.column_element_info_dict[self.unexplored_drugs_list[0]])


        """
        Condition where we have multiple canisters for all the drugs.
        """
        if result_min_loss == None:
            all_multiple = True
            result_min_loss = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_min_loss.append(cluster)

        '''
        - added_drug_id_list will be different for both robots according to drug usage in pack distribution
        - We will add added_drug_id_list according to pack distribution for both clusters afterwards
        '''
        for cluster in result_min_loss:
            cluster["packs"] = set(cluster["packs"])
            cluster["drugs"] = set(list(cluster["drugs"]))
            remainder_pack_list = remainder_pack_list - cluster["packs"]

        logger.debug("Remainder Packs in post-processing {} {}".format(len(remainder_pack_list), remainder_pack_list))
        #print("REMAINDER PACKS:- ", len(remainder_pack_list))
        """
        for checking purpose:
        """
        common_packs = len(result_min_loss[0]['packs'] & result_min_loss[1]['packs'])
        packs0 = len(result_min_loss[0]['packs'])
        packs1 = len(result_min_loss[1]['packs'])

        if(len(total_pack_list) == (packs0 + packs1 - common_packs) + len(remainder_pack_list)):
            pack_diff = 0
        else:
            pack_diff = -1000


        """
        """
        remainder_pack_list = list(remainder_pack_list)
        total_pack_length = len(total_pack_list)
        split_count = math.ceil((1 / num_of_robots) * total_pack_length)

        sorted_result_min_loss = sorted(result_min_loss, key=lambda x: len(x['packs']), reverse=False)

        req_cluster0_packs = split_count
        req_cluster1_packs = total_pack_length - split_count

        cluster0_packlen = len(sorted_result_min_loss[0]['packs'])
        cluster1_packlen = len(sorted_result_min_loss[1]['packs'])
        cluster0_pack_diff = req_cluster0_packs - cluster0_packlen
        cluster1_pack_diff = req_cluster1_packs - cluster1_packlen

        # create packs - delivery_date dict

        if all_multiple:# or remainder_pack_list:
            sorted_result_min_loss = self.pack_balancing_for_multicanister_drugs(num_of_robots=num_of_robots,
                                                                                 total_pack_length=total_pack_length,
                                                                                 sorted_result_min_loss=sorted_result_min_loss)
            return sorted_result_min_loss

        sorted_remainder_pack_list = sorted(remainder_pack_list, key=lambda x: self.pack_delivery_date[x])

        max_cluster_len = max(len(sorted_result_min_loss[0]['packs']),len(sorted_result_min_loss[1]['packs']))

        if max_cluster_len != len(sorted_result_min_loss[0]['packs']):
            # Add sorted remainder pack list here

            diff_length = max_cluster_len - len(sorted_result_min_loss[0]['packs'])
            sorted_result_min_loss[0]['packs'] = set(
                list(sorted_remainder_pack_list)[0:diff_length] + list(sorted_result_min_loss[0]['packs']))

            sorted_remainder_pack_list = sorted_remainder_pack_list[diff_length: ]

        if max_cluster_len != len(sorted_result_min_loss[1]['packs']):
            # Add sorted remainder pack list here
            diff_length = max_cluster_len - len(sorted_result_min_loss[0]['packs'])
            sorted_result_min_loss[0]['packs'] = set(
                list(sorted_remainder_pack_list)[0:diff_length] + list(sorted_result_min_loss[0]['packs']))

            sorted_remainder_pack_list = sorted_remainder_pack_list[diff_length:]

        # After this both the cluster will have same lenght
        delivery_date_wise_reminder_packs = {}
        for pack in sorted_remainder_pack_list:
            delivery_date = self.pack_delivery_date[pack]
            delivery_date_wise_reminder_packs.setdefault(delivery_date, []).append(pack)

        for delivery_date, packs in delivery_date_wise_reminder_packs.items():
            # divide the packs in 2. Add in both
            pack_len = len(packs)
            sorted_result_min_loss[0]['packs'] = set(packs[:pack_len//2] + list(sorted_result_min_loss[0]['packs']))
            sorted_result_min_loss[1]['packs'] = set(packs[pack_len//2:] + list(sorted_result_min_loss[1]['packs']))

        # if (len(remainder_pack_list) < cluster0_pack_diff):
        #     sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:cluster0_pack_diff] + list(sorted_result_min_loss[0]['packs']))
        # elif (len(remainder_pack_list) < cluster1_pack_diff):
        #     sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[0:cluster1_pack_diff] + list(sorted_result_min_loss[1]['packs']))
        # else:
        #     sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:cluster0_pack_diff] + list(sorted_result_min_loss[0]['packs']))
        #     sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[cluster0_pack_diff:cluster0_pack_diff + cluster1_pack_diff] + list(sorted_result_min_loss[1]['packs']))
        #
        #     remainder_pack_list = remainder_pack_list[cluster0_pack_diff + cluster1_pack_diff:]
        #     remainder_split_count = math.ceil((1/num_of_robots) * len(remainder_pack_list))
        #
        #     sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:remainder_split_count] + list(sorted_result_min_loss[0]['packs']))
        #     sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[remainder_split_count:] + list(sorted_result_min_loss[1]['packs']))


        '''
        remove drugs that are not required for the packs.
        i.e. after splitting into two clusters, if split individual df has a drug which is not used by any packs, then we simply remove drug
        '''

        cluster0_packs = sorted_result_min_loss[0]['packs']
        cluster1_packs = sorted_result_min_loss[1]['packs']

        # generate dataframes for manual drugs, to know which manual drug need to be added in the cluster
        # 1. keep the columns that are required
        df0 = self.df[list(added_drug_id_list)]
        df1 = self.df[list(added_drug_id_list)]

        # 2. keep only rows (packs) that are present in cluster packs
        df0 = df0.loc[cluster0_packs]
        df1 = df1.loc[cluster1_packs]
        # print("********** RUN ALGORITHM -----> MULTI-ROBOT POST-PROCESSING **********")
        # print("Shape of Manual drugs: df0:", df0.shape, "df1: ", df1.shape)
        df0 = df0.loc[:, (df0 != 0).any(axis=0)]
        df1 = df1.loc[:, (df1 != 0).any(axis=0)]

        #print("Shape of Manual drugs: df0:", df0.shape, "df1: ", df1.shape)
        cluster0_added_drug_id_list = list(df0)
        cluster1_added_drug_id_list = list(df1)
        logger.debug("In Multi-Robot Post-Processing...dataframe consisting of only manual drugs")
        logger.debug("manual drug + multiple canister dimensions :: df0: {}, df1: {}".format(df0.shape, df1.shape))

        '''
        add manual drugs and multiple canister drugs to each cluster according to usage of drug in that cluster packs
        i.e. the only drugs will be added which are being used within cluster packs(It will be not added if it is being used in another cluster packs)
        '''
        sorted_result_min_loss[0]['drugs'] = set(list(sorted_result_min_loss[0]['drugs']) + cluster0_added_drug_id_list)
        sorted_result_min_loss[1]['drugs'] = set(list(sorted_result_min_loss[1]['drugs']) + cluster1_added_drug_id_list)

        """
        Appending pack and drug length info in the cluster dictionary
        """
        for cluster in sorted_result_min_loss:
            cluster['pack_length'] = len(cluster['packs'])
            cluster['drug_length'] = len(cluster['drugs'])

        return sorted_result_min_loss

    def generate_independent_cluster_tree(self, limit_tree_factor, debug_mode = False):
        """
        This method will generate independent cluster list.
        :return:
        """
        """
        TODO: needed to be changed from drugs to packs
        """
        independent_cluster_tree = {}
        cluster_info_dict = {}
        last_used_id = 0
        all_drug_list = self.unexplored_drugs_list
        self.qu = Queue()
        self.qu.push([all_drug_list,-1,last_used_id])
        while not self.qu.isEmpty():
            parent = self.qu.pop()
            parent_drug_list = parent[0]
            parent_independence_degree = parent[1]
            parent_id = parent[2]
            # print ("parent id", parent_id)
            independent_cluster_tree[parent_id,parent_independence_degree] = []
            if parent_independence_degree>limit_tree_factor or len(parent_drug_list)==1:
                continue
            # print ("input drug list", parent_drug_list, "\n", "independence degree", parent_independence_degree+1)
            cluster_list = self.generate_independent_clusters(parent_drug_list, parent_independence_degree+1)
            # print ("cluster list", cluster_list)
            for cluster in cluster_list:
                # print ("cluster", cluster)
                child_independence_degree = parent_independence_degree+1
                last_used_id +=1
                child_id = last_used_id
                child = [cluster["drugs"], child_independence_degree, child_id]
                self.qu.push(child)
                independent_cluster_tree[(parent_id, parent_independence_degree)].append((child_id, child_independence_degree))
                cluster_info_dict[(child_id, child_independence_degree)] = cluster
        return independent_cluster_tree,cluster_info_dict
        pass

    def generate_independent_clusters(self,drugs_list, degree_of_independence = 0):
        """

        :param drugs_list:
        :param degree_of_independence:
        :return:
        """
        """
        TODO: required to be changed from packs to drugs
        """

        independent_cluster_list = []
        for drug in drugs_list:
            # print ("drug", drug)
            cluster_found_flag = False
            packs_of_given_drug = self.for_given_drug_return_list_of_packs(drug)
            found_cluster_list = []
            for num, cluster in enumerate(independent_cluster_list):
                # print ("cluster", cluster)
                common_packs = set(packs_of_given_drug).intersection(cluster["packs"])
                if len(common_packs) > degree_of_independence:
                    found_cluster_list.append(num)
                    cluster["packs"].update(set(packs_of_given_drug))
                    cluster["drugs"].add(drug)
                    cluster_found_flag = True
            if cluster_found_flag and len(found_cluster_list)>0:
                independent_cluster_list = self.merge_clusters(found_cluster_list, independent_cluster_list)
            if not cluster_found_flag:
                # print ("new cluster made")
                cluster = {"drugs": set([drug]), "packs":set(packs_of_given_drug)}
                independent_cluster_list.append(cluster)
        for drug_pack_set in independent_cluster_list:
            for key, value in drug_pack_set.items():
                value_list = list(value)
                value_list.sort()
                drug_pack_set[key] = value_list
        return independent_cluster_list

    def merge_clusters(self, found_cluster_list, independent_cluster_list):
        """
        We will merge cluster index suggested by found_cluster_list into independent_cluster_list.
        :param found_cluster_list:
        :param independent_cluster_list:
        :return: independnent_
        """
        # print("independent_cluster_list independent_cluster_list",independent_cluster_list)
        if len(found_cluster_list) == 1:
            return independent_cluster_list
        else:
            new_independent_cluster_dict = {}
            tempdruglist = []
            temppacklist = []
            indexlist = []
            for num,value in enumerate(independent_cluster_list):
                if num  not in found_cluster_list:
                    continue
                tempdruglist.append(independent_cluster_list[num]["drugs"])
                temppacklist.append(independent_cluster_list[num]["packs"])
                indexlist.append(num)
            new_independent_cluster_dict["drugs"] = tempdruglist
            new_independent_cluster_dict["packs"] = temppacklist
            new_independent_cluster_dict["drugs"] = set(more_itertools.collapse(new_independent_cluster_dict["drugs"]))
            new_independent_cluster_dict["packs"] = set(more_itertools.collapse(new_independent_cluster_dict["packs"]))
            new_independent_cluster_dict = new_independent_cluster_dict
            independent_cluster_list.append(new_independent_cluster_dict)
            templist_indpendent_list = []
            for index in indexlist:
                templist_indpendent_list.append(independent_cluster_list[index])
            for element in templist_indpendent_list:
                independent_cluster_list.remove(element)

            # print("new_independent_cluster_dictnew_independent_cluster_dict", independent_cluster_list)
            return independent_cluster_list
        pass

    def for_given_pack_return_list_of_drugs(self, pack):
        """
        For given pack it will return list of drugs which are present in given opack id.
        :param pack_id:
        :return:
        """
        return self.get_nonzero_colum_elements_for_given_row_element_from_data_frame(pack)

    def for_given_drug_return_list_of_packs(self, drug):
        """
        For given pack it will return list of drugs which are present in given opack id.
        :param drug:
        :return:
        """
        return self.get_nonzero_row_elements_for_given_column_element_from_data_frame(drug)


class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0


class TreeTrace:
    """
    This class will be requiring a tree in argument.
    It will trace the given tree and will find optimum cluster configuration.
    1) First we will define how to process given configuration. Configuration pertains to given list of nodes in particular trace of our tree.
    - For given configuration, we will make list of all possible combinations which can be formed.
    - For every possible combination we will calculate loss function.
    - We will append top n% combination into a list with their loss function.
    2) For opening tree we will decide different criterias.
    - We need to decide that will this criteria be specific to configuration or combination of configuration.

    TODO: Need some more clarity.
    TODO: Right now we will hard codedly open the tree and will make a method to process a configuration.
    TODO: After that our only concern will be to decide which node to open.
    """

    def __init__(self):
        self.balance_strategy_cluster_info_dict = {}
        self.balance_strategy_last_clusters_id = 0
        self.total_number_of_packs = -1
        self.minimum_loss_function = 10000
        self.result_with_minimum_loss_function = None
        self.debug_mode = False
        self.flag = True
        loss_counted = 0
        pass

    def tracing_tree(self,total_number_of_packs, tree_dict, cluster_info_dict,debug_mode, num_of_robots,row_element_list,added_canister_drug_id_list,df,column_element_list,split_function_id,total_packs,total_robots=None):
        """
        In this method we will trace out entire tree.
        :return:
        """
        self.total_packs = total_packs
        self.total_robots = total_robots
        self.minimum_loss_function = 10000
        self.total_pack_list = row_element_list
        self.unexplored_drugs_list = column_element_list
        self.added_canister_drug_id_list = added_canister_drug_id_list
        self.df = df
        self.total_number_of_packs = total_number_of_packs
        trace_array = [(0, -1)]
        degree_of_independence = -1
        while degree_of_independence < 5:
            configuration_list = []
            configuration_loss_result = []
            degree_of_independence += 1
            for node in trace_array:
                if len(tree_dict[node]) == 0:
                    # if split_function_id is None:
                    #     self.result_with_minimum_loss_function = self.algorithm_post_processing_v3_multi_robot(result_min_loss=self.result_with_minimum_loss_function,total_pack_list=self.total_pack_list,added_drug_id_list=self.added_canister_drug_id_list,num_of_robots=num_of_robots)
                    continue
                temp_trace_array = deepcopy(trace_array)
                temp_trace_array.remove(node)
                while len(tree_dict[node]) == 1 and len(tree_dict[tree_dict[node][0]]) != 0:
                    node = tree_dict[node][0]
                temp_trace_array.extend(tree_dict[node])
                configuration_list.append(temp_trace_array)
            logger.debug("####### LEVEL: {} #######".format(degree_of_independence))
            logger.debug("Total configurations at {} level: {}".format(degree_of_independence, len(configuration_list)))
            #print("Total configurations at this level: ",len(configuration_list))
            if len(configuration_list) == 0:
                logger.debug("configuration list is empty!")
                #print ("configuration list is empty: all configurations has been traversed")
                break
            for configuration in configuration_list:
                configuration_loss_result.append(self.multi_robot_balance_scale_algo(configuration, cluster_info_dict, num_of_robots,split_function_id))
            trace_array = configuration_list[np.argmin(configuration_loss_result)]
        # Logging the trace.
        append_dictionary_to_json_file(deepcopy(self.balance_strategy_cluster_info_dict), "balance_strategy_cluster_info_dict",
                                       save_json=False)



    def algorithm_post_processing_v3_multi_robot(self, result_min_loss, total_pack_list, added_drug_id_list, num_of_robots):
        """
        Fill manual and multiple drugs so as to balance the packs in each node according to number of robots
        :param result_min_loss: Best result returned from the previous
        :param total_pack_list:
        :param added_drug_id_list:
        :param robot_list:
        :return:
        """
        # Required if there is only one drug as input in IndependentClusterAnalysis
        dfu = DataFrameUtil(df=deepcopy(self.df))

        total_pack_list = set(total_pack_list)
        #print("Total Packs in POST PROCESSING", len(total_pack_list))
        remainder_pack_list = deepcopy(total_pack_list)

        '''
        Condition where there is only one distinct drug and other drugs have multiple canisters
        '''
        if result_min_loss is None and len(self.unexplored_drugs_list) == 1:
            result_min_loss = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_min_loss.append(cluster)

            result_min_loss[0]['drugs'] = set(self.unexplored_drugs_list)
            result_min_loss[0]['packs'] = list(dfu.column_element_info_dict[self.unexplored_drugs_list[0]])


        """
        Condition where we have multiple canisters for all the drugs.
        """
        if result_min_loss == None:
            result_min_loss = []
            for i in range(2):
                cluster = {}
                cluster['packs'] = []
                cluster['drugs'] = []
                result_min_loss.append(cluster)

        '''
        - added_drug_id_list will be different for both robots according to drug usage in pack distribution
        - We will add added_drug_id_list according to pack distribution for both clusters afterwards
        '''
        for cluster in result_min_loss:
            cluster["packs"] = set(cluster["packs"])
            cluster["drugs"] = set(list(cluster["drugs"]))
            remainder_pack_list = remainder_pack_list - cluster["packs"]

        logger.debug("Remainder Packs in post-processing {} {}".format(len(remainder_pack_list), remainder_pack_list))
        #print("REMAINDER PACKS:- ", len(remainder_pack_list))
        """
        for checking purpose:
        """
        common_packs = len(result_min_loss[0]['packs'] & result_min_loss[1]['packs'])
        packs0 = len(result_min_loss[0]['packs'])
        packs1 = len(result_min_loss[1]['packs'])

        if(len(total_pack_list) == (packs0 + packs1 - common_packs) + len(remainder_pack_list)):
            pack_diff = 0
        else:
            pack_diff = -1000


        """
        """
        remainder_pack_list = list(remainder_pack_list)
        total_pack_length = len(total_pack_list)
        split_count = math.ceil((1 / num_of_robots) * total_pack_length)

        sorted_result_min_loss = sorted(result_min_loss, key=lambda x: len(x['packs']), reverse=False)

        req_cluster0_packs = split_count
        req_cluster1_packs = total_pack_length - split_count

        cluster0_packlen = len(sorted_result_min_loss[0]['packs'])
        cluster1_packlen = len(sorted_result_min_loss[1]['packs'])
        cluster0_pack_diff = req_cluster0_packs - cluster0_packlen
        cluster1_pack_diff = req_cluster1_packs - cluster1_packlen

        if (len(remainder_pack_list) < cluster0_pack_diff):
            sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:cluster0_pack_diff] + list(sorted_result_min_loss[0]['packs']))
        elif (len(remainder_pack_list) < cluster1_pack_diff):
            sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[0:cluster1_pack_diff] + list(sorted_result_min_loss[1]['packs']))
        else:
            sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:cluster0_pack_diff] + list(sorted_result_min_loss[0]['packs']))
            sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[cluster0_pack_diff:cluster0_pack_diff + cluster1_pack_diff] + list(sorted_result_min_loss[1]['packs']))

            remainder_pack_list = remainder_pack_list[cluster0_pack_diff + cluster1_pack_diff:]
            remainder_split_count = math.ceil((1/num_of_robots) * len(remainder_pack_list))

            sorted_result_min_loss[0]['packs'] = set(list(remainder_pack_list)[0:remainder_split_count] + list(sorted_result_min_loss[0]['packs']))
            sorted_result_min_loss[1]['packs'] = set(list(remainder_pack_list)[remainder_split_count:] + list(sorted_result_min_loss[1]['packs']))


        '''
        remove drugs that are not required for the packs.
        i.e. after splitting into two clusters, if split individual df has a drug which is not used by any packs, then we simply remove drug
        '''

        cluster0_packs = sorted_result_min_loss[0]['packs']
        cluster1_packs = sorted_result_min_loss[1]['packs']

        # generate dataframes for manual drugs, to know which manual drug need to be added in the cluster
        # 1. keep the columns that are required
        df0 = self.df[list(added_drug_id_list)]
        df1 = self.df[list(added_drug_id_list)]

        # 2. keep only rows (packs) that are present in cluster packs
        df0 = df0.loc[cluster0_packs]
        df1 = df1.loc[cluster1_packs]
        # print("********** RUN ALGORITHM -----> MULTI-ROBOT POST-PROCESSING **********")
        # print("Shape of Manual drugs: df0:", df0.shape, "df1: ", df1.shape)
        df0 = df0.loc[:, (df0 != 0).any(axis=0)]
        df1 = df1.loc[:, (df1 != 0).any(axis=0)]

        #print("Shape of Manual drugs: df0:", df0.shape, "df1: ", df1.shape)
        cluster0_added_drug_id_list = list(df0)
        cluster1_added_drug_id_list = list(df1)
        logger.debug("In Multi-Robot Post-Processing...dataframe consisting of only manual drugs")
        logger.debug("manual drug + multiple canister dimensions :: df0: {}, df1: {}".format(df0.shape, df1.shape))

        '''
        add manual drugs and multiple canister drugs to each cluster according to usage of drug in that cluster packs
        i.e. the only drugs will be added which are being used within cluster packs(It will be not added if it is being used in another cluster packs)
        '''
        sorted_result_min_loss[0]['drugs'] = set(list(sorted_result_min_loss[0]['drugs']) + cluster0_added_drug_id_list)
        sorted_result_min_loss[1]['drugs'] = set(list(sorted_result_min_loss[1]['drugs']) + cluster1_added_drug_id_list)

        """
        Appending pack and drug length info in the cluster dictionary
        """
        for cluster in sorted_result_min_loss:
            cluster['pack_length'] = len(cluster['packs'])
            cluster['drug_length'] = len(cluster['drugs'])

        return sorted_result_min_loss

    def process_given_configuration_balance_the_scale_algo(self, configuration, cluster_info_dict, number_of_clusters =2, debug_mode = False):
        """
        This method will do following list of tasks.
        a) It will first divide given configurations as per the balanced scale algorithm in given number of clusters.
        b) It will find load difference between divided clusters.
           - It will be measured as per the following formula.
           Load difference = sigma[ (cluster_i - cluster_with_minimum number_of_packs) ]
        c) It will also find the total number of packs which are supposed to attend multiple robots.
        :param configuration:
        :param cluster_info_dict:
        :return: min(loss_value_for_combination)
        """
        """
        Prepraring robot_cluster_list
        which is a priority queue.
        """
        robot_cluster_list = PriorityQueue()
        for i in range(number_of_clusters):
            robot_cluster_list.push([], 0)
        """
        Preparing configuration priority queue.
        """
        configuration_priority_queue = PriorityQueue()
        for i in configuration:
            packs_for_given_pack = cluster_info_dict[i]["packs"]
            priority = -1*len(packs_for_given_pack)
            configuration_priority_queue.push(i, priority)
        """
        Algorithm of balancing the scale.
        """
        while not configuration_priority_queue.isEmpty():
            item, priority_for_item = configuration_priority_queue.pop()
            priority_for_item *= -1
            # print("item", item, "number of packs", priority_for_item)
            robot_cluster, priority_for_cluster = robot_cluster_list.pop()
            # print("robot cluster", robot_cluster, "number of packs", priority_for_cluster)
            robot_cluster.append(item)
            priority_for_cluster += priority_for_item
            robot_cluster_list.push(robot_cluster, priority_for_cluster)
            # print("whole list", robot_cluster_list.heap)
        """
        Saving data of balance scale algorithm
        """
        generated_cluster_data = []
        all_packs_addition = 0
        all_packs_legnth_list = []
        all_packs_set = set([])
        while not robot_cluster_list.isEmpty():
            item, number_of_packs = robot_cluster_list.pop()
            cluster = {"packs":set([]), "drugs":set([]), "nodes":[]}
            for i in item:
                packs = cluster_info_dict[i]["packs"]
                drugs = cluster_info_dict[i]["drugs"]
                cluster["nodes"].append(i)
                cluster["packs"].update(packs)
                cluster["drugs"].update(drugs)
            all_packs_addition += len(cluster["packs"])
            all_packs_legnth_list.append(len(cluster["packs"]))
            all_packs_set.update(set(cluster["packs"]))
            if debug_mode and self.debug_mode and True:
                print("cluster", cluster)
                print ("all packs addition", all_packs_addition)
                print ("all packs legnth list", all_packs_legnth_list)
                print ("all packs set", all_packs_set)
                input("check cluster")
            generated_cluster_data.append(cluster)
        if debug_mode and self.debug_mode and True:
            print ("generated_cluster_data", generated_cluster_data)
        daviation = np.std(all_packs_legnth_list)
        common_packs = all_packs_addition - len(all_packs_set)
        loss_counted = 0.5 * 2 * common_packs + 0.5 * daviation
        if debug_mode and self.debug_mode and True:
            print("generated cluster data", generated_cluster_data)
            print ("common packs", common_packs)
            print ("daviation", daviation)
            input("check all cluster together")
        self.balance_strategy_last_clusters_id += 1
        self.balance_strategy_cluster_info_dict[self.balance_strategy_last_clusters_id] = (generated_cluster_data, common_packs, daviation, configuration)

        if loss_counted < self.minimum_loss_function:
            self.minimum_loss_function = loss_counted
            self.result_with_minimum_loss_function = generated_cluster_data
        return loss_counted
        pass

    def multi_robot_balance_scale_algo(self, configuration, cluster_info_dict, num_of_robots,split_function_id):
        """

        :param configuration:
        :param cluster_info_dict:
        :param robot_list:
        :return:
        """

        total_packs = set()
        for node in configuration:
            total_packs.update(cluster_info_dict[node]['packs'])
        total_packs_length = len(total_packs)
        # print("########### TRACING TREE ----> BALANCING ALGO ############")
        # print("Total packs: (Before POST-PROCESSING)", total_packs_length)
        # print("ROBOTS: ", num_of_robots)

        split_ratio = math.ceil((1/num_of_robots)*total_packs_length)
        # required clusters pack counts
        req_min_packs_cluster_count = split_ratio
        req_max_packs_cluster_count = total_packs_length - split_ratio
        logger.debug("Required Pack-Distribution {} {}".format(req_min_packs_cluster_count, req_max_packs_cluster_count))
        #print("REQUIRED pack-distribution", req_min_packs_cluster_count, req_max_packs_cluster_count)
        configwise_packlen_list = []
        for node in configuration:
            configwise_packlen_list.append(len(cluster_info_dict[node]['packs']))

        sorted_packlen_list = sorted(configwise_packlen_list)[::-1]
        sorted_config_list = [x for _, x in sorted(zip(configwise_packlen_list, configuration))[::-1]]

        sorted_config_packlen_list = list(zip(sorted_config_list, sorted_packlen_list))
        temp_sorted_config_packlen_list = deepcopy(sorted_config_packlen_list)

        cluster0_config = []
        cluster1_config = []
        cluster0_sum = 0
        cluster1_sum = 0

        while(len(temp_sorted_config_packlen_list) != 0):
            node_tuple = temp_sorted_config_packlen_list.pop(0)
            temp_node = node_tuple[0]
            temp_packlen = node_tuple[1]

            if (cluster0_sum + temp_packlen <= req_min_packs_cluster_count):
                cluster0_config.append(temp_node)
                cluster0_sum = cluster0_sum + temp_packlen
            elif (cluster1_sum + temp_packlen <= req_max_packs_cluster_count):
                cluster1_config.append(temp_node)
                cluster1_sum = cluster1_sum + temp_packlen
            else:
                if(abs(req_min_packs_cluster_count - (cluster0_sum + temp_packlen)) <= abs(req_max_packs_cluster_count - (cluster1_sum + temp_packlen))):
                    cluster0_config.append(temp_node)
                    cluster0_sum = cluster0_sum + temp_packlen
                else:
                    cluster1_config.append(temp_node)
                    cluster1_sum = cluster1_sum + temp_packlen

        if self.total_robots == 1:
            cluster0_sum = split_ratio
            cluster1_config = []
            cluster1_sum = 0
            for node in sorted_config_packlen_list:
                cluster0_config.append(node[0])


        #assert req_min_packs_cluster_count + req_max_packs_cluster_count == cluster0_sum + cluster1_sum, "Sum error"
        assert cluster0_config != cluster1_config
        assert set(cluster0_config + cluster1_config) == set(sorted_config_list)

        """
        For debugging purpose
        """
        cluster0_packs = set()
        cluster1_packs = set()
        common_packs = set()
        for id in cluster0_config:
            for cluster_id, cluster in cluster_info_dict.items():
                if id == cluster_id:
                    cluster0_packs.update(cluster['packs'])

        for id in cluster1_config:
            for cluster_id, cluster in cluster_info_dict.items():
                if id == cluster_id:
                    cluster1_packs.update(cluster['packs'])

        common_packs = cluster0_packs & cluster1_packs

        logger.debug("Common Packs between clusters: {} {}".format(len(common_packs), common_packs))
        logger.info("Check: Total Packs {} :: C0-packs + C1-Packs - Common Packs {}".format(total_packs_length, cluster0_sum + cluster1_sum - len(common_packs)))
        #print("CHECK: Total packs :: c0 packs + c1 packs sum: ",total_packs_length, cluster0_sum + cluster1_sum)
        robot_cluster_list = [(cluster0_sum, cluster0_config), (cluster1_sum, cluster1_config)]
        # print("Optimum grouping of Clusters: ")
        # print("Total clusters in configuration: ", len(configuration))
        # print("C0: ", cluster0_sum, cluster0_config)
        # print("C1: ", cluster1_sum, cluster1_config)
        logger.debug("total clusters in config: {} {}".format(len(configuration), configuration))

        """
        Saving data of balance scale algorithm
        """
        generated_cluster_data = []
        all_packs_addition = 0
        all_packs_legnth_list = []
        all_packs_set = set([])
        while(len(robot_cluster_list)!= 0):
            number_of_packs, item = robot_cluster_list.pop()
            cluster = {"packs":set([]), "drugs":set([]), "nodes":[]}
            for i in item:
                packs = cluster_info_dict[i]["packs"]
                drugs = cluster_info_dict[i]["drugs"]
                cluster["nodes"].append(i)
                cluster["packs"].update(packs)
                cluster["drugs"].update(drugs)
            all_packs_addition += len(cluster["packs"])
            all_packs_legnth_list.append(len(cluster["packs"]))
            all_packs_set.update(set(cluster["packs"]))

            generated_cluster_data.append(cluster)

        #print("COMMON PACKS between CLUSTERS:-",len(generated_cluster_data[0]['packs'] & generated_cluster_data[1]['packs'] ))
        logger.debug("Common Packs between clusters {}".format(len(generated_cluster_data[0]['packs'] & generated_cluster_data[1]['packs'])))
        max_packlen = max(all_packs_legnth_list)
        min_packlen = min(all_packs_legnth_list)
        normalized_packlen_list = [max_packlen, min_packlen*(num_of_robots -1)]

        split_ratio = math.ceil((1 / num_of_robots) * len(self.total_packs))
        # required clusters pack counts
        req_min_packs_cluster_count = split_ratio
        req_max_packs_cluster_count = len(self.total_packs) - split_ratio

        remaining_packs = len(self.total_packs) - total_packs_length

        for i in range(1,remaining_packs+1):

            if (cluster0_sum + 1 <= req_min_packs_cluster_count):
                cluster0_sum = cluster0_sum + 1
            elif (cluster1_sum + 1 <= req_max_packs_cluster_count):
                cluster1_sum = cluster1_sum + 1
            else:
                if (abs(req_min_packs_cluster_count - (cluster0_sum + 1)) <= abs(
                        req_max_packs_cluster_count - (cluster1_sum + 1))):
                    cluster0_sum = cluster0_sum + 1
                else:
                    cluster1_sum = cluster1_sum + 1
        result_distribution = {}
        diff = abs(cluster1_sum-cluster0_sum)

        # loss_counted = 1.5*len(common_packs) + 1.25*max(cluster0_sum,cluster1_sum) + diff


        if split_function_id == 1:
            loss_counted = 10000000000
            if len(common_packs) == 0:
                split_tuple = (cluster0_sum,cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)


        elif split_function_id == 2:
            loss_counted = 10000000000
            if len(common_packs) <= 20 and len(common_packs) > 10:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)

        elif split_function_id == 3:
            loss_counted = 10000000000
            if len(common_packs) <= 30 and len(common_packs) > 20:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)

        elif split_function_id == 4:
            loss_counted = 10000000000
            if len(common_packs) <= 40 and len(common_packs) > 30:
                loss_counted = max(cluster0_sum,cluster1_sum)

        elif split_function_id == 5:
            loss_counted = 10000000000
            if len(common_packs) <= 50 and len(common_packs) > 40:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)

        elif split_function_id == 6:
            loss_counted = 10000000000
            if len(common_packs) <= 60 and len(common_packs) > 50:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)
        elif split_function_id == 7:
            loss_counted = 10000000000
            if len(common_packs) <= 80 and len(common_packs) > 60:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)
        elif split_function_id == 8:
            loss_counted = 10000000000
            if len(common_packs) <= 100 and len(common_packs) > 80:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)
        elif split_function_id == 9:
            loss_counted = 10000000000
            if len(common_packs) > 100:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)
        elif split_function_id == 10:
            loss_counted = 10000000000
            if len(common_packs) > 0 and len(common_packs) <= 10:
                split_tuple = (cluster0_sum, cluster1_sum)
                logger.info('In selected split id, The split is: {}'.format(split_tuple))
                loss_counted = max(cluster0_sum,cluster1_sum)
        else:
            split_tuple = (cluster0_sum, cluster1_sum)
            logger.info('No split selected, The split is: {}'.format(split_tuple))
            # loss_counted = 1.5*len(common_packs) + 1.25*max(cluster0_sum,cluster1_sum) + diff
            loss_counted = len(common_packs)
        # loss_counted = 10000000000
        deviation = np.std(normalized_packlen_list)
        # common_packs = all_packs_addition - len(all_packs_set)
        # #print("common_packs:--", common_packs)
        # if common_packs == 0:
        #     loss_counted = max(cluster0_sum, cluster1_sum)
        self.balance_strategy_last_clusters_id += 1
        self.balance_strategy_cluster_info_dict[self.balance_strategy_last_clusters_id] = (generated_cluster_data, common_packs, deviation, configuration)

        if loss_counted < self.minimum_loss_function:
            self.minimum_loss_function = loss_counted
            # if split_function_id is not None:
            self.result_with_minimum_loss_function = generated_cluster_data
            # else:
            #     self.result_with_minimum_loss_function = result_distribution
        # if loss_counted < self.minimum_loss_function:
        #     self.minimum_loss_function = loss_counted
        #     self.result_with_minimum_loss_function = generated_cluster_data
        #print("RESULT with MINIMUM LOSS: ", len(self.result_with_minimum_loss_function[0]['packs']), len(self.result_with_minimum_loss_function[1]['packs']))
        return loss_counted

    def process_given_combination(self, combination, cluster_info_dict):
        """
        This method will find loss function for given combination and return its value.
        :param combination:
        :return: loss_value
        """
        toptemplist = []
        for combination_part in combination:
            templist = []
            for node in combination_part:
                templist.append(cluster_info_dict[node]['packs'])
            toptemplist.append(len(list(more_itertools.collapse(templist))))

        # print("standard deviation loss funciton calculated value",self.loss_function_a(toptemplist))
        return self.loss_function_a(toptemplist)

    def loss_function_a(self, nums):
        """
        Loss function
        :return:
        """
        self.deviation = np.std(nums)
        return self.deviation
        pass


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (priority, a, item) = heapq.heappop(self.heap)
        return item, priority

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

