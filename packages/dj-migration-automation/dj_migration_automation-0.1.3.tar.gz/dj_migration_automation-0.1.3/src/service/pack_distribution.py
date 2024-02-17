import collections
import datetime
import json
import math
from collections import OrderedDict, defaultdict
from copy import deepcopy

import pandas as pd
from peewee import IntegrityError, InternalError, DataError, fn, DoesNotExist

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_time
from dosepack.validation.validate import validate
from src import constants
from src.dao.batch_dao import get_system_wise_batch_id
from src.dao.canister_dao import get_alternate_canister_for_batch_data, validate_reserved_canisters, \
    db_get_canister_fndc_txr, get_zonewise_avilability_by_drug
from src.dao.canister_transfers_dao import db_canister_transfer_replace_canister, db_reserved_canister_replace_canister
from src.dao.device_manager_dao import get_robot_quad_can_capacity_batch_sch, get_disabled_locations_of_devices, \
    get_system_zone_mapping, db_get_robots_by_systems
from src.dao.drug_dao import get_active_alternate_drug_data
from src.dao.mfd_dao import get_batch_data
from src.dao.misc_dao import get_system_setting_by_system_id, get_company_setting_data_by_company_id, \
    get_system_setting_info, update_sequence_no_for_pre_processing_wizard
from src.dao.pack_analysis_dao import db_replace_canister, get_robot_status, get_pending_progress_pack_count
from src.dao.pack_dao import db_get_pack_details_batch_scheduling, db_get_pack_and_drug_by_patient, \
    db_get_half_pill_drug_drop_by_pack_id, get_extra_hours_dao, get_packs_by_facility_distribution_id, \
    get_patient_drug_alternate_flag_data, get_pack_slot_drug_data, get_batch_scheduled_start_date_and_packs, \
    get_pack_wise_delivery_date, db_get_pack_drugs_by_pack, get_original_drug_id, get_unscheduled_packs_dao, \
    get_packs_by_facility, save_distributed_packs_by_batch, save_distributed_packs_by_batch_v3, get_pack_slotwise_drugs
from src.dao.pack_distribution_dao import recommend_canister_to_register, get_pack_drug_slot_data, \
    get_pack_drug_slot_details, get_canister_data, create_dataset, get_pack_data_query, cr_analysis_fetch_data
from src.dao.patient_dao import get_patient_wise_delivery_date, get_patient_facility_id_data, \
    db_get_patient_name_from_patient_id_dao
from src.dao.reserve_canister_dao import db_delete_reserved_canister
from src.dao.zone_dao import get_zone_wise_system_ids, get_zone_wise_canister_drugs
from src.independentclusters import RecommendCanistersToTransfer, PriorityQueue
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_details import SlotDetails
from src.service.misc import update_timestamp_couch_db_pre_processing_wizard
from src.service.revert_batch import revert_batch_v3

logger = settings.logger


@log_args_and_response
@validate(required_fields=["batch_id", "devices"])
def delete_reserved_canister(batch_info):
    """
    Will delete entry for canisters for given robots
    This will make canister available for other systems.

    :param batch_info: dict
    :return: str
    """
    batch_id = batch_info["batch_id"]
    device_ids = batch_info["devices"]
    try:
        status = db_delete_reserved_canister(batch_id, device_ids)
        return create_response(status)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_alternate_canister_for_batch(batch_id, company_id,
                                     alt_in_robot=True,
                                     alt_available=True,
                                     ignore_reserve_status=False):
    try:
        results = get_alternate_canister_for_batch_data(
            company_id,
            alt_in_robot=alt_in_robot,
            alt_available=alt_available,
            ignore_reserve_status=ignore_reserve_status,
            skip_canisters=False
        )
        return create_response(results)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return e


@log_args_and_response
@validate(required_fields=['replace_canisters', 'batch_id', 'user_id', 'company_id'])
def update_pack_analysis_canisters(replace_canisters_info):
    try:
        replace_canisters = replace_canisters_info['replace_canisters']
        batch_id = replace_canisters_info['batch_id']
        user_id = replace_canisters_info['user_id']
        valid_canisters = validate_reserved_canisters(list(replace_canisters.values()))
        if not valid_canisters:
            return error(1020, "One of the alternate canister is already reserved.")
        logger.info('Replacing Pack Analysis Canister for batch_id {}, user_id {} - '
                    'replace_canisters: {}'.format(batch_id, user_id, replace_canisters))
        with db.transaction():
            for canister_id, alt_canister_id in replace_canisters.items():
                # CanisterTransfers.db_replace_canister(batch_id, canister_id, alt_canister_id)
                db_canister_transfer_replace_canister(batch_id=batch_id, canister_id=canister_id,
                                                      alt_canister_id=alt_canister_id)

                db_replace_canister(batch_id, canister_id, alt_canister_id)
                # ReservedCanister.db_replace_canister(batch_id, canister_id, alt_canister_id)
                db_reserved_canister_replace_canister(canister_id=canister_id,
                                                      alt_canister_id=alt_canister_id)
        return create_response(True)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


