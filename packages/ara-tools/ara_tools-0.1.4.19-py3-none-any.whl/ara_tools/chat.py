import os
from ara_tools.prompt_handler import send_prompt

class Chat:
    def __init__(self, chat_name):
        self.chat_name = self.setup_chat(chat_name)
        self.chat_history = []

    def setup_chat(self, chat_name):
        if chat_name.endswith('.md'):
            return self.handle_existing_chat(chat_name)
        if chat_name == "chat" and os.path.exists("chat.md"):
            return self.handle_existing_chat("chat.md")
        return self.initialize_new_chat(chat_name)

    def handle_existing_chat(self, chat_name):
        if not os.path.exists(chat_name):
            print("Couldn't continue existing chat. Provided chat file doesn't exist in this directory.")
            sys.exit(1)
        self.chat_history = self.load_chat_history(chat_name)
        print(f"Reloaded {chat_name} content:")
        return chat_name

    def initialize_new_chat(self, chat_name):
        if chat_name != "chat":
            chat_name = f"{chat_name}-chat"
        chat_name = f"{chat_name}.md"
        open(chat_name, 'a', encoding='utf-8').close()
        return chat_name

    def start(self):
        print("Start chatting (type 'GO' to send, 'END' to finish):")
        while True: 
            user_input = self.get_user_input()
            if user_input == "END":
                print("Chat ended")
                return
            self.handle_user_input(user_input)

    def get_user_input(self):
        user_input = ""
        while True:
            line = input()
            if line in ["END", "GO", "CONTINUE"]:
                return f"{user_input.strip()}" if line == "GO" else line
            user_input += f"{line} "

    def handle_user_input(self, user_input):
        if user_input == "CONTINUE":
            # Delete last response if it exists and resend chat history up to the last prompt
            self.resend_message()
        else:
            # Don't save message if command was continue
            self.save_message("You", user_input)
        prompt_to_send = "\n".join([message for message in self.chat_history])
        response = send_prompt(prompt_to_send)
        print(f"GPT-4: {response}")
        self.save_message("ChatGPT", response)

    def resend_message(self):
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            index_to_remove = self.find_last_reply_index(lines)
            if index_to_remove is not None:
                with open(self.chat_name, 'w', encoding='utf-8') as file:
                    file.writelines(lines[:index_to_remove])
            self.chat_history = self.load_chat_history(self.chat_name)

    def find_last_reply_index(self, lines):
        index_to_remove = None
        for i, line in enumerate(reversed(lines)):
            if "#### You" in line:
                # Last reply was already deleted
                break
            if "#### ChatGPT" in line:
                # Delete last reply
                index_to_remove = len(lines) - i - 1
                break
        return index_to_remove

    def save_message(self, role, message):
        line_to_write = f"#### {role}:\n{message}\n\n"
        with open(self.chat_name, 'a', encoding='utf-8') as file:
            file.write(line_to_write)
        self.chat_history.append(line_to_write)

    def load_chat_history(self, chat_file):
        chat_history = []
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as file:
                chat_history = file.readlines()
        return chat_history