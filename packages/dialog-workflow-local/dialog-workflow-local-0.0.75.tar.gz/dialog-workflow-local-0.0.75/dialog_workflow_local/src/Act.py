# TODO Rename the file From Act.py to action.py

from circles_local_database_python.connector import Connector
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from .utils import *
from .TablesAsObjects import DialogWorkflowRecord, ProfileContext
import time
# import msvcrt
# import requests
# from AgeDetection import DetectAge
from variable_local.variable import VariablesLocal
from variable_local.template import ReplaceFieldsWithValues
from dotenv import load_dotenv
load_dotenv()


object_to_insert = {
    'component_id': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'idan.a@circ.zone and guy.n@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)


class action(object):
    def __init__(self, incoming_message: str, profile_id: int, language: str, profile_curr_state: int, variables: VariablesLocal):
        self.incoming_message = incoming_message
        self.profile_id = profile_id
        self.language = language
        self.variables = variables
        self.profile_curr_state = profile_curr_state
        self.accumulated_message = ""
        self.profile = ProfileContext(self.profile_id)
        self.variable = VariablesLocal()

    def act(self, dialog_workflow_record: DialogWorkflowRecord, got_response: bool):
        """This function applies the action of the relevant record with the profile's current state id.
        Params:
            1. dialog_workflow_record: The current record from the dialog workflow state table that is applied.
            2. got_response a bool indicator telling us if the user had sent back a response to the last outgoing message
               that we sent him from the same action or not. This will help understand if the action should 
               apply the begging part of the action (i.e to send a request to the user),
               or the second part of the action (i.e got a response and now deal with it)

        Returns:
            1. True if the action resulted in a change of state, False otherwise
            2. The outgoing message json object that the user will recieve if the action needed to send a message to the user,
                or None if the action doesn't need to send a message to the user .

        Note : some of the actions are divided into 2 parts: 
            1. The action before sendig the outgoing message to the user (i.e got_response = false)
            2. The action after sending the outgoing message, and getting an incoming_message reply back (i.e got_respone = true). """
        logger.start(pbject={'dialog_workflow_record': str(
            dialog_workflow_record), 'got_response': got_response})
        self.record = dialog_workflow_record
        self.got_response = got_response
        action = self.record.workflow_action_id
        if action == action_enum.LABEL_ACTION.value:
            selected_act = False, None
        elif action == action_enum.TEXT_MESSAGE_ACTION.value:
            selected_act = self.text_message_action()
        elif action == action_enum.QUESTION_ACTION.value:
            selected_act = self.question_action()
        elif action == action_enum.JUMP_ACTION.value:
            selected_act = self.jump_action()
        elif action == action_enum.SEND_REST_API_ACTION:
            selected_act = self.send_rest_api_action()
        elif action == action_enum.ASSIGN_VARIABLE_ACTION.value:
            selected_act = self.assign_variable_action()
        elif action == action_enum.INCREMENT_VARIABLE_ACTION.value:
            selected_act = self.increment_variable_action()
        elif action == action_enum.DECREMENT_VARIABLE_ACTION.value:
            selected_act = self.decrement_variable_action()
        elif action == action_enum.MENU_ACTION.value:
            selected_act = self.menu_action()
        elif action == action_enum.AGE_DETECTION.value:
            selected_act = self.age_detection()
        elif action == action_enum.MULTI_CHOICE_POLL.value:
            selected_act = self.multi_choice_poll()
        elif action == action_enum.PRESENT_CHILD_GROUPS_NAMES_BY_ID.value:
            selected_act = self.present_child_groups_names_by_id()
        elif action == action_enum.PRESENT_GROUPS_WITH_CERTAIN_TEXT.value:
            selected_act = self.present_groups_with_certain_text()
        elif action == action_enum.INSERT_MISSING_DATA.value:
            selected_act = self.insert_missing_data()
        elif action == action_enum.PRESENT_AND_CHOOSE_SCRIPT.value:
            selected_act = self.present_and_choose_script()

        # TODO Please add support to question_schema i.e. ASK_QUESTION_ID
        
        logger.end(object={'selected_act': str(selected_act)})
        return selected_act

    def text_message_action(self):
        """Prints the paramter1 message after formatting: 
        "Hello {First Name}, how are you {feeling|doing}?" --> "Hello Tal, how are you doing? """
        logger.start()
        message = self.record.parameter1
        replace_fields_with_values_class = ReplaceFieldsWithValues(
            message, self.language, self.variable)
        formatted_message = replace_fields_with_values_class.get_variable_values_and_chosen_option(self.profile_id)
        self.accumulated_message = self.accumulated_message + formatted_message + '~'
        text_message_act = False, None
        logger.end(object={'text_message_act': str(text_message_act)})
        return text_message_act

    # TODO Rename all those functions to question_workflow_action() - Add the word 'workflow'
    # TODO Use question.question_table
    # TODO send to the logger the question_id
    # TODO confirm we didn't ask this question in the period mention in question.question_table
    def question_action(self):
        """Asks a question and waits for an answer from user on STDIN. If the user responded in a certain amount of time,
        then moves to next state, otherwise moves to a different state.
        Note: this function waits for input for a certain amount of time only if using console application.
              If using websocket we send a json message to the user and exit the code normally"""
        logger.start()
        if not self.got_response:
            self.accumulated_message += self.record.parameter1
            outgoing_message = process_message(
                communication_type=COMMUNICATION_TYPE, action_type=action_enum.TEXT_MESSAGE_ACTION.value, message=self.accumulated_message)
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                question_act = False, outgoing_message
                logger.end(object={'question_act': question_act})
                return question_act
            else:
                self.accumulated_message = ""

            waiting_time = self.record.no_feedback_milliseconds
            start_time = time.monotonic()
            input_str = None
            # while True:
            # if msvcrt.kbhit():
            # input_str = input().strip()
            # insert_profile_variable_value(self.profile_id, self.record.variable1_id, input_str, self.profile_curr_state)
            # break
            # elif time.monotonic() - start_time > waiting_time:
            # break
            input_str = input().strip()
            if input_str == None:
                self.profile_curr_state = self.record.next_state_id_if_there_is_no_feedback
                question_act = True, None
                logger.end(object={'question_act': question_act})
                return question_act
            else:
                question_act = False, None
                logger.end(object={'question_act': question_act})
                return question_act
        else:
            self.variable.set_variable_value_by_variable_id(
                self.record.variable1_id, self.incoming_message, self.profile_id,self.profile_curr_state)
            question_act = False, None
            logger.end(object={'question_act': question_act})
            return question_act

    def jump_action(self):
        """Jumps from one state to another."""
        logger.start()
        self.profile_curr_state = int(self.record.parameter1)
        update_profile_curr_state_in_DB(
            self.profile_id, int(self.record.parameter1))
        jump_act = True, None
        logger.end(object={'jump_Act': jump_act})
        return jump_act

    def send_rest_api_action(self):
        """Sends a REST API post"""
        # TODO: implament this function
        logger.start()
        # api_url = self.record.parameter1
        # payload_variable_id = self.record.variable1_id
        # json_payload_string = get_variable_value_by_id(self.language, payload_variable_id)
        # json_payload = json.loads(json_payload_string)
        # incoming_message = requests.post(api_url, json=json_payload)
        # incoming_message_string = json.dumps(incoming_message.json())
        # insert_profile_variable_value(self.profile_id, self.variable.get_variable_id("Post Result"), incoming_message_string, self.profile_curr_state)
        API_post = False, None
        logger.end(object={'API_post': API_post})
        return API_post

    def assign_variable_action(self):
        """Assigns a value to a given variable"""
        logger.start()
        parameter_value = self.record.parameter1
        variable_id = self.record.variable1_id
        self.variable.set_variable_value_by_variable_id(
             variable_id, parameter_value, self.profile_id,self.profile_curr_state)
        assinged_variable_action = self.got_response, None
        logger.end(
            object={'assinged_variable_action': assinged_variable_action})
        return assinged_variable_action

    def increment_variable_action(self):
        """Increments a value to a given variable by the amount of the given paramter1"""
        logger.start()
        number_to_add = int(self.record.parameter1)
        variable_id = self.record.variable1_id
        current_variable_value = get_variable_value_by_id(
            self.language, variable_id)
        self.variables.set_variable_value_by_variable_id(variable_id, str(
            int(current_variable_value) + number_to_add), self.profile_id,self.profile_curr_state)
        incremented_variable_action = self.got_response, None
        logger.end(
            object={'incremented_variable_action': incremented_variable_action})
        return incremented_variable_action

    def decrement_variable_action(self):
        """Increments a value to a given variable by the amount of the given paramter1"""
        logger.start()
        number_to_add = int(self.record.parameter1)
        variable_id = self.record.variable1_id
        current_variable_value = get_variable_value_by_id(
            self.language, variable_id)
        self.variable.set_variable_value_by_variable_id(variable_id, str(
            current_variable_value - number_to_add), self.profile_id)
        decremented_variable_action = False, None
        logger.end(
            object={'decremented_variable_action': decremented_variable_action})
        return decremented_variable_action

    """I have put this in remark right now because this action need to work with multiple profiles,
    But right now this change makes it difficult to do that. Will work on it later."""
    # def condition_action(self):
    #     cursor.execute("""SELECT * FROM dialog_workflow_state  WHERE parent_state_id = %s""", [record.curr_state_id])
    #     child_nodes = cursor.fetchall()
    #     """I am assuming that in these child records the varaible id must be the same id of the parent variable id,
    #     and the parameter1 value is the value of a profile_id from which i shall get the age"""
    #     for child in child_nodes:
    #         profile_id = child["parameter1"]
    #         child_age = (profiles_dict_class.get(profile_id)).get_variable_value_by_id(record.variable1_id)
    #         if child_age < record.result_figure_max and child_age > record.result_figure_min:
    #             profile.curr_state_id = child["next_state_id"]
    #             return True, None
    #     return False, None

    def menu_action(self):
        """This action show a menu of options to the user for which he should choose one from it.
            the options we show are the records such that their parent id is the id of the current record.
            First part of the action is sending the user the options.
            Second part of the action is getting the chosen option (i.e incoming_message) and dealing with it."""
        logger.start()
        fields_to_select = ["parameter1", "next_state_id"]
        table_name = "dialog_workflow_state_view"
        values_from_where_to_select = [self.record.curr_state_id]
        variables_from_where_to_select = ["parent_state_id"]
        child_nodes = get_child_nodes_of_current_state(
            fields_to_select, table_name, values_from_where_to_select, variables_from_where_to_select)
        self.record.parameter1 = "" if self.record.parameter1 == None else self.record.parameter1
        # Adds the question and instructions to the accumulated_message to be sent to user.
        if not self.got_response:
            self.accumulated_message = self.accumulated_message + self.record.parameter1 + \
                "~" + \
                f"Please choose EXACTLY ONE option between 1-{len(child_nodes)}:~"
        is_state_changed, next_state_id, outgoing_message = generic_user_choice_action(
            self.record, self.accumulated_message, child_nodes, choose_exactly_one_option=True, got_response=self.got_response, chosen_numbers=self.incoming_message, profile=self.profile)
        if outgoing_message != None:  # returns the outgoing message to send to the user.
            menu_action_selected = False, outgoing_message
            logger.end(object={'menu_action_selected': menu_action_selected})
            return menu_action_selected
        self.profile_curr_state = next_state_id
        self.accumulated_message = ""
        menu_action_selected = is_state_changed, None
        logger.end(object={'menu_action_selected': menu_action_selected})
        return menu_action_selected

    def age_detection(self):
        # TODO: implament this function
        logger.start()
        #     """Action that recieves a path to a picture (for now the picture has to be stored in the folder)
        #         and returns the approximate age of the person in the picture.
        #         Stores the picture in database storage."""
        #     if not self.got_response:
        #         self.accumulated_message += "Please insert a path to the picture~"
        #         outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.AGE_DETECTION.value, message= self.accumulated_message)
        #         if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
        #             return False, outgoing_message
        #         else:
        #             self.accumulated_message = ""
        #             self.incoming_message = input()
        #     age_range = DetectAge.detect(self.incoming_message)
        #     self.accumulated_message += f'The approximate age of the picture you have sent is: {age_range}~'
        #     insert_profile_variable_value(self.profile_id, self.record.variable1_id, age_range, self.profile_curr_state)
        #     store_age_detection_picture(age_range, self.profile_curr_state)
        age_detected = False, None
        logger.end(object={'age_detected': age_detected})
        return age_detected

    def multi_choice_poll(self):
        """ Similar to Menu Action. If the user chose a single option we jump to next_state_id of the chosen option. 
            Otherwise we save the answers and jump to the next_state_id of the parent."""
        logger.start()
        fields_to_select = ["parameter1", "next_state_id"]
        table_name = "dialog_workflow_state_view"
        values_from_where_to_select = [self.record.curr_state_id]
        variables_from_where_to_select = ["parent_state_id"]
        child_nodes = get_child_nodes_of_current_state(
            fields_to_select, table_name, values_from_where_to_select, variables_from_where_to_select)
        self.record.parameter1 = "" if self.record.parameter1 == None else self.record.parameter1
        # Adds the question and instructions to the accumulated_message to be sent to user.
        if not self.got_response:
            self.accumulated_message = self.accumulated_message + self.record.parameter1 + "~" + \
                f"Please select your desired choices, You may select any of the numbers between 1-{len(child_nodes)} with a comma seperator between each choice:~"
        is_state_changed, next_state_id, outgoing_message = generic_user_choice_action(
            self.record, self.accumulated_message, child_nodes, choose_exactly_one_option=False, got_response=self.got_response, chosen_numbers=self.incoming_message, profile=self.profile)
        if outgoing_message != None:  # returns the outgoing message to send to the user.
            choises = False, outgoing_message
            logger.end(object={'choises': choises})
            return choises
        self.profile_curr_state = next_state_id
        choises = is_state_changed, None
        logger.end(object={'choises': choises})
        return choises

    def present_child_groups_names_by_id(self):
        """Presents all of the groups that their parent id is the given one. Does so recursively"""
        logger.start()
        child_groups = group(int(self.record.parameter1))
        self.accumulated_message="Here are the interests:~"
        groups=child_groups.get_child_group_names()
        for i in range(len(groups)):
            self.accumulated_message+=groups[i]+"~"+str(i)+"\n"
        child_groups_names_by_id = True, self.accumulated_message
        logger.end(
            object={'child_groups_names_by_id': child_groups_names_by_id})
        return child_groups_names_by_id

    def present_groups_with_certain_text(self):
        """Present all groups that their text contains the given text. (e.g given text: 'sport' -> 'sports', 'walking sport..).
            Saves the chosen options in profile context."""
        logger.start()
        groups = get_groups_with_text(self.record.parameter1)
        if not self.got_response:
            self.accumulated_message += "Please choose your desired interests. You may select more than one choice with a comma seperator.~"
            for i, child in enumerate(groups):
                self.accumulated_message = self.accumulated_message + \
                    f'{i+1}) {child["title"]}~'

            outgoing_message = process_message(
                communication_type=COMMUNICATION_TYPE, action_type=action_enum.PRESENT_GROUPS_WITH_CERTAIN_TEXT.value, message=self.accumulated_message)
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                groups_with_certain_text = False, outgoing_message
                logger.end(
                    object={'groups_with_certain_text': groups_with_certain_text})
                return groups_with_certain_text
            else:
                self.accumulated_message = ""
                chosen_numbers = input()
        else:
            chosen_numbers = self.incoming_message.split(',')
            chosen_numbers_list = [int(x) for x in chosen_numbers]
            self.profile.groups.extend(
                [groups[chosen_number] for chosen_number in chosen_numbers_list])
            groups_with_certain_text = False, None
            logger.end(
                object={'groups_with_certain_text': groups_with_certain_text})
        return groups_with_certain_text

    def insert_missing_data(self):
        """Asks the user for missing data (e.g please insert your first name), and after getting a response,
            inserts the given value to the relevant table to fill the missing data.
            The record, field name, table and scehma in which the data should be inserted into are given in parameter1 as:
            <schema>,<table>,<field name>,<record id> (e.g. user,user_table,first_name,1)"""
        logger.start()
        parameter1_list = self.record.parameter1.split(",")
        schema = parameter1_list[0]
        table = parameter1_list[1]
        field_name = parameter1_list[2]
        record_id = parameter1_list[3]
        if not self.got_response:
            self.accumulated_message += f"Please insert your {field_name}~"
            outgoing_message = process_message(
                communication_type=COMMUNICATION_TYPE, action_type=action_enum.TEXT_MESSAGE_ACTION.value, message=self.accumulated_message)
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                missing_data = False, outgoing_message
                logger.end(object={'missing_data': missing_data})
                return missing_data
            else:
                self.accumulated_message = ""
                self.incoming_message = input()
        else:
            try:
                connection = Connector.connect(schema)
                cursor = connection.cursor(dictionary=True, buffered=True)
                # cursor.execute(f"""USE {schema}""")
                cursor.execute(
                    f"""UPDATE {table} SET {field_name} = '{self.incoming_message}' WHERE (id= {record_id})""")
                # cursor.execute("""USE dialog_workflow""")
                connection.commit()
            except:  # If one of the arguments isn't valid
                logger.error("Invalid parameter1")
        missing_data = False, None
        logger.end(object={'missing_data': missing_data})
        return missing_data

    def present_and_choose_script(self):
        """Action for asking the user which workflo script he would like to run next and change the next state id according to his choice."""
        logger.start()
        connection = Connector.connect('dialog_workflow')
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute(
            """SELECT d.start_state_id, dml.name FROM dialog_workflow_script_view AS d JOIN dialog_workflow_script_ml_view AS dml on dml.dialog_workflow_script_id=d.dialog_workflow_script_id WHERE dml.lang_code = %s""", [self.language])
        available_scripts_dict = cursor.fetchall()
        available_scripts = [script["name"]
                             for script in available_scripts_dict]
        outgoing_message = "Please choose your desired script out of the following:~"
        menu = generic_menu(available_scripts, self.got_response, self.incoming_message,
                            choose_one_option=True, outgoing_message=outgoing_message)
        if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value and not self.got_response:
            present_and_choosed_script = False, menu
            logger.end(
                object={'present_and_choosed_script': present_and_choosed_script})
            return present_and_choosed_script
        else:
            self.profile_curr_state = available_scripts_dict[menu[0] -
                                                             1]["start_state_id"]
            present_and_choosed_script = True, None
            logger.end(
                object={'present_and_choosed_script': present_and_choosed_script})
            return present_and_choosed_script


def generic_user_choice_action(record: DialogWorkflowRecord, accumulated_message: str, child_nodes: list, choose_exactly_one_option: bool, got_response: bool, chosen_numbers: str, profile: ProfileContext):
    """Sends the user a question with a couple of answers. This function is generic and can let the user choose either
        exactly one option, or more than one. Each case is handeled differently.
        Returns: 
            1. True if the users' next state should be changed to a child next state, False if there's no need to change it's state
            2. The next state id that the profile should be in, or None if the action didn't result in a change of state.
            3. The outging message to be sent to the user, or None if the message had already been sent."""
    # This is the first part of the action: sending the request to the user and waiting for an answer.
    logger.start(object={'record': str(record), 'accumulated_message': str(accumulated_message), 'child_nodes': str(child_nodes), 'choose_exactly_one_option': str(
        choose_exactly_one_option), 'got_response': str(got_response), 'chosen_numbers': str(chosen_numbers), 'profile': str(profile)})
    if not got_response:
        for i, child in enumerate(child_nodes):
            accumulated_message = accumulated_message + \
                f'{i+1}) {child["parameter1"]}~'
        outgoing_message = process_message(communication_type=COMMUNICATION_TYPE,
                                           action_type=action_enum.TEXT_MESSAGE_ACTION.value, message=accumulated_message)
        if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
            generic_user_choice_act = False, record.next_state_id, outgoing_message
            logger.end(
                object={'generic_user_choice_act': generic_user_choice_act})
            return generic_user_choice_act
        else:
            chosen_numbers = input()

    # The user has to pick exactly one option
    if choose_exactly_one_option:
        profile_next_state = (
            child_nodes[int(chosen_numbers)-1])["next_state_id"]
        generic_user_choice_act = True, profile_next_state, None
        logger.end(object={'generic_user_choice_act': generic_user_choice_act})
        return generic_user_choice_act
    # In this case the user can choose more than one option:
    else:
        chosen_numbers = chosen_numbers.split(',')
        chosen_numbers_list = [int(x) for x in chosen_numbers]
        # If he still chooses exactly one we jump to the next_state_id of the option.
        if len(chosen_numbers_list) == 1:
            profile_next_state = (
                child_nodes[chosen_numbers_list[0]-1])["next_state_id"]
            generic_user_choice_act = True, profile_next_state, None
            logger.end(
                object={'generic_user_choice_act': generic_user_choice_act})
            return generic_user_choice_act
        # If he chooses more than one, we store the chosen options and jump to the next_state_id of the parent.
        else:
            list_of_options = [option["parameter1"] for option in child_nodes]
            profile.save_chosen_options(
                record.parameter1, record.variable1_id, chosen_numbers_list, list_of_options)
            generic_user_choice_act = False, record.next_state_id, None
            logger.end(
                object={'generic_user_choice_act': generic_user_choice_act})
            return generic_user_choice_act


def get_groups_with_text(text: str) -> list:
    logger.start(object={'text': text})
    connection = Connector.connect('group')
    cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE `group`""")
    cursor.execute(
        f"""SELECT title, group_id FROM group_ml_table WHERE title LIKE '%{text}%'""")
    groups_with_text = cursor.fetchall()
    logger.end(object={'groups_with_text': groups_with_text})
    return groups_with_text
