from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements


DEFAULT_SETTINGS = {
    "my_setting": "x"
}





class ReplaceSkillNameSkill(OVOSSkill):
    
    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )   
    
    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        self.settings.merge(DEFAULT_SETTINGS, new_only=True)
        self.add_event("ovos_testpkg.openvoiceos.home", self.handle_homescreen)

    def handle_homescreen(self, message):
        """ handle open skill """
        self.gui.show_text("hello homescreen!", override_idle=True)

    @intent_handler('HowAreYou.intent')
    def handle_how_are_you_intent(self, message):
        """ This is a Padatious intent handler.
        It is triggered using a list of sample phrases."""
        self.speak_dialog("how.are.you")

    @intent_handler(IntentBuilder('HelloWorldIntent')
                    .require('HelloKeyword').optionally("WorldKeyword"))
    def handle_hello_world_intent(self, message):
        """ Skills can log useful information. These will appear in the CLI and
        the skills.log file."""
        self.log.info("There are five types of log messages: "
                      "info, debug, warning, error, and exception.")
        self.speak_dialog("hello.world")

    @intent_handler(IntentBuilder('YesNoIntent')
                    .one_of('YesKeyword', 'NoKeyword')
                    .optionally("WorldKeyword"))
    def handle_yesno_world_intent(self, message):
        if message.data.get("YesKeyword"):
            self.speak("yes")
        else:
            self.speak("no")
        if message.data.get("WorldKeyword"):
            self.speak("world!")

    def stop(self):
        pass


def create_skill():
    return ReplaceSkillNameSkill()