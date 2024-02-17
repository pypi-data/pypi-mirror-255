from pathlib import Path
from time import perf_counter


class TrialContext:
    """
    Trial context for a given trial.
    """

    def __init__(self, team_name, character, trial_number, log_file_path):
        self.__team_name = team_name
        self.__character = character
        self.__trial_number = trial_number
        self.__log_file_path = log_file_path
        self.__start_time = perf_counter()
        self.__prompt_token_count = 0
        self.__output_token_count = 0

    def get_team_name(self):
        return self.__team_name

    def get_character(self):
        return self.__character

    def get_trial_number(self):
        return self.__trial_number

    def get_start_time(self):
        return self.__start_time

    def get_log_file_path(self):
        return self.__log_file_path

    def get_output_folder_path(self):
        return Path(self.__team_name) / "raw" / Path(self.__character)

    def get_output_file_path(self):
        return self.get_output_folder_path() / f"{self.get_team_name()}_{self.get_character()}_{self.get_trial_number()}.txt"

    def add_prompt_token_count(self, count: int):
        self.__prompt_token_count += count

    def add_output_token_count(self, count: int):
        self.__output_token_count += count

    def get_total_token_count(self):
        return self.__prompt_token_count + self.__output_token_count

    def __str__(self):
        return (f"TrialContext(team_name={self.__team_name}, "
                f"character={self.__character}, "
                f"trial_number={self.__trial_number}, "
                f"log_file_path={self.__log_file_path}, "
                f"start_time={self.__start_time}, "
                f"prompt_token_count={self.__prompt_token_count}, "
                f"output_token_count={self.__output_token_count})")