class MultiBatchRecommender:

    def __init__(self, split_info, patient_fill_schedule_date_dict, patient_packs, date_pack_count_dict,
                 automatic_system_region_wise_date_capacity_dict, manual_system_region_wise_date_capacity_dict,
                 pack_delivery_date_dict, pack_schedule_date_dict, pack_drugs, canister_drugs, company_id, system_id,
                 system_info, system_end_date,patient_drugs,zone_id,drug_alternate_drug_dict,pack_slot_drug_dict,
                 unique_drugs=None, sorted_patient_list=None):
        if settings.FACILITY_WISE:
            self.automatic_system_packs = split_info['automatic_system_facilities']
        else:
            self.automatic_system_packs = split_info['automatic_system_patients']
        self.manual_system_packs = {}  # split_info['manual_system_patients']
        self.system_end_date = system_end_date
        self.system_timings = system_info
        self.patient_fill_schedule_date_dict = patient_fill_schedule_date_dict
        self.patient_packs = patient_packs
        self.date_pack_count_dict = date_pack_count_dict
        self.automatic_system_region_wise_date_capacity_dict = automatic_system_region_wise_date_capacity_dict
        self.manual_system_region_wise_date_capacity_dict = manual_system_region_wise_date_capacity_dict
        self.pack_delivery_date_dict = pack_delivery_date_dict
        self.pack_schedule_date_dict = pack_schedule_date_dict
        # self.previous_batch_drugs = previous_batch_drugs
        self.pack_drugs = pack_drugs
        self.canister_drugs = canister_drugs
        self.company_id = company_id
        self.system_id = system_id
        self.patient_drugs = patient_drugs
        self.zone_id = zone_id
        self.drug_alternate_drug_dict = drug_alternate_drug_dict
        self.pack_slot_drug_dict = pack_slot_drug_dict
        self.sorted_patient_list= sorted_patient_list

        """
        Variables for region in inspection
        """
        self.region_in_inspection_start_date = None
        self.region_in_inspection_end_date = None
        self.is_change_in_region_in_inspection = None
        self.region_remaining_packs_capacity = None
        self.own_region_packs = None
        self.batch_date = ''
        self.batch_split = {}
        self.system_packs = list()
        self.pack_patient = dict()
        self.region_filling_count_dict = {}
        self.region_change_index = 0
        self.distributed_pack_count = {}
        self.distributed_pack_id = {}
        self.batch_start_date_dict = {}
        self.batch_processing_time_dict = {}
        self.batch_processing_time = {}
        self.multi_batch_info_dict = OrderedDict()
        self.multi_batch_info_dict_with_details = OrderedDict()
        self.id = 1
        self.batch_count = 1
        self.last_batch_pack_count = 0
        self.batch_canister_drugs = set()
        self.batch_manual_drugs = set()
        self.manual_slots = []
        self.total_batch_slots = []
        self.batch_analysis_data = {}
        # self.pack_slot_drug_dict = {}
        self.pack_canister_drugs = set()
        self.unique_drugs = unique_drugs
        self.batch_cut = False

    # def over_loaded_packs_temp(self):
    #     packs = [17450, 17461, 17468, 17469, 17470, 17471, 17472, 17473, 17475, 17478, 17480, 17481, 17483, 17484, 17485, 17486, 17487, 17488, 17489, 17491, 17492, 17493, 17494, 17495, 17496, 17497, 17498, 17500]
    #     over_loaded_pack_dict = {}
    #     over_all_dict = {}
    #     over_loaded_pack_dict["Overloaded_packs"] = []
    #
    #     for pack_id in packs:
    #         pack_info = get_pack_details_dao(
    #             pack_id, robot_id=None, system_id=2)
    #
    #         over_loaded_pack_dict["Overloaded_packs"].append(pack_info)
    #     over_all_dict["over_loaded_packs"] = {}
    #     over_all_dict["over_loaded_packs"][2] = over_loaded_pack_dict
    #     return over_loaded_pack_dict

    # def temp_fun_for_manual_system(self):
    #     manual_system_distribution = {}
    #     manual_system_distribution_with_details = {}
    #     over_all_dict = {}
    #     count = 1
    #     manual_packs = [18011, 18012, 18014, 18015, 18016, 18017, 18019, 18020, 18021, 18024, 18027, 18028, 18029, 18030, 18035, 18037, 18038, 18039, 18042, 18043, 18045, 18047, 18048, 18049, 18050, 18051, 18052, 18053, 18054, 18055, 18096, 18097, 18098, 18102, 18103, 18105, 18108, 18109, 18112, 18113, 18114, 18116, 18119, 18121, 18122, 18124, 18125, 18127, 18130, 18131, 18132, 18133, 18134, 18136, 18137, 18138, 18140, 18141, 18143, 18144, 18145, 18147, 18149, 18152, 18153, 18156, 18158, 18160, 18163, 18165, 18166, 18167, 18170, 18173, 18174, 18178, 18179, 18181, 18182, 18184, 18186, 18187, 18189, 18190, 18191, 18193, 18194, 18196, 18197, 18198, 18201, 18202, 18203, 18204, 18206, 18207, 18209, 18210, 18212, 18213, 18214, 18215, 18216, 18217, 18218, 18219, 18220, 18221, 18222, 18223, 18224, 18225, 18226, 18227, 18228, 18229, 18230, 18231, 18277, 18279, 18280, 18281, 18283, 18286, 18287, 18288, 18289, 18292, 18293, 18297, 18298, 18300, 18301, 18302, 18304, 18305, 18308, 18309, 18311, 18313, 18315, 18316, 18317, 18319, 18321, 18323, 18325, 18326, 18328, 18329, 18331, 18332, 18333, 18334, 18335, 18337, 18339, 18340, 18341, 18342, 18343, 18344, 18345, 18347, 18349, 18350, 18351, 18352, 18353, 18356, 18357, 18358, 18359, 18360, 18361, 18363, 18364, 18365, 18367, 18368, 18370, 18371, 18372, 18373, 18375, 18376, 18377, 18378, 18380, 18381, 18384, 18391, 18392, 18393, 18395, 18396, 18397, 18399, 18400, 18401, 18404, 18405, 18406, 18409, 18410, 18417, 18418, 18419, 18420, 18425, 18426, 18427, 18428, 18433, 18434, 18435, 18437, 18438, 18441, 18442, 18443, 18444, 18445, 18446, 18447, 18448, 18449, 18450, 18451, 18454, 18455, 18456, 18457, 18459, 18463, 18464, 18465, 18466, 18468, 18472, 18473, 18474, 18475, 18476, 18481, 18482, 18483, 18484, 18486, 18487, 18489, 18490, 18491, 18494, 18495, 18498, 18499, 18501, 18503, 18504, 18507, 18508, 18509, 18510, 18534, 18549, 18556, 18560, 18562, 18564, 18565, 18566, 18567, 18570, 18571, 18572, 18574, 18575, 18577, 18578, 18579, 18580, 18581, 18582, 18583, 18584, 18585, 18586, 18587, 18589, 18590, 18591, 18592, 18593, 18594, 18595, 18596, 18598, 18599, 18600, 18601]
    #
    #     for date in self.total_schedule_dates:
    #         if date not in manual_system_distribution:
    #             manual_system_distribution["Manual_system" + "  " + date] = []
    #             # count+=1
    #         for pack in manual_packs:
    #             if count % 15 == 0:
    #                 for pack_id in manual_system_distribution["Manual_system" + "  " + date]:
    #                     pack_info = get_pack_details_dao(
    #                         pack_id, robot_id=None, system_id=2)
    #                     if "Manual_system" + "  " + date not in manual_system_distribution_with_details:
    #                         manual_system_distribution_with_details["Manual_system" + "  " + date] = []
    #                     manual_system_distribution_with_details["Manual_system" + "  " + date].append(pack_info)
    #                 break
    #             else:
    #                 manual_system_distribution["Manual_system" + "  " + date].append(pack)
    #                 count+=1
    #
    #     return manual_system_distribution_with_details

    def get_weekdays(self, year, month, day):

        thisXMas = datetime.date(year, month, day)
        thisXMasDay = thisXMas.weekday()
        weekday = settings.WEEKDAYS[thisXMasDay]
        return weekday

    # TODO: need to refactor by Payal
    def get_canister_drugs(self):

        fndc_txrs = set()
        query = CanisterMaster.select(
            fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, ''))
                .alias('fndc_txr')
        ).distinct() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id)\
            .where(CanisterMaster.company_id == self.company_id,
                   CanisterMaster.active == settings.is_canister_active,CanisterZoneMapping.zone_id == self.zone_id)
        for record in query.dicts():
            fndc_txrs.add(record['fndc_txr'])


        query1 = PackDetails.select(fn.CONCAT(DrugMaster.formatted_ndc,'##',DrugMaster.txr).alias('fndc_txr'))\
            .join(PackRxLink,on=PackRxLink.pack_id == PackDetails.id)\
            .join(SlotDetails,on=SlotDetails.pack_rx_id == PackRxLink.id)\
            .join(DrugMaster,on=DrugMaster.id == SlotDetails.drug_id)\
            .where(PackDetails.id << self.system_packs)

        for record in query1.dicts():
            if record['fndc_txr'] in fndc_txrs:
                self.pack_canister_drugs.add(record['fndc_txr'])


    # def get_batch_distribution(self,system_region_wise_dict,system_packs):
    #     multi_batch_info_dict = self.multi_batch_recommendation_algorithm(system_region_wise_dict,system_packs)

    def get_batch_distribution(self, system_region_wise_dict, system_patients):
        multi_batch_info_dict, automatic_batch_patient_dict, batch_split, batch_processing_time_dict, batch_analysis_data = \
            self.multi_batch_recommendation_algorithm(system_region_wise_dict, system_patients, self.sorted_patient_list)
        return multi_batch_info_dict, automatic_batch_patient_dict, batch_split, batch_processing_time_dict, batch_analysis_data

    def multi_batch_recommendation_algorithm(self, system_region_wise_dict, system_patients,sorted_patient_list):
        """
        1) Prepare needed data structures
        2) Algorithm logic
        - update_region_pack_allowing_condition
        - pop_and_save_pack
        - update_algorithm_dictionaries
        :return:
        """

        '''
        1)
        '''
        c1_pack_with_delivery_date = OrderedDict()
        pack_with_delivery_date = OrderedDict()
        cluster_pack_delivery_date_dict = OrderedDict()

        self.system_region_wise_dict = system_region_wise_dict
        self.system_patients = system_patients
        self.prepare_needed_data_structures()
        self.get_canister_drugs()
        cluster_groups = get_initial_clusters_of_packs(self.system_packs, company_id=self.company_id,
                                                       system_id=self.system_id, pack_delivery_date_dict=self.pack_delivery_date_dict)
        for cluster_id, cluster in enumerate(cluster_groups):
            c1_pack_with_delivery_date = OrderedDict()
            for pack in cluster['packs']:
                c1_pack_with_delivery_date[pack] = self.pack_delivery_date_dict[pack]
            pack_with_delivery_date = sorted(c1_pack_with_delivery_date.items(), key=lambda x: x[1])
            cluster_pack_delivery_date_dict[cluster_id] = pack_with_delivery_date

        # commented as of now to get patient list sorted based on can drugs
        # self.sorted_patients = self.get_sorted_packs_new(cluster_pack_delivery_date_dict)
        print("sorted_patient_list: ", sorted_patient_list)

        self.sorted_patients = list()
        for pat in sorted_patient_list:
            self.sorted_patients.append(pat[0])

        self.maximum_system_capacity_date_wise = {}

        for date, capacity in self.automatic_system_region_wise_date_capacity_dict.items():
            self.maximum_system_capacity_date_wise[date] = capacity

        self.region_pack_list_dict = {}
        # self.sorted_patients = self.system_patients
        self.automatic_batch_patient_dict = {}
        self.batch_patient_list = set()
        self.multi_batch_info_dict_keys = []
        self.batch_packs_list = []

        """
        Sort system packs
        """
        # self.sorted_packs =self.get_sorted_packs(packs_to_sort=self.system_packs)

        """
        Algorithm Variables
        """
        self.load_variables_on_region_change()
        while len(self.sorted_patients) != 0:
            self.update_region_pack_allowing_condition()
            patient_list = self.pop_and_save_pack()
            if patient_list is None and len(self.sorted_patients) == 0:
                break

            self.update_algorithm_dictionaries(patient_list)
            if self.batch_cut:
                break

        return self.multi_batch_info_dict_with_details, self.automatic_batch_patient_dict, self.batch_split, self.batch_processing_time,self.batch_analysis_data

    def get_sorted_packs_new(self, cluster_pack_delivery_date_dict):
        """
        This function will return the sorted patients based on two clusters.
        :param cluster_pack_delivery_date_dict: {cluster_id:{pack_id:delivery_date,..}}
        :return: sorted_patient_list
        """

        cluster_patient_list = defaultdict(list)  # cluster wise patient list

        for cluster, pack_data in cluster_pack_delivery_date_dict.items():
            cluster_patient_list[cluster] = []
            for pack in pack_data:
                if self.pack_patient[pack[0]] not in cluster_patient_list[cluster]:
                    cluster_patient_list[cluster].append(self.pack_patient[pack[0]])

        common_patients = set(cluster_patient_list[0]) & set(cluster_patient_list[1])
        for patient in common_patients:
            cluster_patient_list[1].remove(patient)

        # Arrange the patient from two clusters in such a way : [cluster_1_patient,cluster_2_patient,cluster_1_patient,cluster_2_patient...]
        sorted_patient_list = [item for pair in zip(cluster_patient_list[0], cluster_patient_list[1] + [0])
                               for item in pair]

        for patient in sorted_patient_list[:]:
            if patient == 0:
                sorted_patient_list.remove(patient)

        if len(sorted_patient_list) != len(self.system_patients):
            # If any list is greater than other list than append it to small length cluster
            diff = len(cluster_patient_list[0]) - len(cluster_patient_list[1])
            diff -= 1
            if diff > 0:
                for patient in list(reversed(cluster_patient_list[0]))[0:diff]:
                    sorted_patient_list.append(patient)
            elif diff < 0:
                for patient in list(reversed(cluster_patient_list[1]))[0:abs(diff + 1)]:
                    sorted_patient_list.append(patient)

        return sorted_patient_list

    def get_sorted_packs(self, packs_to_sort):
        sorted_pack_list = []
        pack_drug_match_dict = defaultdict()
        pack_prev_batch_drug_dict = defaultdict(set)

        for pack in packs_to_sort:
            if pack not in self.pack_drugs:
                continue
            if pack not in pack_drug_match_dict:
                pack_drug_match_dict[pack] = 0
            for drug in self.pack_drugs[pack]:
                if drug in self.previous_batch_drugs:
                    if drug not in self.canister_drugs:
                        continue
                    pack_drug_match_dict[pack] += 1
                    pack_prev_batch_drug_dict[pack].update(drug.split(','))
        if not settings.SORTING_LOGIC:
            ord = OrderedDict(sorted(pack_drug_match_dict.items(), key=lambda x: x[1], reverse=True))
            for pack in ord.keys():
                sorted_pack_list.append(pack)
        if settings.SORTING_LOGIC:
            for i in range(25):
                if i == 15:
                    print("P")
                for pack, drug_count in pack_drug_match_dict.items():
                    if (len(self.pack_drugs[pack]) - drug_count) == i:
                        # if self.pack_drugs[pack]-pack_prev_batch_drug_dict[pack] in self.canister_drugs:
                        sorted_pack_list.append(pack)

        return sorted_pack_list

    def pop_and_save_pack(self):
        """
        - Based on region pack allowing conditions, we will be popping a pack from remaining packs.
        - All the logic deciding order of pack will be inside this method.
        - This method can also deliver multiple or single pack, based on logic.
        :return: [ list_of_packs]
        """
        patient_to_process = []
        for index, patient in enumerate(self.sorted_patients):
            patient_date = self.patient_fill_schedule_date_dict[patient]
            if self.region_allowing_dict[patient_date]:
                if self.region_in_inspection_end_date in self.distributed_pack_count.keys():
                    if patient_date != self.region_in_inspection_end_date and \
                            (len(self.patient_packs[patient]) + len(
                                self.distributed_pack_id[self.region_in_inspection_end_date]) +
                             self.maximum_system_capacity_date_wise[self.region_in_inspection_end_date] >
                             self.automatic_system_region_wise_date_capacity_dict[self.region_in_inspection_end_date]) \
                            and self.date_wise_to_be_filled_dict[self.region_in_inspection_end_date] > 0:
                        continue
                    else:
                        # patient_to_process.append(self.sorted_patients.pop(index))
                        # rem_cap = self.region_remaining_packs_capacity[self.patient_packs[self.sorted_patients.pop(index)]]
                        return [self.sorted_patients.pop(index)]

                else:
                    return [self.sorted_patients.pop(index)]

    def update_region_pack_allowing_condition(self):
        """
        This method will update region_allowing_dict.
        1) Reset Flags on region change
        Whenever region in inspection is changed, all keys of dictionary will be reset to True, except for following
        conditions.
        - if own region packs are exhausted, we will not make this flag true.
        2) Find total needed mandatory packs.
        3) Update flags
        - for any region, own packs exhausted, make flag false.
        - for any region maximum left side movable pack exhausted, make all next flags False.
        # TODO: Make this dictionary sorted.
        - For any region remaining packs is same as mendatory packs, make all region flags false except mendatory once.
        :return:
        """

        """
        1
        """
        if self.is_change_in_region_in_inspection:
            for date in self.region_allowing_dict.keys():
                self.region_allowing_dict[date] = (self.date_wise_to_be_filled_dict[date] > 0)
            self.is_change_in_region_in_inspection = False
        """
        2
        """
        # TODO : commented below code because don't want date wise packs limitation which is calcuated by system
        #  capacity to fill automated packs per hour

        # make_all_next_region_false = False
        # for date in sorted(self.region_allowing_dict.keys()):
        #     if date < self.region_in_inspection_end_date:
        #         continue
        #     if make_all_next_region_false:
        #         self.region_allowing_dict[date] = False
        #         continue
        #     # make_all_next_region_false = False
        #     if self.date_wise_to_be_filled_dict[date] <= 0:
        #         self.region_allowing_dict[date] = False
        #     if self.maximum_left_side_moveble_pack_dict[date] <= 0:
        #         make_all_next_region_false = True
        #         continue
        pass

    def update_algorithm_dictionaries(self, patient_list):
        """
        This method is updating dictionaries needed to run algorithm. The list of dictionaries are as follows.
        1) own_region_pack_dictionary
        2) maximum_left_side_movable_pack_dict
        TODO: Write here when it will be updated
        :return:
        """
        manual_slot = 0
        try:
            if patient_list is None and len(self.sorted_patients) != 0:
                self.load_variables_on_region_change()

            else:
                logger.info("update_algorithm_dictionaries - patient_list: " + str(patient_list))
                for patient in patient_list:
                    patient_date = self.patient_fill_schedule_date_dict[patient].split(' ')[0]
                    for pack in self.patient_packs[patient]:
                        # for pack in packs:
                        for slot, drugs in self.pack_slot_drug_dict[int(pack)].items():
                            self.total_batch_slots.append(slot)
                            for drug in drugs:
                                if drug not in self.patient_drugs[patient]:
                                    drug = self.drug_alternate_drug_dict[drug] if drug in self.drug_alternate_drug_dict else drug
                                if drug not in self.pack_canister_drugs:
                                    manual_slot = 1
                            if manual_slot:
                                self.manual_slots.append(slot)
                                manual_slot = 0
                    for drug in self.patient_drugs[patient]:
                        if drug in self.pack_canister_drugs:
                            self.batch_canister_drugs.add(drug)
                        else:
                            self.batch_manual_drugs.add(drug)
                    """
                    1
                    """
                    self.date_wise_to_be_filled_dict[patient_date] -= len(self.patient_packs[patient])
                    self.maximum_system_capacity_date_wise[self.region_in_inspection_end_date] -= len(
                        self.patient_packs[patient])
                    if patient_date > self.region_in_inspection_end_date:
                        for date in self.maximum_left_side_moveble_pack_dict:
                            if date < patient_date:
                                self.maximum_left_side_moveble_pack_dict[date] -= len(self.patient_packs[patient])
                    '''
                    3
                    '''
                    self.batch_patient_list.add(patient)
                    self.batch_packs_list.extend(list(map(int, self.patient_packs[patient])))
                    if self.region_in_inspection_end_date not in self.region_filling_count_dict:
                        self.region_filling_count_dict[self.region_in_inspection_end_date] = 0
                    self.region_filling_count_dict[self.region_in_inspection_end_date] += len(self.patient_packs[patient])
                    if self.region_in_inspection_end_date not in self.distributed_pack_id.keys():
                        self.distributed_pack_id[self.region_in_inspection_end_date] = []
                        self.distributed_pack_count[self.region_in_inspection_end_date] = {}
                    # self.distributed_pack_id[self.region_in_inspection_end_date].append((pack,self.pack_fill_schedule_date_dict[pack]))
                    self.distributed_pack_id[self.region_in_inspection_end_date].extend(self.patient_packs[patient])
                    if self.patient_fill_schedule_date_dict[patient] not in self.distributed_pack_count[
                        self.region_in_inspection_end_date]:
                        self.distributed_pack_count[self.region_in_inspection_end_date][
                            self.patient_fill_schedule_date_dict[patient]] = 0
                    self.distributed_pack_count[self.region_in_inspection_end_date][
                        self.patient_fill_schedule_date_dict[patient]] += len(self.patient_packs[patient])
                    self.region_remaining_packs_capacity -= len(self.patient_packs[patient])
                    # print(self.region_remaining_packs_capacity)
                    '''
                    4
                    '''

                    self.batch_cut_logic()
                    if self.batch_cut:
                        break

        except Exception as e:
            logger.error(e)
            raise error(0)

    def batch_cut_logic(self):
        batch_cut = False
        try:
            automatic_per_day_hours = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
            mfd_canister_threshold_per_hour = int(self.system_timings['MFD_CANISTER_THRESHOLD_PER_HOUR'])
            batch_duration_in_days = int(self.system_timings['BATCH_DURATION_IN_DAYS'])

            batch_cut_due_to_duration_limit = False
            batch_cut_due_to_mfd_threshold = False

            if settings.USE_BATCH_DIST_UPDATED:
                processing_hours = self.calculate_processing_hours()

                if processing_hours >= batch_duration_in_days * automatic_per_day_hours:
                    logger.info(f"batch cut due to duration limit, processing hours: {processing_hours}")
                    batch_cut_due_to_duration_limit = True

                mfd_canister_threshold = batch_duration_in_days * automatic_per_day_hours * mfd_canister_threshold_per_hour
                # mfd_canister_threshold = 100000000
                if int(len(self.manual_slots)/4) >= mfd_canister_threshold:
                    logger.info(f"batch cut due to mfd threshold, no manual_slots: {len(self.manual_slots)} and "
                                f"processing hours: {processing_hours}")
                    batch_cut_due_to_mfd_threshold = True

            if self.unique_drugs <= len(self.batch_canister_drugs) <= self.unique_drugs + 8 or \
                    batch_cut_due_to_duration_limit or batch_cut_due_to_mfd_threshold:

                logger.info(f"batch cut, no of unique_drugs: {self.unique_drugs} and "
                            f"no of batch_canister_drugs: {len(self.batch_canister_drugs)}")

                batch_cut = True
                sorted_patients = deepcopy(self.sorted_patients)
                # todo: code commented to reduce iteration max_quad_count = get_initial_clusters_of_packs(
                #  self.batch_packs_list, self.company_id, self.system_id, drops=1) if max_quad_count <= 140:
                if settings.CONSIDER_SIMILAR_PACKS:
                    for pat in sorted_patients:
                        if self.patient_drugs[pat].issubset(self.batch_canister_drugs):
                            # TODO: remove below two "for" loops as we already check in above line that patient drugs are
                            #  subset of canister drugs
                            manual_slot = 0
                            for pack in self.patient_packs[pat]:

                                for slot, drugs in self.pack_slot_drug_dict[int(pack)].items():
                                    self.total_batch_slots.append(slot)
                                    for drug in drugs:
                                        if drug not in self.pack_canister_drugs:
                                            manual_slot = 1
                                    if manual_slot:
                                        self.manual_slots.append(slot)
                                        manual_slot = 0
                            for drug in self.patient_drugs[pat]:
                                if drug in self.pack_canister_drugs:
                                    self.batch_canister_drugs.add(drug)
                                else:
                                    self.batch_manual_drugs.add(drug)
                            self.sorted_patients.remove(pat)
                            self.batch_patient_list.add(pat)
                            self.batch_packs_list.extend(list(map(int, self.patient_packs[pat])))
                # sorted_patients = deepcopy(self.sorted_patients)

                    # todo: code commented to reduce iteration
                    # for pat in sorted_patients:
                    #     self.batch_packs_list.extend(list(map(int, self.patient_packs[pat])))
                    #     self.batch_patient_list.add(pat)
                    #     self.sorted_patients.remove(pat)
                    #
                    #     max_quad_count = get_initial_clusters_of_packs(self.batch_packs_list, self.company_id,
                    #                                                    self.system_id, drops=1)
                    #
                    #     if max_quad_count <= 140 and max_quad_count > 135:
                    #         break

            if (self.region_remaining_packs_capacity <= 0 and not settings.USE_BATCH_DIST_UPDATED) or len(
                    self.sorted_patients) == 0 or batch_cut:

                logger.info(f"batch cut, no of sorted_patients: {len(self.sorted_patients)} and "
                            f"batch_cut: {batch_cut}")

                pack_list_batch = []
                self.pending_patient_flag = False
                self.calculate_batch_start_date()
                if len(self.batch_split) == 0:
                    self.batch_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())  # str(satetime.date.today(
                else:
                    self.batch_date = datetime.date(int(self.batch_date.split("-")[0]), int(self.batch_date.split("-")[1]),
                                                    int(self.batch_date.split("-")[2]))
                    self.batch_date += datetime.timedelta(days=2)
                    self.batch_date = str(self.batch_date)

                if (self.region_remaining_packs_capacity <= 0 or settings.USE_BATCH_DIST_UPDATED) and len(self.sorted_patients) != 0:
                    self.pending_patient_flag = False
                    for patient in self.sorted_patients:
                        if self.patient_fill_schedule_date_dict[patient] == self.region_in_inspection_end_date:
                            self.pending_patient_flag = True

                if not self.pending_patient_flag:
                    # TODO : Uncomment when we need to show batch split to front end or testing
                    # cluster = get_initial_clusters_of_packs(self.batch_packs_list,self.company_id,self.system_id)
                    # self.batch_split["Batch" + '-' + str(self.batch_count)] = {'Robot_1': cluster[0]['pack_length'],
                    #                                                            'Robot_2': cluster[1]['pack_length'],
                    #                                                            'Common_packs': len(
                    #                                                                set(cluster[0]['packs']) & set(
                    #                                                                    cluster[1]['packs']))}

                    self.batch_cut = True
                    for pack_id in self.batch_packs_list:
                        if int(pack_id) in self.pack_delivery_date_dict:
                            pack_info = db_get_pack_details_batch_scheduling(
                                pack_id=int(pack_id), delivery_date=self.pack_delivery_date_dict[int(pack_id)],
                                system_id=2)
                            if "Batch" + '-' + str(self.batch_count) + '  ' + (str(self.current_batch_start_date_dict[
                                                                                       self.batch_count])) not in self.multi_batch_info_dict_with_details:
                                self.multi_batch_info_dict_with_details[
                                    "Batch" + '-' + str(self.batch_count) + '  ' + str(
                                        self.current_batch_start_date_dict[self.batch_count])] = []
                            self.multi_batch_info_dict_with_details["Batch" + '-' + str(self.batch_count) + '  ' + str(
                                self.current_batch_start_date_dict[self.batch_count])].append(pack_info)
                    # if len(self.sorted_patients) == 0:
                    self.batch_processing_time["Batch" + '-' + str(self.batch_count) + '  ' + str(
                        self.current_batch_start_date_dict[self.batch_count])] = {
                        'hours': int(self.batch_processing_time_dict[self.batch_count]),
                        'min': round((self.batch_processing_time_dict[self.batch_count] -
                                      int(self.batch_processing_time_dict[self.batch_count])) * 60)}

                    self.batch_analysis_data["Batch" + '-' + str(self.batch_count) + '  ' + str(
                        self.current_batch_start_date_dict[self.batch_count])] = {'pack_list': self.batch_packs_list,
                                                                                  'total_packs': len(
                                                                                      self.batch_packs_list),
                                                                                  'total_batch_slots': len(
                                                                                      self.total_batch_slots),
                                                                                  'manual_slots': len(
                                                                                      self.manual_slots),
                                                                                  'canister_drugs': len(
                                                                                      self.batch_canister_drugs),
                                                                                  'manual_drugs': len(
                                                                                      self.batch_manual_drugs)}

                    logger.info(f"batch analysis info, total_packs: {len(self.batch_packs_list)} ,"
                                f" manual_slots: {len(self.manual_slots)}, canister_drugs: {len(self.batch_canister_drugs)},"
                                f" manual_drugs: {len(self.batch_manual_drugs)}")

                    logger.info("batch_processing_time: " + str(self.batch_processing_time))
                    # self.unique_drugs += 5
                    self.id += 1
                    self.batch_count += 1
                    self.last_batch_pack_count = len(self.batch_packs_list)
                    self.batch_packs_list = []
                    self.total_batch_slots = []
                    self.manual_slots = []
                    self.batch_canister_drugs = set()
                    self.batch_manual_drugs = set()
                    batch_cut = False
                if (self.region_remaining_packs_capacity <= 0 or settings.USE_BATCH_DIST_UPDATED) and len(
                        self.sorted_patients) != 0:
                    # self.previous_batch_drugs = get_last_batch_drug_list(pack_list=pack_list_batch)
                    # self.sorted_packs = self.get_sorted_packs(packs_to_sort=self.sorted_packs)
                    if not self.pending_patient_flag:
                        self.load_variables_on_region_change()

        except Exception as e:
            logger.error(e)
            raise error(0)

    def calculate_batch_start_date(self):
        AUTOMATIC_PER_DAY_HOURS = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(self.system_timings['AUTOMATIC_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(self.system_timings['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(self.system_timings['AUTOMATIC_SUNDAY_HOURS'])
        batch_date_day_dict = {}
        self.current_batch_start_date_dict = {}
        rem_cap = 0
        # self.batch_count = 2
        # last_batch_start_date_str = '2020-03-17'
        # self.batch_start_date_dict[1] = datetime.date(int(last_batch_start_date_str.split("-")[0]), int(last_batch_start_date_str.split("-")[1]),
        #                   int(last_batch_start_date_str.split("-")[2]))
        # self.last_batch_pack_count = 20
        processing_hours = 0
        if self.batch_count == 1:
            # last_batch_start_date = BatchMaster.db_get_scheduled_start_date_of_last_batch()
            if self.system_end_date < datetime.datetime.now(settings.PY_TIME_ZONE).date():
                last_batch_end_date = datetime.datetime.now(settings.PY_TIME_ZONE).date()
                last_batch_start_date = last_batch_end_date
            else:
                last_batch_end_date = self.system_end_date
                last_batch_start_date = last_batch_end_date + datetime.timedelta(days=1)
            last_batch_start_date_str = str(last_batch_start_date)  # this is in date format
            last_batch_packs_count = len(self.batch_packs_list)
            self.last_batch_pack_count = last_batch_packs_count
        else:
            last_batch_start_date = self.batch_start_date_dict[self.batch_count - 1]
            last_batch_start_date_str = str(last_batch_start_date)
            last_batch_packs_count = len(self.batch_packs_list)
            self.last_batch_pack_count = last_batch_packs_count
            # # date_count = [1,2]
            # # if last_batch_packs_count == 0:
            # #     batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            # #         int(last_batch_start_date_str.split('-')[0]),
            # #         int(last_batch_start_date_str.split('-')[1]),
            # #         int(last_batch_start_date_str.split('-')[2]))
            # #     current_batch_count = len(self.batch_packs_list)
            # #     while current_batch_count > 0:
            # #         last_batch_start_date_str = str(last_batch_start_date)
            # #         batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            # #             int(last_batch_start_date_str.split('-')[0]),
            # #             int(last_batch_start_date_str.split('-')[1]),
            # #             int(last_batch_start_date_str.split('-')[2]))
            # #         if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
            # #             if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            # #                 current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
            # #                 last_batch_start_date += datetime.timedelta(days=1)
            # #                 processing_hours += AUTOMATIC_SATURDAY_HOURS
            # #                 if last_batch_packs_count == 0:
            # #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #             elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            # #                 # current_batch_count = 0
            # #                 processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            # #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                 self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #         elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
            # #             if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            # #                 current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
            # #                 last_batch_start_date += datetime.timedelta(days=1)
            # #                 processing_hours += AUTOMATIC_SUNDAY_HOURS
            # #                 if current_batch_count == 0:
            # #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #             elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            # #                 current_batch_count = 0
            # #                 processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            # #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                 self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #         else:
            # #             if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            # #                 current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
            # #                 last_batch_start_date += datetime.timedelta(days=1)
            # #                 processing_hours += AUTOMATIC_PER_DAY_HOURS
            # #                 if current_batch_count == 0:
            # #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #             elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            # #                 # current_batch_count = 0
            # #                 processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            # #                 current_batch_count = 0
            # #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # #                 self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            # #     break
            # if last_batch_packs_count == 0:
            #     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            # last_batch_start_date_str = str(self.batch_start_date_dict[self.batch_count]) if self.batch_count in self.batch_start_date_dict else last_batch_start_date_str
            # last_batch_packs_count = self.last_batch_pack_count
            # self.current_batch_start_date_dict[self.batch_count] = last_batch_start_date
            # batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            #     int(last_batch_start_date_str.split('-')[0]),
            #     int(last_batch_start_date_str.split('-')[1]),
            #     int(last_batch_start_date_str.split('-')[2]))
            # while last_batch_packs_count > 0:
            #     last_batch_start_date_str = str(last_batch_start_date)
            #     batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            #         int(last_batch_start_date_str.split('-')[0]),
            #         int(last_batch_start_date_str.split('-')[1]),
            #         int(last_batch_start_date_str.split('-')[2]))
            #     if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_SATURDAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            #             last_batch_packs_count = 0
            #             processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             self.batch_processing_time_dict[self.batch_count] = processing_hours
            #     elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_SUNDAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            #             last_batch_packs_count = 0
            #             processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             self.batch_processing_time_dict[self.batch_count] = processing_hours
            #     else:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_PER_DAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            #             processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
            #             last_batch_packs_count = 0
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             self.batch_processing_time_dict[self.batch_count] = processing_hours
            # self.last_batch_pack_count = len(self.batch_packs_list)
            # last_batch_packs_count = self.last_batch_pack_count
            # processing_hours = 0

            # if last_batch_packs_count == 0:
            #     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #     if len(self.sorted_patients) == 0:
            #         batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            #             int(last_batch_start_date_str.split('-')[0]),
            #             int(last_batch_start_date_str.split('-')[1]),
            #             int(last_batch_start_date_str.split('-')[2]))
            #         current_batch_count = len(self.batch_packs_list)
            #         while current_batch_count > 0:
            #             last_batch_start_date_str = str(last_batch_start_date)
            #             batch_date_day_dict[last_batch_start_date] = self.get_weekdays(
            #                 int(last_batch_start_date_str.split('-')[0]),
            #                 int(last_batch_start_date_str.split('-')[1]),
            #                 int(last_batch_start_date_str.split('-')[2]))
            #             if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
            #                 if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            #                     current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
            #                     current_batch_count += datetime.timedelta(days=1)
            #                     processing_hours += AUTOMATIC_SATURDAY_HOURS
            #                     if last_batch_packs_count == 0:
            #                         self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                         self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #                 elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
            #                     # current_batch_count = 0
            #                     processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #             elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
            #                 if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            #                     current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
            #                     last_batch_start_date += datetime.timedelta(days=1)
            #                     processing_hours += AUTOMATIC_SUNDAY_HOURS
            #                     if current_batch_count == 0:
            #                         self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                         self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #                 elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
            #                     current_batch_count = 0
            #                     processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #             else:
            #                 if current_batch_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            #                     current_batch_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
            #                     last_batch_start_date += datetime.timedelta(days=1)
            #                     processing_hours += AUTOMATIC_PER_DAY_HOURS
            #                     if current_batch_count == 0:
            #                         self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                         self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #                 elif current_batch_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
            #                     # current_batch_count = 0
            #                     processing_hours += current_batch_count / AUTOMATIC_PER_HOUR
            #                     self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                     self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            #
            # while last_batch_packs_count > 0:
            #     last_batch_start_date_str = str(last_batch_start_date)
            #     batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
            #                                                                    int(last_batch_start_date_str.split('-')[1]),
            #                                                                    int(last_batch_start_date_str.split('-')[2]))
            #     if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_SATURDAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 # self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS:
            #             # rem_cap = AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS - batch_packs_count
            #             # if rem_cap <= AUTOMATIC_PER_HOUR:
            #             #     last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += last_batch_packs_count/AUTOMATIC_PER_HOUR
            #             last_batch_packs_count = 0
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             # self.batch_processing_time_dict[self.batch_count] = processing_hours
            #     elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR*AUTOMATIC_SUNDAY_HOURS and AUTOMATIC_SUNDAY_HOURS > 0:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR*AUTOMATIC_SUNDAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_SUNDAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 # self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR*AUTOMATIC_SUNDAY_HOURS:
            #             processing_hours += last_batch_packs_count/AUTOMATIC_PER_HOUR
            #             last_batch_packs_count = 0
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             # self.batch_processing_time_dict[self.batch_count] = processing_hours
            #     else:
            #         if last_batch_packs_count >= AUTOMATIC_PER_HOUR*AUTOMATIC_PER_DAY_HOURS:
            #             last_batch_packs_count -= AUTOMATIC_PER_HOUR*AUTOMATIC_PER_DAY_HOURS
            #             last_batch_start_date += datetime.timedelta(days=1)
            #             processing_hours += AUTOMATIC_PER_DAY_HOURS
            #             if last_batch_packs_count == 0:
            #                 self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #                 # self.batch_processing_time_dict[self.batch_count] = processing_hours
            #         elif last_batch_packs_count < AUTOMATIC_PER_HOUR*AUTOMATIC_PER_DAY_HOURS:
            #             last_batch_packs_count = 0
            #             processing_hours += last_batch_packs_count/AUTOMATIC_PER_HOUR
            #             self.batch_start_date_dict[self.batch_count] = last_batch_start_date
            #             # self.batch_processing_time_dict[self.batch_count] = processing_hours
        self.current_batch_start_date_dict[self.batch_count] = last_batch_start_date
        batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                       int(last_batch_start_date_str.split('-')[1]),
                                                                       int(last_batch_start_date_str.split('-')[2]))
        while last_batch_packs_count > 0:
            last_batch_start_date_str = str(last_batch_start_date)
            batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                           int(last_batch_start_date_str.split('-')[1]),
                                                                           int(last_batch_start_date_str.split('-')[2]))
            if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SATURDAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                        self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                    self.batch_processing_time_dict[self.batch_count] = processing_hours
            elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SUNDAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                        self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                    self.batch_processing_time_dict[self.batch_count] = processing_hours
            else:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_PER_DAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                        self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                    self.batch_processing_time_dict[self.batch_count] = processing_hours

    def calculate_processing_hours(self):
        AUTOMATIC_PER_DAY_HOURS = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(self.system_timings['AUTOMATIC_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(self.system_timings['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(self.system_timings['AUTOMATIC_SUNDAY_HOURS'])
        batch_date_day_dict = {}
        rem_cap = 0
        # self.batch_count = 2
        # last_batch_start_date_str = '2020-03-17'
        # self.batch_start_date_dict[1] = datetime.date(int(last_batch_start_date_str.split("-")[0]), int(last_batch_start_date_str.split("-")[1]),
        #                   int(last_batch_start_date_str.split("-")[2]))
        # self.last_batch_pack_count = 20
        processing_hours = 0
        if self.batch_count == 1:
            # last_batch_start_date = BatchMaster.db_get_scheduled_start_date_of_last_batch()
            if self.system_end_date < datetime.datetime.now(settings.PY_TIME_ZONE).date():
                last_batch_end_date = datetime.datetime.now(settings.PY_TIME_ZONE).date()
                last_batch_start_date = last_batch_end_date
            else:
                last_batch_end_date = self.system_end_date
                last_batch_start_date = last_batch_end_date + datetime.timedelta(days=1)
            last_batch_start_date_str = str(last_batch_start_date)  # this is in date format
            last_batch_packs_count = len(self.batch_packs_list)
        else:
            last_batch_start_date = self.batch_start_date_dict[self.batch_count - 1]
            last_batch_start_date_str = str(last_batch_start_date)
            last_batch_packs_count = len(self.batch_packs_list)

        batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                       int(last_batch_start_date_str.split('-')[1]),
                                                                       int(last_batch_start_date_str.split('-')[2]))
        while last_batch_packs_count > 0:
            last_batch_start_date_str = str(last_batch_start_date)
            batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                           int(last_batch_start_date_str.split('-')[1]),
                                                                           int(last_batch_start_date_str.split('-')[2]))
            if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SATURDAY_HOURS
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0

            elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SUNDAY_HOURS
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0

            else:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_PER_DAY_HOURS
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0

        return processing_hours

    def calulate_processing_time_for_last_batch(self):
        AUTOMATIC_PER_DAY_HOURS = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(self.system_timings['AUTOMATIC_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(self.system_timings['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(self.system_timings['AUTOMATIC_SUNDAY_HOURS'])
        batch_date_day_dict = {}
        processing_hours = 0

        last_batch_start_date = self.batch_start_date_dict[self.batch_count - 1]
        last_batch_start_date_str = str(last_batch_start_date)
        last_batch_packs_count = self.last_batch_pack_count
        batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                       int(last_batch_start_date_str.split('-')[1]),
                                                                       int(last_batch_start_date_str.split('-')[2]))
        while last_batch_packs_count > 0:
            last_batch_start_date_str = str(last_batch_start_date)
            batch_date_day_dict[last_batch_start_date] = self.get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                           int(last_batch_start_date_str.split('-')[1]),
                                                                           int(last_batch_start_date_str.split('-')[2]))
            if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SATURDAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count = 0
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SUNDAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_start_date_dict[self.batch_count] = last_batch_start_date
                        self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count = 0
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
            else:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_PER_DAY_HOURS
                    if last_batch_packs_count == 0:
                        self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count = 0
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    self.batch_processing_time_dict[self.batch_count - 1] = processing_hours
        self.batch_processing_time[
            "Batch" + '-' + str(self.batch_count - 1) + '  ' + str(
                self.batch_start_date_dict[self.batch_count - 1])] = {
            'hours': int(self.batch_processing_time_dict[self.batch_count - 1]),
            'min': (self.batch_processing_time_dict[
                        self.batch_count - 1] - int(
                self.batch_processing_time_dict[self.batch_count - 1])) * 60}

    def prepare_needed_data_structures(self):
        """
        This method will prepare all dictionaries needed to run algorithm.
        The list of needed dictionaries are as follows.
        1) date_wise_to_be_filled_dict
        2) maximum_left_side_moveble_pack_dict
        :return:
        """

        """
        Temporary code
        """
        if settings.STATIC_FLAG:
            count = 1
            self.total_schedule_dates = ['2019-10-06', '2019-10-07', '2019-10-08', '2019-10-09']
            self.pack_fill_schedule_date_dict = {}
            # self.total_packs = [16384, 16385, 16386, 16387, 16388, 16389, 16391, 16392, 16393, 16394, 16395, 16397, 16398, 16399, 16400, 16401, 16402, 16403, 16404, 16405, 16406, 16407, 16408, 16409, 16410, 16411, 16412, 16413, 16414, 16415, 16416, 16417, 16418, 16419, 16420, 16421, 16422, 16423, 16424, 16425, 16426, 16427, 16428, 16429, 16430, 16431, 16432, 16433, 16434, 16435, 16436, 16437, 16438, 16439, 16440, 16441, 16442, 16443, 16444, 16445, 16446, 16447, 16448, 16449, 16450, 16451, 16452, 16453, 16454, 16455, 16456, 16457, 16458, 16459, 16460, 16461, 16462, 16463, 16464, 16465, 16466, 16467, 16468, 16469, 16470, 16471, 16472, 16473, 16474, 16475, 16476, 16477, 16478, 16479, 16480, 16481, 16482, 16483, 16484, 16485, 16486, 16487, 16488, 16489, 16490, 16491, 16492, 16493, 16494, 16495, 16496, 16497, 16498, 16499, 16500, 16501, 16502, 16503, 16504, 16505, 16506, 16507, 16508, 16510, 16511, 16512, 16513, 16514, 16515, 16516, 16517, 16518, 16519, 16520, 16521, 16522, 16523, 16524, 16525, 16526, 16527, 16528, 16529, 16530, 16531, 16532, 16533, 16534, 16535, 16536, 16537, 16538, 16539, 16540, 16541, 16542, 16543, 16544, 16545, 16546, 16547, 16548, 16549, 16550, 16551, 16552, 16553, 16554, 16555, 16556, 16557, 16558, 16559, 16560, 16561, 16562, 16563, 16564, 16565, 16566, 16567, 16568, 16569, 16571, 16572, 16573, 16574, 16575, 16576, 16577, 16578, 16579, 16581, 16582, 16583, 16584, 16585, 16586, 16587, 16588, 16589, 16590, 16591, 16592, 16593, 16594, 16595, 16596, 16597, 16598, 16599, 16600, 16601, 16602, 16603, 16604, 16605, 16606, 16607, 16608, 16609, 16610, 16611, 16612, 16613, 16614, 16615, 16616, 16617, 16618, 16619, 16620, 16621, 16622, 16623, 16624, 16625, 16626, 16627, 16628, 16629, 16630, 16631, 16632, 16633, 16634, 16635, 16636, 16637, 16638, 16639, 16640, 16641, 16642, 16643, 16644, 16645, 16646, 16647, 16648, 16649, 16650, 16651, 16652, 16653, 16654, 16655, 16656, 16657, 16658, 16659, 16660, 16661, 16662, 16663, 16664, 16665, 16666, 16667, 16668, 16669, 16670, 16671, 16674, 16675, 16677, 16681, 16682, 16683, 16684, 16685, 16689, 16690, 16692, 16693, 16694, 16695, 16696, 16698, 16702, 16703, 16704, 16705, 16706, 16711, 16712, 16713, 16714, 16715, 16716, 16717, 16718, 16719, 16721, 16723, 16724, 16725, 16726, 16727, 16729, 16731, 16732, 16733, 16734, 16735, 16736, 16738, 16739, 16740, 16742, 16744, 16745, 16746, 16747, 16748, 16750, 16751, 16752, 16753, 16754, 16758, 16759, 16761, 16762, 16763, 16764, 16765, 16769, 16770, 16772, 16773, 16774, 16776, 16777, 16778, 16781, 16784, 16785, 16786, 16787, 16790, 16791, 16792, 16794, 16795, 16796, 16797, 16798, 16799, 16800, 16801, 16802, 16803, 16804, 16805, 16806, 16807, 16808, 16809, 16810, 16811, 16812, 16813, 16814, 16815, 16816, 16817, 16818, 16819, 16820, 16821, 16822, 16823, 16824, 16825, 16826, 16827, 16828, 16829, 16830]
            self.system_packs = []
            for i in range(400):
                self.system_packs.append(i)
            for p in self.system_packs:
                if count <= 50:
                    self.pack_fill_schedule_date_dict[p] = '2019-10-06'
                elif count > 50 and count <= 170:
                    self.pack_fill_schedule_date_dict[p] = '2019-10-07'
                elif count > 170 and count <= 290:
                    self.pack_fill_schedule_date_dict[p] = '2019-10-08'
                elif count > 290 and count <= 400:
                    self.pack_fill_schedule_date_dict[p] = '2019-10-09'
                count += 1
            # random.shuffle(self.system_packs)
        """
        Temporary code end
        """
        if not settings.STATIC_FLAG:
            self.pack_fill_schedule_date_dict = {}
            for p, d in self.patient_fill_schedule_date_dict.items():
                for pack in self.patient_packs[p]:
                    self.pack_fill_schedule_date_dict[int(pack)] = d

            self.total_schedule_dates = []
            for patient in self.system_patients:
                self.total_schedule_dates.append(self.patient_fill_schedule_date_dict[patient].split(' ')[0])
            self.total_schedule_dates = sorted(list(set(self.total_schedule_dates)))

        # Make datewise to be filled dictionary
        self.date_wise_to_be_filled_dict = {}

        for patient in self.system_patients:
            if self.patient_fill_schedule_date_dict[patient] not in self.date_wise_to_be_filled_dict:
                self.date_wise_to_be_filled_dict[self.patient_fill_schedule_date_dict[patient].split(' ')[0]] = 0
            self.date_wise_to_be_filled_dict[self.patient_fill_schedule_date_dict[patient].split(' ')[0]] += len(
                self.patient_packs[patient])
        self.region_allowing_dict = {}
        for date in self.total_schedule_dates:
            self.region_allowing_dict[date] = True

        for patient, packs in self.patient_packs.items():
            for pack in packs:
                self.pack_patient[int(pack)] = patient

        self.patient_fill_schedule_date_dict = OrderedDict(self.patient_fill_schedule_date_dict)
        self.date_wise_to_be_filled_dict = OrderedDict(self.date_wise_to_be_filled_dict)
        if settings.STATIC_FLAG:
            self.date_wise_to_be_filled_dict = OrderedDict(
                {'2019-10-09': 110, '2019-10-08': 120, '2019-10-07': 120,
                 '2019-10-06': 50}
            )
            self.system_region_wise_dict = OrderedDict(
                {'2019-10-09': 100, '2019-10-08': 100, '2019-10-07': 100,
                 '2019-10-06': 100}
            )
            for p, d in self.patient_fill_schedule_date_dict.items():
                for pack in self.patient_packs[p]:
                    self.pack_fill_schedule_date_dict[int(pack)] = d

        # Make maximum left side movable pack dict
        self.maximum_left_side_moveble_pack_dict = OrderedDict()
        required_pack_count = 0
        total_count = 0
        for date in sorted(self.date_wise_to_be_filled_dict):
            pack_count = self.date_wise_to_be_filled_dict[date]
            required_pack_count += pack_count
            # total_count += self.system_region_wise_dict[date]
            if date not in self.maximum_left_side_moveble_pack_dict:
                self.maximum_left_side_moveble_pack_dict[date] = 0
            self.maximum_left_side_moveble_pack_dict[date] = self.system_region_wise_dict[
                                                                 date] + total_count - required_pack_count
            total_count += self.system_region_wise_dict[date]

        for patient in self.system_patients:
            self.system_packs.extend(list(map(int, self.patient_packs[patient])))
        return

    def load_variables_on_region_change(self):
        """
        1) region_start and end date
        2) is_change_in_region_in_inspection
        :return:
        """
        # TODO: make start and end date logic dynamic
        if len(self.total_schedule_dates) != 0:
            self.region_in_inspection_start_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
            self.region_in_inspection_end_date = self.total_schedule_dates[self.region_change_index]
            self.region_change_index += 1
            self.is_change_in_region_in_inspection = True
            self.region_remaining_packs_capacity = self.system_region_wise_dict[self.region_in_inspection_end_date]
            self.own_region_packs = self.date_wise_to_be_filled_dict[self.region_in_inspection_end_date]

    def prepare_needed_data_structures_for_manual_batch_distribution(self, manual_packs, company_id):
        """
        This method will return the dict that has date wise filtered set of packs
        key: date
        Sort datewise_manual_patient_dict
        """

        datewise_manual_patient_dict = {}
        patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, manual_packs)
        total_patients = [patient for patient in patient_packs.keys()]
        patient_delivery_date_dict = get_patient_wise_delivery_date(total_patients)

        patient_fill_schedule_date_dict = {}
        fill_date_day_dict = {}
        count = 0
        fill_complete_date = ''
        days_count = 0

        for patient, del_date in patient_delivery_date_dict.items():

            while count != settings.BUFFER_BETWEEN_DELIVERY_DATE_AND_FILL_DATE:
                fill_complete_date = del_date - datetime.timedelta(days_count + 1)
                fill_complete_date = str(fill_complete_date).split(' ')[0]
                fill_date_day_dict[fill_complete_date] = self.get_weekdays(int(fill_complete_date.split("-")[0]),
                                                                           int(fill_complete_date.split("-")[1]),
                                                                           int(fill_complete_date.split("-")[2]))
                if fill_date_day_dict[fill_complete_date] == settings.SUNDAY:
                    days_count += 1
                    continue
                else:
                    count += 1
                    days_count += 1
            if fill_complete_date == '':
                patient_fill_schedule_date_dict[patient] = str(del_date).split(' ')[0]
            else:
                patient_fill_schedule_date_dict[patient] = str(fill_complete_date)

        for p, d in patient_fill_schedule_date_dict.items():
            if d not in datewise_manual_patient_dict.keys():
                datewise_manual_patient_dict[d] = set()
            datewise_manual_patient_dict[d].add(p)

        datewise_manual_patient_dict = OrderedDict(sorted(datewise_manual_patient_dict.items(), key=lambda x: x[0]))

        return datewise_manual_patient_dict, patient_packs


