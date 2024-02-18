import argparse
import subprocess
import tempfile
import os
import configparser
import platform
import requests


class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

    def get_api_key(self, key_name, section_name):
        api_key = os.getenv(key_name)

        if (
            not self.config.has_section(section_name)
            or "API_KEY" not in self.config[section_name]
        ):
            if not api_key:
                api_key = input(f"Please enter your {section_name} key: ")
            self.config[section_name] = {"API_KEY": api_key}
            with open("config.ini", "w") as configfile:
                self.config.write(configfile)
        else:
            api_key = self.config[section_name]["API_KEY"]
        return api_key

    def set_api_key(self, key_name, section_name, new_api_key):
        self.config[section_name] = {"API_KEY": new_api_key}
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)


class CommandParser:
    def __init__(self, query, history_manager, new_api_key=None):
        self.query = query
        self.history_manager = history_manager
        self.config_manager = ConfigManager()
        if new_api_key:
            self.config_manager.set_api_key("OPENAI_API_KEY", "OPENAI", new_api_key)

    def get_command(self, api_key, messages):
        # url = "http://127.0.0.1:5000/api"
        url = "https://convertly-41cf77f682ee.herokuapp.com/api"

        data = {
            "api_key": api_key,
            "messages": messages,
        }
        request = requests.post(url, json=data)
        try:
            data = request.json()
        except Exception as e:
            print(f"Error: {e}")
            data = {"status": 500, "response": "Error: " + str(e)}
        response = data.get("response", "")
        status_code = int(data.get("status", 500))

        if status_code != 200:
            raise Exception(f"Error: {status_code} - {response}")

        return response, status_code

    def parse(self):
        api_key = self.config_manager.get_api_key("OPENAI_API_KEY", "OPENAI")
        history = self.history_manager.get_recent_history(5)
        history_prompt = self._generate_history_prompt(history)
        system_prompt = self._generate_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Answer this as briefly as possible and using the latest context: "
                + self.query,
            },
        ]

        if history:
            messages.insert(
                1,
                {
                    "role": "user",
                    "content": history_prompt,
                },
            )
        print(f"\033[1;33;40mRunning...\033[0m", end="\r")
        response, status_code = self.get_command(api_key, messages)
        if status_code != 200:
            error_message = response.get("error", "Unknown error")
            print(
                f"\033[1;31;40mError: Unable to get command, status code: {status_code}, error: {error_message}\033[0m"
            )

        return response

    def _generate_history_prompt(self, history):
        return (
            "For context, here's the history of the last five questions, answers and the status of their execution, if a query has failed, try something different. \n\n"
            + "\n".join(history)
        )

    def _generate_system_prompt(self):
        latest_history_status = self.history_manager.get_recent_history(1)
        if latest_history_status:
            status_part = latest_history_status[0].split("Status: ")[-1]
        else:
            status_part = "No error"

        return f"""You are a command line utility for the {platform.system()} OS that quickly and succinctly converts images, videos, files and manipulates them. When a user asks a question, you MUST respond with ONLY the most relevant command that will be executed within the command line, along with the required packages that need to be installed. If absolutely necessary, you may execute Python code to do a conversion. Your responses should be clear and console-friendly. If there are file or folder paths, then they MUST be quoted in your response.

        If there was an error in the previous command, YOU MUST echo the problem and why the error: {status_part} occurred FIRST in the format echo "Error: (error)", and consider it when generating the next command, only if it's relevant. If there is no error, IGNORE this.

        Things to NOT do:

        - Do not include codeblocks or any ``` in your response, this is not a bash script, it is a command line utility. Commands should be directly executable in the command line.
        - Do not assume a user has pre-requisite packages installed, always install it anyways. 

Here's how your responses should look:

EXAMPLE 1

<Users Question>
conv file.webp to png
<Your Answer>
dwebp "file.webp" -o "file.png"
<User Question>
rotate that image by 90 degrees
<Your Answer>
brew install imagemagick
convert "file.png" -rotate 90 "rotated_file.png"

EXAMPLE 2

<Users Question>
rotate an image by 90 degrees
<Your Answer>
brew install imagemagick
convert "file.png" -rotate 90 "rotated_file.png"

EXAMPLE 3

<Users Question>
convert a video in /path/to/video.mp4 to a gif
<Your Answer>
ffmpeg -i "/path/to/video.mp4" "/path/to/video.gif"

EXAMPLE 4

<Users Question>
avif to png for file.avif
<Your Answer>
magick "file.avif" "file.png"

EXAMPLE 5

<Users Question>
convert my pdf to docx, the file is /Users/path/file.pdf
<Your Answer>
pip install pdf2docx
python3 -c "from pdf2docx import parse; pdf_file = r'/Users/path/file.pdf'; docx_file = r'/Users/path/file.docx'; parse(pdf_file, docx_file, start=0, end=None)"

EXAMPLE 6

<Users Question>
copy all of Documents/Screenshots to a folder called Screenshots2 in the same directory
<Your Answer>
cp -a "Documents/Screenshots Documents/test"


"""


