import logging
import os
import sys
from collections import OrderedDict, defaultdict
from copy import deepcopy
from itertools import product
import numpy as np

import settings
from src.dao.canister_recommendation_configuration_dao import get_configuration_for_recommendation, \
    get_total_column_and_row_from_pack_grid

logger = settings.logger


class RecommendDrops:
    """

    """

    def __init__(self, distribution_response, unique_matrix_list=[], unique_matrix_data_list=[]):
        self.distribution_response = distribution_response
        '''
        Variables to be used
        '''
        self.conf_to_id_dict = dict()
        self.quadrant_drugs = dict()
        self.pack_slot_drug = dict()
        self.pack_slot_id_mat = list()  # This will become array
        # self.valid_slot_quadrant = {1: {2, 3}, 2: {2, 3}, 3: {2, 3}, 4: {2, 3}, 5: {2, 3}, 6: {2, 3}, 7: {3},
        #                             8: {1, 2, 3, 4}, 9: {1, 2, 3, 4}, 10: {1, 2, 3, 4}, 11: {1, 2, 3, 4},
        #                             12: {1, 2, 3, 4}, 13: {1, 2, 3, 4}, 14: {3, 4}, 15: {1, 2, 3, 4}, 16: {1, 2, 3, 4},
        #                             17: {1, 2, 3, 4}, 18: {1, 2, 3, 4}, 19: {1, 2, 3, 4}, 20: {1, 2, 3, 4}, 21: {3, 4},
        #                             22: {1, 4}, 23: {1, 4}, 24: {1, 4}, 25: {1, 4}, 26: {1, 4}, 27: {1, 4}, 28: {4}}
        # self.valid_slot_quadrant = {1: {2}, 2: {2, 3}, 3: {2, 3}, 4: {2, 3}, 5: {2, 3}, 6: {2, 3}, 7: {2, 3}, 8: {3},
        #                             9: {1, 2}, 10: {1, 2, 3, 4}, 11: {1, 2, 3, 4}, 12: {1, 2, 3, 4}, 13: {1, 2, 3, 4},
        #                             14: {1, 2, 3, 4}, 15: {1, 2, 3, 4}, 16: {3, 4}, 17: {1, 2}, 18: {1, 2, 3, 4},
        #                             19: {1, 2, 3, 4}, 20: {1, 2, 3, 4}, 21: {1, 2, 3, 4}, 22: {1, 2, 3, 4},
        #                             23: {1, 2, 3, 4}, 24: {3, 4}, 25: {1}, 26: {1, 4}, 27: {1, 4}, 28: {1, 4},
        #                             29: {1, 4}, 30: {1, 4}, 31: {1, 4}, 32: {4}}

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

        self.pack_slot_drop_info_dict = dict()
        self.drop_slots_dict = dict()
        self.slot_drop_id_dict = dict()
        self.final_drops = list()
        self.pack_mat = list()  # This has info of slot quadrant. This is matrix.
        self.total_slots = list()
        self.pack_mat_final = {}
        self.selected_slot_quadrant = dict()
        self.reserved_slots = set()
        self.final_slot_group_independent_quad_slots = dict()
        self.final_slot_group_multiple_quad_slots = dict()
        self.edge_slots = list()
        self.drop_slots_dict = dict()
        self.slot_drop_id_dict = dict()
        self.drops = list()
        self.slot_conf_id_dict = dict()
        self.pack_slot_drop_info_dict = dict()
        self.unique_matrix_list = unique_matrix_list
        self.unique_matrix_data_list = unique_matrix_data_list

    def get_pack_fill_analysis(self):
        """

        @return:
        """
        logger.info("get_pack_fill_analysis")

        try:
            configuration_details = {1: {(1, 1), (2, 2), (3, 3), (4, 4)}, 2: {(1, 2), (4, 3)}, 3: {(1, 4), (2, 3)},
                                     4: {(2, 1), (3, 4)}, 5: {(4, 1), (3, 2)}, 6: {(1, 3)}, 7: {(2, 4)}, 8: {(3, 1)},
                                     9: {(4, 2)}}
            self.conf_to_id_dict = {}

            for con_id, details in configuration_details.items():
                for conf in details:
                    self.conf_to_id_dict[conf] = con_id

            self.pack_slot_drug = self.distribution_response['pack_slot_drug_dict']
            # for slot in self.pack_slot_drug[72738]:
            #     if slot % 2 == 0:
            #         self.pack_slot_drug[72738][slot].add('678770248##60293')
            self.quadrant_drugs = self.distribution_response['quadrant_drugs']
            self.pack_slot_drug_global = self.distribution_response['pack_slot_drug_dict_global']
            self.pack_slot_quad_dict = self.distribution_response['pack_slot_quad']

            reserved_packs = []
            pack_cluster = set()
            cluster_count = 0
            similar_pack_set_dict = {}
            pack_to_set_id_dict = {}
            logger.info("pack_slot_drug")
            for pack in self.pack_slot_drug:
                pack_cluster = set()
                if pack in reserved_packs:
                    continue
                pack_cluster.add(pack)
                reserved_packs.append(pack)
                cluster_count += 1
                pack_to_set_id_dict[pack] = cluster_count
                for pack1 in self.pack_slot_drug:
                    if pack == pack1 or pack1 in reserved_packs:
                        continue
                    if self.pack_slot_drug[pack] == self.pack_slot_drug[pack1]:
                        pack_cluster.add(pack1)
                        reserved_packs.append(pack1)
                        pack_to_set_id_dict[pack1] = cluster_count
                similar_pack_set_dict[cluster_count] = pack_cluster

            # pack_slot_id = [[22, 23, 24, 25, 26, 27, 28], [15, 16, 17, 18, 19, 20, 21], [8, 9, 10, 11, 12, 13, 14],
            #                 [1, 2, 3, 4, 5, 6, 7]]
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

            self.pack_slot_id_mat = np.array(pack_slot_id, dtype=object)
            self.pack_slot_id_mat = np.transpose(self.pack_slot_id_mat)

            pack_wise_time = {}
            self.pack_slot_drug_config_id_dict = {}
            self.pack_slot_drug_quad_id_dict = {}
            self.pack_origin_final_matrix = {}
            self.add_to_slot = dict()
            total_time = 0
            self.pack_slot_drop_info_dict = {}
            final_drop_slot_quad_info = {}
            final_slot_quadrant = {}
            matrix_pattern_data = {}
            self.pack_data = {}
            self.pack_slot_drop_info_dict_manual = {}
            column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
            logger.info("get_pack_fill_analysis pack_slot_drug_global")
            for pack, slot_drugs in self.pack_slot_drug_global.items():
                logger.info("get_pack_fill_analysis pack {}".format(pack))
                self.pack_slot_drug_config_id_dict[pack] = {}
                self.pack_slot_drug_quad_id_dict[pack] = {}
                self.drop_slots_dict = {}
                self.slot_drop_id_dict = {}
                self.final_drops = []
                self.selected_slot_quadrant = dict()
                self.reserved_slots = set()
                # self.pack_slot_drop_info_dict[pack] = {}
                self.total_slots = list(slot_drugs.keys())
                # self.pack_mat = np.empty((7, 4), dtype=object)
                self.pack_mat = np.empty((row, column), dtype=object)
                self.slot_quad_drugs = {}
                self.slot_quadrant_data = {}
                self.box_ids_to_use = {}

                """
                Check for similar pack if already processed or not
                """
                if len(similar_pack_set_dict[pack_to_set_id_dict[pack]] & set(self.pack_slot_drop_info_dict.keys())):
                    logger.info("get_pack_fill_analysis In similar packs")
                    processed_packs = similar_pack_set_dict[pack_to_set_id_dict[pack]] & set(
                        self.pack_slot_drop_info_dict.keys())
                    processed_pack = next(iter(processed_packs))
                    self.pack_slot_drop_info_dict[pack] = self.pack_slot_drop_info_dict[processed_pack]
                    self.pack_slot_drug_config_id_dict[pack] = self.pack_slot_drug_config_id_dict[processed_pack]
                    self.pack_slot_drug_quad_id_dict[pack] = self.pack_slot_drug_quad_id_dict[processed_pack]
                    self.pack_origin_final_matrix[pack] = self.pack_origin_final_matrix[processed_pack]
                    self.pack_slot_drop_info_dict_manual[pack] = self.pack_slot_drop_info_dict_manual[processed_pack]
                    pack_wise_time[pack] = pack_wise_time[processed_pack]
                    self.pack_data[str(pack)] = self.pack_data[str(processed_pack)]
                    total_time += pack_wise_time[pack]['time_in_sec.']
                    continue

                self.pack_slot_drop_info_dict[pack] = {}
                self.pack_slot_drop_info_dict_manual[pack] = {}
                self.pack_origin_final_matrix[pack] = {}
                # self.pack_data[pack] = {}

                for slot, drugs in self.pack_slot_drug[pack].items():
                    try:
                        '''
                        Function To get slot to quadrant mapping
                        '''
                        quadrant, slot_quadrant = self.get_slot_to_quad_mapping(slot, drugs)
                        self.pack_mat[self.pack_slot_id_mat == slot] = quadrant
                        self.slot_quadrant_data[slot] = quadrant
                    except Exception as e:
                        raise e
                for slot, drugs in slot_drugs.items():
                    if slot not in self.slot_quadrant_data:
                        self.pack_mat[self.pack_slot_id_mat == slot] = {self.pack_slot_quad_dict[pack][slot]}
                        self.slot_quadrant_data[slot] = {self.pack_slot_quad_dict[pack][slot]}
                '''
                static testing
                '''
                if settings.STATIC_V3:
                    self.get_static_data_for_testing()

                self.pack_origin_final_matrix[pack]['original'] = self.pack_mat
                if self.slot_quadrant_data in self.unique_matrix_list:
                    index = self.unique_matrix_list.index(self.slot_quadrant_data)
                    self.leaf_node_dict = self.unique_matrix_data_list[index]
                else:
                    self.unique_matrix_list.append(self.slot_quadrant_data)
                    self.leaf_node_dict = self.get_pack_with_possible_pattern_for_independent_slots()
                    self.unique_matrix_data_list.append(self.leaf_node_dict)

                # self.pack_mat_final, self.selected_slot_quadrant = self.get_slot_wise_selected_quadrants()
                '''
                See in test.py for temporary basis
                '''
                # box_id_add_dict,box_id_to_connected_box_dict,graph_box_ids_dicts = self.find_possible_graph_for_pattern()
                # self.make_tree(box_id_to_connected_box_dict,graph_box_ids_dicts)

                # slot_gruop_defined, slot_group_address, address_to_slots, self.reserved_slots = self.find_possible_patterns_for_indepandent_quadrants()
                min_drops = 29
                node_count = 0
                if len(self.leaf_node_dict) == 0:
                    logger.info("get_pack_fill_analysis In if condition")
                    self.selected_slot_quadrant = {}
                    self.pack_mat_final = deepcopy(self.pack_mat)
                    self.final_slot_group_independent_quad_slots = self.get_drop_data_for_independent_quad_slots(
                        slot_gruop_defined={},
                        slot_group_address={},
                        address_to_slots={})
                    logger.info("get_pack_fill_analysis can get from independent {}".format(
                        self.final_slot_group_independent_quad_slots))
                    self.final_slot_group_multiple_quad_slots = self.get_drop_data_for_multiple_quad_slots()
                    logger.info("get_pack_fill_analysis can get independent {}".format(
                        self.final_slot_group_multiple_quad_slots))
                    self.edge_slots = self.get_edge_slot_drops()
                    logger.info("can get edge slots {}".format(self.edge_slots))
                    self.drop_slots_dict, self.slot_drop_id_dict, drops = self.get_final_drop_details()
                    logger.info("get_pack_fill_analysis drops slots dict {}, {}".format(self.drop_slots_dict,
                                                                                        self.slot_drop_id_dict))
                    self.slot_conf_id_dict = self.get_configuration_id_for_edge_slots(pack, slot_drugs)
                    logger.info("get_pack_fill_analysis configrations {}".format(self.slot_conf_id_dict))
                    self.make_output_data_format(pack)
                    self.drops = drops
                    final_matrix = self.pack_mat_final
                    #     after adding this ask to meet for changes
                    self.pack_data[str(pack)] = {}
                    # self.pack_data[str(pack)]["initial_data"] = self.slot_quadrant_data
                    # self.pack_data[str(pack)]["box_data"] = self.pattern_id_slot_quad_dict
                    # self.pack_data[str(pack)]["available_slots"] = list(self.available_slots)
                    # self.pack_data[str(pack)]["used_box_data"] = self.box_ids_to_use
                    # self.pack_data[str(pack)]["total_drops"] = len(self.drops)
                    # self.pack_data[str(pack)]["drop_info"] = final_drop_slot_quad_info
                    # self.pack_data[str(pack)]["algo_output"] = final_slot_quadrant

                else:
                    logger.info("In else condition")
                    for id, pack_data in self.leaf_node_dict.items():
                        box_ids_to_use = self.get_box_ids_in_use(pack_data)
                        node_count += 1
                        self.selected_slot_quadrant = {}
                        self.pack_mat_final = deepcopy(pack_data['pack_mat'])
                        self.final_slot_group_independent_quad_slots = self.get_drop_data_for_independent_quad_slots(
                            slot_gruop_defined=deepcopy(pack_data['pattern_slot_group_dict']),
                            slot_group_address=deepcopy(pack_data['pattern_slot_group_address']),
                            address_to_slots=deepcopy(pack_data['add_to_slots']))
                        self.final_slot_group_multiple_quad_slots = self.get_drop_data_for_multiple_quad_slots()
                        self.edge_slots = self.get_edge_slot_drops()
                        self.drop_slots_dict, self.slot_drop_id_dict, drops = self.get_final_drop_details()
                        self.slot_conf_id_dict = self.get_configuration_id_for_edge_slots(pack, slot_drugs)
                        self.drop_slot_quad_info = self.get_drop_slot_quad_data()
                        logger.info("check drops")
                        if len(drops) < min_drops:
                            self.make_output_data_format(pack)
                            min_drops = len(drops)
                            self.drops = drops
                            self.box_ids_to_use = box_ids_to_use
                            final_matrix = self.pack_mat_final
                            final_slot_quadrant = deepcopy(self.selected_slot_quadrant)
                            final_drop_slot_quad_info = deepcopy(self.drop_slot_quad_info)

                        if node_count == settings.NODE_LIMIT:
                            break
                    logger.info("slot quad data")
                    for slot, quad in self.slot_quadrant_data.items():
                        self.slot_quadrant_data[slot] = list(quad)
                    # pack = str(pack)
                    self.pack_data[str(pack)] = {}
                    self.pack_data[str(pack)]["initial_data"] = self.slot_quadrant_data
                    self.pack_data[str(pack)]["box_data"] = self.pattern_id_slot_quad_dict
                    self.pack_data[str(pack)]["available_slots"] = list(self.available_slots)
                    self.pack_data[str(pack)]["used_box_data"] = self.box_ids_to_use
                    self.pack_data[str(pack)]["total_drops"] = len(self.drops)
                    self.pack_data[str(pack)]["drop_info"] = final_drop_slot_quad_info
                    self.pack_data[str(pack)]["algo_output"] = final_slot_quadrant
                logger.info("pack wise time")
                pack_wise_time[pack] = {'drops': self.drops, 'time_in_sec.': len(self.drops) * 10}
                total_time += pack_wise_time[pack]['time_in_sec.']
                self.pack_origin_final_matrix[pack]['final'] = final_matrix
                logger.info("final matrix")
            return self.pack_slot_drop_info_dict, self.pack_slot_drug_config_id_dict, self.pack_slot_drug_quad_id_dict, self.unique_matrix_list, self.unique_matrix_data_list, self.pack_data, self.pack_slot_drop_info_dict_manual
        except Exception as e:
            logger.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.info(
                f"Error in get_pack_fill_analysis: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
            raise e

    def get_drop_slot_quad_data(self):
        """

        @return:
        """
        drop_slot_quad_info = {}
        for drop_id, slots in self.drop_slots_dict.items():
            drop_slot_quad_info[drop_id] = {}
            for slot in slots:
                if slot in self.selected_slot_quadrant.keys():
                    drop_slot_quad_info[drop_id][slot] = self.selected_slot_quadrant[slot]
        return drop_slot_quad_info

    def get_box_ids_in_use(self, pack_data):
        """

        @param pack_data:
        @return:
        """
        box_ids_to_use = {}
        for pattern, slot_group_list in pack_data['pattern_slot_group_dict'].items():
            for slot_group in slot_group_list:
                for id, box_data in self.pattern_id_slot_quad_dict.items():
                    if set(box_data.keys()) == set(slot_group):
                        box_ids_to_use[id] = box_data
                        break
        return box_ids_to_use

    def find_subset_in_oring_of_slots(self, pattern2_array, remaining_pattern, pattern2):
        """
        This method will return true or false
        :return:
        """
        if (type(pattern2_array) != str):
            return pattern2_array.issubset(remaining_pattern), pattern2
        else:
            if '_' in pattern2_array:
                for i in pattern2_array.split('_'):
                    if '&' in i:
                        i = i.split('&')
                    i = {int(i)}
                    if i.issubset(remaining_pattern):
                        return True, str(i.pop())
            else:
                pattern2_array = {int(pattern2_array)}
                return pattern2_array.issubset(remaining_pattern), pattern2
        return False, pattern2

    def modify_group_dicts(self, slot_gruop_defined, slot_group_address, address_to_slots):
        """

        @param slot_gruop_defined:
        @param slot_group_address:
        @param address_to_slots:
        @return:
        """
        for row in range(len(self.pack_mat_final)):
            for col in range(len(self.pack_mat_final[row])):
                if type(self.pack_mat_final[row][col]) == set:
                    if self.pack_mat_final[row][col] is None or len(
                            self.pack_mat_final[row][col] & self.valid_slot_quadrant[
                                self.pack_slot_id_mat[row][col]]) == 0:
                        continue
                    data = self.pack_mat_final[row][col] & self.valid_slot_quadrant[self.pack_slot_id_mat[row][col]]
                    data = set(map(str, data))
                    data = '_'.join(data)
                    if ',' in data:
                        data = data.replace(' ', '')
                        data = data.replace('(', '')
                        data = data.replace(')', '')
                        data = data.replace(',', '&')
                    if data not in slot_gruop_defined:
                        slot_gruop_defined[data] = []
                    slot_gruop_defined[data].append({self.pack_slot_id_mat[row][col]})
                    if data not in slot_group_address:
                        slot_group_address[data] = []
                    slot_group_address[data].append([(row, col)])
                    address_to_slots[(row, col)] = {self.pack_slot_id_mat[row][col]}
                elif self.pack_mat_final[row][col] is not None:
                    self.selected_slot_quadrant[self.pack_slot_id_mat[row][col]] = self.pack_mat_final[row][col]
                self.add_to_slot[(row, col)] = self.pack_slot_id_mat[row][col]
        slot_gruop_defined_1 = OrderedDict()
        slot_group_address_1 = OrderedDict()
        # for slot_group in slot_gruop_defined:
        #     if type(slot_group) == tuple:
        #         slot_gruop_defined_1[slot_group] = slot_gruop_defined[slot_group]
        #         slot_group_address_1[slot_group] = slot_group_address[slot_group]
        for pattern in settings.SORTED_PATTERNS:
            if pattern in slot_gruop_defined:
                slot_gruop_defined_1[pattern] = slot_gruop_defined[pattern]
                slot_group_address_1[pattern] = slot_group_address[pattern]
        # slot_gruop_defined_1 = sorted(slot_gruop_defined_1, key=len,reverse=True)
        # slot_group_address_1 = sorted(slot_group_address_1, key=len,reverse=True)
        for slot_group in slot_gruop_defined:
            if slot_group not in slot_gruop_defined_1:
                slot_gruop_defined_1[slot_group] = slot_gruop_defined[slot_group]
                slot_group_address_1[slot_group] = slot_group_address[slot_group]
        slot_gruop_defined = slot_gruop_defined_1
        slot_group_address = slot_group_address_1
        return slot_gruop_defined, slot_group_address, address_to_slots

    def find_quad_with_best_match(self, ptrn_list, slot_group_address, address_to_slots, base_pattern):
        """

        @param ptrn_list:
        @param slot_group_address:
        @param address_to_slots:
        @param base_pattern:
        @return:
        """
        # TODO: Need optimization here
        slot_group_address_copy = deepcopy(slot_group_address)
        add_final_group_len = {}
        final_slot_group = []
        ptrn_list.sort()
        for ptrn in ptrn_list:
            cnt = 0
            slot_group_address = deepcopy(slot_group_address_copy)
            if type(ptrn) == str:
                pattern_set = {ptrn}
            else:
                pattern_set = set(ptrn)
            quadrant_array = set([1, 2, 3, 4])
            pattern_slot_groups = deepcopy(slot_group_address[base_pattern])

            # while len(slot_group_address[pattern]) > 0:
            for add in pattern_slot_groups:
                addition = set()
                set_to_remove = deepcopy(set(map(int, pattern_set)))
                group_set = set()
                group_set.update(address_to_slots[add[0]])

                for pattern2 in slot_group_address.keys():
                    pattern2_slot_groups = deepcopy(slot_group_address[pattern2])
                    set_to_remove.update(addition)
                    remaining_pattern = quadrant_array - set_to_remove

                    if type(pattern2) == int:
                        pattern2_set = set()
                        pattern2_set.add(pattern2)
                        pattern2_array = pattern2_set
                    else:
                        if type(pattern2) != str:
                            pattern2_array = set(pattern2)
                        else:
                            pattern2_array = pattern2

                    """
                    Skip if not slot group available for given pattern
                    """
                    if len(pattern2_slot_groups) == 0:
                        continue
                    if base_pattern == pattern2:
                        continue
                    """
                    Pattern2 should be subset of remaining quadrants
                    """
                    is_valid_match, pattern2_array = self.find_subset_in_oring_of_slots(pattern2_array,
                                                                                        remaining_pattern, base_pattern)
                    if not is_valid_match:
                        continue
                    # if not pattern2_array.issubset(remaining_pattern):
                    #     continue
                    min_distance = 1000
                    min_distance_slot = None
                    for slot_address in pattern2_slot_groups:
                        distance = self.find_distance_between_two_slot_group(add[0], slot_address[0])
                        if distance < min_distance:
                            min_distance = distance
                            min_distance_slot = slot_address
                    slot_group_address[pattern2].remove(min_distance_slot)
                    # slot_group_address_copy[pattern2_array].append(min_distance_slot)
                    if add in slot_group_address[base_pattern]:
                        slot_group_address[base_pattern].remove(add)
                        # slot_group_address_copy[pattern].remove(add)
                    group_set.update(set(address_to_slots[min_distance_slot[0]]))
                    group_set.update(set(address_to_slots[add[0]]))
                    if type(pattern2) == str:
                        addition.update({int(pattern2)})
                    else:
                        addition.update(set(pattern2))
                final_slot_group.append(group_set)
                if add[0] in add_final_group_len:
                    if cnt % 2 == 0:
                        add_final_group_len[add[0]] = ptrn
                        cnt += 1
                    else:
                        cnt += 1
                else:
                    add_final_group_len[add[0]] = ptrn
                    cnt += 1
        return add_final_group_len

    def finalize_group_dicts(self, slot_gruop_defined, slot_group_address, address_to_slots):
        """

        @param slot_gruop_defined:
        @param slot_group_address:
        @param address_to_slots:
        @return:
        """
        final_slot_group = []
        # slot_group_address = {(1, 2, 3, 4): [[(5, 2), (5, 3), (6, 3), (6, 2)], [(0, 1), (0, 2), (1, 2), (1, 1)],
        #                 [(2, 2), (2, 3), (3, 3), (3, 2)], [(4, 0), (4, 1), (5, 1), (5, 0)]],
        #  (3, 4, 1): [[(2, 1), (2, 0), (1, 0)]], (1, 2): [[(4, 2), (4, 3)]], (3, 4): [[(6, 1), (6, 0)],[(4,0),(4,1)]], '1_2': [[(0, 0)],[(5,0)]],
        #  '2_3': [[(0, 3)], [(1, 3)]], '1&2_3&4': [[(3, 0)], [(3, 1)],[(5,1)]]}
        # slot_gruop_defined = {(1, 2, 3, 4): [{7, 13, 6, 14}, {8, 9, 16, 15}, {3, 10, 11, 4}], (3, 4, 1): [{24, 17, 23}],
        #  (1, 2): [{12, 5},{26,19}], (3, 4): [{28, 21}], '1_2': [{22},{27}], '2_3': [{1}, {2}], '1&2_3&4': [{25}, {18},{20}]}

        slot_gruop_defined_copy = deepcopy(slot_gruop_defined)
        slot_group_address_copy = deepcopy(slot_group_address)
        if (1, 2, 3, 4) in slot_group_address:
            del slot_group_address[(1, 2, 3, 4)]
        for pattern in slot_group_address.keys():
            pattern_set = set(pattern)

            if type(pattern) == str:
                if '_' in pattern:
                    ptrn_list = pattern.split('_')
                    ptrn_list_new = []
                    for ptrn in ptrn_list[:]:
                        if '&' in ptrn:
                            ptrn = ptrn.split('&')
                            ptrn = tuple(map(int, ptrn))
                            ptrn_list_new.append(ptrn)
                    if len(ptrn_list_new):
                        ptrn_list = ptrn_list_new
                    # ptrn_list = list(map(int,ptrn))
                    add_pattern_dict = self.find_quad_with_best_match(ptrn_list, slot_group_address, address_to_slots,
                                                                      pattern)
                    for add, ptn in add_pattern_dict.items():
                        self.pack_mat_final[add[0]][add[1]] = int(ptn)
                        if ptn not in slot_gruop_defined_copy:
                            slot_group_address_copy[ptn] = []
                            slot_gruop_defined_copy[ptn] = []
                        slot_group_address_copy[ptn].append([add])
                        slot_group_address_copy[pattern].remove([add])
                        slot_gruop_defined_copy[ptn].append({self.pack_slot_id_mat[add[0]][add[1]]})
                        slot_gruop_defined_copy[pattern].remove({self.pack_slot_id_mat[add[0]][add[1]]})
                        address_to_slots[(add[0], add[1])] = {self.pack_slot_id_mat[add[0]][add[1]]}
                    del slot_group_address_copy[pattern]
                    del slot_gruop_defined_copy[pattern]
                    continue
                else:
                    pattern_set = {int(pattern)}
            """
            Initialise quadrant array
            """
            quadrant_array = set([1, 2, 3, 4])
            pattern_slot_groups = deepcopy(slot_group_address[pattern])
            # reserved = False

            # while len(slot_group_address[pattern]) > 0:
            for add in pattern_slot_groups:
                # reserved = False
                addition = set()
                set_to_remove = deepcopy(set(map(int, pattern_set)))
                group_set = set()
                group_set.update(address_to_slots[add[0]])

                for pattern2 in slot_group_address.keys():
                    pattern2_slot_groups = deepcopy(slot_group_address[pattern2])
                    set_to_remove.update(addition)
                    remaining_pattern = quadrant_array - set_to_remove

                    if type(pattern2) == int:
                        pattern2_set = set()
                        pattern2_set.add(pattern2)
                        pattern2_array = pattern2_set
                    else:
                        if type(pattern2) != str:
                            pattern2_array = set(pattern2)
                        else:
                            pattern2_array = pattern2

                    """
                    Skip if not slot group available for given pattern
                    """
                    if len(pattern2_slot_groups) == 0:
                        continue
                    """
                    Pattern2 should be subset of remaining quadrants
                    """
                    is_valid_match, pattern2_array = self.find_subset_in_oring_of_slots(pattern2_array,
                                                                                        remaining_pattern, pattern2)
                    if not is_valid_match:
                        continue
                    # if not pattern2_array.issubset(remaining_pattern):
                    #     continue
                    min_distance = 1000
                    min_distance_slot = None
                    for slot_address in pattern2_slot_groups:
                        distance = self.find_distance_between_two_slot_group(add[0], slot_address[0])
                        if distance < min_distance:
                            min_distance = distance
                            min_distance_slot = slot_address
                    slot_group_address[pattern2].remove(min_distance_slot)
                    if pattern2_array not in slot_group_address_copy:
                        slot_group_address_copy[pattern2_array] = []
                        slot_gruop_defined_copy[pattern2_array] = []
                    if min_distance_slot not in slot_group_address_copy[pattern2_array]:
                        slot_group_address_copy[pattern2_array].append(min_distance_slot)
                        slot_gruop_defined_copy[pattern2_array].append(
                            {self.pack_slot_id_mat[min_distance_slot[0][0]][min_distance_slot[0][1]]})
                    if add in slot_group_address[pattern]:
                        slot_group_address[pattern].remove(add)
                        # slot_group_address_copy[pattern].remove(add)
                        # slot_gruop_defined_copy[pattern].append(self.pack_slot_id_mat[add[0][0]][add[0][1]])
                        # address_to_slots[(add[0][0], add[0][1])] = {self.pack_slot_id_mat[add[0][0]][add[0][1]]}
                    group_set.update(set(address_to_slots[min_distance_slot[0]]))
                    group_set.update(set(address_to_slots[add[0]]))
                    # reserved = True
                    if type(pattern2) == str:
                        addition.update({int(pattern2_array)})
                    else:
                        addition.update(set(pattern2))
                final_slot_group.append(group_set)
        return slot_group_address_copy, slot_gruop_defined_copy, address_to_slots

    def get_drop_data_for_independent_quad_slots(self, slot_gruop_defined, slot_group_address, address_to_slots):
        """
        This function will give us drop slot groups for independent quad slots.
        :param slot_gruop_defined:
        :param slot_group_address:
        :param address_to_slots:
        :param reserved_slots:
        :return:
        """
        try:
            pattern2_array = []
            done_slots = []
            slot_gruop_defined, slot_group_address, address_to_slots = self.modify_group_dicts(slot_gruop_defined,
                                                                                               slot_group_address,
                                                                                               address_to_slots)
            for slots in slot_gruop_defined.values():
                for grp in slots:
                    self.reserved_slots.update(grp)

            slot_group_address, slot_gruop_defined, address_to_slots = self.finalize_group_dicts(slot_gruop_defined,
                                                                                                 slot_group_address,
                                                                                                 address_to_slots)
            final_slot_group = []
            selected_count = 0
            if (1, 2, 3, 4) in slot_gruop_defined and (1, 2, 3, 4) in slot_group_address:
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
                    set_to_remove = deepcopy(set(map(int, pattern_set)))
                    group_set = set()
                    group_set.update(address_to_slots[add[0]])

                    for pattern2 in slot_group_address.keys():
                        pattern2_slot_groups = deepcopy(slot_group_address[pattern2])
                        set_to_remove.update(addition)
                        remaining_pattern = quadrant_array - set_to_remove

                        if type(pattern2) == int:
                            pattern2_set = set()
                            pattern2_set.add(pattern2)
                            pattern2_array = pattern2_set
                        else:
                            if type(pattern2) != str:
                                pattern2_array = set(pattern2)
                            else:
                                pattern2_array = pattern2

                        """
                        Skip if not slot group available for given pattern
                        """
                        if len(pattern2_slot_groups) == 0:
                            continue
                        """
                        Pattern2 should be subset of remaining quadrants
                        """
                        is_valid_match, pattern2_array = self.find_subset_in_oring_of_slots(pattern2_array,
                                                                                            remaining_pattern, pattern2)
                        if not is_valid_match:
                            continue
                        # if not pattern2_array.issubset(remaining_pattern):
                        #     continue
                        min_distance = 1000
                        min_distance_slot = None
                        add_count = -1
                        for slot_address in pattern2_slot_groups:
                            distance = self.find_distance_between_two_slot_group(add[0], slot_address[0])
                            add_count += 1
                            if distance < min_distance:
                                min_distance = distance
                                min_distance_slot = slot_address
                                selected_count = add_count
                        # slot_group_address[pattern2].remove(min_distance_slot)
                        if add in slot_group_address[pattern]:
                            slot_group_address[pattern].remove(add)
                        if type(pattern) == str:
                            self.selected_slot_quadrant[next(iter(address_to_slots[add[0]]))] = int(pattern) if type(
                                pattern) == str else pattern
                            self.pack_mat_final[add[0][0]][add[0][1]] = int(
                                pattern) if type(pattern) == str else pattern
                        for i in range(len(pattern2_array)):
                            for slot in slot_gruop_defined[pattern2_array][selected_count]:
                                if int(slot) in done_slots:
                                    continue
                                # self.selected_slot_quadrant[self.pack_slot_id_mat[min_distance_slot[0][0]][
                                # min_distance_slot[0][1]]] = int(pattern2_array) if type(pattern2_array) == str else
                                # pattern2_array self.pack_mat_final[min_distance_slot[0][0]][min_distance_slot[0][
                                # 1]] = int(pattern2_array) if type(pattern2_array) == str else pattern2_array
                                self.selected_slot_quadrant[int(slot)] = int(pattern2_array) if type(
                                    pattern2_array) == str else pattern2_array[i]
                                self.pack_mat_final[slot_group_address[pattern2_array][selected_count][i][0]][
                                    slot_group_address[pattern2_array][selected_count][i][1]] = int(
                                    pattern2_array) if type(pattern2_array) == str else pattern2_array[i]
                                done_slots.append(int(slot))
                                break
                        group_set.update(set(address_to_slots[min_distance_slot[0]]))
                        group_set.update(set(address_to_slots[add[0]]))
                        slot_group_address[pattern2].remove(min_distance_slot)
                        slot_gruop_defined[pattern2].remove(slot_gruop_defined[pattern2_array][selected_count])
                        if type(pattern2) == str:
                            addition.update({int(pattern2)})
                        else:
                            addition.update(set(pattern2))
                    final_slot_group.append(group_set)
                    for slot in group_set:
                        if slot not in self.selected_slot_quadrant and len(group_set) == 1:
                            self.selected_slot_quadrant[slot] = int(pattern) if type(pattern) == str else pattern
                            self.pack_mat_final[add[0][0]][add[0][1]] = int(pattern) if type(
                                pattern) == str else pattern
            return final_slot_group
        except Exception as e:
            logger.info("Error in get_drop_data_for_independent_quad_slots")
            logger.info(e)

    def get_drop_data_for_multiple_quad_slots(self):
        """
        This function find pairs of slots for which drugs are to be dropped from multiple quadrant
        Here We are skipping edge slots for which quad are not lying in specific quads
        :return: This returns list of drop set of multiple quadrant slots.
        """

        total_quadrants = {1, 2, 3, 4}
        self.quad_slots = defaultdict(set)
        self.slot_quads = {}
        reserved_slot_multiple = set()
        group_set = set()
        all_slot_quadrants = []  # quadrant id tuple of slot for which are fille from multiple quadrants.
        not_consider_in_drop = []
        final_slot_group_multiple_quad_slots = []
        for slot_grp in self.final_slot_group_independent_quad_slots:
            if len(slot_grp) > 1:
                for slot in slot_grp:
                    reserved_slot_multiple.add(slot)

        try:
            column, row = get_total_column_and_row_from_pack_grid(column=True, row=True)
            # for i in range(7):
            for i in range(row):
                for j in range(column):
                    self.slot_quads[self.pack_slot_id_mat[i][j]] = self.pack_mat_final[i][j]
                    if type(self.pack_mat_final[i][j]) == set:
                        for quad in self.pack_mat_final[i][j]:
                            # TODO: Check out this for multiple cases
                            # quad = quad if type(quad) == tuple else tuple(self.pack_mat_final[i][j])
                            self.quad_slots[quad].add(self.pack_slot_id_mat[i][j])
                            quad = set(quad) if type(quad) == tuple else self.pack_mat_final[i][j]
                            all_slot_quadrants.append(quad)
                        # self.quad_slots[tuple(self.pack_mat_final[i][j])].add(self.pack_slot_id_mat[i][j])
                    else:
                        self.quad_slots[self.pack_mat_final[i][j]].add(self.pack_slot_id_mat[i][j])
                    # if self.pack_mat_final[i][j] is not None and type(self.pack_mat_final[i][j]) == set:
                    #     all_slot_quadrants.append(tuple(self.pack_mat_final[i][j]))

            for slot, quads in self.slot_quads.items():
                group_set = set()
                consider = 0
                considered_quads = set()
                if type(quads) == int or quads is None:
                    continue
                edge_slot = get_configuration_for_recommendation(edge_slot=True)
                if slot in edge_slot:
                    for qd in quads:
                        qad = set(qd) if type(qd) == tuple else quads
                        if qad == self.valid_slot_quadrant[slot]:
                            considered_quads.add(qd)
                            consider = 1
                    if not consider:
                        not_consider_in_drop.append(slot)
                        continue
                    self.slot_quads[slot] = considered_quads
                    self.pack_mat_final[self.pack_slot_id_mat == int(slot)] = considered_quads

            for slot, quads in self.slot_quads.items():
                if type(quads) == int or quads is None:
                    continue
                # todo check why empty coming
                if not len(quads):
                    continue
                if slot in reserved_slot_multiple or slot in not_consider_in_drop:
                    continue
                quads = list(quads)
                quads.sort()
                for slot_tpl in quads:
                    slot_set = quads if type(slot_tpl) == int else set(slot_tpl)
                    # rem_quad = tuple(total_quadrants - slot_set)
                    rem_quad = total_quadrants - slot_set
                    group_set.add(slot)
                    if rem_quad in all_slot_quadrants:
                        for slt in self.quad_slots[tuple(rem_quad) if len(rem_quad) > 1 else next(iter(rem_quad))]:
                            if slt in not_consider_in_drop or slt in reserved_slot_multiple:
                                continue
                            group_set.add(slt)
                            reserved_slot_multiple.add(slt)
                            self.reserved_slots.add(slt)
                            self.selected_slot_quadrant[slot] = slot_tpl
                            self.selected_slot_quadrant[slt] = tuple(rem_quad)
                            self.pack_mat_final[self.pack_slot_id_mat == int(slot)] = {slot_tpl}
                            self.pack_mat_final[self.pack_slot_id_mat == int(slt)] = {tuple(rem_quad)} if len(
                                rem_quad) > 1 else next(iter(rem_quad))
                            if {slt} in self.final_slot_group_independent_quad_slots:
                                self.final_slot_group_independent_quad_slots.remove({slt})
                            break
                self.reserved_slots.add(slot)
                reserved_slot_multiple.add(slot)
                if slot not in self.selected_slot_quadrant:
                    self.selected_slot_quadrant[slot] = quads[0]
                final_slot_group_multiple_quad_slots.append(group_set)
                group_set = set()
            return final_slot_group_multiple_quad_slots
        except Exception as e:
            logger.info("Error in get_drop_data_for_multiple_quad_slots")
            logger.info(e)

    def get_final_drop_details(self):
        """
        This function merges all drop data and make global dat of drops
        :return:
        """
        final_drops = []
        drop_slots_dict = {}
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

            return drop_slots_dict, slot_drop_id_dict, final_drops
        except Exception as e:
            logger.info("Error in get_final_drop_details")
            logger.info(e)

    def get_edge_slot_drops(self):
        """
        This function returns slot group for edge slots.
        :return: list of drop set for edge slots
        """
        edge_slot_drops_temp = set(self.total_slots) - self.reserved_slots
        edge_slot_drops_updated = list()
        drop_set = set()
        for slot in edge_slot_drops_temp:
            drop_set = set()
            if self.slot_quads[slot] is None:
                continue
            drop_set.add(slot)
            edge_slot_drops_updated.append(drop_set)
        return edge_slot_drops_updated

    def get_configuration_id_for_edge_slots(self, pack, slot_drugs):
        """
        This function provide us configuration id based on quadrants.
        This function is majorly for edge slots.

        group_slot_dict : It is grouping of edge slot which are binded with particular quadrants.
            1: {1, 2, 3, 4, 5, 6} = It is binded whith quadrant 2 and 3
            2: {7} = It is binded whith quadrant 3
            3: {14, 21} = It is binded whith quadrant 3 and 4
            4: {22, 23, 24, 25, 26, 27} = It is binded whith quadrant 1 and 4
            5: {28} = It is binded whith quadrant 4
        :return:slotid to configid dict
        """
        # group_slot_dict = {1: {1, 2, 3, 4, 5, 6}, 2: {7}, 3: {14, 21}, 4: {22, 23, 24, 25, 26, 27}, 5: {28}}
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
            for group_id, slots in group_slot_dict.items():
                for slot in slots:
                    slot_group_map[slot] = group_id

            slot_quad = deepcopy(self.slot_quads)
            for slot, quad in slot_quad.items():
                if quad is None or (type(quad) == set and len(quad) == 0):
                    del self.slot_quads[slot]
                    if {slot} in self.edge_slots:
                        slot = {slot}
                        self.edge_slots.remove(slot)

            slot_conf_details_dict = {}
            slot_conf_id_dict = {}

            # This dict denotes config mapping for above groups Ex: {small_hopper_quad:pf_tray_quad}
            # edge_slot_group_wise_conf_mapping = {1: {1: 2, 4: 3}, 2: {1: 3, 2: 3, 4: 3}, 3: {1: 3, 2: 4},
            #                                      4: {2: 1, 3: 4},
            #                                      5: {1: 4, 2: 4, 3: 4}}
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

            for slot in self.edge_slots:
                slot = next(iter(slot))
                quads = self.slot_quads[slot]
                """
                below changes solve the bug of mfd_recommendation
                >> this bug is similar to the bug of canister recommendation complete information regarding this
                   bug is provided in the optimised_drops_v3.py file at line 891.
                """
                if len(quads) > 1:
                    for combination in quads:
                        if type(combination) == tuple:
                            drugs = set()
                            for quad in combination:
                                drugs.update(self.slot_quad_drugs[slot][quad])

                            if drugs == slot_drugs[slot]:
                                quads = {combination}
                                break

                quads = next(iter(quads)) if type(next(iter(quads))) != int else quads
                slot_conf_details_dict[slot] = list()
                if type(quads) != int:
                    for quad in quads:
                        if quad not in edge_slot_group_wise_conf_mapping[slot_group_map[slot]]:
                            slot_conf_details_dict[slot].append((quad, quad))
                            # config_id.append(1)
                            continue
                        # slot_conf_details_dict[slot][quad] = 0
                        # slot_conf_details_dict[slot].update({quad:edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quad]})
                        slot_conf_details_dict[slot].append(
                            (quad, edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quad]))
                else:
                    # slot_conf_details_dict[slot][quads] = 0
                    # slot_conf_details_dict[slot].update(
                    #     {quads: edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quads]})
                    slot_conf_details_dict[slot].append(
                        (quads, edge_slot_group_wise_conf_mapping[slot_group_map[slot]][quads]))

            for slot in self.slot_quads:
                selected_quadrant = set()
                slot_conf_id_dict[slot] = set()
                if {slot} not in self.edge_slots:
                    slot_conf_id_dict[slot].add(1)
                    continue
                for conf in slot_conf_details_dict[slot]:
                    slot_conf_id_dict[slot].add(self.conf_to_id_dict[conf])
                    if len(slot_conf_details_dict[slot]) == 1:
                        self.selected_slot_quadrant[slot] = conf[0]
                        continue
                    if slot not in self.pack_slot_drug_config_id_dict[pack]:
                        self.pack_slot_drug_config_id_dict[pack][slot] = {}
                    if slot not in self.pack_slot_drug_quad_id_dict[pack]:
                        self.pack_slot_drug_quad_id_dict[pack][slot] = {}
                    for drug in self.slot_quad_drugs[slot][conf[0]]:
                        selected_quadrant.add(conf[0])
                        self.pack_slot_drug_config_id_dict[pack][slot][drug] = self.conf_to_id_dict[conf]
                        self.pack_slot_drug_quad_id_dict[pack][slot][drug] = conf[0]
                    self.selected_slot_quadrant[slot] = tuple(selected_quadrant)

            return slot_conf_id_dict
        except Exception as e:
            logger.info("Error in get_configuration_id_for_edge_slots")
            logger.info(e)

    def get_slot_wise_selected_quadrants(self):
        """
        We are selecting particular quadrant for particular slot.
        Whole quadrant selection logic is inside this function.
        # TODO: Need to Optimise this function.
        :return: This function returns matrix with selected quadrants and slot with selected quad dict
        """
        try:
            selected_slot_quadrant = {}
            pack_mat_final = self.pack_mat.copy()

            for i in range(len(self.pack_mat)):
                for j in range(len(self.pack_mat[i])):
                    selected_quadrant = self.pop_quadrant_for_slot(i, j)
                    if selected_quadrant == 0:
                        continue
                    selected_slot_quadrant[self.pack_slot_id_mat[i][j]] = selected_quadrant
                    if type(selected_quadrant) == int:
                        pack_mat_final[self.pack_slot_id_mat == self.pack_slot_id_mat[i][j]] = selected_quadrant
                    else:
                        pack_mat_final[self.pack_slot_id_mat == self.pack_slot_id_mat[i][j]] = set(selected_quadrant)
            return pack_mat_final, selected_slot_quadrant
        except Exception as e:
            logger.info("Error in get_slot_wise_selected_quadrants" + e)

    def pop_quadrant_for_slot(self, row, column):
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

    def find_possible_patterns_for_indepandent_quadrants(self):
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
        for pt in settings.PATTERNS:
            slot_gruop_defined[pt] = []
            slot_group_address[pt] = []
            single_slot_gruop_defined[pt] = []
            single_slot_group_address[pt] = []
        pattern_cnt = 0
        for pattern in settings.PATTERNS:
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] - 7] == 2 and 2 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] - 7]:  # 'q2':
                                    if quad_slots[self.pack_slot_id_mat[i][j] - 6] == 3 and 3 in \
                                            self.valid_slot_quadrant[
                                                self.pack_slot_id_mat[i][j] - 6]:  # 'q3':
                                        if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 4 and 4 in \
                                                self.valid_slot_quadrant[self.pack_slot_id_mat[i][j] + 1]:  # 'q4':
                                            if self.pack_slot_id_mat[i][j] in reserved_slots or \
                                                    self.pack_slot_id_mat[i][
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 3 and 3 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q3':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 7] == 4 and 4 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] + 7]:  # 'q4':
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 4 and 4 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] + 1]:  # 'q4':
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 2 and 2 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q2':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 1] == 3 and 3 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] + 1]:  # 'q3':
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 1 and 1 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q1':
                                if quad_slots[self.pack_slot_id_mat[i][j] - 6] == 3 and 3 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] - 6]:  # 'q3':
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == 2 and 2 in self.valid_slot_quadrant[
                                self.pack_slot_id_mat[i][j]]:  # 'q2':
                                if quad_slots[self.pack_slot_id_mat[i][j] + 8] == 4 and 4 in self.valid_slot_quadrant[
                                    self.pack_slot_id_mat[i][j] + 8]:  # 'q4':
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
                            if quad_slots[self.pack_slot_id_mat[i][j]] == pattern[0] and pattern[0] in \
                                    self.valid_slot_quadrant[self.pack_slot_id_mat[i][j]]:
                                if self.pack_slot_id_mat[i][j] in reserved_slots:
                                    continue
                                slots.add(self.pack_slot_id_mat[i][j])
                                reserved_slots = reserved_slots | slots
                                slot_gruop_defined[pattern].append(self.pack_slot_id_mat[i][j])
                                address = (i, j)
                                address_to_slots[address] = slots
                                slot_group_address[pattern].append(address)
            except Exception as e:
                logger.info("Error in finding possible combinations")
                logger.info(e)

            pattern_cnt += 1

        return slot_gruop_defined, slot_group_address, address_to_slots, reserved_slots

    def get_slot_to_quad_mapping(self, slot, drugs):
        """
        We will find the slot can be filled from which quadrant
        :param slot_id: slot_id
        :param drugs: drug_set
        :return: quadrant(independent or multiple),slot_quadrant_dict
        """
        try:
            logger.info("In get slot to quad mapping")
            slot_quadrant = dict()
            independent_quadrant = self.get_indepandent_quads(slot, drugs)
            if len(independent_quadrant) != 0:
                slot_quadrant[slot] = independent_quadrant
                return independent_quadrant, slot_quadrant
            else:
                self.get_quad_to_drugs_dict_for_slot(slot, drugs)
                possible_multi_quadrants = self.get_multiple_quads(slot, drugs)
                slot_quadrant[slot] = possible_multi_quadrants
                return possible_multi_quadrants, slot_quadrant

            pass

        except Exception as e:
            logger.error(e)
            return e

    def get_indepandent_quads(self, slot, drugs):
        """
        This function is to find slot which are to be filled from any one of the quadrant.
        :param slot: slot_id
        :param drugs: drugs set of that slot
        :return:
        """
        try:
            qd_count = 1
            drug_count = 0
            independant_quadrant = set()
            current_quadrant = 0
            while qd_count != 5:
                drug_count = 0
                for drug in drugs:
                    if qd_count in self.quadrant_drugs.keys():
                        if drug in self.quadrant_drugs[qd_count]['drugs']:
                            drug_count += 1
                if drug_count == len(drugs):
                    if qd_count in self.valid_slot_quadrant[slot]:
                        independant_quadrant.add(qd_count)
                        # We are adding this condition for now on temp base
                        # TODO: Need to optimise
                        # break
                    else:
                        current_quadrant = qd_count
                qd_count += 1
            if len(independant_quadrant) == 0 and current_quadrant != 0:
                independant_quadrant.add(current_quadrant)
            return independant_quadrant

        except Exception as e:
            logger.error(e)
            return e

    def get_quad_to_drugs_dict_for_slot(self, slot, drugs):
        """

        @param slot:
        @param drugs:
        """
        self.quad_to_drugs_dict = defaultdict(set)
        for quad in settings.TOTAL_QUADRANTS:
            self.quad_to_drugs_dict[quad] = set()
            for drug in drugs:
                if quad in self.quadrant_drugs.keys():
                    if drug in self.quadrant_drugs[quad]['drugs']:
                        self.quad_to_drugs_dict[quad].add(drug)
        pass

    def get_multiple_quads(self, slot, drugs):
        """
        This method is to find slots to be filled from multiple quadrants. And also find min no. of quadrants.
        :param slot:slot_id
        :param drugs:drug set
        :return: It returns set of tuples of quadrants. Ex:{(1,2),(1,4)}
        """
        possible_combinations = set()
        reserved = set()
        reserved_set = []

        '''
        Check for only if Two quadrants are required
        '''
        try:
            for qd in settings.TOTAL_QUADRANTS:
                for qd1 in settings.TOTAL_QUADRANTS:
                    if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1]) == len(drugs):
                        quad_list = (qd, qd1)
                        reserved = set()
                        if set(quad_list) in reserved_set:
                            continue
                        reserved_set.append(set(quad_list))
                        if slot not in self.slot_quad_drugs:
                            self.slot_quad_drugs[slot] = {}
                        self.slot_quad_drugs[slot][qd] = self.quad_to_drugs_dict[qd]
                        self.slot_quad_drugs[slot][qd1] = drugs - self.quad_to_drugs_dict[qd]
                        possible_combinations.add(quad_list)
                        '''
                        For now we are putting this for now
                        '''
                        # TODO: Need to optimise this
                        # return possible_combinations
                #         break
                #
                # else:
                #     continue
                # break

            if len(possible_combinations) != 0:
                return possible_combinations
            '''
            Check for if Three quadrants are required 
            '''
            for qd in settings.TOTAL_QUADRANTS:
                for qd1 in settings.TOTAL_QUADRANTS:
                    for qd2 in settings.TOTAL_QUADRANTS:
                        if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1] | self.quad_to_drugs_dict[
                            qd2]) == len(drugs):
                            reserved = set()
                            quad_list = (qd, qd1, qd2)
                            if set(quad_list) in reserved_set:
                                continue
                            reserved_set.append(set(quad_list))
                            if slot not in self.slot_quad_drugs:
                                self.slot_quad_drugs[slot] = {}
                            self.slot_quad_drugs[slot][qd] = self.quad_to_drugs_dict[qd]
                            reserved.update(self.quad_to_drugs_dict[qd])
                            self.slot_quad_drugs[slot][qd1] = (self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[
                                qd1]) - \
                                                              self.quad_to_drugs_dict[qd]
                            reserved.update(self.slot_quad_drugs[slot][qd1])
                            self.slot_quad_drugs[slot][qd2] = drugs - reserved
                            possible_combinations.add(quad_list)
                            '''
                            For now we are putting this for now
                            '''
                            # TODO: Need to optimise this
                            # return possible_combinations
                #             break
                #     else:
                #         continue
                #     break
                # else:
                #     continue
                # break

            if len(possible_combinations) != 0:
                return possible_combinations
            '''
            Check for all four quadrant required
            '''
            for qd in settings.TOTAL_QUADRANTS:
                for qd1 in settings.TOTAL_QUADRANTS:
                    for qd2 in settings.TOTAL_QUADRANTS:
                        for qd3 in settings.TOTAL_QUADRANTS:
                            if len(self.quad_to_drugs_dict[qd] | self.quad_to_drugs_dict[qd1] | self.quad_to_drugs_dict[
                                qd2] |
                                   self.quad_to_drugs_dict[qd3]) == len(drugs):
                                quad_list = (qd, qd1, qd2, qd3)
                                if slot not in self.slot_quad_drugs:
                                    self.slot_quad_drugs[slot] = {}
                                self.slot_quad_drugs[slot][qd] = self.quad_to_drugs_dict[qd]
                                reserved.update(self.quad_to_drugs_dict[qd])
                                self.slot_quad_drugs[slot][qd1] = (self.quad_to_drugs_dict[qd] |
                                                                   self.quad_to_drugs_dict[
                                                                       qd1]) - \
                                                                  self.quad_to_drugs_dict[qd]
                                reserved.update(self.quad_to_drugs_dict[qd1])
                                self.slot_quad_drugs[slot][qd2] = (self.quad_to_drugs_dict[qd] |
                                                                   self.quad_to_drugs_dict[
                                                                       qd1] | self.quad_to_drugs_dict[
                                                                       qd2]) - \
                                                                  reserved
                                reserved.update(self.quad_to_drugs_dict[qd2])
                                self.slot_quad_drugs[slot][qd3] = drugs - reserved
                                possible_combinations.add(quad_list)
                                return possible_combinations
                                '''
                                For now we are putting this for now
                                '''
                                # TODO: Need to optimise this
                                # return possible_combinations
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
            return possible_combinations

        except Exception as e:
            logger.error(e)

    def find_distance_between_two_slot_group(self, address, slot_address):
        """

        @param address:
        @param slot_address:
        @return:
        """
        distance = abs(address[0] - slot_address[0]) + abs(address[1] - slot_address[1])
        return distance

    def make_tree(self, box_id_to_connected_box_dict, box_id_slots_dict, graph_box_ids_dicts, box_id_add_dict, pattern,
                  pattern_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots, reserved_address=[],
                  leaf_node_dict={}):
        """
        This function will make an tree with different type of data at each level of tree
        :param box_id_to_connected_box_dict:
        :param graph_box_ids_dicts:
        :return:
        """

        independent_cluster_tree = {}
        leaf_nodes = {}
        leaf_nodes_list = []
        leaf_node_data_dict = {}
        pattern_slot_group_address_core = {}
        pattern_slot_group_dict_core = {}
        no_of_edges = []
        box_id_conn_len_dict = {}
        reserved_addresses_group_list = []
        cluster_info_dict = {}
        combination_add_dict = {}
        add_quad_dict = {}
        add_to_slots = {}
        add_quad_dict_core = {}
        add_to_slots_core = {}
        pattern_slot_group_address = {}
        pattern_slot_group_dict = {}
        no_of_children = 0
        copy_box_id_to_connected_box_dict = deepcopy(box_id_to_connected_box_dict)
        len_box_id_conn_dict = defaultdict(
            set)  # length of connection and for that length nodes of that len of connectivity
        qu = Queue()
        node_id = 0
        if len(leaf_node_dict):
            pattern_slot_group_address_core = leaf_node_dict['pattern_slot_group_address']
            pattern_slot_group_dict_core = leaf_node_dict['pattern_slot_group_dict']
            add_quad_dict_core = leaf_node_dict['add_quad_dict']
            add_to_slots_core = leaf_node_dict['add_to_slots']
        if len(box_id_to_connected_box_dict) == 0:
            # self.leaf_node_id+=1
            # leaf_node_data_dict[self.leaf_node_id] = {'pattern_slot_group_dict': pattern_slot_group_dict_core,
            #                                           'pattern_slot_group_address': pattern_slot_group_address_core,
            #                                           'add_quad_dict': add_quad_dict_core, 'add_to_slots': add_to_slots_core}
            return leaf_node_dict['leaf_nodes'], leaf_node_dict['reserved_addresses_group_list'], leaf_node_dict[
                'combination_wise_address'], leaf_node_dict["leaf_node_data_dict"]
        qu.push([box_id_to_connected_box_dict, -1, node_id])

        for id, boxes in box_id_to_connected_box_dict.items():
            box_id_conn_len_dict[id] = len(boxes)
            len_box_id_conn_dict[len(boxes)].add(id)

        level_nodes_dict = {}

        while not qu.isEmpty():
            parent = qu.pop()
            parent_connectivity = parent[0]
            parent_independence_degree = parent[1]
            parent_id = parent[2]
            # logger.info(parent_id)
            len_box_id_conn_dict = defaultdict(set)
            box_id_conn_len_dict = {}
            no_of_edges = []  # length of connected nodes of each node
            for lst in parent_connectivity.values():
                no_of_edges.append(len(lst))
            max_edge = max(no_of_edges)
            for id, boxes in parent_connectivity.items():
                box_id_conn_len_dict[id] = len(boxes)
                len_box_id_conn_dict[len(boxes)].add(id)

            independent_cluster_tree[parent_id, parent_independence_degree] = []

            if max_edge <= 1:
                '''
                This condition is for if we have all independent nodes on graph or connected graph with max no of edge is 1
                Then make child nodes with no of possibilities of combinations.
                This will be the last level of that particular parent
                '''
                grp_list = []
                final_grp_list = []
                reserved_grps = []
                for gr1, gr2 in parent_connectivity.items():
                    grp_list = []
                    grp_list.append(gr1)
                    grp_list.extend(gr2)
                    if len(set(grp_list) & set(reserved_grps)):
                        continue
                    reserved_grps.extend(grp_list)
                    final_grp_list.append(grp_list)
                final_nodes = list(product(*final_grp_list))
                final_nodes = list(set(final_nodes))
                # if len(final_nodes) == 1:
                #     final_nodes = [tuple(grp_list[0]),tuple(grp_list[1])]
                # leaf_nodes = []
                for combination in final_nodes:
                    associated_addresses = deepcopy(reserved_address)
                    node_id += 1
                    child_id = node_id
                    child_independence_degree = parent_independence_degree + 1
                    child = [combination, child_independence_degree, child_id]
                    independent_cluster_tree[parent_id, parent_independence_degree].append(
                        (child_id, child_independence_degree))
                    cluster_info_dict[(child_id, child_independence_degree)] = combination
                    combination = set(combination)
                    if combination in leaf_nodes_list:
                        continue
                    self.leaf_node_id += 1
                    leaf_nodes_list.append(combination)
                    leaf_nodes[self.leaf_node_id] = combination
                    pattern_slot_group_dict = deepcopy(pattern_slot_group_dict_core)
                    pattern_slot_group_address = deepcopy(pattern_slot_group_address_core)
                    add_quad_dict = deepcopy(add_quad_dict_core)
                    add_to_slots = deepcopy(add_to_slots_core)
                    for box_id in combination:
                        associated_addresses.extend(box_id_add_dict[box_id])
                        reserved_addresses_group_list.append(associated_addresses)
                        add_quad_dict.update(box_id_add_quad[box_id])
                        add_to_slots.update(box_id_add_slots[box_id])
                        for pattern_id, slots in box_id_slots_dict[box_id].items():
                            if pattern_dict[pattern][pattern_id] not in pattern_slot_group_dict:
                                pattern_slot_group_dict[pattern_dict[pattern][pattern_id]] = []
                            if slots not in pattern_slot_group_dict[pattern_dict[pattern][pattern_id]]:
                                pattern_slot_group_dict[pattern_dict[pattern][pattern_id]].append(slots)
                        for pattern_id, add in box_id_pattern_add_dict[box_id].items():
                            if pattern_dict[pattern][pattern_id] not in pattern_slot_group_address:
                                pattern_slot_group_address[pattern_dict[pattern][pattern_id]] = []
                            if add not in pattern_slot_group_address[pattern_dict[pattern][pattern_id]]:
                                pattern_slot_group_address[pattern_dict[pattern][pattern_id]].append(add)
                    combination_list = list(combination)
                    combination_list.sort()
                    combination_add_dict[tuple(combination_list)] = associated_addresses
                    leaf_node_data_dict[self.leaf_node_id] = {'pattern_slot_group_dict': pattern_slot_group_dict,
                                                              'pattern_slot_group_address': pattern_slot_group_address,
                                                              'add_quad_dict': add_quad_dict,
                                                              'add_to_slots': add_to_slots}

                continue
            # if parent_independence_degree == -1:
            #     '''
            #     This condition is for At the starting of Tree , We have to make children based on no. of graphs available with us.
            #     So at first level we have nodes as graphs possible with us.
            #     '''
            #     no_of_children = len(graph_box_ids_dicts)
            #     # no_of_children = len(len_box_id_conn_dict[max_edge])
            #     for i in range(no_of_children):
            #         child_independence_degree = parent_independence_degree + 1
            #         node_id += 1
            #         child_id = node_id
            #         new_box_id_to_connected_box_dict = {}
            #         for gr_id in graph_box_ids_dicts[i+1]:
            #             new_box_id_to_connected_box_dict[gr_id] = box_id_to_connected_box_dict[gr_id]
            #         child = [new_box_id_to_connected_box_dict, child_independence_degree, child_id]
            #         qu.push(child)
            #         independent_cluster_tree[(parent_id, parent_independence_degree)].append(
            #             (child_id, child_independence_degree))
            #         cluster_info_dict[(child_id, child_independence_degree)] = new_box_id_to_connected_box_dict
            else:
                '''
                This is the condition for intermidiate levels
                We find groups with max_edge and remove that group from everywhere and store data in child node for further level
                This level is fill for every group with max_edge.  
                '''
                for box_id in len_box_id_conn_dict[max_edge]:
                    if len(independent_cluster_tree[(parent_id, parent_independence_degree)]) >= 50:
                        break
                    child_independence_degree = parent_independence_degree + 1
                    if child_independence_degree not in level_nodes_dict:
                        level_nodes_dict[child_independence_degree] = []
                    if len(level_nodes_dict[child_independence_degree]) >= 50:
                        break
                    else:
                        level_nodes_dict[child_independence_degree].append((node_id, child_independence_degree))
                    node_id += 1
                    child_id = node_id
                    copy_parent_connectivity = deepcopy(parent_connectivity)
                    for k, v in parent_connectivity.items():
                        if k == box_id:
                            del copy_parent_connectivity[k]
                            continue
                        if box_id in v:
                            copy_parent_connectivity[k].remove(box_id)
                    child = [copy_parent_connectivity, child_independence_degree, child_id]
                    qu.push(child)
                    independent_cluster_tree[(parent_id, parent_independence_degree)].append(
                        (child_id, child_independence_degree))
                    cluster_info_dict[(child_id, child_independence_degree)] = copy_parent_connectivity
        return leaf_nodes, reserved_addresses_group_list, combination_add_dict, leaf_node_data_dict

    def find_possible_graph_for_pattern(self, pack_mat_final, pattern, pattern_dict, reserved_address=[],
                                        leaf_node_dict={}):
        """
        This function is to find no. of possible pattern(currently box) and connectivity between them.
        1) Find box to addresses associated between them.
        2) Find box connectivity as which box is connected to which box
        3) Find how many diff possible independent connection of boxes and form a group of those connections

        :param pack_mat_final:
        :return: all 3 dictionary - box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts
        """

        '''
        1)
        '''
        box_id_add_dict = {}
        data_list = []
        addr_list = []
        box_id_slots_dict = {}
        box_id_pattern_add_dict = {}
        box_id_add_slots = {}
        box_id_add_quad = {}
        add_quad_dict = {}
        add_to_slots = {}
        slots = set()
        box_id = 1
        if pattern == 'box':
            for row in range(len(pack_mat_final)):
                for col in range(len(pack_mat_final[row])):
                    data_list = []
                    addr_list = []
                    add_quad_dict = {}
                    add_to_slots = {}
                    slots = list()
                    if col + 1 < (len(pack_mat_final[row])) and row + 1 < len(pack_mat_final):
                        data_list.append(pack_mat_final[row][col])
                        slots.append(self.pack_slot_id_mat[row][col])
                        addr_list.append((row, col))
                        data_list.append(pack_mat_final[row][col + 1])
                        slots.append(self.pack_slot_id_mat[row][col + 1])
                        addr_list.append((row, col + 1))
                        data_list.append(pack_mat_final[row + 1][col + 1])
                        slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                        addr_list.append((row + 1, col + 1))
                        data_list.append(pack_mat_final[row + 1][col])
                        slots.append(self.pack_slot_id_mat[row + 1][col])
                        addr_list.append((row + 1, col))
                        if None in data_list:
                            continue
                        if (1, 2, 3, 4) in list(product(*data_list)):
                            box_id_add_dict[box_id] = addr_list
                            if box_id not in box_id_slots_dict:
                                box_id_slots_dict[box_id] = {}
                            if box_id not in box_id_add_slots:
                                box_id_add_slots[box_id] = {}
                            box_id_add_slots[box_id][addr_list[0]] = slots
                            box_id_slots_dict[box_id][1] = slots
                            if box_id not in box_id_pattern_add_dict:
                                box_id_pattern_add_dict[box_id] = {}
                            box_id_pattern_add_dict[box_id][1] = addr_list
                            for id, pattern_frmt in pattern_dict[pattern].items():
                                pattern_frmt = list(pattern_frmt)
                                if box_id not in box_id_add_quad:
                                    box_id_add_quad[box_id] = {}
                                for index, qd in enumerate(pattern_frmt):
                                    box_id_add_quad[box_id][addr_list[index]] = qd
                            box_id += 1

        elif pattern == 'triple':
            for pattern_id, pattern_format in pattern_dict[pattern].items():
                for row in range(len(pack_mat_final)):
                    for col in range(len(pack_mat_final[row])):
                        data_list = []
                        addr_list = []
                        slots = list()
                        if col + 1 < (len(pack_mat_final[row])) and row + 1 < len(pack_mat_final):
                            if pattern_id == 1:
                                data_list.append(pack_mat_final[row][col])
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                            if pattern_id == 2:
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                            if pattern_id == 3:
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                                data_list.append(pack_mat_final[row][col])
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                            if pattern_id == 4:
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                                data_list.append(pack_mat_final[row][col])
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                            # data_list.append(pack_mat_final[row + 1][col])
                            # addr_list.append((row + 1, col))
                            if None in data_list:
                                continue
                            if pattern_format in list(product(*data_list)):
                                box_id_add_dict[box_id] = addr_list
                                if box_id not in box_id_slots_dict:
                                    box_id_slots_dict[box_id] = {}
                                if box_id not in box_id_add_slots:
                                    box_id_add_slots[box_id] = {}
                                box_id_add_slots[box_id][addr_list[0]] = slots
                                box_id_slots_dict[box_id][pattern_id] = slots
                                if box_id not in box_id_pattern_add_dict:
                                    box_id_pattern_add_dict[box_id] = {}
                                box_id_pattern_add_dict[box_id][pattern_id] = addr_list
                                for id, pattern_frmt in pattern_dict[pattern].items():
                                    if pattern_frmt != pattern_format:
                                        continue
                                    pattern_frmt = list(pattern_frmt)
                                    if box_id not in box_id_add_quad:
                                        box_id_add_quad[box_id] = {}
                                    for index, qd in enumerate(pattern_frmt):
                                        box_id_add_quad[box_id][addr_list[index]] = qd
                                box_id += 1

        elif pattern == 'verti-hori':
            for pattern_id, pattern_format in pattern_dict[pattern].items():
                for row in range(len(pack_mat_final)):
                    for col in range(len(pack_mat_final[row])):
                        data_list = []
                        addr_list = []
                        slots = list()
                        if col + 1 < (len(pack_mat_final[row])) and row + 1 < len(pack_mat_final):
                            if pattern_id == 1:
                                data_list.append(pack_mat_final[row][col])
                                if len({} if pack_mat_final[row][col] is None else pack_mat_final[row][col] &
                                                                                   self.valid_slot_quadrant[
                                                                                       self.pack_slot_id_mat[row][
                                                                                           col]]) == 0 or \
                                        len({} if pack_mat_final[row][col + 1] is None else pack_mat_final[row][
                                                                                                col + 1] &
                                                                                            self.valid_slot_quadrant[
                                                                                                self.pack_slot_id_mat[
                                                                                                    row][
                                                                                                    col + 1]]) == 0:
                                    continue
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                            if pattern_id == 2:
                                if len({} if pack_mat_final[row + 1][col + 1] is None else pack_mat_final[row + 1][
                                                                                               col + 1] &
                                                                                           self.valid_slot_quadrant[
                                                                                               self.pack_slot_id_mat[
                                                                                                   row + 1][
                                                                                                   col + 1]]) == 0 or \
                                        len({} if pack_mat_final[row + 1][col] is None else pack_mat_final[row + 1][
                                                                                                col] &
                                                                                            self.valid_slot_quadrant[
                                                                                                self.pack_slot_id_mat[
                                                                                                    row + 1][
                                                                                                    col]]) == 0:
                                    continue
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                            if pattern_id == 3:
                                if len({} if pack_mat_final[row][col] is None else pack_mat_final[row][col] &
                                                                                   self.valid_slot_quadrant[
                                                                                       self.pack_slot_id_mat[row][
                                                                                           col]]) == 0 or \
                                        len({} if pack_mat_final[row + 1][col] is None else pack_mat_final[row + 1][
                                                                                                col] &
                                                                                            self.valid_slot_quadrant[
                                                                                                self.pack_slot_id_mat[
                                                                                                    row + 1][
                                                                                                    col]]) == 0:
                                    continue
                                data_list.append(pack_mat_final[row][col])
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                            if pattern_id == 4:
                                if len({} if pack_mat_final[row + 1][col + 1] is None else pack_mat_final[row + 1][
                                                                                               col + 1] &
                                                                                           self.valid_slot_quadrant[
                                                                                               self.pack_slot_id_mat[
                                                                                                   row + 1][
                                                                                                   col + 1]]) == 0 or \
                                        len({} if pack_mat_final[row][col + 1] is None else pack_mat_final[row][
                                                                                                col + 1] &
                                                                                            self.valid_slot_quadrant[
                                                                                                self.pack_slot_id_mat[
                                                                                                    row][
                                                                                                    col + 1]]) == 0:
                                    continue
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                            if None in data_list:
                                continue
                            if pattern_format in list(product(*data_list)):
                                box_id_add_dict[box_id] = addr_list
                                if box_id not in box_id_slots_dict:
                                    box_id_slots_dict[box_id] = {}
                                if box_id not in box_id_add_slots:
                                    box_id_add_slots[box_id] = {}
                                box_id_add_slots[box_id][addr_list[0]] = slots
                                box_id_slots_dict[box_id][pattern_id] = slots
                                if box_id not in box_id_pattern_add_dict:
                                    box_id_pattern_add_dict[box_id] = {}
                                box_id_pattern_add_dict[box_id][pattern_id] = addr_list
                                for id, pattern_frmt in pattern_dict[pattern].items():
                                    if pattern_frmt != pattern_format:
                                        continue
                                    pattern_frmt = list(pattern_frmt)
                                    if box_id not in box_id_add_quad:
                                        box_id_add_quad[box_id] = {}
                                    for index, qd in enumerate(pattern_frmt):
                                        box_id_add_quad[box_id][addr_list[index]] = qd
                                box_id += 1
        elif pattern == 'cross':
            for pattern_id, pattern_format in pattern_dict[pattern].items():
                for row in range(len(pack_mat_final)):
                    for col in range(len(pack_mat_final[row])):
                        data_list = []
                        addr_list = []
                        slots = list()
                        if col + 1 < (len(pack_mat_final[row])) and row + 1 < len(pack_mat_final):
                            if pattern_id == 1:
                                if len({} if pack_mat_final[row][col] is None else pack_mat_final[row][col] &
                                                                                   self.valid_slot_quadrant[
                                                                                       self.pack_slot_id_mat[row][
                                                                                           col]]) == 0 or \
                                        len({} if pack_mat_final[row + 1][col + 1] is None else pack_mat_final[row + 1][
                                                                                                    col + 1] &
                                                                                                self.valid_slot_quadrant[
                                                                                                    self.pack_slot_id_mat[
                                                                                                        row + 1][
                                                                                                        col + 1]]) == 0:
                                    continue
                                data_list.append(pack_mat_final[row][col])
                                slots.append(self.pack_slot_id_mat[row][col])
                                addr_list.append((row, col))
                                data_list.append(pack_mat_final[row + 1][col + 1])
                                slots.append(self.pack_slot_id_mat[row + 1][col + 1])
                                addr_list.append((row + 1, col + 1))
                            else:
                                if len({} if pack_mat_final[row + 1][col] is None else pack_mat_final[row + 1][col] &
                                                                                       self.valid_slot_quadrant[
                                                                                           self.pack_slot_id_mat[
                                                                                               row + 1][col]]) == 0 or \
                                        len({} if pack_mat_final[row][col + 1] is None else pack_mat_final[row][
                                                                                                col + 1] &
                                                                                            self.valid_slot_quadrant[
                                                                                                self.pack_slot_id_mat[
                                                                                                    row][
                                                                                                    col + 1]]) == 0:
                                    continue
                                data_list.append(pack_mat_final[row][col + 1])
                                slots.append(self.pack_slot_id_mat[row][col + 1])
                                addr_list.append((row, col + 1))
                                data_list.append(pack_mat_final[row + 1][col])
                                slots.append(self.pack_slot_id_mat[row + 1][col])
                                addr_list.append((row + 1, col))
                            # data_list.append(pack_mat_final[row + 1][col])
                            # addr_list.append((row + 1, col))
                            if None in data_list:
                                continue
                            if pattern_format in list(product(*data_list)):
                                box_id_add_dict[box_id] = addr_list
                                if box_id not in box_id_slots_dict:
                                    box_id_slots_dict[box_id] = {}
                                if box_id not in box_id_add_slots:
                                    box_id_add_slots[box_id] = {}
                                box_id_add_slots[box_id][addr_list[0]] = slots
                                box_id_slots_dict[box_id][pattern_id] = slots
                                if box_id not in box_id_pattern_add_dict:
                                    box_id_pattern_add_dict[box_id] = {}
                                box_id_pattern_add_dict[box_id][pattern_id] = addr_list
                                for id, pattern_frmt in pattern_dict[pattern].items():
                                    if pattern_frmt != pattern_format:
                                        continue
                                    pattern_frmt = list(pattern_frmt)
                                    if box_id not in box_id_add_quad:
                                        box_id_add_quad[box_id] = {}
                                    for index, qd in enumerate(pattern_frmt):
                                        box_id_add_quad[box_id][addr_list[index]] = qd
                                box_id += 1

        '''
        2)
        '''
        box_id_to_connected_box_dict = {}
        for box_id_outer, address_outer in box_id_add_dict.items():
            box_id_to_connected_box_dict[box_id_outer] = []
            for box_id_inner, address_inner in box_id_add_dict.items():
                if box_id_inner == box_id_outer:
                    continue
                if len(set(address_outer) & set(address_inner)):
                    box_id_to_connected_box_dict[box_id_outer].append(box_id_inner)

        '''
        3)
        '''

        graph_box_ids_dicts = defaultdict(set)
        graph_id = 0
        connected_box_list = []
        cluster_found = False
        total_boxes = set()
        for id, connected_box in box_id_to_connected_box_dict.items():
            cluster_found = False
            total_boxes = set()
            total_boxes.add(id)
            total_boxes.update(set(connected_box))
            for graph_id, groups in graph_box_ids_dicts.items():
                if len(total_boxes & groups):
                    graph_box_ids_dicts[graph_id].update(total_boxes)
                    cluster_found = True

            if not cluster_found:
                graph_id += 1
                graph_box_ids_dicts[graph_id].update(total_boxes)

        return box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts, box_id_slots_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots

    def get_matrix_with_reserved_address(self, pack_mat, reserved_address=[]):
        """

        @param pack_mat:
        @param reserved_address:
        @return:
        """
        pack_mat_reserved = deepcopy(pack_mat)
        for row in range(len(pack_mat)):
            for col in range(len(pack_mat[row])):
                if type(pack_mat[row][col]) == int:
                    pack_mat_reserved[row][col] = {pack_mat[row][col]}
                if (row, col) in reserved_address:
                    pack_mat_reserved[row][col] = None
        return pack_mat_reserved

    def process_pattern(self, pack_mat, pattern, pattern_dict, reserved_addresses_group_list, leaf_node_dict):
        """
        This function processes every pattern and find that pattern in pack matrix and make graph and tree according to it
        :param pack_mat: base pack matrix
        :param pattern: pattern to find
        :param pattern_dict: pattern name with details
        :param reserved_addresses_group_list: reserved addresses of matrix
        :return:
        """
        self.leaf_node_id = 0
        leaf_node_list = []
        leaf_node_id = 0
        leaf_node_dict = leaf_node_dict
        if len(reserved_addresses_group_list) == 0:
            pack_mat_reserved = self.get_matrix_with_reserved_address(pack_mat)
            box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts, box_id_slots_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots = self.find_possible_graph_for_pattern(
                pack_mat_reserved,
                pattern,
                pattern_dict)
            if len(box_id_add_dict) == 0:
                return leaf_node_dict
            leaf_nodes, reserved_group_with_addresses, combination_add_dict, leaf_node_data_dict = self.make_tree(
                box_id_to_connected_box_dict,
                box_id_slots_dict,
                graph_box_ids_dicts,
                box_id_add_dict, pattern,
                pattern_dict,
                box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots)
            # leaf_node_list.extend(leaf_nodes)
            if settings.V3_TEST:
                self.make_test_data(box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts,
                                    box_id_slots_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots)
            leaf_node_dict[leaf_node_id] = {'leaf_node_list': leaf_nodes, 'box_add_dict': box_id_add_dict,
                                            'combination_wise_address': combination_add_dict,
                                            'leaf_node_data_dict': leaf_node_data_dict}
        else:
            for reserved_address in reserved_addresses_group_list:
                leaf_node_list = []
                leaf_node_id += 1
                pack_mat_reserved = self.get_matrix_with_reserved_address(pack_mat, reserved_address)
                box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts, box_id_slots_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots = self.find_possible_graph_for_pattern(
                    pack_mat_reserved,
                    pattern,
                    pattern_dict, reserved_address=reserved_address, leaf_node_dict=leaf_node_dict[leaf_node_id])
                leaf_nodes, reserved_group_with_addresses, combination_add_dict, leaf_node_data_dict = self.make_tree(
                    box_id_to_connected_box_dict, box_id_slots_dict, graph_box_ids_dicts, box_id_add_dict, pattern,
                    pattern_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots,
                    reserved_address=reserved_address, leaf_node_dict=leaf_node_dict[leaf_node_id])
                # leaf_node_id += 1
                # leaf_node_list.extend(leaf_nodes)
                if settings.V3_TEST:
                    self.make_test_data(box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts,
                                        box_id_slots_dict, box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots)
                leaf_node_dict[leaf_node_id] = {'leaf_node_list': leaf_nodes, 'box_add_dict': box_id_add_dict,
                                                'combination_wise_address': combination_add_dict,
                                                'leaf_node_data_dict': leaf_node_data_dict}
        return leaf_node_dict

    def select_leaf_node_to_process(self, leaf_node_dict, pack_mat_copy):
        """

        @param leaf_node_dict:
        @param pack_mat_copy:
        @return:
        """
        reserved_addresses_group_list = []
        leaf_node_to_process = {}
        leaf_node_dict_updated = {}
        pack_mat_final = deepcopy(pack_mat_copy)
        add_quad_dict = {}
        add_to_slots = {}
        leaf_node_data_dict = {}
        combination_wise_address = {}
        leaf_node_to_process_copy = {}
        for id, leaf_node_data in leaf_node_dict.items():
            # reserved_addresses_group_list = []
            for node_id, leaf_node in leaf_node_data['leaf_node_data_dict'].items():
                pack_mat_final = deepcopy(pack_mat_copy)
                add_quad_dict = {}
                add_to_slots = {}
                # leaf_node_to_process = {}
                leaf_node_to_process_copy = {}
                leaf_node_copy = {}
                leaf_node_copy = deepcopy(leaf_node)
                leaf_node_data_dict = {}
                leaf_node_to_process[node_id] = leaf_node_data['leaf_node_list'][node_id]
                leaf_node_to_process_copy[node_id] = deepcopy(leaf_node_to_process[node_id])
                add_quad_dict.update(leaf_node['add_quad_dict'])
                add_to_slots.update(leaf_node['add_to_slots'])
                leaf_node_to_process_list = list(leaf_node_to_process[node_id])
                leaf_node_to_process_list.sort()
                for add, quad in add_quad_dict.items():
                    pack_mat_final[self.pack_slot_id_mat == self.pack_slot_id_mat[add[0]][add[1]]] = quad
                reserved_addresses_group_list.append(
                    leaf_node_data['combination_wise_address'][tuple(leaf_node_to_process_list)])
                core_id = len(reserved_addresses_group_list)
                leaf_node_data_dict[node_id] = leaf_node_copy
                combination_wise_address[tuple(leaf_node_to_process_list)] = leaf_node_data['combination_wise_address'][
                    tuple(leaf_node_to_process_list)]
                leaf_node_dict_updated[core_id] = {'leaf_nodes': leaf_node_to_process_copy,
                                                   'combination_wise_address': combination_wise_address,
                                                   'reserved_addresses_group_list': reserved_addresses_group_list,
                                                   'pattern_slot_group_dict':
                                                       leaf_node_data['leaf_node_data_dict'][node_id][
                                                           'pattern_slot_group_dict'], 'pattern_slot_group_address':
                                                       leaf_node_data['leaf_node_data_dict'][node_id][
                                                           'pattern_slot_group_address'],
                                                   'add_quad_dict': add_quad_dict, 'add_to_slots': add_to_slots,
                                                   'pack_mat': pack_mat_final,
                                                   "leaf_node_data_dict": leaf_node_data_dict}
            #     if len(leaf_node_to_process) >= 5:
            #         break
            # else:
            #     continue
            # break

        # for node in leaf_node_to_process:

        return reserved_addresses_group_list, leaf_node_to_process, leaf_node_dict_updated

    def get_pack_with_possible_pattern_for_independent_slots(self):
        """

        @return:
        """
        reserved_addresses_group_list = []
        pattern_data_dict = {}
        pattern_dict = {'box': {1: (1, 2, 3, 4)}, 'triple': {1: (1, 2, 3), 2: (2, 3, 4), 3: (3, 4, 1), 4: (4, 1, 2)},
                        'verti-hori': {1: (1, 2), 2: (3, 4), 3: (1, 4), 4: (2, 3)}, 'cross': {1: (1, 3), 2: (2, 4)}}
        leaf_node_dict = {}
        leaf_node_dict_updated = {}
        leaf_node_to_process = []
        pack_mat_copy = deepcopy(self.pack_mat)
        self.pattern_id_slot_quad_dict = {}
        self.pattern_count = 1
        self.unique_pattern_data_list = []
        self.available_slots = set()

        for pattern in settings.EVERY_PATTERN:
            leaf_node_dict = self.process_pattern(self.pack_mat, pattern, pattern_dict, reserved_addresses_group_list,
                                                  leaf_node_dict_updated)
            if len(leaf_node_dict) > 0:
                reserved_addresses_group_list, leaf_node_to_process, leaf_node_dict_updated = self.select_leaf_node_to_process(
                    leaf_node_dict, pack_mat_copy)
            pattern_data_dict[pattern] = {'leaf_node_core_dict': leaf_node_dict,
                                          'selected_leaf_nodes': leaf_node_to_process}
        return leaf_node_dict_updated

    def make_test_data(self, box_id_add_dict, box_id_to_connected_box_dict, graph_box_ids_dicts, box_id_slots_dict,
                       box_id_pattern_add_dict, box_id_add_quad, box_id_add_slots):
        '''
        This function makes data for testing purpose.
        :param leaf_node_dict:
        :param pack_mat_copy:
        :return:
        '''

        overlapping_boxes = []
        for box_id, connected_box in box_id_to_connected_box_dict.items():
            if len(connected_box) > 0:
                overlapping_boxes.append(box_id)

        for box_id, slots_data in box_id_slots_dict.items():
            if box_id not in overlapping_boxes:
                continue
            for patten_id, slots in slots_data.items():
                if set(slots) in self.unique_pattern_data_list:
                    continue
                self.unique_pattern_data_list.append(set(slots))
                self.available_slots.update(set(slots))
                addresses = box_id_add_dict[box_id]
                address_slot = dict(zip(addresses, slots))
                self.pattern_id_slot_quad_dict[self.pattern_count] = {}
                for add in address_slot:
                    self.pattern_id_slot_quad_dict[self.pattern_count][address_slot[add]] = box_id_add_quad[box_id][add]
                self.pattern_count += 1

        # for id,data in leaf_node_dict.items():
        #     for key,pattern_data in data['leaf_node_data_dict'].items():
        #         for pattern,slot_groups in pattern_data['pattern_slot_group_dict'].items():
        #             for slot_group in slot_groups:
        #                 if set(slot_group) in self.unique_pattern_data_list:
        #                     continue
        #                 self.unique_pattern_data_list.append(set(slot_group))
        #                 index = slot_groups.index(slot_group)
        #                 addresses = pattern_data['pattern_slot_group_address'][pattern][index]
        #                 address_slot = dict(zip(addresses,slot_group))
        #                 self.pattern_id_slot_quad_dict[self.pattern_count] = {}
        #                 for add in address_slot:
        #                     self.pattern_id_slot_quad_dict[self.pattern_count][address_slot[add]] = pattern_data['add_quad_dict'][add]
        #                 self.pattern_count += 1

    def make_output_data_format(self, pack):
        """
        This function makes output data format as required
        :param pack: pack_id
        :return:
        """
        try:
            for slot in self.total_slots:
                if slot in self.pack_slot_quad_dict[pack] and slot in self.selected_slot_quadrant.keys():
                    self.pack_slot_drop_info_dict_manual[pack][slot] = {'drop_number': self.slot_drop_id_dict[slot],
                                                                        'configuration_id': next(
                                                                            iter(self.slot_conf_id_dict[slot])),
                                                                        "quadrant": self.selected_slot_quadrant[slot]}
                    continue

                if slot in self.slot_conf_id_dict and slot in self.selected_slot_quadrant:
                    self.pack_slot_drop_info_dict[pack][slot] = {'drop_number': self.slot_drop_id_dict[slot],
                                                                 'configuration_id': self.slot_conf_id_dict[slot],
                                                                 "quadrant": self.selected_slot_quadrant[slot]}

        except Exception as e:
            logger.error("Error in make_output_data_format {}".format(e))
            raise e

    def get_static_data_for_testing(self):
        """
        This function prepares data for static testing for our ref.
        :return:
        """
        self.pack_mat = [['q1', 'q1', 'q4', 'q1', 'q1', 'q2', 'q4'], ['q4', 'q2', 'q1', 'q4', 'q2', 'q1', 'q3'],
                         ['q1', 'q2', 'q2', 'q3', 'q1', 'q4', 'q3'], ['q2', 'q3', 'q2', 'q3', 'q2', 'q3', 'q3']]
        self.pack_mat = [[1, 1, 4, 4, 1, 2, 4], [4, 2, 1, 3, 2, 1, 3],
                         [1, 2, 2, 3, 1, 4, 3], [2, 3, 2, 3, 2, 3, 3]]
        self.pack_mat = [[{1}, {(2, 3)}, {1}, {4}, {2}, {4}, {3}],
                         [{(1, 2)}, {(2, 3, 4)}, {(1, 3)}, {2}, {(1, 4)}, {3}, {1}],
                         [{1}, {(2, 4)}, {3}, {4}, {(2, 3, 4)}, {(1, 2, 3, 4)}, {2}],
                         [{(2, 4)}, {(2, 3)}, {2}, {2}, {2}, {3}, {1}]]
        self.pack_mat = [[{1}, {1, 4}, {4}, {4}, {1}, {1, 4}, {3, 4}],
                         [{1, 2}, {2, 3, 4}, {1, 3}, {4}, {1, 2, 4}, {2, 3, 4}, {1, 3}],
                         [{1, 2}, {3, 4}, {1, 3}, {3, 4}, {2, 1, 4}, {1, 2, 3, 4}, {4}],
                         [{2, 4}, {2}, {2}, {3}, {2}, {2}, {3}]]
        self.pack_mat = [[{1}, {(2, 3), (1, 2)}, {1}, {4}, {2}, {4}, {3}],
                         [{(1, 2)}, {(2, 3, 4)}, {(1, 3)}, {2}, {(1, 4)}, {3}, {1}],
                         [{1}, {(2, 4)}, {3}, {4}, {(2, 3, 4)}, {(1, 2, 3, 4)}, {2}],
                         [{(2, 4)}, {(2, 3)}, {2}, {2}, {2}, {3}, {1}]]
        self.pack_mat = [[None, None, None, None, None, None, None],
                         [{(1, 2)}, {(2, 3, 4)}, {(1, 3), (2, 3), (1, 4)}, {2}, {(1, 4)}, {3}, {1}],
                         [{1}, {(2, 4)}, {3}, {4}, {(2, 3, 4)}, {(1, 2, 3, 4)}, {2}],
                         [{(2, 4), (2, 3)}, {(2, 3)}, {2}, {2}, {2}, {3}, {1}]]
        self.pack_mat = [[None, None, None, None, None, None, None],
                         [{(1, 2)}, {(2, 3, 4)}, {(1, 3), (2, 3), (1, 4)}, {(1, 2)}, {(1, 4)}, {(1, 3, 4)}, {(3, 4)}],
                         [{(1, 4), (2, 3)}, {(2, 4)}, {(1, 2, 3)}, {(1, 2, 3), (2, 3, 4)}, {(2, 3, 4)}, {(1, 2, 3, 4)},
                          {(1, 2)}],
                         [{(2, 4), (2, 3)}, {(2, 3)}, {2}, {2}, {2}, {2}, {2}]]
        self.pack_mat = [[{(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}],
                         [{4}, {4}, {4}, {4}, {4}, {4}, {4}],
                         [{(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}],
                         [{4}, {4}, {4}, {4}, {4}, {4}, {4}]]
        self.pack_mat = [[{(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}],
                         [{1}, {4}, {1}, {(1, 4), (1, 3)}, {4}, {4}, {4}],
                         [{(1, 2, 3)}, {(2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}, {(1, 2, 3)}],
                         [{4}, {4}, {4}, {4}, {4}, {4}, {4}]]
        self.pack_mat = [[{1}, {1, 4}, {4}, {4}, {1}, {1, 4}, {3, 4}],
                         [{1, 2}, {2, 3, 4}, {1, 3}, {4}, {1, 2, 4}, {2, 3, 4}, {1, 3}],
                         [{1, 2}, {3, 4}, {1, 3}, {3, 4}, {2, 1, 4}, {1, 2, 3, 4}, {4}],
                         [{2, 4}, {2}, {2}, {3}, {2}, {2}, {3}]]
        self.pack_mat = np.array(self.pack_mat, dtype=object)
        self.pack_mat = np.transpose(self.pack_mat)
        # self.total_slots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
        #                     24, 25, 26, 27, 28]
        # self.total_slots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
        #                     26, 27, 28, 29, 30, 31, 32]

        # TODO : self.total_slots can get from databse
        self.total_slots = get_configuration_for_recommendation(total_slots=True)
        # max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).sclar()
        # self.total_slots = [i for i in range(1,max_slot+1)]


class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."

    def __init__(self):
        self.list = []

    def push(self, item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0, item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

# {1: {'drugs': {'317220537##44633', '763850104##4590', '435980166##27960', '005361064##3011', '009047591##1645', '683820116##21156', '458020650##18698', '678770248##60293', '005364046##2532', '678770223##21414', '710930132##13318', '009046751##16995', '009046457##3009', '763850105##4591', '683820080##3974', '683820114##21154'},
#      'combinations': [['009046457##3009'], ['763850104##4590'], ['005364046##2532', '435980166##27960'], ['627560797##4539'], ['763850105##4591'], ['009046751##16995'], ['683820116##21156', '763850105##4591', '683820114##21154'], ['115340165##2366', '005363790##64176'], ['435980166##27960'], ['683820079##3977', '678770248##60293'], ['005361064##3011', '678770223##21414'], ['317220537##44633'], ['678770223##21414'], ['710930132##13318'], ['009046751##16995', '763850104##4590'], ['005364046##2532', '763850105##4591'], ['763850105##4591', '005364046##2532'], ['683820114##21154'], ['009046457##3009', '678770223##21414'], ['005361064##3011'], ['005364046##2532'], ['683820080##3974', '458020650##18698'], ['009046457##3009', '005361064##3011', '678770223##21414'], ['009046457##3009', '678770223##21414', '009047591##1645'], ['627560798##4540'], ['683820116##21156'], ['009046457##3009', '005361064##3011'], ['501110434##46242', '627560797##4539'], ['009047591##1645']], 'slots': 0},
#  2: {'drugs': {'317220537##44633', '005361064##3011', '009047591##1645', '683820116##21156', '627560797##4539', '005364046##2532', '683820080##3974', '710930132##13318', '763850105##4591', '678770223##21414', '009046457##3009'},
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                'combinations': [['009046457##3009'], ['005364046##2532', '435980166##27960'], ['763850105##4591'], ['627560797##4539'], ['683820116##21156', '763850105##4591', '683820114##21154'], ['005361064##3011', '678770223##21414'], ['317220537##44633'], ['005364046##2532', '763850105##4591'], ['763850105##4591', '005364046##2532'], ['710930132##13318'], ['678770223##21414'], ['009046457##3009', '678770223##21414'], ['005361064##3011'], ['005364046##2532'], ['683820080##3974', '458020650##18698'], ['009046457##3009', '005361064##3011', '678770223##21414'], ['009046457##3009', '678770223##21414', '009047591##1645'], ['683820116##21156'], ['009046457##3009', '005361064##3011'], ['501110434##46242', '627560797##4539'], ['009047591##1645']], 'slots': 0}, 3: {'drugs': {'005361064##3011', '678770223##21414'}, 'combinations': [['005361064##3011', '678770223##21414'], ['678770223##21414'], ['009046457##3009', '005361064##3011', '678770223##21414'], ['009046457##3009', '678770223##21414', '009047591##1645'], ['009046457##3009', '678770223##21414'], ['009046457##3009', '005361064##3011'], ['005361064##3011']], 'slots': 0}, 4: {'drugs': {
#     '627560798##4540','005363790##64176'}, 'combinations': [], 'slots': 0}}
