# TODO Why do we call this file TablesAsObjects.py? - Per our methodology each class is a file.

from .Constants import *
from .utils import get_curr_state
from variable_local.variable import VariablesLocal
from dotenv import load_dotenv
load_dotenv()
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from circles_local_database_python.connector import Connector

object_to_insert = {
    'component_id': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'idan.a@circ.zone and guy.n@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

# class Variable(object):
#     def __init__(self):
#         self.name2id_dict = {}
#         self.id2name_dict = {}
#         self.next_variable_id = 1
#         for variable_id in VARIABLE_NAMES_DICT:
#             self.add(variable_id, VARIABLE_NAMES_DICT[variable_id])

#     def add(self, variable_id : int, variable_name : str):
#         try:
#             self.name2id_dict[variable_name] = variable_id
#             self.id2name_dict[variable_id] = variable_name
#             cursor.execute("""INSERT INTO variable_table(id, name) VALUES (%s, %s)""", [variable_id, variable_name])
#             connection.commit()

#         except:
#             """TODO: add error to logger"""

#     def get_variable_id(self, variable_name : str):
#         return self.name2id_dict[variable_name]

#     def get_variable_name(self, variable_id : int):
#         return self.id2name_dict[variable_id]

#     def get_variable_value_by_name(self, language: str, variable_name : str) -> str:
#         variable_id = self.get_variable_id(variable_name)
#         return get_variable_value_by_id(self, language, variable_id)


class ProfileContext (object):
    # TODO We should consider to take ProfileContact to a separate package or merge it with UserContext
    def __init__(self, profile_id):
        self.dict = {}
        self.profile_id = profile_id
        self.chosen_poll_options = {}
        self.curr_state_id = get_curr_state(self.profile_id)
        self.variables = VariablesLocal()
        self.groups = []

    # TODO get_variable_value_by_variable_id
    def get_variable_value_by_id(self, variable_id: int) -> str:
        logger.start(object={'variable_id': variable_id})
        variable_value = self.dict[variable_id]
        logger.end(object={'variable_value': variable_value})
        return variable_value

    def save_chosen_options(self, question_asked: str, variable_id: int, chosen_numbers_list: list, list_of_options: list):
        """Saves the options chosen by the user in the multi_choice_poll action in a dict with the question as the key
            and a list of the options chosen as the value i.e: {<question asked> : [<chosen option 1>, <chosen option 2>..]}
            Also saves the chosen options in the database."""
        logger.start(object={'question_asked': question_asked, 'variable_id': variable_id, 'chosen_numbers_list': chosen_numbers_list, 'list_of_options': list_of_options})
        self.chosen_poll_options[question_asked] = [
            list_of_options[chosen_option-1] for chosen_option in chosen_numbers_list]
        variable_value_to_insert = question_asked + " "
        for chosen_option in self.chosen_poll_options[question_asked]:
            variable_value_to_insert = variable_value_to_insert + \
                str(chosen_option) + ", "
        self.variables.set_variable_value_by_variable_id(
             variable_id, variable_value_to_insert, self.profile_id,self.curr_state_id)
        logger.end()

    def get_variable_value_by_name(self, variable_name: str) -> str:
        # TODO get_variable_value_by_variable_name
        logger.start(object={'variable_name': variable_name})
        # TODO self.get_variable_value_by_id( -> self.get_variable_value_by_variable_id(
        variable_value = self.get_variable_value_by_id(self.variables.get_variable_id(variable_name))
        logger.end(object={'variable_value': variable_value})
        return variable_value
    
    # TODO Should be moved to variable-value-local-python-package
    def set(self, variable_id: int, variable_value: str):
        logger.start(object={'variable_id': variable_id, 'variable_value': variable_value})
        self.dict[variable_id] = variable_value
        connection = Connector.connect('logger')
        cursor = connection.cursor(dictionary=True, buffered=True)
        # cursor.execute("""USE logger""")
         # TODO Can we replace it with GenericCRUD
        cursor.execute("""INSERT INTO logger
                        (profile_id, state_id, variable_id, variable_value_new) 
                        VALUES (%s,%s,%s,%s)""",
                       (self.profile_id, self.curr_state_id, variable_id, variable_value))
        # cursor.execute("""USE dialog_workflow""")
        connection.commit()
        logger.end()


class ProfilesDict(object):
    def __init__(self):
        self.profiles_dict = {}

    def add(self, profile: ProfileContext):
        logger.start(object={'profile': profile})
        # TODO Should we also keep in the database?
        self.profiles_dict[profile.profile_id] = profile
        logger.end()

    def get(self, profile_id: int) -> ProfileContext:
        logger.start(object={'profile_id': profile_id})
        if profile_id not in self.profiles_dict:
            logger.end()
            return None
        else:
            profile_dict = self.profiles_dict[profile_id]
            logger.end(object={'profile_dict': profile_dict})
            return profile_dict
        # return None if profile_id not in self.profiles_dict else self.profiles_dict[profile_id]


class DialogWorkflowRecord(object):
    def __init__(self, record):
        self.curr_state_id: int = record["state_id"] if "state_id" in record else None
        self.parent_state_id: int = record["parent_state_id"] if "parent_state_id" in record else None
        self.workflow_action_id: int = record["workflow_action_id"] if "workflow_action_id" in record else None
        self.lang_code = record["lang_code"] if "lang_code" in record else None
        self.parameter1 = record["parameter1"] if "parameter1" in record else None
        self.variable1_id: int = record["variable1_id"] if "variable1_id" in record else None
        self.result_logical = record["result_logical"] if "result_logical" in record else None
        self.result_figure_min: float = record["result_figure_min"] if "result_figure_min" in record else None
        self.result_figure_max: float = record["result_figure_max"] if "result_figure_max" in record else None
        self.next_state_id: int = record["next_state_id"] if "next_state_id" in record else None
        self.no_feedback_milliseconds: float = record[
            "no_feedback_milliseconds"] if "no_feedback_milliseconds" in record else None
        self.next_state_id_if_there_is_no_feedback: int = record[
            "next_state_id_if_there_is_no_feedback"] if "next_state_id_if_there_is_no_feedback" in record else None
