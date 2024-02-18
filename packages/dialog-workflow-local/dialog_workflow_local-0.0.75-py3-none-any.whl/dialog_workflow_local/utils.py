# TODO: Let's talk about Constants and the usage in this file
from .Constants import *
import json
from dotenv import load_dotenv
load_dotenv()
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD

object_to_insert = {
    'component_id': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'idan.a@circ.zone and guy.n@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

# from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage

# TOOD: Please include type to all parameters.
# TODO: Please include return value.
# TODO: Please add short documentation per PEP8 standard

# TODO:Let's move to Object Oriented Programming

def get_variable_value_by_id(language: str, variable_id : int) -> str:
    logger.start(object={'variable_id': variable_id})
    connection = Connector.connect('logger')
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("""SELECT variable_value_new FROM logger_dialog_workflow_state_history_view WHERE variable_id= %s ORDER BY timestamp DESC""", [variable_id])
    variable_value = (cursor.fetchone())["variable_value_new"]
    logger.end(object={'variable_value': variable_value})
    return variable_value

# This code is commended since it moved to variable-local:

# class replace_fields_with_values(object):
#     def __init__(self, message, language: str, variable):
#         self.message = message
#         self.language = language
#         self.variable = variable

#     def choose_option(self, message_index : int, first_param: str):
#         """ Gets a messsage, an index of the first apearance of '|' , and the first parameter of the options
#             Returns:
#             1. One of the options randomly selected
#             2. The index of one char after the next '}'"""
#         list_of_params = [first_param]
#         while(self.message[message_index] != '}'):
#             next_param = ""
#             while(self.message[message_index] != '|' and self.message[message_index] != '}'):
#                 next_param = next_param + self.message[message_index]
#                 message_index = message_index + 1
#             list_of_params.append(next_param)
#             message_index = message_index + 1 if self.message[message_index] != '}' else message_index
#         random_index = random.randint(0, len(list_of_params)-1)
#         return list_of_params[random_index], message_index + 1

#     """For the following function to work the message must not have single '{' or '}'. They should always come in pairs"""
#     def get_variable_names_and_chosen_option(self):
#         """Returns:
#             1. A list of all variable names that were inside curly braces of message
#             2. A string that's a copy of the message but without the variable names inside curly braces,
#             and a randomly chosen parameter out of each curly braces options:
#             "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?" 
#         """
#         variable_names_list = []
#         message_without_variable_names = ""
#         message_index = 0
#         while message_index < len(self.message):
#             index_after_choosing_option = None
#             if(self.message[message_index] == '{'):
#                 message_index = message_index + 1
#                 next_variable_name = ""
#                 chosen_parameter = None
#                 while self.message[message_index] != '}':
#                     if self.message[message_index] == '|':
#                         chosen_parameter, index_after_choosing_option = self.choose_option(message_index+1, next_variable_name)
#                         break
#                     next_variable_name = next_variable_name + self.message[message_index]
#                     message_index = message_index + 1
#                 if chosen_parameter != None:
#                     message_without_variable_names = message_without_variable_names + chosen_parameter
#                 else:
#                     message_without_variable_names = message_without_variable_names + "{}"
#                     variable_names_list.append(next_variable_name)
#             else:
#                 message_without_variable_names = message_without_variable_names + self.message[message_index]
#             message_index = message_index + 1 if index_after_choosing_option == None else index_after_choosing_option
#         return variable_names_list, message_without_variable_names

#     def get_variable_values_and_chosen_option(self):
#         """Returns:
#             1. A list of all variable values by variable names that were inside curly braces of message 
#             2. A string that's a copy of the message but without the variable names inside curly braces
#             and a randomly chosen parameter out of each curly braces options:
#             "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?"
#         """
#         variable_names_list, message_without_variable_names = self.get_variable_names_and_chosen_option()
#         variable_value_list = []
#         for variable_name in variable_names_list:
#             variable_id = self.variable.get_variable_id(variable_name)
#             variable_value = get_variable_value_by_id(self.language, variable_id)
#             variable_value_list.append(variable_value)    
#         return message_without_variable_names.format(", ".join(variable_value_list))

# TODO change the ints to types/enums/classes
def process_message(communication_type : int, action_type : int, message : str):
    """Processes message according to which communication_type is used: console or websocket
        If console then we continue the code normally.
        If websocket then we create a json out of the given message and exit(0)"""
    logger.start(object={'communication_type': communication_type,'action_type': action_type, 'message': message})
    if communication_type == communication_type_enum.CONSOLE.value:
        message = message.replace('~', '\n')
        logger.end()
        return None
    if communication_type == communication_type_enum.WEBSOCKET.value:
        message = update_json_message(action_type, message)
        logger.end(object={'message': message})
        return message

def update_json_message(action_type: int, message: str) -> json:
    """Update message to json format"""
    logger.start(object={"action_type": action_type, "message": message})
    json_message = {"message": message}
    if action_type == action_enum.AGE_DETECTION.value:
        json_message["type"] = "command"
    else:
        json_message["type"] = "text"
    json_dumps = json.dumps(json_message) 
    logger.end(object={'json_dumps': json_dumps}) 
    return json_dumps

def update_profile_curr_state_in_DB(new_state: int, profile_id):
    """This function updates the last_dialog_workflow_state_id in the profile table to the new state.
       Note that this function UPDATES the field sand doesn't INSERT into the table. """
    logger.start(object={"new_state": new_state, 'profile_id': profile_id})
    connection = Connector.connect('profile')
    cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE profile""")
    cursor.execute("""UPDATE profile_table SET last_dialog_workflow_state_id = %s WHERE (profile_id= %s)""", [new_state, profile_id])
    # cursor.execute("""USE dialog_workflow""")
    connection.commit()
    logger.end()

# TODO Should be moved to variable-value-local-python-package
def insert_profile_variable_value(profile_id: int, variable_id : int, variable_value : str, profile_curr_state: int):
    """This function inserts a variable value into the logger table for a given profile"""
    logger.start(object={'profile_id': profile_id, 'variable_id': variable_id, 'variable_value': variable_value, 'profile_curr_state': profile_curr_state})
    # connection = Connector.connect('logger')
    # cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE logger""")    
    # cursor.execute("""INSERT INTO logger_table
    #                 (profile_id, state_id, variable_id, variable_value_new) 
    #                 VALUES (%s,%s,%s,%s)""", 
    #                 (profile_id, profile_curr_state, variable_id, variable_value))
    object = {'profile_id': profile_id, 'state_id': profile_curr_state, 'variable_id': variable_id, 'variable_value_new': variable_value}
    logger.info(object = object)
    # cursor.execute("""USE dialog_workflow""")
    # connection.commit()
    logger.end()