class AutomaticManualDistributionRecommender(object):

    def __init__(self, zone_facility_drug_dict,facility_packs,facility_delivery_date_dict,facility_patients,patient_packs,zone_patient_drugs,patient_delivery_date_dict, manual_user_id, system_timings,zone_canister_drug_dict,current_system,pack_half_pill_drug_drop_count):
        self.patient_packs = patient_packs
        self.zone_patient_drugs = zone_patient_drugs
        self.current_system = current_system
        self.patient_delivery_date_dict = patient_delivery_date_dict
        self.manual_user_id = manual_user_id
        self.system_timings = system_timings
        self.zone_facility_drug_dict = zone_facility_drug_dict
        self.facility_packs = facility_packs
        self.facility_delivery_date_dict = facility_delivery_date_dict
        self.facility_patients = facility_patients
        self.pack_half_pill_drug_drop_count = pack_half_pill_drug_drop_count
        self.output_dict = {}
        self.zone_canister_drug_dict = zone_canister_drug_dict
        self.pending_patients = []
        self.pending_facilities = []

    def get_split_recommendations(self, zone, pending_patients):
        total_packs = list()

        total_patients = []
        self.pending_patients = pending_patients

        for patient, packs in self.patient_packs.items():
            total_packs.extend(packs)
            total_patients.append(patient)


        system_split = {"automatic_system_packs":{},"manual_system_packs":{},"overloaded_packs":{}}
        date_pack_count_dict = {}
        automatic_system_region_wise_date_capacity_dict = {}
        manual_system_region_wise_date_capacity_dict = {}

        # Form patient to its fill complete date with 2 days offset

        self.patient_fill_schedule_date_dict = OrderedDict()
        l = []
        patient_delivery_date_dict = {}
        patient_schedule_date_dict = {}
        fill_date_day_dict = {}
        facility_schedule_not_followed_list = []

        # for patient in total_patients:
        #     for facility_id,value in self.schedule_data.items():
        #         if patient in value["patient_ids"]:
        #             # patient_fill_schedule_date_dict[patient] = self.schedule_data[facility_id]["delivery_date"]
        #             if "delivery_date" not in self.schedule_data[facility_id]:
        #                 facility_schedule_not_followed_list.append(patient)
        #                 break
        #             if self.schedule_data[facility_id]["delivery_date"] == '':
        #                 if self.schedule_data[facility_id]["ips_delivery_date"] == '':
        #                     facility_schedule_not_followed_list.append(patient)
        #                     patient_delivery_date_dict[patient] = " "
        #                 else:
        #                     del_date = datetime.date(2019, int(
        #                         self.schedule_data[facility_id]["ips_delivery_date"].split("-")[0]), int(
        #                         self.schedule_data[facility_id]["ips_delivery_date"].split("-")[1]))
        #             else:
        #                 del_date = datetime.date(2019, int(self.schedule_data[facility_id]["delivery_date"].split("-")[0]), int(self.schedule_data[facility_id]["delivery_date"].split("-")[1]))
        #             count = 0
        #             fill_complete_date = ''
        #             days_count = 0
        #
        #             patient_delivery_date_dict[patient] = str(del_date)
        #             patient_schedule_date_dict[patient] = self.schedule_data[facility_id]["schedule_date"]
        #
        #             while count != settings.BUFFER_BETWEEN_DELIVERY_DATE_AND_FILL_DATE:
        #                 fill_complete_date = del_date - timedelta(days_count+1)
        #                 fill_complete_date = str(fill_complete_date)
        #                 fill_date_day_dict[fill_complete_date] = self.get_weekdays(int(fill_complete_date.split("-")[0]), int(fill_complete_date.split("-")[1]),
        #                                             int(fill_complete_date.split("-")[2]))
        #                 if fill_date_day_dict[fill_complete_date] == settings.SUNDAY:
        #                     days_count += 1
        #                     continue
        #                 else:
        #                     count += 1
        #                     days_count += 1
        #             self.patient_fill_schedule_date_dict[patient] = str(fill_complete_date)
        #         else:
        #             facility_schedule_not_followed_list.append(patient)

        # patient_fill_schedule_date_dict = {}
        # test_patients = [13, 15, 1041, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 1068, 1069, 1071, 1074, 1076, 1078, 1080, 1085, 1088, 68, 69, 70, 71, 72, 73, 1099, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 1111, 89, 90, 91, 92, 93, 95, 96, 97, 98, 99, 100, 1126, 104, 105, 106, 107, 108, 1042, 110, 111, 112, 115, 116, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 130, 131, 132, 133, 135, 136, 137, 138, 139, 141, 142, 143, 144, 145, 146, 147, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 165, 166, 167, 169, 170, 171, 172, 173, 174, 200, 1097, 184, 185, 186, 187, 191, 193, 194, 195, 196, 198, 1224, 1226, 204, 205, 206, 207, 1232, 209, 210, 1237, 1240, 222, 223, 224, 225, 226, 227, 1229, 1280, 260, 261, 262, 263, 264, 265, 266, 267, 268, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 1104, 1094, 430, 431, 433, 1459, 1460, 1461, 438, 1463, 1464, 1465, 1466, 1467, 445, 1470, 448, 1473, 1474, 1475, 1476, 1478, 1479, 1480, 1481, 1483, 1484, 1485, 1486, 1101, 464, 1489, 1490, 467, 1492, 1493, 1494, 1496, 1497, 1498, 475, 476, 1501, 1502, 1503, 480, 1505, 482, 1510, 1105, 491, 1106, 494, 495, 496, 1107, 500, 501, 503, 504, 505, 508, 509, 510, 511, 512, 513, 517, 518, 519, 520, 87, 526, 527, 528, 530, 531, 532, 534, 1113, 549, 1116, 554, 557, 1117, 560, 561, 562, 435, 564, 569, 571, 572, 573, 574, 437, 1121, 584, 586, 588, 589, 593, 594, 595, 596, 598, 601, 602, 603, 605, 606, 607, 608, 102, 1469, 446, 1130, 1044, 449, 109, 452, 455, 685, 456, 535, 460, 461, 465, 744, 746, 747, 749, 638, 1219, 473, 1288, 1157, 436, 817, 478, 479, 1162, 1119, 1506, 1166, 1167, 1222, 874, 879, 1515, 493, 925, 930, 933, 934, 936, 937, 945, 499, 953, 995, 999, 1002, 1006, 1007, 1008, 1009, 1010, 1012, 1014]
        #
        # date_fill = {'2019-10-15':150,'2019-10-16':150,'2019-10-17':150,'2019-10-18':150,'2019-10-19':150,'2019-10-21':150,'2019-10-22':81}
        # count = 0
        # for i in test_patients:
        #     patient_fill_schedule_date_dict[i] = '2019-10-15'
        #     count+=1
        #     if count == 150:
        #         break

        # self.patient_fill_schedule_date_dict = deepcopy(self.patient_delivery_date_dict)
        # for patient,dd in self.patient_fill_schedule_date_dict.items():
        #     fill_date = str(dd).split(' ')[0]
        #     self.patient_fill_schedule_date_dict[patient] = fill_date

        # zone_list = [2,3]
        # for zone in zone_list:
        '''
        This code is temporarily commented. It will be on when we required buffer days
        '''
        sorted_patient_list = self.get_sorted_list(zone)
        # fill_complete_date = ''
        #
        # sorted_pack_list = self.get_sorted_list()
        for patient in sorted_patient_list:
            if patient[0] in self.patient_delivery_date_dict:
                self.patient_fill_schedule_date_dict[patient[0]] = \
                str(self.patient_delivery_date_dict[patient[0]]).split(' ')[0]

        #         count = 0
        #         days_count = 0
        #         while count != settings.BUFFER_BETWEEN_DELIVERY_DATE_AND_FILL_DATE:
        #             fill_complete_date = self.patient_delivery_date_dict[patient[0]] - timedelta(days_count + 1)
        #             fill_complete_date = str(fill_complete_date).split(' ')[0]
        #             fill_date_day_dict[fill_complete_date] = self.get_weekdays(int(fill_complete_date.split("-")[0]),
        #                                                                        int(fill_complete_date.split("-")[1]),
        #                                                                        int(fill_complete_date.split("-")[2]))
        #             if fill_date_day_dict[fill_complete_date] == settings.SUNDAY:
        #                 days_count += 1
        #                 continue
        #             else:
        #                 count += 1
        #                 days_count += 1

        self.total_schedule_dates = []
        for date in self.patient_fill_schedule_date_dict.values():
            self.total_schedule_dates.append(date)
        self.total_schedule_dates = sorted(list(set(self.total_schedule_dates)))

        self.output_dict['total_schedule_dates'] = self.total_schedule_dates
        self.output_dict['patient_fill_schedule_date_dict'] = self.patient_fill_schedule_date_dict
        system_split, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict,\
        manual_system_region_wise_date_capacity_dict, manual_system_packs, overloaded_pack_list = self.get_system_split(
            sorted_patient_list, total_packs)

        return system_split, self.patient_fill_schedule_date_dict, date_pack_count_dict,\
               automatic_system_region_wise_date_capacity_dict, manual_system_region_wise_date_capacity_dict,\
               manual_system_packs, overloaded_pack_list, sorted_patient_list, self.pending_patients, sorted_patient_list

    def get_split_recommendation_facility(self, zone, pending_facilities):
        total_packs = list()

        total_facilities = []
        self.pending_facilities = pending_facilities

        for facility, packs in self.facility_packs.items():
            total_packs.extend(packs)
            total_facilities.append(facility)
            # self.pending_patients.append(patient)

        system_split = {"automatic_system_packs": {}, "manual_system_packs": {}, "overloaded_packs": {}}
        date_pack_count_dict = {}
        automatic_system_region_wise_date_capacity_dict = {}
        manual_system_region_wise_date_capacity_dict = {}

        # Form patient to its fill complete date with 2 days offset

        self.facility_fill_schedule_date_dict = OrderedDict()
        l = []
        patient_delivery_date_dict = {}
        patient_schedule_date_dict = {}
        fill_date_day_dict = {}
        facility_schedule_not_followed_list = []

        # for patient in total_patients:
        #     for facility_id,value in self.schedule_data.items():
        #         if patient in value["patient_ids"]:
        #             # patient_fill_schedule_date_dict[patient] = self.schedule_data[facility_id]["delivery_date"]
        #             if "delivery_date" not in self.schedule_data[facility_id]:
        #                 facility_schedule_not_followed_list.append(patient)
        #                 break
        #             if self.schedule_data[facility_id]["delivery_date"] == '':
        #                 if self.schedule_data[facility_id]["ips_delivery_date"] == '':
        #                     facility_schedule_not_followed_list.append(patient)
        #                     patient_delivery_date_dict[patient] = " "
        #                 else:
        #                     del_date = datetime.date(2019, int(
        #                         self.schedule_data[facility_id]["ips_delivery_date"].split("-")[0]), int(
        #                         self.schedule_data[facility_id]["ips_delivery_date"].split("-")[1]))
        #             else:
        #                 del_date = datetime.date(2019, int(self.schedule_data[facility_id]["delivery_date"].split("-")[0]), int(self.schedule_data[facility_id]["delivery_date"].split("-")[1]))
        #             count = 0
        #             fill_complete_date = ''
        #             days_count = 0
        #
        #             patient_delivery_date_dict[patient] = str(del_date)
        #             patient_schedule_date_dict[patient] = self.schedule_data[facility_id]["schedule_date"]
        #
        #             while count != settings.BUFFER_BETWEEN_DELIVERY_DATE_AND_FILL_DATE:
        #                 fill_complete_date = del_date - timedelta(days_count+1)
        #                 fill_complete_date = str(fill_complete_date)
        #                 fill_date_day_dict[fill_complete_date] = self.get_weekdays(int(fill_complete_date.split("-")[0]), int(fill_complete_date.split("-")[1]),
        #                                             int(fill_complete_date.split("-")[2]))
        #                 if fill_date_day_dict[fill_complete_date] == settings.SUNDAY:
        #                     days_count += 1
        #                     continue
        #                 else:
        #                     count += 1
        #                     days_count += 1
        #             self.patient_fill_schedule_date_dict[patient] = str(fill_complete_date)
        #         else:
        #             facility_schedule_not_followed_list.append(patient)

        # patient_fill_schedule_date_dict = {}
        # test_patients = [13, 15, 1041, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 1068, 1069, 1071, 1074, 1076, 1078, 1080, 1085, 1088, 68, 69, 70, 71, 72, 73, 1099, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 1111, 89, 90, 91, 92, 93, 95, 96, 97, 98, 99, 100, 1126, 104, 105, 106, 107, 108, 1042, 110, 111, 112, 115, 116, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 130, 131, 132, 133, 135, 136, 137, 138, 139, 141, 142, 143, 144, 145, 146, 147, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 165, 166, 167, 169, 170, 171, 172, 173, 174, 200, 1097, 184, 185, 186, 187, 191, 193, 194, 195, 196, 198, 1224, 1226, 204, 205, 206, 207, 1232, 209, 210, 1237, 1240, 222, 223, 224, 225, 226, 227, 1229, 1280, 260, 261, 262, 263, 264, 265, 266, 267, 268, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 1104, 1094, 430, 431, 433, 1459, 1460, 1461, 438, 1463, 1464, 1465, 1466, 1467, 445, 1470, 448, 1473, 1474, 1475, 1476, 1478, 1479, 1480, 1481, 1483, 1484, 1485, 1486, 1101, 464, 1489, 1490, 467, 1492, 1493, 1494, 1496, 1497, 1498, 475, 476, 1501, 1502, 1503, 480, 1505, 482, 1510, 1105, 491, 1106, 494, 495, 496, 1107, 500, 501, 503, 504, 505, 508, 509, 510, 511, 512, 513, 517, 518, 519, 520, 87, 526, 527, 528, 530, 531, 532, 534, 1113, 549, 1116, 554, 557, 1117, 560, 561, 562, 435, 564, 569, 571, 572, 573, 574, 437, 1121, 584, 586, 588, 589, 593, 594, 595, 596, 598, 601, 602, 603, 605, 606, 607, 608, 102, 1469, 446, 1130, 1044, 449, 109, 452, 455, 685, 456, 535, 460, 461, 465, 744, 746, 747, 749, 638, 1219, 473, 1288, 1157, 436, 817, 478, 479, 1162, 1119, 1506, 1166, 1167, 1222, 874, 879, 1515, 493, 925, 930, 933, 934, 936, 937, 945, 499, 953, 995, 999, 1002, 1006, 1007, 1008, 1009, 1010, 1012, 1014]
        #
        # date_fill = {'2019-10-15':150,'2019-10-16':150,'2019-10-17':150,'2019-10-18':150,'2019-10-19':150,'2019-10-21':150,'2019-10-22':81}
        # count = 0
        # for i in test_patients:
        #     patient_fill_schedule_date_dict[i] = '2019-10-15'
        #     count+=1
        #     if count == 150:
        #         break

        # self.patient_fill_schedule_date_dict = deepcopy(self.patient_delivery_date_dict)
        # for patient,dd in self.patient_fill_schedule_date_dict.items():
        #     fill_date = str(dd).split(' ')[0]
        #     self.patient_fill_schedule_date_dict[patient] = fill_date

        # zone_list = [2,3]
        # for zone in zone_list:
        '''
        This code is temporarily commented. It will be on when we required buffer days
        '''
        sorted_facility_list = self.get_sorted_list_facility(zone)
        # fill_complete_date = ''
        #
        # sorted_pack_list = self.get_sorted_list()
        for facility in sorted_facility_list:
            if facility[0] in self.facility_delivery_date_dict:
                self.facility_fill_schedule_date_dict[facility[0]] = \
                    str(self.facility_delivery_date_dict[facility[0]]).split(' ')[0]

        #         count = 0
        #         days_count = 0
        #         while count != settings.BUFFER_BETWEEN_DELIVERY_DATE_AND_FILL_DATE:
        #             fill_complete_date = self.patient_delivery_date_dict[patient[0]] - timedelta(days_count + 1)
        #             fill_complete_date = str(fill_complete_date).split(' ')[0]
        #             fill_date_day_dict[fill_complete_date] = self.get_weekdays(int(fill_complete_date.split("-")[0]),
        #                                                                        int(fill_complete_date.split("-")[1]),
        #                                                                        int(fill_complete_date.split("-")[2]))
        #             if fill_date_day_dict[fill_complete_date] == settings.SUNDAY:
        #                 days_count += 1
        #                 continue
        #             else:
        #                 count += 1
        #                 days_count += 1

        self.total_schedule_dates = []
        for date in self.facility_fill_schedule_date_dict.values():
            self.total_schedule_dates.append(date)
        self.total_schedule_dates = sorted(list(set(self.total_schedule_dates)))

        self.output_dict['total_schedule_dates'] = self.total_schedule_dates
        self.output_dict['patient_fill_schedule_date_dict'] = self.facility_fill_schedule_date_dict
        system_split, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict = self.get_system_split_facility(
            sorted_facility_list, total_packs)
        return system_split, self.facility_fill_schedule_date_dict, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict, sorted_facility_list, self.pending_facilities

    def get_sorted_list(self, zone):
        """
        1) Get the patient drug information
        2) Sort patient by its canister drugs and manual drugs

        :param canister_drugs:
        :param patient_packs:
        :param patient_drugs:
        :return:
        """

        # total_packs = set([])
        # for patient_specific_packs in self.patient_packs.values():
        #     total_packs |= patient_specific_packs
        # number_of_total_packs = len(total_packs)

        '''
        1)
        '''
        pack_set = set()
        patient_can_drug_manual_drug_len_data_list = []
        current_patient_packs = set()
        for patient in list(self.zone_patient_drugs[zone].keys()):
            if patient not in self.pending_patients:
                continue
            current_patient_packs = self.patient_packs[patient]
            pack_set.update(current_patient_packs)
            patient_drugs_set = self.zone_patient_drugs[zone][patient]
            patient_drug_length = len(patient_drugs_set)
            patient_canister_drugs = patient_drugs_set & self.zone_canister_drug_dict[zone]
            # patient_multiple_canister_drugs = patient_drugs_set & self.multiple_canisters_drugs
            patient_canister_drug_length = len(patient_canister_drugs)
            # patient_multiple_canister_drugs_length = len(patient_multiple_canister_drugs)
            patient_manual_drug_length = patient_drug_length - patient_canister_drug_length
            packs_with_half_pill = current_patient_packs.intersection(self.pack_half_pill_drug_drop_count)
            for pack in packs_with_half_pill:
                patient_manual_drug_length += 1 + int(self.pack_half_pill_drug_drop_count[pack] / 7)
            patient_can_drug_manual_drug_len_data_list.append(
                (patient, patient_manual_drug_length, patient_canister_drug_length))


            # new_patient_can_drug_manual_drug_len_data_list = []

        # for each_patient, patient_manual_drug_length, patient_canister_drug_length in patient_can_drug_manual_drug_len_data_list:
        #     packs_for_given_patient = self.patient_packs[each_patient]
        #
        #     for pack in packs_for_given_patient:
        #         pack = int(pack)
        #         if pack not in self.pack_half_pill_drug_drop_count:
        #             continue
        #         else:
        #             patient_manual_drug_length += 1 + int(pack_half_pill_drug_drop_count[pack] / 7)
        #             # patient_canister_drug_length -= 1 + int(pack_half_pill_drug_drop_count[pack]/7)
        #     new_patient_can_drug_manual_drug_len_data_list.append(
        #         (each_patient, patient_manual_drug_length, patient_canister_drug_length))

        '''
        2)
        '''
        # Sorting patient_can_drug_manual_drug_len_data_list, we will first sort based on canister drug len in descending order and
        # after that sort based on manual_drug_len in ascending order
        sorted_patient_len_data = sorted(patient_can_drug_manual_drug_len_data_list, key=lambda x: (x[1],-x[2]))
        self.output_dict['sorted_patient_len_data'] = list(list(value) for value in sorted_patient_len_data)
        return sorted_patient_len_data

    def get_sorted_list_facility(self, zone):
        """
        1) Get the patient drug information
        2) Sort patient by its canister drugs and manual drugs

        :return:
        """

        # total_packs = set([])
        # for patient_specific_packs in self.patient_packs.values():
        #     total_packs |= patient_specific_packs
        # number_of_total_packs = len(total_packs)

        '''
        1)
        '''
        pack_set = set()
        facility_can_drug_manual_drug_len_data_list = []
        for facility in list(self.zone_facility_drug_dict[zone].keys()):
            if facility not in self.pending_facilities:
                continue
            pack_set.update(self.facility_packs[facility])
            facility_drugs_set = self.zone_facility_drug_dict[zone][facility]
            facility_drug_length = len(facility_drugs_set)
            facility_canister_drugs = facility_drugs_set & self.zone_canister_drug_dict[zone]
            # patient_multiple_canister_drugs = patient_drugs_set & self.multiple_canisters_drugs
            facility_canister_drug_length = len(facility_canister_drugs)
            # patient_multiple_canister_drugs_length = len(patient_multiple_canister_drugs)
            facility_manual_drug_length = facility_drug_length - facility_canister_drug_length
            facility_can_drug_manual_drug_len_data_list.append(
                (facility, facility_manual_drug_length, facility_canister_drug_length))

        pack_half_pill_drug_drop_count = db_get_half_pill_drug_drop_by_pack_id(list(pack_set))
        new_facility_can_drug_manual_drug_len_data_list = []

        for each_facility, facility_manual_drug_length, facility_canister_drug_length in facility_can_drug_manual_drug_len_data_list:
            packs_for_given_facility = self.facility_packs[each_facility]

            for pack in packs_for_given_facility:
                pack = int(pack)
                if pack not in pack_half_pill_drug_drop_count:
                    continue
                else:
                    facility_manual_drug_length += 1 + int(pack_half_pill_drug_drop_count[pack] / 7)
                    # patient_canister_drug_length -= 1 + int(pack_half_pill_drug_drop_count[pack]/7)
            new_facility_can_drug_manual_drug_len_data_list.append(
                (each_facility, facility_manual_drug_length, facility_canister_drug_length))

        '''
        2)
        '''
        # Sorting patient_can_drug_manual_drug_len_data_list, we will first sort based on canister drug len in descending order and
        # after that sort based on manual_drug_len in ascending order
        sorted_facility_len_data = sorted(new_facility_can_drug_manual_drug_len_data_list, key=lambda x: (x[1],-x[2]))
        self.output_dict['sorted_facility_len_data'] = list(list(value) for value in sorted_facility_len_data)
        return sorted_facility_len_data

    def get_system_split(self, sorted_patient_list, total_packs):
        """
        1) List total fill schedule dates for which we need to fill some packs
        2) Make list of dates in which we can fill packs
        3)form date to weekdays dictionary
        4)Make datewise upto pak count dictionary (Till this(fill_schedule date) date based on current date , we can fill this number of packs based on robot fill capacity per day)
        5)Core Logic based on delivery date
            -> date_pack_count_dict(which we made in step 4)
            -> total_schedule_dates list
        6)Make Manual pack list

        :param sorted_pack_list:
        :param patient_fill_schedule_date_dict:
        :param total_packs:
        :param patient_packs:
        :return:
        """

        '''
        1)
        '''
        self.total_schedule_dates = []
        for date in self.patient_fill_schedule_date_dict.values():
            self.total_schedule_dates.append(date)
        self.total_schedule_dates = sorted(list(set(self.total_schedule_dates)))

        '''
        2)
        '''
        # Find total date range for imported packs
        # total_date_range = []
        # numdays = math.ceil(len(total_packs)/settings.ROBOT_CAPACITY_PER_DAY)
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        base = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                             int(current_date.split("-")[2]))  # datetime.str(datetime.date.today()
        max_date = max(self.total_schedule_dates)
        max_date = max_date.split(' ')
        final_date = datetime.date(int(max_date[0].split("-")[0]), int(max_date[0].split("-")[1]),
                                   int(max_date[0].split("-")[2]))
        numdays = (final_date - base).days + 1
        date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]

        AUTOMATIC_PER_DAY_HOURS = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(self.system_timings['AUTOMATIC_PER_HOUR'])
        MANUAL_PER_DAY_HOURS = int(self.system_timings['MANUAL_PER_DAY_HOURS']) * len(self.manual_user_id)
        MANUAL_PER_HOUR = int(self.system_timings['MANUAL_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(self.system_timings['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(self.system_timings['AUTOMATIC_SUNDAY_HOURS'])
        MANUAL_SUNDAY_HOURS = int(self.system_timings['MANUAL_SUNDAY_HOURS']) * len(self.manual_user_id)
        MANUAL_SATURDAY_HOURS = int(self.system_timings['MANUAL_SATURDAY_HOURS']) * len(self.manual_user_id)

        '''
        3)
        '''
        # Form date weekday dict
        date_day_dict = {}
        for date in date_list:
            date = str(date)
            date_day_dict[date] = self.get_weekdays(int(date.split("-")[0]), int(date.split("-")[1]),
                                                    int(date.split("-")[2]))

        '''
        4)
        '''
        # datewise upto pack count for automatic
        date_extra_hours_automatic = get_extra_hours_dao(date_list, self.current_system)
        date_pack_count_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        current_date = str(current_date)
        for date in self.total_schedule_dates:
            date = date.split(' ')
            if date[0] not in date_pack_count_dict:
                date_pack_count_dict[date[0]] = 0
            f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                   int(current_date.split("-")[2]))
            l_date = datetime.date(int(date[0].split("-")[0]), int(date[0].split("-")[1]), int(date[0].split("-")[2]))

            days = (l_date - f_date).days
            upto_schedule_date_list = []
            for i in range(days):
                upto_schedule_date_list.append(f_date)
                f_date += datetime.timedelta(days=1)
            if len(date_list) != 0:
                date_list.remove(max(date_list))
            for date_i in upto_schedule_date_list:
                if date_day_dict[str(date_i)] == settings.SATURDAY:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)

                elif date_day_dict[str(date_i)] == settings.SUNDAY:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                else:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)

                if str(date_i) in date_extra_hours_automatic.keys():
                    date_pack_count_dict[date[0]] = date_pack_count_dict[date[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_i)])

            if date[0] in date_extra_hours_automatic.keys():
                date_pack_count_dict[date[0]] = date_pack_count_dict[date[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[date[0]])

        # datewise upto pack count for manual
        # date_pack_count_dict_manual = {}
        # current_date = '2019-11-25'
        # current_date = str(current_date)
        # for date in self.total_schedule_dates:
        #     if date not in date_pack_count_dict_manual:
        #         date_pack_count_dict_manual[date] = 0
        #     f_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
        #     l_date = datetime.date(2019, int(date.split("-")[1]), int(date.split("-")[2]))
        #
        #     days = (l_date - f_date).days
        #     upto_schedule_date_list_manual = []
        #     for i in range(days):
        #         upto_schedule_date_list_manual.append(f_date)
        #         f_date += datetime.timedelta(days=1)
        #     date_list.remove(max(date_list))
        #     for date_i in upto_schedule_date_list_manual:
        #         if date_day_dict[str(date_i)] == settings.SATURDAY:
        #             date_pack_count_dict_manual[date] += (settings.MANUAL_CAPACITY_FOR_SATURDAY)
        #         elif date_day_dict[str(date_i)] == settings.SUNDAY:
        #             date_pack_count_dict_manual[date] += (settings.MANUAL_CAPACITY_FOR_SUNDAY)
        #         else:
        #             date_pack_count_dict_manual[date] += settings.MANUAL_CAPACITY_PER_DAY

        # Make region wise date pack capacity dict
        automatic_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in self.total_schedule_dates:
            date_str = date.split(' ')
            if date not in automatic_system_region_wise_date_capacity_dict:
                automatic_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(self.total_schedule_dates):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (self.total_schedule_dates.index(date)) - 1
                fdate = self.total_schedule_dates[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

        pack_fill_schedule_date_dict = {}
        total_patients = []

        for p, d in self.patient_fill_schedule_date_dict.items():
            total_patients.append(p)
            for pack in self.patient_packs[p]:
                pack_fill_schedule_date_dict[int(pack)] = d
        '''
        5)
        '''
        # Core Logic
        date_pack_dict = {}
        date_patient_dict = {}
        automatic_system_packs = []
        automatic_system_patients = []
        manual_pack_list = []
        manual_patient_list = []
        date_pack_count_dict_cpy = deepcopy(date_pack_count_dict)
        # copy_sorted_pack_list = deepcopy(sorted_pack_list)
        x = []
        total_schedule_dates = sorted(self.total_schedule_dates)

        for k, v in date_pack_count_dict.items():
            if v <= 0 and k in total_schedule_dates:
                del date_pack_count_dict_cpy[k]
                indx = total_schedule_dates.index(k)
                for ind in range(indx + 1):
                    del total_schedule_dates[0]

        # for patient_tuple in total_packs:
        for patient in total_patients:
            patient = int(patient)

            if patient in self.patient_fill_schedule_date_dict:
                if self.patient_fill_schedule_date_dict[patient] in total_schedule_dates:
                    automatic_system_packs.extend(self.patient_packs[patient])
                    automatic_system_patients.append(patient)
                    self.pending_patients.remove(patient)
                    if self.patient_fill_schedule_date_dict[patient] not in date_patient_dict:
                        date_patient_dict[self.patient_fill_schedule_date_dict[patient]] = set()
                    date_patient_dict[self.patient_fill_schedule_date_dict[patient]].add(patient)
                    if self.patient_fill_schedule_date_dict[patient] not in date_pack_dict:
                        date_pack_dict[self.patient_fill_schedule_date_dict[patient]] = set()
                    date_pack_dict[self.patient_fill_schedule_date_dict[patient]].update(self.patient_packs[patient])
                    for dt in date_pack_count_dict:
                        if dt >= self.patient_fill_schedule_date_dict[patient]:
                            if date_pack_count_dict[self.patient_fill_schedule_date_dict[patient]] < 0:
                                date_pack_count_dict[dt] -= (
                                            date_pack_count_dict[self.patient_fill_schedule_date_dict[patient]] + len(
                                        self.patient_packs[patient]))
                            else:
                                date_pack_count_dict[dt] -= len(self.patient_packs[patient])
                    if len(list(filter(lambda y: (y <= 0), list(date_pack_count_dict.values())))) > 0:
                        # if len(self.patient_packs[patient_tuple[0]]) > 0:
                        #     automatic_system_packs.extend(list(map(int,self.patient_packs[patient_tuple[0]])))
                        #     ln = len(automatic_system_packs) - len(set(automatic_system_packs))
                        #     for dt in date_pack_count_dict:
                        #         if dt >= pack_fill_schedule_date_dict[pack]:
                        #             date_pack_count_dict[dt] -= ln

                        for k, v in date_pack_count_dict.items():
                            if v <= 0 and k in total_schedule_dates:
                                del date_pack_count_dict_cpy[k]
                                indx = total_schedule_dates.index(k)
                                for ind in range(indx + 1):
                                    del total_schedule_dates[0]
                        # break
                else:
                    manual_pack_list.extend(self.patient_packs[patient])
                    manual_patient_list.append(patient)
                    # self.pending_patients.append(patient)

            # if self.patient_packs[patient_tuple[0]] not in automatic_system_packs:
            #     copy_sorted_pack_list.remove(patient_tuple)
        self.output_dict['date_patient_dict'] = date_patient_dict
        self.output_dict['automatic_system_patients'] = automatic_system_patients
        total_schedule_dates_automatic = []
        for patient in automatic_system_patients:
            if self.patient_fill_schedule_date_dict[patient] not in total_schedule_dates_automatic:
                total_schedule_dates_automatic.append(self.patient_fill_schedule_date_dict[patient])

        total_schedule_dates_automatic = sorted(total_schedule_dates_automatic)
        automatic_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in total_schedule_dates_automatic:
            date_str = date.split(' ')
            if date not in automatic_system_region_wise_date_capacity_dict:
                automatic_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(total_schedule_dates_automatic):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (total_schedule_dates_automatic.index(date)) - 1
                fdate = total_schedule_dates_automatic[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

        '''
        6)
        '''
        total_schedule_dates_manual = []
        manual_patient_list.reverse()
        for patient in manual_patient_list:
            if self.patient_fill_schedule_date_dict[patient] not in total_schedule_dates_manual:
                total_schedule_dates_manual.append(self.patient_fill_schedule_date_dict[patient])

        total_schedule_dates_manual = sorted(total_schedule_dates_manual)
        date_extra_hours_manual = get_extra_hours_dao(date_list, 5)
        date_pack_count_dict_manual = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        current_date = str(current_date)
        for date in total_schedule_dates_manual:
            date = date.split(' ')
            if date[0] not in date_pack_count_dict_manual:
                date_pack_count_dict_manual[date[0]] = 0
            f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                   int(current_date.split("-")[2]))
            l_date = datetime.date(int(date[0].split("-")[0]), int(date[0].split("-")[1]), int(date[0].split("-")[2]))

            days = (l_date - f_date).days
            upto_schedule_date_list_manual = []
            for i in range(days):
                upto_schedule_date_list_manual.append(f_date)
                f_date += datetime.timedelta(days=1)
            if len(date_list) != 0:
                date_list.remove(max(date_list))
            for date_i in upto_schedule_date_list_manual:
                if date_day_dict[str(date_i)] == settings.SATURDAY:
                    date_pack_count_dict_manual[date[0]] += (MANUAL_PER_HOUR * MANUAL_SATURDAY_HOURS)
                elif date_day_dict[str(date_i)] == settings.SUNDAY:
                    date_pack_count_dict_manual[date[0]] += (MANUAL_PER_HOUR * MANUAL_SUNDAY_HOURS)
                else:
                    date_pack_count_dict_manual[date[0]] += (MANUAL_PER_HOUR * MANUAL_PER_DAY_HOURS)
                if str(date_i) in date_extra_hours_manual.keys():
                    date_pack_count_dict_manual[date[0]] = date_pack_count_dict_manual[date[0]] + (
                            MANUAL_PER_HOUR * date_extra_hours_manual[str(date_i)])

        manual_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in total_schedule_dates_manual:
            date_str = date.split(' ')
            if date_str[0] not in manual_system_region_wise_date_capacity_dict:
                manual_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(total_schedule_dates_manual):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SUNDAY_HOURS)
                    else:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_PER_DAY_HOURS)
                    if str(date_i) in date_extra_hours_manual.keys():
                        manual_system_region_wise_date_capacity_dict[date_str[0]] = \
                        manual_system_region_wise_date_capacity_dict[date_str[0]] + (
                                MANUAL_PER_HOUR * date_extra_hours_manual[str(date_i)])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (total_schedule_dates_manual.index(date)) - 1
                fdate = total_schedule_dates_manual[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SUNDAY_HOURS)
                    else:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_PER_DAY_HOURS)
                    if str(date_i) in date_extra_hours_manual.keys():
                        manual_system_region_wise_date_capacity_dict[date_str[0]] = \
                        manual_system_region_wise_date_capacity_dict[date_str[0]] + (
                                MANUAL_PER_HOUR * date_extra_hours_manual[str(date_i)])

        overloaded_pack_list = []
        overloaded_patient_list = []
        manual_patient_list_extend = []
        overloaded_patient_datewise = {}
        for date in self.total_schedule_dates:
            overloaded_patient_datewise[date] = set()
        # total_schedule_dates = []
        manual_system_packs = []
        date_pack_dict = {}

        date_pack_count_dict_manual_cpy = deepcopy(date_pack_count_dict_manual)
        # for pack in manual_pack_list:
        #     if pack_fill_schedule_date_dict[pack] not in total_schedule_dates:
        #         total_schedule_dates.append(pack_fill_schedule_date_dict[pack])

        total_schedule_dates = sorted(total_schedule_dates_manual)

        for k, v in date_pack_count_dict_manual.items():
            if v <= 0 and k in total_schedule_dates:
                del date_pack_count_dict_manual_cpy[k]
                indx = total_schedule_dates.index(k)
                for ind in range(indx + 1):
                    del total_schedule_dates[0]

        for patient in manual_patient_list:
            if patient in self.patient_fill_schedule_date_dict:
                if self.patient_fill_schedule_date_dict[patient] in total_schedule_dates:
                    manual_system_packs.extend(self.patient_packs[patient])
                    manual_patient_list_extend.append(patient)

                    if self.patient_fill_schedule_date_dict[patient] not in date_pack_dict:
                        date_pack_dict[self.patient_fill_schedule_date_dict[patient]] = set()
                    date_pack_dict[self.patient_fill_schedule_date_dict[patient]].update(self.patient_packs[patient])
                    for dt in date_pack_count_dict_manual:
                        if dt >= self.patient_fill_schedule_date_dict[patient]:
                            if date_pack_count_dict_manual[self.patient_fill_schedule_date_dict[patient]] < 0:
                                date_pack_count_dict_manual[dt] -= (date_pack_count_dict_manual[
                                                                        self.patient_fill_schedule_date_dict[
                                                                            patient]] + len(
                                    self.patient_packs[patient]))
                            else:
                                date_pack_count_dict_manual[dt] -= len(self.patient_packs[patient])
                    if len(list(filter(lambda y: (y <= 0), list(date_pack_count_dict_manual.values())))) > 0:

                        # if len(self.patient_packs[patient_tuple[0]]) > 0:
                        #     automatic_system_packs.extend(list(map(int, self.patient_packs[patient_tuple[0]])))
                        #     ln = len(automatic_system_packs) - len(set(automatic_system_packs))
                        #     for dt in date_pack_count_dict:
                        #         if dt >= pack_fill_schedule_date_dict[pack]:
                        #             date_pack_count_dict[dt] -= ln

                        for k, v in date_pack_count_dict_manual.items():
                            if v <= 0 and k in total_schedule_dates:
                                del date_pack_count_dict_manual_cpy[k]
                                indx = total_schedule_dates.index(k)
                                for ind in range(indx + 1):
                                    del total_schedule_dates[0]
                        # break
                else:
                    overloaded_pack_list.extend(self.patient_packs[patient])
                    overloaded_patient_list.append(patient)
                    if patient in self.patient_fill_schedule_date_dict:
                        overloaded_patient_datewise[self.patient_fill_schedule_date_dict[patient]].update(
                            self.patient_packs[patient])

        self.output_dict['manual_patient_list_extend'] = manual_patient_list_extend

        total_schedule_dates_manual = []
        for patient in manual_patient_list_extend:
            if self.patient_fill_schedule_date_dict[patient] not in total_schedule_dates_manual:
                total_schedule_dates_manual.append(self.patient_fill_schedule_date_dict[patient])

        manual_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in total_schedule_dates_manual:
            date_str = date.split(' ')
            if date_str[0] not in manual_system_region_wise_date_capacity_dict:
                manual_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(total_schedule_dates_manual):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SUNDAY_HOURS)
                    else:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_PER_DAY_HOURS)
                    if str(date_i) in date_extra_hours_manual.keys():
                        manual_system_region_wise_date_capacity_dict[date_str[0]] = \
                        manual_system_region_wise_date_capacity_dict[date_str[0]] + (
                                MANUAL_PER_HOUR * date_extra_hours_manual[str(date_i)])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (total_schedule_dates_manual.index(date)) - 1
                fdate = total_schedule_dates_manual[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_SUNDAY_HOURS)
                    else:
                        manual_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    MANUAL_PER_HOUR * MANUAL_PER_DAY_HOURS)
                    if str(date_i) in date_extra_hours_manual.keys():
                        manual_system_region_wise_date_capacity_dict[date_str[0]] = \
                        manual_system_region_wise_date_capacity_dict[date_str[0]] + (
                                MANUAL_PER_HOUR * date_extra_hours_manual[str(date_i)])

        automatic_system_patients = list(map(int, automatic_system_patients))
        manual_system_patients = list(map(int, manual_patient_list_extend))
        overloaded_patients = list(map(int, overloaded_patient_list))
        overloaded_packs = []
        overloaded_patient_datewise_sorted = {k: v for k, v in
                                              sorted(overloaded_patient_datewise.items(), key=lambda item: item[0],
                                                     reverse=True)}
        split_info = {"automatic_system_patients": automatic_system_patients,
                      "manual_system_patients": manual_system_patients, "overloaded_patients": overloaded_patients,
                      "output_dict": self.output_dict,
                      "overloaded_patient_datewise": overloaded_patient_datewise_sorted}
        return split_info, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict, manual_system_region_wise_date_capacity_dict, manual_system_packs, overloaded_pack_list

    def get_system_split_facility(self, sorted_pack_list, total_packs):
        """
        1) List total fill schedule dates for which we need to fill some packs
        2) Make list of dates in which we can fill packs
        3)form date to weekdays dictionary
        4)Make datewise upto pak count dictionary (Till this(fill_schedule date) date based on current date , we can fill this number of packs based on robot fill capacity per day)
        5)Core Logic based on delivery date
            -> date_pack_count_dict(which we made in step 4)
            -> total_schedule_dates list
        6)Make Manual pack list

        :param sorted_pack_list:
        :param facility_fill_schedule_date_dict:
        :param total_packs:
        :param facility_packs:
        :return:
        """

        '''
        1)
        '''
        self.total_schedule_dates = []
        for date in self.facility_fill_schedule_date_dict.values():
            self.total_schedule_dates.append(date)
        self.total_schedule_dates = sorted(list(set(self.total_schedule_dates)))

        '''
        2)
        '''
        # Find total date range for imported packs
        # total_date_range = []
        # numdays = math.ceil(len(total_packs)/settings.ROBOT_CAPACITY_PER_DAY)
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        base = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                             int(current_date.split("-")[2]))  # datetime.str(datetime.date.today()
        max_date = max(self.total_schedule_dates)
        max_date = max_date.split(' ')
        final_date = datetime.date(int(max_date[0].split("-")[0]), int(max_date[0].split("-")[1]),
                                   int(max_date[0].split("-")[2]))
        numdays = (final_date - base).days + 1
        date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]

        AUTOMATIC_PER_DAY_HOURS = int(self.system_timings['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(self.system_timings['AUTOMATIC_PER_HOUR'])
        MANUAL_PER_DAY_HOURS = int(self.system_timings['MANUAL_PER_DAY_HOURS']) * len(self.manual_user_id)
        MANUAL_PER_HOUR = int(self.system_timings['MANUAL_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(self.system_timings['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(self.system_timings['AUTOMATIC_SUNDAY_HOURS'])
        MANUAL_SUNDAY_HOURS = int(self.system_timings['MANUAL_SUNDAY_HOURS']) * len(self.manual_user_id)
        MANUAL_SATURDAY_HOURS = int(self.system_timings['MANUAL_SATURDAY_HOURS']) * len(self.manual_user_id)

        '''
        3)
        '''
        # Form date weekday dict
        date_day_dict = {}
        for date in date_list:
            date = str(date)
            date_day_dict[date] = self.get_weekdays(int(date.split("-")[0]), int(date.split("-")[1]),
                                                    int(date.split("-")[2]))

        '''
        4)
        '''
        # datewise upto pack count for automatic
        date_extra_hours_automatic = get_extra_hours_dao(date_list, 2)
        date_pack_count_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        current_date = str(current_date)
        for date in self.total_schedule_dates:
            date = date.split(' ')
            if date[0] not in date_pack_count_dict:
                date_pack_count_dict[date[0]] = 0
            f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                   int(current_date.split("-")[2]))
            l_date = datetime.date(int(date[0].split("-")[0]), int(date[0].split("-")[1]), int(date[0].split("-")[2]))

            days = (l_date - f_date).days
            upto_schedule_date_list = []
            for i in range(days):
                upto_schedule_date_list.append(f_date)
                f_date += datetime.timedelta(days=1)
            if len(date_list) != 0:
                date_list.remove(max(date_list))
            for date_i in upto_schedule_date_list:
                if date_day_dict[str(date_i)] == settings.SATURDAY:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)

                elif date_day_dict[str(date_i)] == settings.SUNDAY:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                else:
                    date_pack_count_dict[date[0]] += (AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)

                if str(date_i) in date_extra_hours_automatic.keys():
                    date_pack_count_dict[date[0]] = date_pack_count_dict[date[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_i)])

            if date[0] in date_extra_hours_automatic.keys():
                date_pack_count_dict[date[0]] = date_pack_count_dict[date[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[date[0]])

        # datewise upto pack count for manual
        # date_pack_count_dict_manual = {}
        # current_date = '2019-11-25'
        # current_date = str(current_date)
        # for date in self.total_schedule_dates:
        #     if date not in date_pack_count_dict_manual:
        #         date_pack_count_dict_manual[date] = 0
        #     f_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
        #     l_date = datetime.date(2019, int(date.split("-")[1]), int(date.split("-")[2]))
        #
        #     days = (l_date - f_date).days
        #     upto_schedule_date_list_manual = []
        #     for i in range(days):
        #         upto_schedule_date_list_manual.append(f_date)
        #         f_date += datetime.timedelta(days=1)
        #     date_list.remove(max(date_list))
        #     for date_i in upto_schedule_date_list_manual:
        #         if date_day_dict[str(date_i)] == settings.SATURDAY:
        #             date_pack_count_dict_manual[date] += (settings.MANUAL_CAPACITY_FOR_SATURDAY)
        #         elif date_day_dict[str(date_i)] == settings.SUNDAY:
        #             date_pack_count_dict_manual[date] += (settings.MANUAL_CAPACITY_FOR_SUNDAY)
        #         else:
        #             date_pack_count_dict_manual[date] += settings.MANUAL_CAPACITY_PER_DAY

        # Make region wise date pack capacity dict
        automatic_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in self.total_schedule_dates:
            date_str = date.split(' ')
            if date not in automatic_system_region_wise_date_capacity_dict:
                automatic_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(self.total_schedule_dates):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (self.total_schedule_dates.index(date)) - 1
                fdate = self.total_schedule_dates[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

        pack_fill_schedule_date_dict = {}
        total_facilities = []

        for f, d in self.facility_fill_schedule_date_dict.items():
            total_facilities.append(f)
            # for pack in self.patient_packs[p]:
            #     pack_fill_schedule_date_dict[int(pack)] = d
        '''
        5)
        '''
        # Core Logic
        date_pack_dict = {}
        date_patient_dict = {}
        automatic_system_packs = []
        automatic_system_patients = []
        automatic_system_facilities = []
        manual_pack_list = []
        manual_patient_list = []
        date_pack_count_dict_cpy = deepcopy(date_pack_count_dict)
        copy_sorted_pack_list = deepcopy(sorted_pack_list)
        x = []
        total_schedule_dates = sorted(self.total_schedule_dates)

        for k, v in date_pack_count_dict.items():
            if v <= 0 and k in total_schedule_dates:
                del date_pack_count_dict_cpy[k]
                indx = total_schedule_dates.index(k)
                for ind in range(indx + 1):
                    del total_schedule_dates[0]

        # for patient_tuple in total_packs:
        for facility in total_facilities:
            facility = int(facility)

            if facility in self.facility_fill_schedule_date_dict:
                if self.facility_fill_schedule_date_dict[facility] in total_schedule_dates:
                    automatic_system_packs.extend(self.facility_packs[facility])
                    automatic_system_facilities.append(facility)
                    self.pending_facilities.remove(facility)
                    if self.facility_fill_schedule_date_dict[facility] not in date_patient_dict:
                        date_patient_dict[self.facility_fill_schedule_date_dict[facility]] = set()
                    date_patient_dict[self.facility_fill_schedule_date_dict[facility]].add(facility)
                    if self.facility_fill_schedule_date_dict[facility] not in date_pack_dict:
                        date_pack_dict[self.facility_fill_schedule_date_dict[facility]] = set()
                    date_pack_dict[self.facility_fill_schedule_date_dict[facility]].update(
                        self.facility_packs[facility])
                    for dt in date_pack_count_dict:
                        if dt >= self.facility_fill_schedule_date_dict[facility]:
                            if date_pack_count_dict[self.facility_fill_schedule_date_dict[facility]] < 0:
                                date_pack_count_dict[dt] -= (
                                            date_pack_count_dict[self.facility_fill_schedule_date_dict[facility]] + len(
                                        self.facility_packs[facility]))
                            else:
                                date_pack_count_dict[dt] -= len(self.facility_packs[facility])
                    if len(list(filter(lambda y: (y <= 0), list(date_pack_count_dict.values())))) > 0:
                        # if len(self.patient_packs[patient_tuple[0]]) > 0:
                        #     automatic_system_packs.extend(list(map(int,self.patient_packs[patient_tuple[0]])))
                        #     ln = len(automatic_system_packs) - len(set(automatic_system_packs))
                        #     for dt in date_pack_count_dict:
                        #         if dt >= pack_fill_schedule_date_dict[pack]:
                        #             date_pack_count_dict[dt] -= ln

                        for k, v in date_pack_count_dict.items():
                            if v <= 0 and k in total_schedule_dates:
                                del date_pack_count_dict_cpy[k]
                                indx = total_schedule_dates.index(k)
                                for ind in range(indx + 1):
                                    del total_schedule_dates[0]
                        # break
                else:
                    # manual_pack_list.extend(self.patient_packs[patient])
                    # manual_patient_list.append(patient)
                    print("p")
            # if self.patient_packs[patient_tuple[0]] not in automatic_system_packs:
            #     copy_sorted_pack_list.remove(patient_tuple)
        self.output_dict['date_patient_dict'] = date_patient_dict
        self.output_dict['automatic_system_facilities'] = automatic_system_facilities
        total_schedule_dates_automatic = []
        for facility in automatic_system_facilities:
            if self.facility_fill_schedule_date_dict[facility] not in total_schedule_dates_automatic:
                total_schedule_dates_automatic.append(self.facility_fill_schedule_date_dict[facility])

        total_schedule_dates_automatic = sorted(total_schedule_dates_automatic)
        automatic_system_region_wise_date_capacity_dict = {}
        current_date = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())
        for date in total_schedule_dates_automatic:
            date_str = date.split(' ')
            if date not in automatic_system_region_wise_date_capacity_dict:
                automatic_system_region_wise_date_capacity_dict[date_str[0]] = 0
            if date == min(total_schedule_dates_automatic):
                f_date = datetime.date(int(current_date.split("-")[0]), int(current_date.split("-")[1]),
                                       int(current_date.split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))
                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

            else:
                # current_date = datetime.date(2019, int(current_date.split("-")[1]), int(current_date.split("-")[2]))
                date_index = (total_schedule_dates_automatic.index(date)) - 1
                fdate = total_schedule_dates_automatic[date_index]
                fdate = fdate.split(' ')
                f_date = datetime.date(int(fdate[0].split("-")[0]), int(fdate[0].split("-")[1]),
                                       int(fdate[0].split("-")[2]))
                l_date = datetime.date(int(date_str[0].split("-")[0]), int(date_str[0].split("-")[1]),
                                       int(date_str[0].split("-")[2]))

                days = (l_date - f_date).days
                upto_schedule_date_list = []
                for i in range(days):
                    # f_date += datetime.timedelta(days=1)
                    upto_schedule_date_list.append(f_date)
                    f_date += datetime.timedelta(days=1)

                for date_i in upto_schedule_date_list:
                    if date_day_dict[str(date_i)] == settings.SATURDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS)
                    elif date_day_dict[str(date_i)] == settings.SUNDAY:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS)
                    else:
                        automatic_system_region_wise_date_capacity_dict[date_str[0]] += (
                                    AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS)
                if str(date_str[0]) in date_extra_hours_automatic.keys():
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] = \
                    automatic_system_region_wise_date_capacity_dict[date_str[0]] + (
                            AUTOMATIC_PER_HOUR * date_extra_hours_automatic[str(date_str[0])])

        split_info = {"automatic_system_facilities": automatic_system_facilities, "output_dict": self.output_dict}
        return split_info, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict

    def get_weekdays(self, year, month, day):

        thisXMas = datetime.date(year, month, day)
        thisXMasDay = thisXMas.weekday()
        weekday = settings.WEEKDAYS[thisXMasDay]
        return weekday


