import json
from src.independentclusters import RecommendCanisterToAdd, RecommendCanistersToRemove, RecommendCanistersToTransfer
from copy import deepcopy

print("Import successful")

# TODO: check output of canister to register is None or [] when there are no canister to register.
# TODO: check with Dushyant for the same.
# TODO: None analysis, check where all the drugs are same what happens.
# TODO: check edge cases for all.



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

def append_dictionary_to_json_file(dict, dict_name, save_json, json_name):
    """
    This method will save(append) passed dictionary to json
    :return:
    """
    if save_json:
        dict_to_store = {dict_name: deepcopy(dict)}
        print ("dict to store", dict_to_store)
        # a = json.dumps(dict_to_store, default=date_handler)
        with open(json_name, 'a+') as fp:
            json.dump(dict_to_store, fp, default=date_handler)
    pass


class CanisterRecommender:
    """
    This class will provide given utilities.
    1) It will recommend canisters to add(register) for given data frame.
    2) It will recommend canisters to remove from the dosepacker.
    3) It will recommend canisters to transfer for achieving optimal distribution of packs to the robot.

    Glossary:-
    ------------
    1) Dataframe:-- Pandas data frame containing the list of drugs as columns and the list of packs as rows of a 2d
    Matrix.
    2) Robot_capacity_info_dict:-- Dictionary containing robot id as key and the maximum number of canisters it can
    accommodate as the value.
    3) Drug_canister_info_dict:-- Drug id as key, list of canister ids as value.
    4) canister_location_info_dict:-- canister id as key, tuple containing (robot_id, location_id) as value.
    If the canister is placed outside the robot, robot id will be None.
    5) list_of_canisters_to_add:-- The list of tuples, every tuple contains canister id as the first element and
    quantity(number of canisters to add for that drug) as the second element.
    6) canister_transfer_info_dict:--Dictionary, canister id as key, tuple of (src_robot_id,
    destination_robot_id) as value.
    7) Pack_robot_drug_info_dict:-- Dictionary, key = pack_id, value = {[(drug_id, canister_id, robot_id)]}
    8) Robot_free_location_info_dict:-- Dictionary, key = Robot_id, value = [free location id list]
    """

    def __init__(self, file_name=None, df=None, robot_capacity_info_dict=None, drug_canister_info_dict=None,
                 canister_location_info_dict=None, robot_free_location_info_dict=None, external_manual_drug_list=None):
        # Define for which functionality you will be using the object for this class.
        # self.recommend_canisters_to_add = recommend_canisters_to_add
        # self.recommend_canisters_to_remove = recommend_canisters_to_remove
        # self.recommend_canisters_to_transfer = recommend_canisters_to_transfer

        # Defining Variables
        self.debug_mode = False
        self.file_name = file_name
        self.df = df
        self.robot_capacity_info_dict = robot_capacity_info_dict
        self.drug_canister_info_dict = drug_canister_info_dict
        self.canister_location_info_dict = canister_location_info_dict
        self.save_data_frame = False
        self.robot_free_location_info_dict = robot_free_location_info_dict
        self.external_manual_drug_list = external_manual_drug_list
        if self.save_data_frame:
            # self.writer = pd.ExcelWriter('output.xlsx')
            self.df.to_csv('output.csv')
            # self.writer.save()
        pass

    def recommend_canisters_to_add(self, truncated = True):
        """
        This method will recommmend canisters to add in the form of list of tuple.
        :return: recommended_canister_list_of_tuple
        """
        self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=self.df, drug_canister_info_dict=self.drug_canister_info_dict)
        if truncated:
            _, recommended_canister_list_of_tuple = self.rca.get_recommendation_to_add_canisters_truncated()
            return recommended_canister_list_of_tuple
        else:
            _, recommended_canister_list_of_tuple = self.rca.get_recommendation_to_add_canisters()
            return recommended_canister_list_of_tuple

    def recommend_canisters_to_remove(self):
        """

        :return:
        """
        self.rcr = RecommendCanistersToRemove(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                              drug_canister_info_dict=self.drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict)
        canisters_to_remove_list = self.rcr.recommend_canisters_to_remove()
        return canisters_to_remove_list

    def recommend_canisters_to_transfer(self):
        self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                              drug_canister_info_dict=self.drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict, robot_free_location_info_dict=self.robot_free_location_info_dict)
        canister_transfer_info_dict = self.rct.recommend_canisters_to_transfer()
        return canister_transfer_info_dict

    def recommend_canisters_to_transfer_hybrid(self):
        """
        This method is called when we want to get recommendation of remove and transfer altogether,
        - In this method we will get recommendation for removing canister in the form of dictionary with value tuple.
        - We will append both recommendation.
        :return:
        """
        self.rcr = RecommendCanistersToRemove(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                              drug_canister_info_dict=self.drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict)
        insufficient_space_canister_remove_dict = self.rcr.recommend_canisters_to_remove(hybrid_method=True)
        """
        converting insufficient_space_canister_remove_dict into format of canister transfer info dict.
        """
        canister_transfer_info_dict_for_remove = {}
        for robot_id in insufficient_space_canister_remove_dict.keys():
            for canister_id in insufficient_space_canister_remove_dict[robot_id]:
                canister_transfer_info_dict_for_remove[canister_id] = (robot_id, None)
        self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                drug_canister_info_dict=self.drug_canister_info_dict,
                                                canister_location_info_dict=self.canister_location_info_dict,
                                                robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                external_manual_drug_list=self.external_manual_drug_list)
        canister_transfer_info_dict, analysis = self.rct.recommend_canisters_to_transfer()
        canister_transfer_info_dict.update(canister_transfer_info_dict_for_remove)
        append_dictionary_to_json_file(canister_transfer_info_dict, "canister_transfer_info_dict_hybrid", True, "transfer.json")
        return canister_transfer_info_dict, analysis