#TODO: Make sure we have good testing coverage to this function
def store_age_detection_picture(age_range: str, profile_id: int):
    """Stores the picture in Nir's storage schema, gets a storage_id and inserts into the computer_vision_storage_table"""
    # storage = AwsS3Storage(bucket_name="storage.us-east-1.dvlp1.bubblez.life", region="us-east-1")
    # storage_id = storage.upload_file("C:\\Users\\User\\OneDrive\\Circles\\age-detection-backend\\src\\alonPicture.png", "Alon's picture", "", 1)
    
    age_range_split = age_range.split('-')
     # TODO Why this is commented?
     # TODO Why we commented this? Let's uncomment
    # min_age = int(age_range_split[0][:len(age_range_split[0])-1])
    # max_age = int((age_range_split[1])[1:])
    # cursor.execute("""USE computer_vision_storage""")
    # cursor.execute("""INSERT INTO computer_vision_storage_table 
    #                 (storage_id, profile_id, min_age, max_age) VALUES (%s, %s, %s, %s)""", 
    #                [storage_id, profile_id, min_age, max_age])
    # connection.commit()

# TODO Shall we move it to Profile Context?
def get_curr_state(profile_id: int):
    """Returns profiles' curernt state number"""
    logger.start(object={'profile_id': profile_id})
    connection = Connector.connect('profile')
    cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE profile""")
    cursor.execute("""SELECT last_dialog_workflow_state_id FROM profile_view WHERE profile_id = %s ORDER BY profile_id DESC""", [profile_id])
    curr_state = int((cursor.fetchone())["last_dialog_workflow_state_id"])
    # cursor.execute("""USE dialog_workflow""")
    logger.end(object={'curr_state': curr_state})
    return curr_state

def get_child_nodes_of_current_state(fields : list, table_name : str, values_from_where_to_select : list, variables_from_where_to_select : list):
    """Recieves all of the relevant information and selects the child nodes of the current state from the given table, and returns them"""
    logger.start(object={'fields': fields, 'table_name': table_name, 'values_from_where_to_select': values_from_where_to_select, 'variables_from_where_to_select': variables_from_where_to_select})
    sql_query = "SELECT " + ", ".join(fields) + " FROM " + table_name + " WHERE "
    # Add the variables and values to the SQL query
    for i in range(len(variables_from_where_to_select)):
        sql_query += variables_from_where_to_select[i] + " = %s"
        if i != len(variables_from_where_to_select) - 1:
            sql_query += " AND "
    connection = Connector.connect('dialog_workflow')
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(sql_query, values_from_where_to_select)
    child_nodes = cursor.fetchall()
    logger.end(object={'child_nodes': child_nodes})
    return child_nodes

class group(object):
    def __init__(self, parameter1):
        self.parameter1 = parameter1

    # TODO Make sure we have tests for this and all other methods        
    def get_group_childs_id_bellow_parent_id(self) -> list[int]:  
        """returns all of the childs ids below the given parent_id.
            This function gets all of the id's of records that their parent_state_id is the given id, and continues to add id's  recursively 
            until all of the records that their parent_state_id matches an id in the table."""
        logger.start()
        connection = Connector.connect("group")
        cursor = connection.cursor(dictionary=True, buffered=True)
        # cursor.execute("""USE `group`""")
        # TODO Fix this SQL
        cursor.execute("""WITH RECURSIVE cte AS (
            SELECT group_view.group_id FROM group_view WHERE group_id = %s
            UNION ALL
            SELECT group_view.group_id FROM group_view 
            JOIN cte ON group_view.parent_group_id = cte.group_id
        )
        SELECT cte.group_id FROM cte""", [self.parameter1])  
        group_id_dict = cursor.fetchall()
        # TODO id -> group_id
        group_childs_id = [group['group_id'] for group in group_id_dict]
        logger.end(object={'group_childs_id': group_childs_id})
        return group_childs_id

    def get_child_group_names(self) -> list:
        """Gets all of the child title names from the ml table of the given parent_id."""
        logger.start()
        group_ids = self.get_group_childs_id_bellow_parent_id()
        group_id_string = ','.join(str(id) for id in group_ids)
        connection = Connector.connect('group')
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT title FROM group_ml_en_view WHERE group_id IN ({group_id_string}) ")
        group_name_dict = cursor.fetchall()
        child_group_names = [group['title'] for group in group_name_dict]
        logger.end(object={'child_group_names': child_group_names})
        return child_group_names
    
    # def get_child_group_id(self) -> list[int]:
    #     """Gets the id of all the records with the given group name"""
    #     cursor.execute("""USE `group`""")
    #     cursor.execute("""SELECT group_id from group_ml_en_view WHERE title = %s""", [self.parameter1])
    #     group_id_dict = cursor.fetchall()
    #     return [group['group_id'] for group in group_id_dict]        

# TODO Shall we move this to a menu class?
def generic_menu(options: list, got_response: bool, chosen_numbers: str, choose_one_option: bool, outgoing_message: str):
    """A generic function for displaying a menu for the user.
        Returns: If not got_response: the menu options as json to send to user.
                 Otherwise returns the chosen numbers as list in int"""
    logger.start(object={'options': options, 'got_response': got_response, 'chosen_numbers': chosen_numbers, 'choose_one_option': choose_one_option, 'outgoing_message': outgoing_message})
    if not got_response:
        outgoing_message += f"Please choose EXACTLY ONE option between 1-{len(options)}:~" if choose_one_option else f"Please select your desired choices, You may select any of the numbers between 1-{len(options)} with a comma seperator between each choice:~"        
        for i, option in enumerate(options):
            outgoing_message = outgoing_message + f'{i+1}) {option}~'
            outgoing_message_json = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.TEXT_MESSAGE_ACTION.value, message= outgoing_message) 
        if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
            return outgoing_message_json 
    
    if COMMUNICATION_TYPE == communication_type_enum.CONSOLE.value:  
        chosen_numbers = input()
    chosen_numbers = chosen_numbers.split(',')
    generic_menu_result = [int(x)-1 for x in chosen_numbers]
    logger.end(object={'generic_menu_result': generic_menu_result})
    return generic_menu_result