# DRY RUN and TEST FUNCTIONS
@log_args_and_response
def get_current_split(analysis, canister_dict, fully_manual_pack_drug):
    data = list()
    duplicate_check_lookup = set()
    for pack, drugs in analysis.items():
        pack = int(pack)
        for drug in drugs:
            canister = drug[1]
            if not canister or (pack, drug[0]) in fully_manual_pack_drug:
                continue  # manual because of no canister or half pills
            current_robot = canister_dict[canister][0]

            if canister and (pack, current_robot) not in duplicate_check_lookup:
                duplicate_check_lookup.add((pack, current_robot))
                data.append({
                    'pack': pack,
                    'robot': current_robot
                })
    df = pd.DataFrame(data, columns=['pack', 'robot'])
    df = df.fillna(0)
    df['robot'] = df['robot'].astype(int)
    # df['robot'] = pd.to_numeric(df['robot'])
    return data, df.groupby('robot')['pack'].count().to_dict()


def test_canister_recommend_add(company_id):
    recommend_canister_to_register({
        'company_id': company_id
    })


def get_initial_clusters_of_packs(pack_list, company_id, system_id, drops=0, pack_delivery_date_dict={}):
    """
    This function runs canister recommendation function and will give two clusters of packs with all its informations
    1) Prepare required data for cansiter recommendation algorithm
    2) Run canister Recommendation algorithm and get Two clusters
    :param pack_schedule_date_dict:
    :param pack_list:
    :param company_id:
    :param system_id:
    :return:
    """

    '''
    1)
    '''

    pack_half_pill_drug_dict = {}

    try:
        pack_ids_set, drug_ids_set, \
        pack_mapping, cache_drug_data, \
        pack_manual, pack_drug_manual, \
        facility_packs = get_pack_data(pack_list, company_id)

        pack_drug_slot_id_dict = get_pack_drug_slot_data(pack_list)
        pack_drug_slot_number_slot_id_dict = get_pack_drug_slot_details(pack_list)

        system_zone_mapping, zone_list = get_system_zone_mapping(system_id)

        canister_location, drug_canisters, canister_data, canister_expiry_status_dict = get_canister_data(company_id, zone_list=zone_list,
                                                                             ignore_reserved=True)
        robot_ids, robots_data, robot_capacity, \
        system_robots = get_robot_data_batch_sch(system_id_list=system_id)

        robot_max_canisters = {robot['id']: robot['max_canisters'] for system, robots in robots_data.items()
                               for robot in robots}

        robot_empty_locations = LocationMaster.db_get_empty_locationsV3(robot_max_canisters)

        pack_slot_drug_dict, pack_slot_detail_drug_dict, pack_drug_half_pill_slots_dict = get_pack_slotwise_drugs(pack_list)

        df, column_list = create_dataset(
            pack_ids_set,
            drug_ids_set,
            pack_mapping
        )

        for pack in pack_list:
            for drug in pack_drug_manual[pack]:
                if pack_drug_manual[pack][drug]:
                    pack_half_pill_drug_dict[pack] = []
                    pack_half_pill_drug_dict[pack].append(drug)

        '''
        2)
        '''

        rct = RecommendCanistersToTransfer(file_name=None, df=df,
                                           robot_capacity_info_dict=robot_capacity,
                                           drug_canister_info_dict=drug_canisters,
                                           canister_location_info_dict=canister_location,
                                           canister_expiry_status_dict=canister_expiry_status_dict,
                                           robot_free_location_info_dict=robot_empty_locations,
                                           robot_list=system_robots[system_id[0]],
                                           pack_drug_manual_dict=pack_drug_manual,
                                           pack_half_pill_drug_dict=pack_half_pill_drug_dict,
                                           total_packs=pack_list, pack_slot_drug_dict=pack_slot_drug_dict,
                                           pack_drug_slot_number_slot_id_dict=pack_drug_slot_number_slot_id_dict,
                                           total_robots=len(system_robots[system_id[0]]),
                                           pack_drug_half_pill_slots_dict=pack_drug_half_pill_slots_dict, pack_delivery_date=pack_delivery_date_dict)

        if drops:
            canister_transfer_info_dict,analysis = rct.recommend_canisters_to_transfer_v3()
            max_quad_count = get_max_quadrant_canister_count(canister_transfer_info_dict)
            return max_quad_count
        multi_split_info = rct.recommend_multiple_split(batch_formation=True)

        return multi_split_info

    except Exception as e:
        logger.error(e)
        raise error(0)


