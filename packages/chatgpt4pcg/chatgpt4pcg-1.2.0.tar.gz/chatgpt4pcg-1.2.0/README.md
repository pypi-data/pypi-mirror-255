# ChatGPT4PCG

ChatGPT4PCG is a python package containing required and utility functions as a part of [ChatGPT4PCG](http://chatgpt4pcg.github.io) competition.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ChatGPT4PCG.

```bash
pip install chatgpt4pcg
```

## Dependency

This file uses the following Python libraries:

- `openai`

## Functions

### `run_evaluation(team_name: str, fn: Type[TrialLoop], num_trials=10, characters: list[str] = None)`

This function runs a trial for each character in the alphabet for a given team. It creates directories for logging and
output, and generates a log file with a timestamp and timezone in the filename. It then runs trials for each character,
skipping any that already exist.

### `run_trial(ctx: TrialContext, fn: Type[TrialLoop])`

This function runs a single trial. It writes the result of the trial to the log file and the final response to a text
file in the output directory.

### `chat_with_chatgpt(ctx: TrialContext, messages: []) -> list[str]`

This function chats with ChatGPT. It sends a list of messages to the ChatGPT model and writes the response and token
counts to the log file. It also checks for time and token limits, raising errors if these are exceeded.

## Usage

To use this file, import it and call the `run_evaluation` function with the team name and trial loop function as
arguments. You can also specify the number of trials to run and the characters to run trials for.

```python
from chatgpt4pcg.competition import run_evaluation, TrialLoop, TrialContext, chat_with_chatgpt


class ZeroShotPrompting(TrialLoop):
    @staticmethod
    def run(ctx: TrialContext, target_character: str) -> str:
        message_history = [{
            "role": "user",
            "content": "Return this is a test message."
        }]

        response = chat_with_chatgpt(ctx, message_history)
        return response[0]


run_evaluation("x_wing", ZeroShotPrompting)
```