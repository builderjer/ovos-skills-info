import json
import re
import os
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.skills import skill_api_method
from mycroft.util.log import LOG
from pathlib import Path

class OVOSSkillsInfo(MycroftSkill):

    def __init__(self):
        super(OVOSSkillsInfo, self).__init__(name="OVOSSkillsInfo")
        self.skill_info_model = []
        self.skill_model_blacklist = ["mycroft-stop.mycroftai", "mycroft-stock.mycroftai", "mycroft-configuration.mycroftai"]

    def initialize(self):
        self.build_skills_model()

    def build_skills_model(self):
        self.skill_info_model.clear()
        osDirPath = os.path.dirname(os.path.realpath(__file__))
        dirPath = Path(osDirPath).parent
        subfolders = [ f.path for f in os.scandir(dirPath) if f.is_dir() ]
        fileName = "README.md"

        for x in range(len(subfolders)):
            subfolder_name = subfolders[x].rsplit('/', 1)[-1]
            if subfolder_name not in self.skill_model_blacklist:
                target = os.path.join(subfolders[x], fileName)
                try:
                    fileParse = open(target, 'r').read()
                    matchedRegex = self._getDataFromRegex(fileName, fileParse, r"<img[^>]*src='([^']*)'.*\/>\s(.*)")
                    matchedExamples = self._getDataFromRegex(fileName, fileParse, r'## Examples.*\n.*\"(.*)\"\n\*\s\"(.*)\"')
                    matchedCategory = self._getDataFromRegex(fileName, fileParse, r'## Category.*\n\*\*(.*)\*\*')
                    if matchedRegex is not None and matchedExamples is not None and matchedCategory is not None:
                        metaFileObject = {
                            "imgSrc": matchedRegex.groups()[0],
                            "title": matchedRegex.groups()[1],
                            "category": matchedCategory.groups()[0],
                            "examples": list(matchedExamples.groups())
                        }
                        self.skill_info_model.append(metaFileObject)
                except:
                    self.log.warning("Readme File Not Found")

    @skill_api_method
    def skill_info_examples(self):
        examples = [d['examples'] for d in self.skill_info_model]
        flat_list = [item for sublist in examples for item in sublist]
        return flat_list

    def _getDataFromRegex(self, fileName, fileText, matchRegex):
        match = re.search(matchRegex, fileText);
        if match.groups() is None or len(match.groups()) == 0:
            self.log.warning("README.md file is not properly defined, it's missing data for the following regex:")
            self.log.warning("Please fix the README.md file of the skill")
            self.log.warning("This warning is for skill developers")
            self.log.warning("if you are not a developer, fill a bug on the corresponding skill.\n")
        return match;

    def stop(self):
        pass


def create_skill():
    return OVOSSkillsInfo()