@log_args_and_response
def overloaded_packs_distribution(split_info, manual_users, system_timings, overload_distribution_type=None):
    try:
        #  TODO : add in system setting capacity for manual hours and change this to dynamic
        MANUAL_PER_HOUR = int(system_timings['MANUAL_PER_HOUR'])

        if overload_distribution_type == "automatic":
            system_list = split_info['system_list']
            overloaded_distribution = {"automatic": []}
        elif overload_distribution_type == "manual":
            overloaded_distribution = {"manual": []}
        else:
            system_list = split_info['system_list']
            overloaded_distribution = {"automatic": [], "manual": [], "both": []}
        date_list = list(split_info['overloaded_patient_datewise'].keys())

        ordered_overloaded_patient_datewise = OrderedDict(
            sorted(split_info['overloaded_patient_datewise'].items(), key=lambda date: date[0]))

        overloaded_patient_datewise = {}

        for overload_date, overload_pack in ordered_overloaded_patient_datewise.items():
            overloaded_patient_datewise[overload_date] = len(overload_pack)
        logger.info("overloaded_patient_datewise {}".format(ordered_overloaded_patient_datewise))
        split_date = {}
        pack_count = []
        split_date_packs = dict()
        to_add = []

        while len(date_list) != 0:
            for dates, packs in ordered_overloaded_patient_datewise.items():
                count_list = [len(values) for values in ordered_overloaded_patient_datewise.values()]
                if len(packs) == 0 and len(split_date) > 0:
                    to_add.append(dates)
                elif len(packs) == 0 and len(split_date) == 0:
                    split_date[dates] = len(packs)
                    split_date_packs[dates] = packs
                    break
                elif len(packs) > 0 and 0 in count_list and len(split_date) > 0 and len(to_add) > 0:
                    break
                elif len(packs) > 0 and 0 in count_list and len(to_add) == 0:
                    split_date[dates] = len(packs)
                    split_date_packs[dates] = packs
                    pack_count.append(len(packs))

                elif len(packs) > 0 and 0 not in count_list:
                    split_date[dates] = len(packs)
                    split_date_packs[dates] = packs
                    break

            for s_date in split_date.keys():
                date_list.remove(s_date)
                del ordered_overloaded_patient_datewise[s_date]
            if len(to_add) > 0:
                for date in to_add:
                    date_list.remove(date)
                    del ordered_overloaded_patient_datewise[date]
            if len(pack_count) > 0 and len(split_date) > 0 and len(to_add) > 0:
                max_pack = max(split_date, key=split_date.get)
                if split_date[max_pack] >= len(to_add) + 1:
                    split = math.ceil(split_date[max_pack] / (len(to_add) + 1))
                    for add_date in to_add:
                        overloaded_patient_datewise[add_date] = split
                    overloaded_patient_datewise[max_pack] = split
                else:
                    for add_date in to_add:
                        split_date[max_pack] -= 1
                        overloaded_patient_datewise[add_date] = 1
                        if split_date[max_pack] == 1:
                            break
                    overloaded_patient_datewise[max_pack] = 1

            split_date.clear()
            pack_count.clear()
            to_add.clear()
        logger.info("overloaded_patient_datewise {}".format(overloaded_patient_datewise))
        for date, pack_no in overloaded_patient_datewise.items():
            if pack_no > 0:
                if overload_distribution_type == "automatic":
                    packs = list(range(1, pack_no + 1))
                    system_wise_pack = collections.defaultdict(list)

                    for i, pack in enumerate(packs):  # get the index of the number and the number
                        system = system_list[i % len(system_list)]  # round-robin over the employees...
                        system_wise_pack[system].append(pack)  # ... and associate a number with a name.

                    for each_system in system_list:
                        AUTOMATIC_PER_HOUR = int(system_timings[each_system]['AUTOMATIC_PER_HOUR'])
                        extra_auto = len(system_wise_pack[each_system]) / AUTOMATIC_PER_HOUR
                        extra_min_auto = (extra_auto - int(extra_auto)) * 60
                        extra_auto_hours = {"hours": int(extra_auto), "min": (round(extra_min_auto))}
                        overloaded_distribution["automatic"].append(
                            {"fill_date": date, "pack_count": len(system_wise_pack[each_system]),
                             'extra_working_hours': extra_auto_hours, 'system': each_system,
                             'pack_list': split_date_packs[date]})

                elif overload_distribution_type == "manual":
                    extra_manu = pack_no / (MANUAL_PER_HOUR * manual_users)
                    extra_min_manual = (extra_manu - int(extra_manu)) * 60
                    extra_manu_hours = {"hours": int(extra_manu), "min": (round(extra_min_manual))}
                    overloaded_distribution["manual"].append(
                        {"fill_date": date, "pack_count": pack_no,
                         'extra_working_hours': extra_manu_hours,
                         'pack_list': split_date_packs[date]})

                elif overload_distribution_type == "both":
                    extra_both = pack_no / (
                            AUTOMATIC_PER_HOUR + (MANUAL_PER_HOUR * manual_users))
                    extra_min_both = (extra_both - int(extra_both)) * 60
                    extra_both_hours = {"hours": int(extra_both), "min": (round(extra_min_both))}
                    overloaded_distribution["both"].append({"fill_date": date,
                                                            'pack_list': split_date_packs[date],
                                                            "pack_count": {
                                                                "automatic": round(extra_both * AUTOMATIC_PER_HOUR),
                                                                "manual": round(
                                                                    extra_both * MANUAL_PER_HOUR * manual_users)},
                                                            'extra_working_hours': {"automated": extra_both_hours,
                                                                                    "manual": extra_both_hours}})
                    logger.info("overloaded_distribution {}".format(overloaded_distribution))
        return overloaded_distribution

    except Exception as e:
        logger.info(e)
        raise


@log_args_and_response
def get_max_quadrant_canister_count(canister_transfer_info_dict):
    robot_quad_canister_count = {}
    for canister,tpl in canister_transfer_info_dict.items():
        if tpl[1] not in robot_quad_canister_count:
            robot_quad_canister_count[tpl[1]] = {}
        if tpl[4] not in robot_quad_canister_count[tpl[1]]:
            robot_quad_canister_count[tpl[1]][tpl[4]] = 0
        robot_quad_canister_count[tpl[1]][tpl[4]] += 1
    max_count = 0
    max_count_quad = 0
    for robot,quad_data in  robot_quad_canister_count.items():
        for quad,count in quad_data.items():
            if count >= max_count:
                max_count_quad = deepcopy(quad)
                max_count = deepcopy(count)
    return max_count


