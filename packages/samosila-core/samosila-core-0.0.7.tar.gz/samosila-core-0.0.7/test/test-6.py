from dotenv import load_dotenv
from openserver.integrations.callbacks.context import ContextCallbackHandler
from openserver.integrations.callbacks.prompt_layer import PromptLayerCallbackHandler
from openserver.integrations.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from openserver.integrations.callbacks.launry import LunaryCallbackHandler
from openserver.integrations.manipulations.cache import CacheManipulationHandler, CacheType
from openserver.integrations.manipulations.prompt import PromptManipulationHandler, PromptTypes
from openserver.providers.fake import FakeProvider
# from openserver.providers.gf4 import FreeProvider
from openserver.providers.openai import OpenAIProvider

from openserver.types import (
    CallbackManager, CompleteInput, ManipulationManager, UserMessage
)

load_dotenv()


callback_manager = CallbackManager([
    # ContextCallbackHandler(),
    StreamingStdOutCallbackHandler(),
    # LunaryCallbackHandler(),
    # PromptLayerCallbackHandler(),
])

manipulation_manager = ManipulationManager([
  # PromptManipulationHandler([PromptTypes.SAVE_KITTEN]),
#   CacheManipulationHandler(cache_type=CacheType.SIMILAR),
])
configs = CompleteInput(cache=True, streaming=True,
    provider_model='nousresearch/nous-capybara-7b', base_url="https://openrouter.ai/api/v1", api_key="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")
# configs = CompleteInput(provider_model='gpt-3.5-turbo',
#                         api_key='',)
# configs = CompleteInput(
#     provider_model='gpt-3.5-turbo', base_url="https://neuroapi.host", api_key="sk-DjqQGTZp6530U4Ux2792740a6061435480AeF64e88Eb2bEc")

text = """
Lionel Andrés Messi[note 1] (Spanish pronunciation: [ljoˈnel anˈdɾes ˈmesi] (listen); born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards,[note 2] a record six European Golden Shoes, and in 2020 was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 35 trophies, including 10 La Liga titles, seven Copa del Rey titles and four UEFA Champions Leagues. With his country, he won the 2021 Copa América and the 2022 FIFA World Cup. A prolific goalscorer and creative playmaker, Messi holds the records for most goals in La Liga (474), most hat-tricks in La Liga (36) and the UEFA Champions League (8), and most assists in La Liga (192) and the Copa América (17). He has also the most international goals by a South American male (98). Messi has scored over 795 senior career goals for club and country, and has the most goals by a player for a single club (672).
Born and raised in central Argentina, Messi relocated to Spain at the age of 13 to join Barcelona, for whom he made his competitive debut aged 17 in October 2004. He established himself as an integral player for the club within the next three years, and in his first uninterrupted season in 2008–09 he helped Barcelona achieve the first treble in Spanish football; that year, aged 22, Messi won his first Ballon d'Or. Three successful seasons followed, with Messi winning four consecutive Ballons d'Or, making him the first player to win the award four times. During the 2011–12 season, he set the La Liga and European records for most goals scored in a single season, while establishing himself as Barcelona's all-time top scorer. The following two seasons, Messi finished second for the Ballon d'Or behind Cristiano Ronaldo (his perceived career rival), before regaining his best form during the 2014–15 campaign, becoming the all-time top scorer in La Liga and leading Barcelona to a historic second treble, after which he was awarded a fifth Ballon d'Or in 2015. Messi assumed captaincy of Barcelona in 2018, and in 2019 he won a record sixth Ballon d'Or. Out of contract, he signed for Paris Saint-Germain in August 2021.
An Argentine international, Messi holds the national record for appearances and is also the country's all-time leading goalscorer. At youth level, he won the 2005 FIFA World Youth Championship, finishing the tournament with both the Golden Ball and Golden Shoe, and an Olympic gold medal at the 2008 Summer Olympics. His style of play as a diminutive, left-footed dribbler drew comparisons with his compatriot Diego Maradona, who described Messi as his successor. After his senior debut in August 2005, Messi became the youngest Argentine to play and score in a FIFA World Cup in 2006, and reached the final of the 2007 Copa América, where he was named young player of the tournament. As the squad's captain from August 2011, he led Argentina to three consecutive finals: the 2014 FIFA World Cup, for which he won the Golden Ball, and the 2015 and 2016 Copa América, winning the Golden Ball in the 2015 edition. After announcing his international retirement in 2016, he reversed his decision and led his country to qualification for the 2018 FIFA World Cup, a third-place finish at the 2019 Copa América, and victory in the 2021 Copa América, while winning the Golden Ball and Golden Boot for the latter. This achievement would see him receive a record seventh Ballon d'Or in 2021. In 2022, he captained his country to win the 2022 FIFA World Cup, for which he won the Golden Ball for a record second time, and broke the record for most appearances in World Cup tournaments with 26 matches played.
Messi has endorsed sportswear company Adidas since 2006. According to France Football, he was the world's highest-paid footballer for five years out of six between 2009 and 2014, and was ranked the world's highest-paid athlete by Forbes in 2019 and 2022. Messi was among Time's 100 most influential people in the world in 2011 and 2012. In February 2020, he was awarded the Laureus World Sportsman of the Year, thus becoming the first footballer and the first team sport athlete to win the award. Later that year, Messi became the second footballer and second team-sport athlete to surpass $1 billion in career earnings.
"""
                     

# llm = FreeProvider(configs, callback_manager, manipulation_manager)
# llm = OpenAIProvider(configs, callback_manager, manipulation_manager)
llm = FakeProvider(configs, callback_manager, manipulation_manager)
res = llm.completion(text)
# res = llm.chat([UserMessage(
#     content=f"Answer the question using the provided context. Your answer should be in your own words and be no longer than 50 words. \n\n Context: {text} \n\n Question: What trophies does Messi has ? \n\n Answer: ")])
print(res)