class CommandExecutor:
    @staticmethod
    def execute(command):
        status = ""
        if command.startswith('echo "Error:'):
            print(
                f"\033[1;31;40mThe previous command failed: {command.split('Error: ')[-1]}\033[0m"
            )
            status = f"An error occurred while executing the command: {command.split('Error: ')[-1]}"
        else:
            try:
                subprocess.run(command, check=True, shell=True)
                print(f"\033[1;32;40mExecuted: {command}\033[0m")
                status = "Success"
            except subprocess.CalledProcessError as e:
                print(
                    f"\033[1;31;40mAn error occurred while executing the command: {e}\033[0m"
                )
                status = f"An error occurred while executing the command: {e}"
        return status


class HistoryManager:
    def __init__(self, history_file_path):
        self.history_file_path = history_file_path

    def clear_history(self):
        with open(self.history_file_path, "w") as f:
            f.write("")

    def get_recent_history(self, n):
        if not os.path.exists(self.history_file_path):
            open(self.history_file_path, "w").close()

        with open(self.history_file_path, "r") as f:
            blocks = f.read().split("\n\n")[:-1]

        return blocks[-n:]

    def modify_history(self, query, response, status):
        with open(self.history_file_path, "a") as f:
            f.write(f"Question: {query}\nAnswer: {response}\nStatus: {status}\n\n")


def main():
    temp_dir = tempfile.gettempdir()
    history_file_path = os.path.join(temp_dir, "history.txt")
    history_manager = HistoryManager(history_file_path)

    parser = argparse.ArgumentParser(
        description="Conv is a command line tool to easily execute file conversions, image manipulations, and file operations quickly."
    )
    parser.add_argument("query", type=str, nargs="*", help="The query to be processed.")
    parser.add_argument("--clear", action="store_true", help="Clear the history.")
    parser.add_argument(
        "--hist", action="store_true", help="View the recent history of queries."
    )
    parser.add_argument("--key", type=str, help="Enter a new OpenAI API key.")

    args = parser.parse_args()

    if args.clear:
        history_manager.clear_history()
        print("\033[1;32;40mHistory cleared.\033[0m")
        return

    if args.hist:
        history = history_manager.get_recent_history(5)
        print("\033[1;32;40mRecent History:\033[0m")
        for item in history:
            print(item + "\n")
        return

    if args.key:
        new_api_key = args.key
        command_parser = CommandParser("", history_manager, new_api_key)
        print(f"\033[1;32;40mAPI Key updated successfully to: {new_api_key}\033[0m")
        return

    if not args.query:
        print(
            "\033[1;31;40mUsage: python script.py 'conv <query>' or '--clear' to clear history or '--hist' to view history\033[0m"
        )
        return

    query = " ".join(args.query)
    print("\033[1;34;40mQuerying: " + query + "\033[0m")

    command_parser = CommandParser(query, history_manager)
    system_command = command_parser.parse()

    if system_command:
        print("\033[1;36;40mRunning command: " + system_command + "\033[0m")
        status = CommandExecutor.execute(system_command)
        history_manager.modify_history(query, system_command, status)
    else:
        print(
            "Could not parse or execute the command. Please ensure the command is valid."
        )


if __name__ == "__main__":
    main()