@log_args_and_response
def get_alternate_drug_data_to_save(company_id, pack_list, user_id, zone_old_new_drug_dict, zone):
    """
    This function makes the argument data for alternate drug saving api which will be called at the time of batch save.
    :param company_id:
    :param pack_list:
    :param user_id:
    :param zone_old_new_drug_dict:
    :param zone:
    :return:
    """
    olddruglist = list(zone_old_new_drug_dict[zone].keys())
    newdruglist = list(zone_old_new_drug_dict[zone].values())
    try:
        if len(olddruglist) == 0:
            dict_alternate_drug_info = {}
            return dict_alternate_drug_info
        list(map(int, olddruglist))
        pack_list = list(map(int, pack_list))

        dict_alternate_drug_info = {"olddruglist": olddruglist, "newdruglist": newdruglist,
                                    "company_id": company_id, "user_id": user_id,
                                    "pack_list": pack_list}
        return dict_alternate_drug_info
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=['company_id', 'system_id', 'facility_distribution_id', 'user_id'])
def get_patient_data(args):
    company_id = args['company_id']
    system_id = args['system_id']
    user_id = args['user_id']
    logger.info("Input for get_patient_data {}".format(args))
    """
    parameters will come in case when this api is called to overload screen.
    automatic_system: list of automatic system that user has selected for processing the overloaded packs
    manual_user_id: list of manual users id which user has selected for processing the overloaded packs
                    this parameters can be none but one from them is mandatory.
    overloaded_patients: list of overloaded patients that was generated when batch distribution was called
    """
    automatic_system = args.get('automatic_system', None)
    manual_user_id = args.get('manual_user_id', None)
    overloaded_pack_list = args.get('overloaded_pack_list', None)

    json_data = {}
    json_data['input'] = args

    try:
        """
        Condition to check weather the call is to distribute packs and create batch or distribute overloaded packs
        Overloaded pack list is None when we want to disctibute packs in batches
        """
        if overloaded_pack_list is None and automatic_system is None:
            # TODO : remove overloaded packs code from this part
            # pack_list = PackDetails.get_packs_by_facility_distribution_id(args['facility_distribution_id'],
            #                                                               company_id)
            pack_list = get_packs_by_facility_distribution_id(facility_distribution_id=args['facility_distribution_id'],
                                                              company_id=company_id)
            logger.info('Length of pack list: {}'.format(len(pack_list)))

            if not len(pack_list):
                return error(2008)

            # TODO : Uncomment this when data is available in device_layout_details table and comment static dict
            zone_system_dict = get_zone_wise_system_ids(system_id)
            # zone_system_dict = {1:[2],2:[3]}
            zone_list = list(zone_system_dict.keys())
            zone_canister_drug_dict, canister_drug_zone_dict = get_zone_wise_canister_drugs(company_id, zone_list)

            drug_alternate_drug_dict, drug_zone_alternate_drug_dict, fndc_txr_drug_id_dict, alternate_fndc_txr_drug_id_dict = get_alternate_drug_data(
                company_id, pack_list, user_id, args['facility_distribution_id'])

            # zone_drug_dict = get_zone_wise_drug_data(company_id)
            patient_drug_alternate_flag_dict = get_patient_drug_alternate_flag_data(pack_list)
            patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, pack_list)

            # patient_fndc_txr_drug_id_dict = PackDetails.db_get_drug_ids_by_patient(company_id, pack_list)

            zone_patient_drug_dict, zone_old_new_drug_dict = get_zone_wise_patient_drugs_with_alternate_drug(
                patient_drugs, patient_drug_alternate_flag_dict, drug_alternate_drug_dict,
                drug_zone_alternate_drug_dict, zone_canister_drug_dict, canister_drug_zone_dict, zone_list,
                fndc_txr_drug_id_dict, patient_packs, alternate_fndc_txr_drug_id_dict)

            system_max_batch_id_dict = get_system_wise_batch_id(system_id)
            pack_slot_drug_dict = get_pack_slot_drug_data(pack_list)
            # zone_pack_slot_drug_dict = get_zone_wise_pack_slot_drug_data(zone_list, patient_packs,
            #                                                              pack_slot_drug_dict,
            #                                                              drug_alternate_drug_dict,
            #                                                              patient_drug_alternate_flag_dict,
            #                                                              drug_zone_alternate_drug_dict)

            system_end_date_dict = {}

            for system, batch in system_max_batch_id_dict.items():
                system_info = get_system_setting_by_system_id(system_id=system)
                total_packs, scheduled_start_date = get_batch_scheduled_start_date_and_packs(batch)
                scheduled_end_date = get_end_date(system_info, total_packs, scheduled_start_date)
                system_end_date_dict[system] = scheduled_end_date

            total_patients = [patient for patient in patient_packs.keys()]
            patient_facility_dict = get_patient_facility_id_data(total_patients)
            patient_delivery_date_dict = get_pack_wise_delivery_date(pack_list)
            pack_drugs = db_get_pack_drugs_by_pack(company_id, pack_list)
            canister_drugs = db_get_canister_fndc_txr(company_id)

            # patient_id_name_dict = PatientMaster.db_get_patient_name_from_patient_id(
            #     list(patient_delivery_date_dict.keys()))
            patient_id_name_dict = db_get_patient_name_from_patient_id_dao(patient_delivery_date_dict)

            pack_half_pill_drug_drop_count = db_get_half_pill_drug_drop_by_pack_id(list(pack_list))

            zone_facility_drug_dict, facility_packs, facility_delivery_date_dict, facility_patients = \
                get_facility_wise_data_from_patient(zone_patient_drug_dict, patient_packs, patient_delivery_date_dict,
                                                    patient_facility_dict)

            system_wise_batch_info = {}
            system_patient_dict = {}
            total_patients = []
            total_packs = []
            pending_patients = []
            total_facilities = []
            pending_facilities = []
            pack_list = set()
            system_patients = set()
            sorted_patient = OrderedDict()
            split_info = {}
            pack_delivery_date_dict = {}
            over_loaded_pack_dict = {}
            overloaded_packs = set()
            alternate_drug_save_info = {}

            zone_system_dict = get_ordered_zone_system_data(zone_system_dict)
            system_patient_drugs = {}

            if settings.PATIENT_WISE:
                for zone, systems in zone_system_dict.items():

                    system_patient_drugs[systems[0]] = {}
                    pack_list = set()
                    if len(pending_patients) == 0:
                        for patient, packs in patient_packs.items():
                            total_packs.extend(packs)
                            total_patients.append(patient)
                            pending_patients.append(patient)

                    system_timings = get_system_setting_by_system_id(system_id=systems[0])
                    am = AutomaticManualDistributionRecommender(zone_facility_drug_dict=zone_facility_drug_dict,
                                                                facility_packs=facility_packs,
                                                                facility_delivery_date_dict=facility_delivery_date_dict,
                                                                facility_patients=facility_patients,
                                                                patient_packs=patient_packs,
                                                                zone_patient_drugs=zone_patient_drug_dict,
                                                                patient_delivery_date_dict=patient_delivery_date_dict,
                                                                manual_user_id=manual_user_id,
                                                                system_timings=system_timings,
                                                                zone_canister_drug_dict=zone_canister_drug_dict,
                                                                current_system=systems[0],
                                                                pack_half_pill_drug_drop_count=pack_half_pill_drug_drop_count)

                    split_info, patient_fill_schedule_date_dict, date_pack_count_dict,\
                    automatic_system_region_wise_date_capacity_dict, manual_system_region_wise_date_capacity_dict,\
                    manual_system_packs, overloaded_pack_list, sorted_pack_list, pending_patients_sys,\
                    sorted_patient_list = am.get_split_recommendations(zone, pending_patients)

                    pending_patients = pending_patients_sys
                    # TODO: change it for multisystem in single zone
                    system_patient_dict[systems[0]] = split_info['automatic_system_patients']

                    for patient in system_patient_dict[systems[0]]:
                        pack_list.update(patient_packs[patient])
                    pack_list = list(pack_list)
                    if len(pack_list) == 0:
                        continue
                    pack_delivery_date_dict = {}
                    pack_schedule_date_dict = {}

                    for p, d in patient_delivery_date_dict.items():
                        if p not in patient_packs:
                            continue
                        for pack in patient_packs[p]:
                            pack_delivery_date_dict[int(pack)] = str(d).split(' ')[0]

                    manual_packs_by_user = {}
                    system_end_date = system_end_date_dict[systems[0]] if systems[
                                                                              0] in system_end_date_dict else datetime.datetime.now(settings.PY_TIME_ZONE).date()

                    robot_quad_can, quad_capacity = get_robot_quad_can_capacity_batch_sch(systems)
                    # changes done for 1x, ed to update this for 4x or 2x
                    robot_can_capacity = quad_capacity * len(settings.TOTAL_QUADRANTS)

                    mbr_automatic = MultiBatchRecommender(split_info=split_info,
                                                          patient_fill_schedule_date_dict=patient_fill_schedule_date_dict,
                                                          patient_packs=patient_packs,
                                                          date_pack_count_dict=date_pack_count_dict,
                                                          automatic_system_region_wise_date_capacity_dict=automatic_system_region_wise_date_capacity_dict,
                                                          manual_system_region_wise_date_capacity_dict=manual_system_region_wise_date_capacity_dict,
                                                          pack_delivery_date_dict=pack_delivery_date_dict,
                                                          pack_schedule_date_dict=pack_schedule_date_dict,
                                                          pack_drugs=pack_drugs, canister_drugs=canister_drugs,
                                                          company_id=company_id, system_id=system_id,
                                                          system_info=system_timings, system_end_date=system_end_date,
                                                          patient_drugs=patient_drugs, zone_id=zone,
                                                          drug_alternate_drug_dict=drug_alternate_drug_dict,
                                                          pack_slot_drug_dict=pack_slot_drug_dict,
                                                          unique_drugs=robot_can_capacity,
                                                          sorted_patient_list=sorted_patient_list)

                    multi_batch_info_dict, automatic_batch_patient_dict, batch_split, batch_processing_time_dict,\
                    batch_analysis_data = mbr_automatic.get_batch_distribution(
                        system_region_wise_dict=automatic_system_region_wise_date_capacity_dict,
                        system_patients=split_info["automatic_system_patients"])

                    system_wise_batch_info[systems[0]] = {"multi_batch_info_dict": multi_batch_info_dict,
                                                          "automatic_batch_patient_dict": automatic_batch_patient_dict,
                                                          "batch_processing_time_dict": batch_processing_time_dict,
                                                          "batch_wise_split": batch_split}

                    for patient in system_patient_dict[systems[0]]:
                        system_patient_drugs[systems[0]][patient_id_name_dict[patient]] = zone_patient_drug_dict[zone][
                            patient]
                    # response = save_alternate_drug(company_id, pack_list, user_id, zone_old_new_drug_dict, zone)
                    alternate_drug_save_info[zone] = get_alternate_drug_data_to_save(company_id, pack_list, user_id,
                                                                                     zone_old_new_drug_dict, zone)

                    sorted_patient = OrderedDict()
                    for tpl in sorted_pack_list:
                        sorted_patient[patient_id_name_dict[tpl[0]]] = {'single_canister_drugs': tpl[2],
                                                                        'manual_drugs': tpl[1]}
                    if len(pending_patients) == 0:
                        break
                split_info['output_dict']['overloaded_patients'] = pending_patients
                for patient in pending_patients:
                    overloaded_packs.update(patient_packs[patient])

            if settings.FACILITY_WISE:
                for zone, systems in zone_system_dict.items():
                    pack_list = set()
                    if len(pending_facilities) == 0:
                        for facility, packs in facility_packs.items():
                            total_packs.extend(packs)
                            total_facilities.append(facility)
                            pending_facilities.append(facility)

                    system_timings = get_system_setting_by_system_id(system_id=systems[0])
                    am = AutomaticManualDistributionRecommender(zone_facility_drug_dict=zone_facility_drug_dict,
                                                                facility_packs=facility_packs,
                                                                facility_delivery_date_dict=facility_delivery_date_dict,
                                                                facility_patients=facility_patients,
                                                                patient_packs=patient_packs,
                                                                zone_patient_drugs=zone_patient_drug_dict,
                                                                patient_delivery_date_dict=patient_delivery_date_dict,
                                                                manual_user_id=manual_user_id,
                                                                system_timings=system_timings,
                                                                zone_canister_drug_dict=zone_canister_drug_dict,
                                                                current_system=systems[0])
                    split_info, facility_fill_schedule_date_dict, date_pack_count_dict, automatic_system_region_wise_date_capacity_dict, sorted_facility_list, pending_facilities_sys = am.get_split_recommendation_facility(
                        zone, pending_facilities)

                    pending_facilities = pending_facilities_sys
                    system_patient_dict[systems[0]] = split_info['automatic_system_facilities']
                    system_patients = set()
                    for facility in system_patient_dict[systems[0]]:
                        system_patients.update(facility_patients[facility])
                    system_patients = list(system_patients)

                    patient_fill_schedule_date_dict = {}
                    for facility, fill_date in facility_fill_schedule_date_dict.items():
                        if facility in system_patient_dict[systems[0]]:
                            for patient in facility_patients[facility]:
                                patient_fill_schedule_date_dict[patient] = fill_date
                                pack_list.update(patient_packs[patient])
                    pack_list = list(pack_list)
                    if len(pack_list) == 0:
                        continue

                    pack_delivery_date_dict = {}
                    pack_schedule_date_dict = {}
                    for p, d in patient_delivery_date_dict.items():
                        if p not in patient_packs:
                            continue
                        for pack in patient_packs[p]:
                            pack_delivery_date_dict[int(pack)] = str(d).split(' ')[0]

                    system_end_date = system_end_date_dict[systems[0]] if systems[
                                                                              0] in system_end_date_dict else datetime.datetime.now(settings.PY_TIME_ZONE).date()
                    mbr_automatic = MultiBatchRecommender(split_info=split_info,
                                                          patient_fill_schedule_date_dict=patient_fill_schedule_date_dict,
                                                          patient_packs=patient_packs,
                                                          date_pack_count_dict=date_pack_count_dict,
                                                          automatic_system_region_wise_date_capacity_dict=automatic_system_region_wise_date_capacity_dict,
                                                          manual_system_region_wise_date_capacity_dict={},
                                                          pack_delivery_date_dict=pack_delivery_date_dict,
                                                          pack_schedule_date_dict=pack_schedule_date_dict,
                                                          pack_drugs=pack_drugs, canister_drugs=canister_drugs,
                                                          company_id=company_id, system_id=system_id,
                                                          system_info=system_timings, system_end_date=system_end_date)
                    multi_batch_info_dict, automatic_batch_patient_dict, batch_split, batch_processing_time_dict,batch_analysis_data = mbr_automatic.get_batch_distribution(
                        system_region_wise_dict=automatic_system_region_wise_date_capacity_dict,
                        system_patients=system_patients)
                    system_wise_batch_info[systems[0]] = {"multi_batch_info_dict": multi_batch_info_dict,
                                                          "automatic_batch_patient_dict": automatic_batch_patient_dict,
                                                          "batch_processing_time_dict": batch_processing_time_dict,
                                                          "batch_wise_split": batch_split}

                    alternate_drug_save_info[zone] = get_alternate_drug_data_to_save(company_id, pack_list, user_id,
                                                                                     zone_old_new_drug_dict, zone)

                    if len(pending_facilities) == 0:
                        break
                split_info['output_dict']['overloaded_facilities'] = pending_facilities
                for facility in pending_facilities:
                    overloaded_packs.update(facility_packs[facility])
                for pack_id in overloaded_packs:
                    pack_info = db_get_pack_details_batch_scheduling(
                        pack_id=pack_id, delivery_date=pack_delivery_date_dict[int(pack_id)])
                    over_loaded_pack_dict["Overloaded_packs"].append(pack_info)

            # split_info['output_dict']['manual_batch_patient_dict'] = manual_batch_patient_dict
            split_info['output_dict']['overloaded_facilities'] = pending_facilities
            split_info['output_dict']['patient_packs'] = patient_packs
            overloaded_pack_list = list(overloaded_packs)

            logger.info("output_dict {}".format(split_info['output_dict']))
            json_data['output'] = split_info['output_dict']
            json_data['current_date'] = str(datetime.datetime.now(settings.PY_TIME_ZONE).date())

            over_loaded_pack_dict["Overloaded_packs"] = []
            overloaded_hours = {"manual_hours": 0, "automatic_hours": {}}

            dates = set()
            for pack_id in overloaded_pack_list:
                dates.add(pack_delivery_date_dict[int(pack_id)])
                pack_info = db_get_pack_details_batch_scheduling(
                    pack_id=pack_id, delivery_date=pack_delivery_date_dict[int(pack_id)], system_id=2)
                over_loaded_pack_dict["Overloaded_packs"].append(pack_info)

            # TODO: Fix system if for manual when flow defined
            """
            Time calculation for overloaded packs
            """
            system_timings = get_manual_capacity_info(company_id)
            # AUTOMATIC_PER_HOUR = int(system_timings['AUTOMATIC_PER_HOUR'])
            MANUAL_PER_HOUR = int(system_timings['MANUAL_PER_HOUR'])

            if len(over_loaded_pack_dict["Overloaded_packs"]) > 0:
                overloaded_hours["manual_hours"] = len(over_loaded_pack_dict["Overloaded_packs"]) / MANUAL_PER_HOUR
                if len(system_id) > 0:
                    overload_packs_each_system = math.ceil(
                        len(over_loaded_pack_dict["Overloaded_packs"]) / len(system_id))
                    for system in system_id:
                        system_timings = get_system_setting_by_system_id(system_id=system)
                        AUTOMATIC_PER_HOUR = int(system_timings['AUTOMATIC_PER_HOUR'])
                        overloaded_hours["automatic_hours"][system] = overload_packs_each_system / AUTOMATIC_PER_HOUR

            over_all_data = {}
            over_all_data["automatic_system"] = {}
            over_all_data["batch_wise_split"] = {}
            over_all_data["manual_system"] = {}
            over_all_data["system_wise_patient_drugs"] = {}
            # over_all_data["over_loaded_packs"] = {}
            over_all_data["batch_processing_time"] = {}
            over_all_data["alternate_drug_data"] = alternate_drug_save_info
            over_all_data["system_wise_patient_drugs"] = system_patient_drugs
            over_all_data["over_loaded_packs_time_info"] = overloaded_hours
            over_all_data["sorted_patient_list"] = sorted_patient

            for system, data in system_wise_batch_info.items():
                over_all_data["automatic_system"][system] = data['multi_batch_info_dict']
                over_all_data["batch_wise_split"][system] = data['batch_wise_split']
                over_all_data["batch_processing_time"][system] = data['batch_processing_time_dict']
            over_all_data["automatic_system_patients"] = split_info['output_dict'][
                'automatic_system_patients'] if settings.PATIENT_WISE else system_patients
            over_all_data["overloaded_pack_list"] = overloaded_pack_list if len(overloaded_pack_list) > 0 else list()
            logger.info("Output for get_patient_data {}".format(over_all_data))

            return create_response(over_all_data)

        else:

            """
            Case when there are overloaded packs and they are need to be distributed in pharmatechs, systems or both.
            Output : time calculation to process overloaded packs
            Firstly check user wants to distribute in user, system or both
            Condition 1: if only users i.e manual distribution then datewise_patient_dict is formed so that packs are 
                        distributed in all the users equal for each date, distribution is carried out patient wise.
                        
            Condition 2: if only automatic then the capacity system wise is checked and packs are divided equally for 
                        each system
                        
            Condition 3: if both are selected then 20% of the packs are distributed in automatic rest in manual, 
                        distribution is carried out patient wise
            """

            pack_delivery_date_dict = dict()
            system_timings = dict()
            overloaded_pack_list_patient = list()

            if automatic_system is not None:
                for system in automatic_system:
                    system_timings[system] = get_system_setting_by_system_id(system_id=system)

            system_timings.update(get_manual_capacity_info(company_id))

            overloaded_pack_list_total = overloaded_pack_list
            logger.info("overloaded pack list {}".format(overloaded_pack_list_total))
            patient_delivery_date_dict_overloaded = get_pack_wise_delivery_date(
                overloaded_pack_list_total)
            overloaded_patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(
                company_id,
                overloaded_pack_list_total)

            for patient, packs_list in overloaded_patient_packs.items():
                for each_pack in packs_list:
                    if patient in patient_delivery_date_dict_overloaded.keys():
                        pack_delivery_date_dict[each_pack] = patient_delivery_date_dict_overloaded[patient]
                    else:
                        pack_delivery_date_dict[each_pack] = None

            # to remove all that packs for which we have not got the patient data
            for patient, packs in overloaded_patient_packs.items():
                overloaded_pack_list_patient.extend(packs)

            overloaded_patient_list = overloaded_patient_packs.keys()
            manual_users = len(manual_user_id) if manual_user_id is not None else None
            automatic_systems = len(automatic_system) if automatic_system is not None else None
            patient_fill_schedule_date_dict = {}
            overloaded_patient_datewise = {}
            split_info = {}

            # check if user wants to distribute packs to auto system or manual or both
            # and divide accordingly
            if manual_users is None:
                overload_distribution = "automatic"

                for patient in overloaded_patient_list:
                    if patient in patient_delivery_date_dict_overloaded:
                        patient_fill_schedule_date_dict[patient] = \
                            str(patient_delivery_date_dict_overloaded[patient]).split(' ')[0]
                for patient, date in patient_fill_schedule_date_dict.items():
                    if date not in overloaded_patient_datewise.keys():
                        overloaded_patient_datewise[date] = []
                    overloaded_patient_datewise[date].extend(overloaded_patient_packs[patient])
                split_info['overloaded_patient_datewise'] = overloaded_patient_datewise
                split_info['system_list'] = automatic_system

                overloaded_distribution = overloaded_packs_distribution(split_info, manual_users, system_timings,
                                                                        overload_distribution)
                print("only automatic distribution")

            elif automatic_system is None:
                overload_distribution = "manual"

                for patient in overloaded_patient_list:
                    if patient in patient_delivery_date_dict_overloaded:
                        patient_fill_schedule_date_dict[patient] = \
                            str(patient_delivery_date_dict_overloaded[patient]).split(' ')[0]
                for patient, date in patient_fill_schedule_date_dict.items():
                    if date not in overloaded_patient_datewise.keys():
                        overloaded_patient_datewise[date] = []
                    overloaded_patient_datewise[date].extend(overloaded_patient_packs[patient])
                split_info['overloaded_patient_datewise'] = overloaded_patient_datewise

                overloaded_distribution = overloaded_packs_distribution(split_info, manual_users, system_timings,
                                                                        overload_distribution)

                MANUAL_PER_HOUR = int(system_timings['MANUAL_PER_HOUR'])
                overloaded_distribution['manual_user_distribution'] = dict()

                for overload_info in overloaded_distribution['manual']:
                    distributed_packs = manual_user_distribution_flow_handler(
                        manual_user_id, overload_info['pack_list'], company_id)
                    for user, manual_packs in distributed_packs.items():
                        if len(manual_packs):
                            if user not in overloaded_distribution['manual_user_distribution']:
                                overloaded_distribution['manual_user_distribution'][user] = dict()
                            if overload_info['fill_date'] not in overloaded_distribution['manual_user_distribution'][user]:
                                overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']] = {
                                    "pack_list":list(),
                                    "extra_working_hours": {"hours": 0, "min": 0}
                                }
                            extra_manu = len(manual_packs) / MANUAL_PER_HOUR
                            extra_min_manual = (extra_manu - int(extra_manu)) * 60

                            overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                'pack_list'].extend(manual_packs)
                            overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                'extra_working_hours']["hours"] += int(extra_manu)
                            overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                'extra_working_hours']["min"] += round(extra_min_manual)

            else:
                overload_distribution = "both"
                total_packs = len(overloaded_pack_list_patient)
                percent_packs = math.ceil(total_packs * (1 / 5))
                automatic_percent_patient_packs_dict = {}
                manual_percent_patient_packs_dict = {}
                packs_for_overloaded = total_packs - math.ceil(percent_packs)
                copy_overloaded_patient_packs = deepcopy(overloaded_patient_packs)
                automatic_percent_packs_list = []
                manual_percent_pack_list = []
                for patient, packs in copy_overloaded_patient_packs.items():
                    if len(automatic_percent_packs_list) < percent_packs:
                        automatic_percent_patient_packs_dict[patient] = packs
                        del overloaded_patient_packs[patient]
                        automatic_percent_packs_list.extend(packs)
                    else:
                        manual_percent_patient_packs_dict[patient] = packs
                        manual_percent_pack_list.extend(packs)

                patient_fill_schedule_date_dict_automatic = {}
                overloaded_patient_datewise_automatic = {}
                split_info_automatic = {}
                for patient in automatic_percent_patient_packs_dict.keys():
                    if patient in patient_delivery_date_dict_overloaded:
                        patient_fill_schedule_date_dict_automatic[patient] = \
                            str(patient_delivery_date_dict_overloaded[patient]).split(' ')[0]
                for patient, date in patient_fill_schedule_date_dict_automatic.items():
                    if date not in overloaded_patient_datewise_automatic.keys():
                        overloaded_patient_datewise_automatic[date] = []
                    overloaded_patient_datewise_automatic[date].extend(copy_overloaded_patient_packs[patient])
                split_info_automatic['overloaded_patient_datewise'] = overloaded_patient_datewise_automatic
                split_info_automatic['system_list'] = automatic_system

                patient_fill_schedule_date_dict_manual = {}
                overloaded_patient_datewise_manual = {}
                split_info_manual = {}
                for patient in manual_percent_patient_packs_dict.keys():
                    if patient in patient_delivery_date_dict_overloaded:
                        patient_fill_schedule_date_dict_manual[patient] = \
                            str(patient_delivery_date_dict_overloaded[patient]).split(' ')[0]
                for patient, date in patient_fill_schedule_date_dict_manual.items():
                    if date not in overloaded_patient_datewise_manual.keys():
                        overloaded_patient_datewise_manual[date] = []
                    overloaded_patient_datewise_manual[date].extend(copy_overloaded_patient_packs[patient])
                split_info_manual['overloaded_patient_datewise'] = overloaded_patient_datewise_manual

                logger.info("overloaded distribution {}".format(overload_distribution))

                # for automatic
                split_info['overloaded_patient_datewise'] = overloaded_patient_datewise
                overloaded_distribution = overloaded_packs_distribution(split_info_automatic, manual_users,
                                                                        system_timings,
                                                                        "automatic")

                # for manual
                if len(manual_percent_pack_list) > 0:
                    overloaded_distribution_manual = overloaded_packs_distribution(split_info_manual, manual_users,
                                                                                   system_timings,
                                                                                   "manual")

                    MANUAL_PER_HOUR = int(system_timings['MANUAL_PER_HOUR'])
                    overloaded_distribution['manual_user_distribution'] = dict()

                    for overload_info in overloaded_distribution_manual['manual']:
                        distributed_packs = manual_user_distribution_flow_handler(
                            manual_user_id, overload_info['pack_list'], company_id)
                        for user, manual_packs in distributed_packs.items():
                            if len(manual_packs):
                                if user not in overloaded_distribution['manual_user_distribution']:
                                    overloaded_distribution['manual_user_distribution'][user] = dict()
                                if overload_info['fill_date'] not in \
                                        overloaded_distribution['manual_user_distribution'][user]:
                                    overloaded_distribution['manual_user_distribution'][user][
                                        overload_info['fill_date']] = {
                                        "pack_list": list(),
                                        "extra_working_hours": {"hours": 0, "min": 0}
                                    }
                                extra_manu = len(manual_packs) / MANUAL_PER_HOUR
                                extra_min_manual = (extra_manu - int(extra_manu)) * 60

                                overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                    'pack_list'].extend(manual_packs)
                                overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                    'extra_working_hours']["hours"] += int(extra_manu)
                                overloaded_distribution['manual_user_distribution'][user][overload_info['fill_date']][
                                    'extra_working_hours']["min"] += round(extra_min_manual)

                else:
                    overloaded_distribution_manual = {"manual": [], "manual_user_distribution": {}}
                overloaded_distribution.update(overloaded_distribution_manual)

            # get pack info for overloaded packs
            overloaded_distribution['overloaded_packs_info'] = list()

            for pack_id in overloaded_pack_list_total:
                pack_info = db_get_pack_details_batch_scheduling(
                    pack_id=pack_id, delivery_date=pack_delivery_date_dict[str(pack_id)], system_id=system_id)
                overloaded_distribution["overloaded_packs_info"].append(pack_info)

            logger.info("overloaded distribution {}".format(overload_distribution))

            return create_response(overloaded_distribution)

    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.info(e)
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.info(e)
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_facility_wise_data_from_patient(zone_patient_drug_dict, patient_packs, patient_delivery_date_dict,
                                        patient_facility_dict):
    zone_facility_drug_dict = {}
    facility_packs = {}
    facility_delivery_date_dict = {}
    facility_patients = {}

    try:
        for zone, patient_drug in zone_patient_drug_dict.items():
            zone_facility_drug_dict[zone] = {}
            for patient, drugs in patient_drug.items():
                if patient_facility_dict[patient] not in zone_facility_drug_dict[zone]:
                    zone_facility_drug_dict[zone][patient_facility_dict[patient]] = set()
                zone_facility_drug_dict[zone][patient_facility_dict[patient]].update(drugs)

        for patient, packs in patient_packs.items():
            if patient_facility_dict[patient] not in facility_packs:
                facility_packs[patient_facility_dict[patient]] = set()
            facility_packs[patient_facility_dict[patient]].update(packs)

        for patient, delivery_date in patient_delivery_date_dict.items():
            if patient_facility_dict[patient] not in facility_delivery_date_dict:
                facility_delivery_date_dict[patient_facility_dict[patient]] = '2018-03-03'
            delivery_date = str(delivery_date).split(' ')[0]
            if delivery_date > facility_delivery_date_dict[patient_facility_dict[patient]]:
                facility_delivery_date_dict[patient_facility_dict[patient]] = delivery_date

        for patient, facility in patient_facility_dict.items():
            if facility not in facility_patients:
                facility_patients[facility] = []
            facility_patients[facility].append(patient)

        return zone_facility_drug_dict, facility_packs, facility_delivery_date_dict, facility_patients

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_zone_wise_patient_drugs_with_alternate_drug(patient_drugs, patient_drug_alternate_flag_dict,
                                                    drug_alternate_drug_dict, drug_zone_alternate_drug_dict,
                                                    zone_canister_drug_dict, canister_drug_zone_dict, zone_list,
                                                    fndc_txr_drug_id_dict, patient_packs,
                                                    alternate_fndc_txr_drug_id_dict):
    zone_patient_drug_dict = {}
    zone_old_new_drug_dict = {}
    try:
        for zone in zone_list:
            zone_patient_drug_dict[zone] = {}
            zone_old_new_drug_dict[zone] = OrderedDict()
            for patient, drug_set in patient_drugs.items():
                zone_patient_drug_dict[zone][patient] = set()
                for drug in drug_set:
                    alternate_used = 0
                    if patient_drug_alternate_flag_dict[patient][drug] and drug in drug_alternate_drug_dict and zone in \
                            drug_zone_alternate_drug_dict[drug]:
                        # for alternate_drug in drug_alternate_drug_dict[drug]:
                        #     if zone in canister_drug_zone_dict[alternate_drug]:
                        original_drug_id = get_original_drug_id(fndc_txr_drug_id_dict[drug], patient_packs, patient)
                        alternate_drug = drug_zone_alternate_drug_dict[drug][zone]
                        zone_patient_drug_dict[zone][patient].update(alternate_drug)
                        zone_old_new_drug_dict[zone][original_drug_id] = \
                        alternate_fndc_txr_drug_id_dict[next(iter(alternate_drug))][0]
                        alternate_used = 1
                    if not alternate_used:
                        zone_patient_drug_dict[zone][patient].add(drug)

        return zone_patient_drug_dict, zone_old_new_drug_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_alternate_drug_data(company_id, pack_list, user_id, facility_distribution_id):
    """
    This function will make data of available alternate drugs
    :param company_id:
    :param pack_list:
    :param user_id:
    :param facility_distribution_id:
    :return: drug_alternate_drug_dict,drug_zone_alternate_drug_dict
    """
    drug_alternate_drug_dict = {}
    drug_zone_alternate_drug_dict = {}
    fndc_txr_drug_id_dict = defaultdict(list)
    alternate_fndc_txr_drug_id_dict = defaultdict(list)
    zone_canister_data_dict = {}
    # facility_distribution_id = get_facility_distribution_id_from_packs(pack_list)
    # alternate_drug_data = AlternateDrugOption.get_alternate_drug(facility_distribution_id)

    try:
        alternate_drug_data_dict, alternate_drug_ids, drug_alternate_drug_dict = \
            get_active_alternate_drug_data(facility_distribution_id, company_id)

        logger.info("get_alternate_drug_data batch dis {}, {}, {}".format(alternate_drug_data_dict,
                                                                          alternate_drug_ids,
                                                                          drug_alternate_drug_dict))
        if alternate_drug_data_dict:
            drug_zone_canister_count_dict,drug_zone_avail_quantity_dict,zone_list = \
                get_zonewise_avilability_by_drug(alternate_drug_ids,company_id)
            logger.info("get_alternate_drug_dict batch dis {}, {}, {}".format(drug_zone_canister_count_dict,
                                                                              drug_zone_avail_quantity_dict,
                                                                              zone_list))

        zone_avail_quantity = {}
        zone_canister_count = {}
        for original_drug,drug_data in alternate_drug_data_dict.items():
            drug = drug_data['fndc_txr']
            fndc_txr_drug_id_dict[drug].extend(list(drug_data['drug_ids']))
            zone_canister_data_dict = {}
            if drug not in drug_zone_alternate_drug_dict:
                drug_zone_alternate_drug_dict[drug] = {}
            for alt_uid,alt_drug_data in drug_data['alternate_drug_data'].items():
                alternate_fndc_txr_drug_id_dict[alt_drug_data['fndc_txr']].extend(list(alt_drug_data['drug_ids']))
                zone_canister_count = {}
                zone_avail_quantity = {}
                # for zone in zone_list:
                #     zone_canister_data_dict[zone] = []
                #     zone_canister_count[zone] = 0
                #     zone_avail_quantity[zone] = 0
                for zone in zone_list:
                    for drug_id in alt_drug_data['drug_ids']:
                        if drug_id not in drug_zone_canister_count_dict.keys():
                            continue
                        if zone not in drug_zone_canister_count_dict[drug_id]:
                            continue
                        if zone not in zone_canister_count:
                            zone_canister_count[zone] = 0
                            zone_avail_quantity[zone] = 0
                        if zone not in zone_canister_data_dict:
                            zone_canister_data_dict[zone] = []
                            # zone_canister_data_dict[zone] = []
                        zone_canister_count[zone] += drug_zone_canister_count_dict[drug_id][zone]
                        zone_avail_quantity[zone] += drug_zone_avail_quantity_dict[drug_id][zone]
                    if zone in zone_canister_count:
                        zone_canister_data_dict[zone].append((alt_drug_data['fndc_txr'], deepcopy(zone_canister_count[zone]), zone_avail_quantity[zone]))
                for zone, canister_data in zone_canister_data_dict.items():
                    if zone not in drug_zone_alternate_drug_dict[drug]:
                        drug_zone_alternate_drug_dict[drug][zone] = []
                    drug_zone_alternate_drug_dict[drug][zone].extend(canister_data)

        # for drug_data in alternate_drug_data:
        #     if not drug_data['active']:
        #         continue
        #     alternate_drug = UniqueDrug.db_get_drug_data_from_unique_drug_id(drug_data['alternate_unique_drug_id'])
        #     alternate_drug_id = get_drug_id_from_unique_drug(
        #         alternate_drug)
        #     is_canister_exist,canister_drug_ids = check_canister_existance(alternate_drug_id,company_id)
        #     # is_active = get_canister_active_status(drug_data['alternate_canister_id'])
        #     if not is_canister_exist:
        #         continue
        #     drug = UniqueDrug.db_get_drug_data_from_unique_drug_id(drug_data['unique_drug_id'])
        #     # alternate_drug = UniqueDrug.db_get_drug_data_from_unique_drug_id(drug_data['alternate_unique_drug_id'])
        #     fndc_txr_drug_id_dict[drug] = get_drug_id_from_unique_drug(drug)
        #     alternate_fndc_txr_drug_id_dict[alternate_drug] = canister_drug_ids
        #     if drug not in drug_alternate_drug_dict:
        #         drug_alternate_drug_dict[drug] = set()
        #     if drug not in drug_zone_alternate_drug_dict:
        #         drug_zone_alternate_drug_dict[drug] = {}
        #     if alternate_drug in drug_alternate_drug_dict[drug]:
        #         continue
        #     drug_alternate_drug_dict[drug].add(alternate_drug)
        #     zone_canister_data = get_zone_wise_canister_count_for_drug(alternate_fndc_txr_drug_id_dict[alternate_drug],alternate_drug,company_id)
        #     for zone,canister_data in zone_canister_data.items():
        #         if zone not in drug_zone_alternate_drug_dict[drug]:
        #             drug_zone_alternate_drug_dict[drug][zone] = []
        #         drug_zone_alternate_drug_dict[drug][zone].extend(canister_data)

            # zone_id = get_zone_id_from_canister(drug_data['alternate_canister_id'])
            # if zone_id not in drug_zone_alternate_drug_dict[drug]:
            #     drug_zone_alternate_drug_dict[drug][zone_id] = set()
            # drug_zone_alternate_drug_dict[drug][zone_id].add(alternate_drug)

        drug_zone_alternate_drug_dict = select_zone_alternate_drug(drug_zone_alternate_drug_dict)

        return drug_alternate_drug_dict, drug_zone_alternate_drug_dict, fndc_txr_drug_id_dict, \
               alternate_fndc_txr_drug_id_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def select_zone_alternate_drug(drug_zone_alternate_drug_dict):
    """
    Select alternate drug per zone based on more no. of canisters and if highest no. of canisters are same then look
    for more quantity
    """
    final_drug_zone_alternate_drug_dict = {}
    try:
        for drug, zone_data in drug_zone_alternate_drug_dict.items():
            final_drug_zone_alternate_drug_dict[drug] = {}
            for zone, drug_canister_list in zone_data.items():
                sorted_drugs = sorted(drug_canister_list, key=lambda k: (-k[1], -k[2]))
                final_drug_zone_alternate_drug_dict[drug][zone] = {sorted_drugs[0][0]}

        return final_drug_zone_alternate_drug_dict
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_ordered_zone_system_data(zone_system_dict):
    zone_list = []
    zone_system_dict_ordered = OrderedDict()
    try:
        for zone, systems in zone_system_dict.items():
            system_timings = get_system_setting_by_system_id(system_id=systems[0])
            per_hour_capacity = int(system_timings['AUTOMATIC_PER_HOUR'])
            zone_list.append((zone, per_hour_capacity))
        zone_list = sorted(zone_list, key=lambda k: (-k[1]))
        for zone in zone_list:
            zone_system_dict_ordered[zone[0]] = zone_system_dict[zone[0]]
        return zone_system_dict_ordered

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@validate(required_fields=['pack_list'])
@log_args_and_response
def get_unscheduled_packs(args):
    pack_list = args['pack_list']
    list_of_unscheduled_packs = []
    for pack_id in pack_list:
        unscheduled_pack_data = get_unscheduled_packs_dao(pack_id)
        if len(unscheduled_pack_data) > 0:
            list_of_unscheduled_packs.append(unscheduled_pack_data)
    return create_response(list_of_unscheduled_packs)


