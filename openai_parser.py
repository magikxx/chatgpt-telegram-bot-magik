#!/usr/bin/python3
# -*- coding: utf-8 -*-

import openai, json, os
import datetime, pickle

class OpenAIParser:

    config_dict = {}
    info_dict = {}


    def __init__(self):
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
        # init openai
        # openai.organization = self.config_dict["ORGANIZATION"] if "ORGANIZATION" in self.config_dict else "Personal"
        openai.api_key = self.config_dict["openai_api_key"]
        try:
            with open("context.pkl", "rb") as f:
                self.context_dict = pickle.load(f)
        except FileNotFoundError:            
            print("Wystąpił błąd:", e)  # dodano blok except z wypisaniem błędu
            self.context_dict = {"system": [], "user": []}  # zmieniono format kontekstu rozmowy na słownik

    def _get_single_response(self, message, context):
        response = openai.Completion.create(
            engine=self.config_dict["openai_engine"],
            prompt=message,
            max_tokens=self.config_dict["openai_max_tokens"],
            temperature=self.config_dict["openai_temperature"],
            top_p=self.config_dict["openai_top_p"],
            frequency_penalty=self.config_dict["openai_frequency_penalty"],
            presence_penalty=self.config_dict["openai_presence_penalty"],
            stop=self.config_dict["openai_stop"]
        )
        return response.choices[0].text.strip()
    
    def get_response(self, userid, user_message, conversation_context=None):  # dodano argument conversation_context
        if conversation_context is None:
            conversation_context = self.context_dict
        conversation_context["user"].append({"role": "user", "content": user_message})
        conversation_context["user"].append({})
        conversation_context["system"].append({"role": "system", "content": "Mówisz zawsze w języku polskim. I jesteś zawsze kobietą."})
        conversation_context["system"].append({})
        try:
            response = self._get_single_response(message="\n".join([x["content"] for x in conversation_context["system"] + conversation_context["user"]] + [""]), context=conversation_context)  # zmieniono sposób przekazywania kontekstu
            with open("responses.pkl", "ab") as f:
                pickle.dump({"role": "system", "content": response}, f)
                pickle.dump({}, f)
            conversation_context["system"].append({"role": "system", "content": response})
            conversation_context["system"].append({})
            with open("context.pkl", "wb") as f:
                pickle.dump(conversation_context, f)  # zmieniono sposób zapisywania kontekstu
            return response
        except Exception as e:
            print("Wystąpił błąd:", e)
            return "Przepraszam, nie czuje się za dobrze. Proszę spróbuj później."

    def speech_to_text(self, userid, audio_file):
        # transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

    def image_generation(self, userid, prompt):
        response = openai.Image.create(prompt = prompt, n=1, size = "1024x1024", user = userid)
        image_url = response["data"][0]["url"]
        # self.update_image_generation_usage(userid)
        # for debug use
        # image_url = "https://catdoctorofmonroe.com/wp-content/uploads/2020/09/iconfinder_cat_tied_275717.png"
        return image_url
    
    def update_image_generation_usage(self, userid):
        # get time
        usage_file_name = datetime.datetime.now().strftime("%Y%m") + "_image_generation_usage.json"
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        # create usage folder
        if not os.path.exists("./usage"):
            os.makedirs("./usage")
        # load usage or create new
        if os.path.exists("./usage/" + usage_file_name):
            with open("./usage/" + usage_file_name) as f:
                self.usage_dict = json.load(f)
        else:
            self.usage_dict = {}
        # update usage
        if now not in self.usage_dict:
            self.usage_dict[now] = {}
        if userid not in self.usage_dict[now]:
            self.usage_dict[now][userid] = {"requests": 0}
        self.usage_dict[now][userid]["requests"] += 1
        # save usage
        with open("./usage/" + usage_file_name, "w") as f:
            json.dump(self.usage_dict, f)

    
    def update_usage(self, total_tokens, userid):
        # get time
        usage_file_name = datetime.datetime.now().strftime("%Y%m") + "_usage.json"
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        # create usage folder
        if not os.path.exists("./usage"):
            os.makedirs("./usage")
        # load usage or create new
        if os.path.exists("./usage/" + usage_file_name):
            with open("./usage/" + usage_file_name) as f:
                self.usage_dict = json.load(f)
        else:
            self.usage_dict = {}
        # update usage
        if now not in self.usage_dict:
            self.usage_dict[now] = {}
        if userid not in self.usage_dict[now]:
            self.usage_dict[now][userid] = {"tokens": 0, "requests": 0}
        self.usage_dict[now][userid]["tokens"] += total_tokens
        self.usage_dict[now][userid]["requests"] += 1
        # save usage
        with open("./usage/" + usage_file_name, "w") as f:
            json.dump(self.usage_dict, f)

if __name__ == "__main__":
    openai_parser = OpenAIParser()
    # print(openai_parser._get_single_response("Tell me a joke."))
    print(openai_parser.get_response("123", [{"role": "user", "content": "Tell me a joke."}]))