@log_args_and_response
def get_manual_capacity_info(company_id: int):
    manual_info: dict = dict()
    try:
        company_setting_query = get_company_setting_data_by_company_id(company_id=company_id)

        for record in company_setting_query.dicts():
            manual_info[record['name']] = record['value']
        return manual_info
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_company_setting_data_by_company_id {}".format(e))
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_weekdays(year, month, day):
    thisXMas = datetime.date(year, month, day)
    thisXMasDay = thisXMas.weekday()
    weekday = settings.WEEKDAYS[thisXMasDay]
    return weekday


@log_args_and_response
def get_system_info():
    system_info = dict()
    system_info_updated = dict()
    query = get_system_setting_info()
    for record in query.dicts():
        system_info[record["id"]] = {record["system_id"]: {record["name"]: record["value"]}}
    for k, v in system_info.items():
        for sys, val in v.items():
            if sys not in system_info_updated:
                system_info_updated[sys] = {}
            system_info_updated[sys].update(val)
    return system_info_updated


@log_args_and_response
def get_end_date(system_info, total_packs, start_date):
    try:
        AUTOMATIC_PER_DAY_HOURS = int(system_info['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(system_info['AUTOMATIC_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(system_info['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(system_info['AUTOMATIC_SUNDAY_HOURS'])
        batch_date_day_dict = {}
        rem_cap = 0
        processing_hours = 0

        last_batch_start_date = start_date
        last_batch_start_date_str = str(last_batch_start_date)  # this is in date format
        last_batch_packs_count = total_packs  # will take from db

        batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                  int(last_batch_start_date_str.split('-')[1]),
                                                                  int(last_batch_start_date_str.split('-')[2]))
        while last_batch_packs_count > 0:
            last_batch_start_date_str = str(last_batch_start_date)
            batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                      int(last_batch_start_date_str.split('-')[1]),
                                                                      int(last_batch_start_date_str.split('-')[2]))
            if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
                if AUTOMATIC_SATURDAY_HOURS == 0:
                    last_batch_start_date += datetime.timedelta(days=1)
                elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SATURDAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    # rem_cap = AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS - batch_packs_count
                    # if rem_cap <= AUTOMATIC_PER_HOUR:
                    #     last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
            elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
                if AUTOMATIC_SUNDAY_HOURS == 0:
                    last_batch_start_date += datetime.timedelta(days=1)
                elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS and AUTOMATIC_SUNDAY_HOURS > 0:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SUNDAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count = 0
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
            else:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_PER_DAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
        return scheduled_end_date

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_scheduled_till_date(dict_batch_info):
    company_id = dict_batch_info['company_id']
    system_robot_data = get_robot_status(company_id)
    if not system_robot_data:
        return system_robot_data
    system_max_batch_id_dict = get_system_wise_batch_id(list(system_robot_data.keys()))
    system_end_date_dict = {}
    for system, batch in system_max_batch_id_dict.items():
        system_info = get_system_setting_by_system_id(system_id=system)
        total_packs,scheduled_start_date = get_batch_scheduled_start_date_and_packs(batch)
        scheduled_end_date = get_end_date(system_info, total_packs, scheduled_start_date)
        system_robot_data[system]['scheduled_end_date'] = scheduled_end_date
    return system_robot_data


@log_args_and_response
def manual_user_distribution_flow_handler(user_hours, manual_packs, company_id):
    """
    Args is a dictionary which has all the data needed for distribution.
    It contains following keys.
    - user_hours:- Manual user and corresponding working hours for which we will distribute the packs
    - manual_packs:- These are the packs which we are supposed to distribute between users.
    - company_id

    Flow of the method will be as follows:
    1) Prepare needed data structures for manual distribution flow.
    :param user_hours
    :param manual_packs
    :param company_id
    :return: datewise_manual_patient_dict, patient_packs
    """

    try:
        logger.info("In manual_user_distribution_flow_handler")
        datewise_manual_patient_dict, patient_packs = prepare_needed_data_structures_for_manual_distribution_flow(
            manual_packs, company_id)
        logger.info("date wise manual patient dict {}".format(datewise_manual_patient_dict))

        """
        2) Divide packs based on number of users and corresponding working hours
        We have followed following formula:
        
        Pack count of user1 = (Total number of Packs X Working hours of user1)/(Total working hours of all users)
        :param args:datewise_manual_patient_dict, user_list, patient_packs
        :return: user_pack_list
        
        """
        user_wise_split = dict()

        # calculating total work hours
        hours_list = []
        for user in user_hours:
            hours_list.append(int(user_hours[user]))
        total_hours = sum(hours_list)
        logger.info("Total working hours {}:".format(total_hours))
        logger.info("Total manual packs {}:".format(len(manual_packs)))

        # calculating user wise hour wise manual
        for user in user_hours:
            user_wise_split[user] = math.ceil(len(manual_packs) * int(user_hours[user]) / total_hours)
        logger.info("User wise manual_pack_split {}:".format(user_wise_split))

        manual_pack_by_user = divide_packs_for_manual_users(datewise_manual_patient_dict, user_hours, user_wise_split,
                                                            patient_packs, company_id, manual_packs)

        print("user pack list", manual_pack_by_user)

        return manual_pack_by_user
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@validate(required_fields=['company_id', 'percentage_packs_for_manual_system', 'pack_list',
                           'maximum_allowed_manual_fill_for_automatic_system'])
@log_args_and_response
def get_manual_packs_with_optimised_manual_fill(args):
    """
    Returns canister packs and manual packs
    :return: json
    """
    logger.info("In get_manual_packs_with_optimised_manual_fill")
    company_id = args['company_id']
    user_hours = args.get('user_hours', None)
    logger.info('args for manual packs with optimised manual fill: {}'.format(args))
    percentage_packs_for_manual_system = args['percentage_packs_for_manual_system']
    percentage_packs_for_automatic_system = 100 - percentage_packs_for_manual_system
    maximum_allowed_manual_fill_for_automatic_system = args['maximum_allowed_manual_fill_for_automatic_system']
    import_state = args.get('import_state', False)
    pack_half_pill_drug_drop_count = dict()
    pack_list_main = args.get("pack_list")

    # prioritize users based on decreasing order of their working hours
    if user_hours is not None:
        user_hours = OrderedDict(sorted(user_hours.items(), key=lambda x: int(x[1]), reverse=True))

    # parameters to shift packs to robot if pack has more than max_pack_drugs drugs and has canister drugs more than or
    # equal to min_robot_drugs
    try:
        patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, pack_list_main)
        patient_delivery_date_dict = get_pack_wise_delivery_date(pack_list_main)
        remaining_patient = set()
        pack_list = []

        # list created to add packs with delivery date null. Case added to send pack for manual with delivery date null
        pack_list_null_delivery_date = []
        for patient, packs in patient_packs.items():
            if patient in patient_delivery_date_dict:
                pack_list.extend(packs)
            else:
                pack_list_null_delivery_date.extend(packs)
        #     if patient_delivery_date_dict[patient] != None:
        #         pack_list.extend(packs)
        #     else:
        #         remaining_patient.add(patient)
        # print("remaining packs", remaining_patient)
        # for each_patient in remaining_patient:
        #     del patient_packs[each_patient]

        canister_drugs = db_get_canister_fndc_txr(company_id)
        if len(pack_list) > 0:
            pack_half_pill_drug_drop_count = db_get_half_pill_drug_drop_by_pack_id(pack_list)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    manual_packs = set()
    canister_packs = set()
    manual_packs_by_user = {}
    manual_split_info_dict = {}
    for maximum_manual_count in range(maximum_allowed_manual_fill_for_automatic_system):
        manual_split_info_dict[maximum_manual_count] = {'manual_packs': 0, 'canister_packs': 0}
    total_packs = set([])
    for patient_specific_packs in patient_packs.values():
        total_packs |= patient_specific_packs
    number_of_total_packs = len(total_packs)
    maximum_allowed_canister_packs = (percentage_packs_for_automatic_system * number_of_total_packs) / 100
    patient_can_drug_manual_drug_len_data_list = []
    for patient in list(patient_drugs.keys()):
        patient_drugs_set = patient_drugs[patient]
        patient_drug_length = len(patient_drugs_set)
        patient_canister_drugs = patient_drugs_set & canister_drugs
        patient_canister_drug_length = len(patient_canister_drugs)
        patient_manual_drug_length = patient_drug_length - patient_canister_drug_length
        patient_can_drug_manual_drug_len_data_list.append(
            (patient, patient_manual_drug_length, patient_canister_drug_length))

    # sorting patient_can_drug_manual_drug_len_data_list, we will first sort based on manual drug length in ascending
    # order and after that sort based on can_drug_len in descending order
    new_patient_can_drug_manual_drug_len_data_list = []
    for patient, patient_manual_drug_length, patient_canister_drug_length in patient_can_drug_manual_drug_len_data_list:
        packs_for_given_patient = patient_packs[patient]
        for pack in packs_for_given_patient:
            pack = int(pack)
            if pack not in pack_half_pill_drug_drop_count:
                continue
            else:
                patient_manual_drug_length += 1 + int(pack_half_pill_drug_drop_count[pack] / 7)
                # patient_canister_drug_length -= 1 + int(pack_half_pill_drug_drop_count[pack]/7)
        new_patient_can_drug_manual_drug_len_data_list.append(
            (patient, patient_manual_drug_length, patient_canister_drug_length))
    sorted_patient_len_data = sorted(new_patient_can_drug_manual_drug_len_data_list, key=lambda x: (x[1], -x[2]))
    logger.info("sorted patient len data {}".format(sorted_patient_len_data))
    copy_sorted_patient_len_data = deepcopy(sorted_patient_len_data)
    new_list = []
    for tuple in sorted_patient_len_data:
        if tuple[2] == 0:
            ind = copy_sorted_patient_len_data.index(tuple)
            copy_sorted_patient_len_data.pop(ind)
            new_list.append(tuple)
    copy_sorted_patient_len_data.extend(new_list)
    sorted_patient_len_data = copy_sorted_patient_len_data
    for patient, patient_manual_drug_length, patient_canister_drug_length in sorted_patient_len_data:
        packs_for_given_patient = patient_packs[patient]
        if len(canister_packs) + len(packs_for_given_patient) <= maximum_allowed_canister_packs:
            canister_packs.update(packs_for_given_patient)
        else:
            manual_packs.update(packs_for_given_patient)
        for maximum_manual_count in manual_split_info_dict.keys():
            if patient_manual_drug_length <= maximum_manual_count and patient_canister_drug_length == 0:
                manual_split_info_dict[maximum_manual_count]["manual_packs"] += len(packs_for_given_patient)
            elif patient_manual_drug_length <= maximum_manual_count:
                manual_split_info_dict[maximum_manual_count]["canister_packs"] += len(packs_for_given_patient)
            else:
                manual_split_info_dict[maximum_manual_count]["manual_packs"] += len(packs_for_given_patient)

    if user_hours:
        manual_packs_by_user = dict()
        for user in user_hours:
            manual_packs_by_user[user] = set()

        if len(manual_packs) > 0:
            print("len of manual packs", len(manual_packs))
            manual_packs = list(map(int, manual_packs))
            manual_packs_by_user = manual_user_distribution_flow_handler(user_hours, manual_packs, company_id)

        if import_state and len(pack_list_null_delivery_date) > 0:
            manual_packs_by_user = manual_user_distribution_null_delivery_date(user_hours, pack_list_null_delivery_date,
                                                                               manual_packs_by_user, company_id)

        response = {'manual_packs_by_user': manual_packs_by_user,
                    'manual_packs': manual_packs,
                    'canister_packs': canister_packs,
                    'manual_split_info_dict': manual_split_info_dict}
    else:
        response = {'manual_packs': manual_packs,
                    'canister_packs': canister_packs,
                    'manual_split_info_dict': manual_split_info_dict}

    return create_response(response)


@log_args_and_response
def manual_user_distribution_null_delivery_date(user_hours, manual_packs, manual_pack_by_user, company_id):
    """
    Args is a dictionary which has all the data needed for distribution.
    It contains folllowing keys.
    - user_list:- Manual user for which we will distribute the packs
    - manual_packs:- These are the packs which we are supposed to distribute between users.
    - company_id

    """
    patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, manual_packs)

    for patient, packs in patient_packs.items():
        user = min(manual_pack_by_user, key=lambda k: len(manual_pack_by_user[k]))
        manual_pack_by_user[user].update(packs)

    return manual_pack_by_user


@log_args_and_response
def prepare_needed_data_structures_for_manual_distribution_flow(manual_packs, company_id):
    """
    This method will return the dict that has date wise filtered set of packs
    key: date
    Sort datewise_manual_patient_dict
    """

    datewise_manual_patient_dict = {}
    try:
        patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, manual_packs)
        # total_patients = [patient for patient in patient_packs.keys()]
        patient_delivery_date_dict = get_pack_wise_delivery_date(manual_packs)

        for p, d in patient_delivery_date_dict.items():

            if d not in datewise_manual_patient_dict:
                datewise_manual_patient_dict[d] = set()
            datewise_manual_patient_dict[d].add(p)

        datewise_manual_patient_dict = OrderedDict(sorted(datewise_manual_patient_dict.items(), key=lambda x: x[0]))

        return datewise_manual_patient_dict, patient_packs
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def divide_packs_for_manual_users(datewise_manual_patient_dict, user_hours, user_wise_split, patient_packs, company_id,
                                  manual_packs):
    """
    In this method packs are divided to users.
    :param args: datewise_manual_patient_dict, user_hours, patient_packs
    :return: manual_packs_by_user (dict having set of packs allocated to each user)

    Flow of this method will be looping over each date and then:
    1) create  facility_packs (facility wise set of packs) dict with help of list of packs.
       :params : facility_pack_count - key: facility_id , values: set of packs by facility
              sorted_facility_pack_count - sorted dict of facility_pack-count

    2) assign one by one pack to each user
       :params : split, free space (number of more packs for that user)
               list_of_packs - to maintain the count of packs remaining to allocate and create
                            pack list of patients of each facility used to create the facility_packs
               user_pack_list - key: user_id , values : set of packs
               facility_patient_packs - dict having key as patient and set of packs as value
               user_list - sorted user list in descending order of their remaining packs
               date_user_pack_dict - dictionary having date as key and user wise allocated packs as value.

    3) Before allocating patient pack to user check whether adding these packs will increase the pack count
       greater than split and if other user have split capacity available for these patient packs

    5) Sort the user_list so as the user having less number of packs goes first on the loop
    :params : manual_packs_by_user - key : user_id, values: total number of packs alllocated to user

    """
    try:
        logger.info("In divide packs for manual user")
        date_user_pack_dict = {}
        date_user_pack_count = {}
        manual_packs_by_user = {}

        user_list = list(user_hours.keys())
        for user_id in user_list:
            manual_packs_by_user[user_id] = set()

        for date, packs in datewise_manual_patient_dict.items():
            user_pack_list = {}
            split = {}
            for user in user_list:
                user_pack_list[user] = set()
            list_of_packs = []
            for patient in packs:
                for p in patient_packs[patient]:
                    list_of_packs.append(p)
            # split = math.ceil(len(list_of_packs) / len(user_list))
            facility_pack_count = {}
            facility_packs = get_packs_by_facility(pack_list=list_of_packs)
            for facility, packs in facility_packs.items():
                facility_pack_count[facility] = len(packs)
            sorted_facility_pack_count = OrderedDict(sorted(facility_pack_count.items(), key=lambda x: x[1], reverse=True))
            copy_sorted_facility = deepcopy(sorted_facility_pack_count)
            while not len(copy_sorted_facility.keys()) == 0:
                facility = list(copy_sorted_facility)[0]
                del copy_sorted_facility[facility]
                for user in user_list:
                    if len(facility_packs[facility]) <= (user_wise_split[user] - len(manual_packs_by_user[user])):
                        user_pack_list[user].update(facility_packs[facility])
                        for one_pack in facility_packs[facility]:
                            list_of_packs.remove(str(one_pack))
                        del facility_packs[facility]
                        del sorted_facility_pack_count[facility]
                        break
                # user_list.clear()
                # for k in sorted(user_pack_list, key=lambda k: len(user_pack_list[k])):
                #     user_list.append(k)

                user_pack_count = {}
                user_remaining_pack_count = {}
                for user in user_list:
                    user_pack_count[user] = len(manual_packs_by_user[user]) + len(user_pack_list[user])
                    user_remaining_pack_count[user] = user_wise_split[user] - user_pack_count[user]
                user_list.clear()
                for k in sorted(user_remaining_pack_count, key=lambda k: user_remaining_pack_count[k], reverse=True):
                    user_list.append(k)

            if len(sorted_facility_pack_count) != 0:
                packs_set = set()
                for facility in sorted_facility_pack_count.keys():
                    packs_set.update(facility_packs[facility])
                s_facility_patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id,
                                                                                                      list(packs_set))
                facility_patient_packs = OrderedDict(
                    sorted(s_facility_patient_packs.items(), key=lambda x: len(x[1]), reverse=True))
                user_cluster_list = PriorityQueue()
                for user in user_list:
                    new_dict = {"cluster": [], "user": user}
                    user_cluster_list.push(new_dict, len(user_pack_list[user]))
                configuration_priority_queue = PriorityQueue()
                for patient, packs in facility_patient_packs.items():
                    priority = -1 * len(packs)
                    configuration_priority_queue.push(patient, priority)

                while not configuration_priority_queue.isEmpty():
                    # print("item", item, "number of packs", priority_for_item)
                    user_cluster, priority_for_cluster = user_cluster_list.pop()
                    # print("robot cluster", robot_cluster, "number of packs", priority_for_cluster)
                    user = user_cluster["user"]
                    if user_remaining_pack_count[user] >= priority_for_cluster:
                        item, priority_for_item = configuration_priority_queue.pop()
                        priority_for_item *= -1
                        user_cluster["cluster"].append(item)
                        priority_for_cluster += priority_for_item
                    else:
                        priority_for_cluster = len(manual_packs) + 1
                    user_cluster_list.push(user_cluster, priority_for_cluster)

                while not user_cluster_list.isEmpty():
                    user_clust, number_of_packs = user_cluster_list.pop()
                    packs = set()
                    for patient in user_clust["cluster"]:
                        packs.update(facility_patient_packs[patient])
                    user_pack_list[user_clust["user"]].update(packs)
                print("data")
            user_pack_count = {}
            for user, packs in user_pack_list.items():
                user_pack_count[user] = len(packs)
            date_user_pack_count[str(date)] = user_pack_count
            date_user_pack_dict[str(date)] = user_pack_list

            for user, packs in user_pack_list.items():
                manual_packs_by_user[user].update(map(str, packs))
            # user_list.clear()
            # # for k in sorted(manual_packs_by_user, key=lambda k: len(manual_packs_by_user[k])):
            # for k in manual_packs_by_user:
            #     user_list.append(k)

        logger.info("date user pack count {}".format(date_user_pack_count))
        logger.info("date user pack dict {}".format(date_user_pack_dict))
        return manual_packs_by_user
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.info(e)
        raise


@log_args_and_response
@validate(required_fields=['pack_list', 'user_list', 'company_id', 'user_id'])
def transfer_manual_packs(manual_packs_dict):
    """
    changes batch_id for pending packs, deletes related data and marks batch as processing done
    :param manual_packs_dict: format: {"batch_id":703, "system_id": 2}
    :return:
    """
    try:
        pack_list = manual_packs_dict['pack_list']
        user_list = manual_packs_dict['user_list']
        company_id = manual_packs_dict['company_id']
        user_id = manual_packs_dict['user_id']

        manual_pack_by_user = manual_user_distribution_flow_handler(user_list, pack_list, company_id)

        return create_response(manual_pack_by_user)

    except (IntegrityError, InternalError) as e:

        logger.error(e, exc_info=True)

        return error(2001)


@log_args_and_response
def get_pack_count_for_canister_skip(company_id: int, system_id: int, batch_id: int, canister_id: int, device_id: int):
    """
    Function to get pack count for which these canisters can be skipped, based on number of packs
    that can be processed in pending hours of the day i.e skip for day
    @param company_id:
    @param system_id:
    @param batch_id:
    @param canister_id:
    @param device_id:
    @return:
    """
    try:
        no_of_packs_to_skip = 0
        # define default format of time
        FMT = '%H:%M:%S'
        current_time = get_current_time()
        current_time_formatted = datetime.datetime.strptime(
            current_time, FMT)
        logger.info("get_pack_count_for_canister_skip current_time {}, {}".format(current_time, current_time_formatted))

        # get system day end time
        system_info = get_system_setting_by_system_id(system_id=system_id)
        logger.info("get_pack_count_for_canister_skip system_info {}".format(system_info))

        automatic_per_hour = int(system_info['AUTOMATIC_PER_HOUR'])
        automatic_day_end_time = float(system_info['AUTOMATIC_DAY_END_TIME'])

        day_end_time_in_hour = str(datetime.timedelta(hours=automatic_day_end_time))
        day_end_time_in_hour_formatted = datetime.datetime.strptime(day_end_time_in_hour, FMT)
        logger.info("get_pack_count_for_canister_skip day_end_time_in_hour {}".format(day_end_time_in_hour))

        # if current time is less than pharmacy day end time
        if current_time_formatted < day_end_time_in_hour_formatted:
            # get pending hours calculate packs that can be skipped considerin system capacity per hour
            remaining_time_in_seconds = (day_end_time_in_hour_formatted - current_time_formatted).seconds
            logger.info(
                "get_pack_count_for_canister_skip remaining_time_in_seconds {}".format(remaining_time_in_seconds))

            remaining_time_in_float = remaining_time_in_seconds / settings.AUTO_SECONDS
            logger.info("get_pack_count_for_canister_skip remaining_time_in_float {}".format(remaining_time_in_float))

            if remaining_time_in_float > 0:
                no_of_packs_to_skip = math.ceil((remaining_time_in_float * automatic_per_hour)/2)

        # get pack count by status id
        packs_list_pending \
            = get_pending_progress_pack_count(system_id, batch_id,
                                              [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                                              device_id)

        batch_pack_count = len(packs_list_pending)
        logger.info(
            "get_pack_count_for_canister_skip batch pack count, no of pack to skip, pack count {}, {}, {}".format(
                batch_pack_count,
                no_of_packs_to_skip,
                packs_list_pending))
        if no_of_packs_to_skip > batch_pack_count:
            no_of_packs_to_skip = batch_pack_count

        response = {
            'packs_to_skip': no_of_packs_to_skip,
            'batch_pack_count': batch_pack_count
        }
        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_pack_count_for_canister_skip {}".format(e))
        raise e


@log_args_and_response
@validate(required_fields=['user_id', 'system_id', 'batch_id', 'company_id', 'version_type'])
def run_recommendations(batch_info):
    """
        This function to run recommendation
        :param batch_info:
        :return:
    """
    batch_id = batch_info.get('batch_id')
    try:
        with db.transaction():
            batch_data = get_batch_data(batch_id)
            if batch_data.sequence_no == constants.PPP_SEQUENCE_IN_PROGRESS:
                return error(2000)
            else:
                previous_sequence = batch_data.sequence_no
                logger.info("In run_recommendations: previous sequence: {} for batch_id:{}".format(previous_sequence, batch_id))

                # run run_recommendations (canister recommendation) if sequence is pending (0)
                if previous_sequence != constants.PPP_SEQUENCE_SAVE_ALTERNATES:
                    return error(1020, 'Batch is not in pending state. ')

                # update sequence_no to PPP_SEQUENCE_IN_PROGRESS(1) in batch master
                seq_status = update_sequence_no_for_pre_processing_wizard(
                    sequence_no=constants.PPP_SEQUENCE_IN_PROGRESS,
                    batch_id=batch_id)
                logger.info("In run_recommendations: run_recommendations execution started and sequence updated : {} for batch_id: {}, changed sequence to: {}"
                             .format(seq_status, batch_id, constants.PPP_SEQUENCE_IN_PROGRESS))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                    logger.info("In run_recommendations : time stamp update for pre processing wizard for in_progress API: {} and batch_id: {}".format(couch_db_status, batch_id))

        if batch_info['version_type'] in settings.V2:
            response = save_distributed_packs_by_batch(batch_info=batch_info)
            return response
        elif batch_info['version_type'] in settings.V3:

            response = save_distributed_packs_by_batch_v3(batch_info=batch_info)

            # update sequence_no to PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE(it means pack_distribution_by_batch api run successfully)
            if json.loads(response)['status'] == settings.SUCCESS_RESPONSE:
                seq_status = update_sequence_no_for_pre_processing_wizard(
                    sequence_no=constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE, batch_id=batch_id)
                logger.info("In run_recommendations: run_recommendations run successfully: {},for batch_id: {}, changed sequence to {} "
                             .format(seq_status, batch_id, constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE,))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                    logger.info("In run_recommendations : time stamp update for pre processing wizard: {} when run_recommendations completed for batch_id: {}".format(couch_db_status, batch_id))
            else:

                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                          batch_id=batch_id)
                logger.info("In run_recommendations: failure in run_recommendations: {} , changed sequence to {} for batch_id: {}"
                             .format(seq_status, previous_sequence, batch_id))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                    logger.info("In run_recommendations : time stamp update for pre processing wizard: {} when response is fail for batch_id: {}".format(couch_db_status, batch_id))

            return response
        else:
            seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                      batch_id=batch_id)
            logger.info("In run_recommendations: failure in run_recommendations: {} when version is mismatch, changed sequence to {} for batch_id: {}"
                         .format(seq_status, previous_sequence, batch_id))
            if seq_status:
                # update couch db timestamp for pack_pre_processing_wizard change
                couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                logger.info(
                    "In run_recommendations : time stamp update for pre processing wizard: {} when version mismatch for batch_id: {}".format(couch_db_status, batch_id))
            return error(1020, "Invalid version type id.")
    except (InternalError, IntegrityError) as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre_processing_wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
            logger.info("In run_recommendations : time stamp update for pre processing wizard: {} when exception occurs change sequence to : {} for batch_id: {}".format(
                couch_db_status,previous_sequence, batch_id))
        logger.error(e, exc_info=True)
        return error(2001, e)
    except Exception as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre_processing_wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
            logger.info("In run_recommendations : time stamp update for pre processing wizard: {} when exception occurs change sequence to : {} for batch_id: {}".format(
                    couch_db_status, previous_sequence, batch_id))
        logger.error(e, exc_info=True)
        return error(2001, e)


@log_args_and_response
def get_robot_data_batch_sch(system_id_list):
    '''
    This function fetches data of all devices including Robots and CSRs
    :param system_id_list:
    :return:
    '''
    robot_capacity = dict()
    system_id_list = list(map(int, system_id_list))
    robots_data = db_get_robots_by_systems(system_id_list=system_id_list)
    # for item in robot_list:
    #     robots_data.setdefault(item["system_id"], list()).append(item)
    robot_ids = [item["id"] for robots in robots_data.values()
                 for item in robots
                 if item["system_id"] in system_id_list]
    disabled_locations = defaultdict(set)
    system_robots = defaultdict(list)
    for record in get_disabled_locations_of_devices(device_ids=robot_ids):
        disabled_locations[record["device_id"]].add(record["location_number"])
    for system, robots in robots_data.items():
        if system in system_id_list:
            for robot in robots:
                system_robots[system].append(robot["id"])
                robot_capacity[robot["id"]] = robot["max_canisters"]

    return robot_ids, robots_data, robot_capacity, system_robots


@log_args_and_response
def get_pack_data(pack_ids_list, company_id):
    """
    """
    pack_ids_set = set()
    drug_ids_set = set()
    facility_packs = defaultdict(set)
    pack_mapping = defaultdict(lambda: defaultdict(float))
    pack_manual = defaultdict(bool)
    pack_drug_manual = defaultdict(dict)  # if drug is only fractional and less than 1, mark manual

    cache_drug_data = dict()

    pack_status_list = [
        settings.PENDING_PACK_STATUS,
        settings.PROGRESS_PACK_STATUS
    ]
    if not pack_ids_list:
        return pack_ids_set, drug_ids_set, pack_mapping, cache_drug_data, pack_manual
    query = get_pack_data_query(pack_ids_list, pack_status_list)

    try:
        for record in query.dicts():
            # list of unique qty for a drug in pack
            quantities = list(set([float(item) % 1 for item in record["quantities"].split(',')]))
            if 0 in quantities:  # keeping only fractional qty in list
                quantities.remove(0)
            if not pack_manual[record["pack_id"]] and len(quantities) > 0:
                # manual based on fractional qty
                pack_manual[record["pack_id"]] = True

            quantity = float(record["quantity"])

            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            robot_drug_quantities = {float(item) for item in record["quantities"].split(",")
                                     if float(item) >= 1}
            # if no quantities are robot quantities, it is fully manual
            pack_drug_manual[record["pack_id"]][fndc_txr] = not bool(robot_drug_quantities)
            pack_mapping[record["pack_id"]][fndc_txr] += quantity
            pack_ids_set.add(record["pack_id"])
            drug_ids_set.add(fndc_txr)
            facility_packs[record["facility_id"]].add(record["pack_id"])

            if fndc_txr not in cache_drug_data:
                cache_drug_data[fndc_txr] = {
                    "drug_name": record["drug_name"],
                    "ndc": record["ndc"],
                    "strength": record["strength"],
                    "formatted_ndc": record["formatted_ndc"],
                    "txr": record["txr"],
                    "strength_value": record["strength_value"],
                    "image_name": record["image_name"],
                    "required_quantity": quantity,
                    "imprint": record["imprint"],
                    "shape": record["shape"],
                    "color": record["color"],
                    "drug_id": record["drug_id"]
                }
            else:
                cache_drug_data[fndc_txr]["required_quantity"] += quantity

    except (DoesNotExist, InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    return pack_ids_set, drug_ids_set, pack_mapping, cache_drug_data, pack_manual, pack_drug_manual, facility_packs


# def cr_analysis(batch_info):
#
#     # Check batch status
#     previous_speed = settings.SYSTEM_SPEED
#     previous_strategy = settings.CR_STRATEGY
#     analysis_data = {}
#     batch_id = batch_info.get('batch_id')
#     speed = batch_info.get('speed', 2)
#     try:
#         with db.transaction():
#             batch_data = get_batch_data(batch_id)
#             if batch_data.sequence_no == constants.PPP_SEQUENCE_IN_PROGRESS:
#                 return error(2000)
#             else:
#                 previous_sequence = batch_data.sequence_no
#                 logger.info(
#                     "In run_recommendations: previous sequence: {} for batch_id:{}".format(previous_sequence, batch_id))
#
#                 # run run_recommendations (canister recommendation) if sequence is pending (0)
#                 if previous_sequence not in [constants.PPP_SEQUENCE_SAVE_ALTERNATES, constants.PPP_SEQUENCE_IN_PENDING]:
#                     return error(1020, 'Batch is not in pending state. ')
#
#                 # update sequence_no to PPP_SEQUENCE_IN_PROGRESS(1) in batch master
#                 seq_status = update_sequence_no_for_pre_processing_wizard(
#                     sequence_no=constants.PPP_SEQUENCE_IN_PROGRESS,
#                     batch_id=batch_id)
#                 logger.info(
#                     "In run_recommendations: run_recommendations execution started and sequence updated : {} for batch_id: {}, changed sequence to: {}"
#                     .format(seq_status, batch_id, constants.PPP_SEQUENCE_IN_PROGRESS))
#         if speed == 1:
#             # run recommendation for 1x
#             settings.SYSTEM_SPEED = 1
#             settings.CR_STRATEGY = 1
#             response = save_distributed_packs_by_batch_v3(batch_info=batch_info)
#             logger.info("Analysis for 1x is executed")
#
#
#             # fetch data for last recommendation
#             if json.loads(response)['status'] == settings.SUCCESS_RESPONSE:
#                 seq_status = update_sequence_no_for_pre_processing_wizard(
#                     sequence_no=constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE, batch_id=batch_id)
#             analysis, drop_count, canister_data, manual_drugs, canister_count = cr_analysis_fetch_data(batch_id)
#             analysis_data['1x'] = {'analysis': analysis, 'drop_count': drop_count, 'canister_data': canister_data,
#                                    "manual_drugs": manual_drugs, "canister_count" :canister_count}
#
#         # Revert batch
#         # args = {"batch_id": batch_id, "company_id": 3, "system_id": 14, "revert_to_screen": "schedule_batch",
#         #         "current_module_id": 2, "pack_ids": [], "call_from_screen": "pack_pre_processing",
#         #         "revert_pack_flag": 0, "user_id": 13}
#         # revert = revert_batch_v3(args)
#         # run recommendation for Nx
#         if speed == 2:
#             settings.SYSTEM_SPEED = 4
#             settings.CR_STRATEGY = 2
#             response = save_distributed_packs_by_batch_v3(batch_info=batch_info)
#             logger.info("Analysis for 2x is executed")
#
#             # fetch data for Nx recommendation
#             if json.loads(response)['status'] == settings.SUCCESS_RESPONSE:
#                 seq_status = update_sequence_no_for_pre_processing_wizard(
#                     sequence_no=constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE, batch_id=batch_id)
#             analysis, drop_count, canister_data, manual_drugs, canister_count = cr_analysis_fetch_data(batch_id)
#             analysis_data['Nx'] = {'analysis': analysis, 'drop_count': drop_count, 'canister_data': canister_data,
#                                    "manual_drugs": manual_drugs, "canister_count" :canister_count}
#
#     except Exception as e:
#         return e
#     finally:
#
#         #  Show both data in formatted manner
#
#         settings.SYSTEM_SPEED = previous_speed
#         settings.CR_STRATEGY = previous_strategy
#         return create_response(analysis_data)