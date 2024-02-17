import time
from dotenv import load_dotenv
from samosila.core.providers.cohere import CohereProvider
from samosila.core.providers.ctranslate import CTranslateProvider
from samosila.core.providers.genai import GoogleGenAIProvider
from samosila.core.providers.gradient import GradientProvider

from samosila.core.providers.huggingface import HuggingFaceProvider
from samosila.core.providers.novita import NovitaProvider
from samosila.core.providers.segmind import SegmindProvider
from samosila.core.providers.together import TogetherProvider
from samosila.core.providers.voyage import VoyageProvider
from samosila.core.providers.openai import OpenAIProvider

from samosila.core.types import (
    CallbackManager, CompleteInput, ManipulationManager, UserMessage
)

load_dotenv()


callback_manager = CallbackManager([])
manipulation_manager = ManipulationManager([])

# configs = CompleteInput(provider_model="voyage-01", api_key="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")
# configs = CompleteInput(provider_model="BAAI/bge-small-en-v1.5",
#                         device="cuda", api_key="T5wu8hE0bMzTO2UIxuxyyAobBWsr4JWA")
# configs = CompleteInput(provider_model="bge-large",
#                         device="cuda", api_key="T5wu8hE0bMzTO2UIxuxyyAobBWsr4JWA")
# configs = CompleteInput(provider_model="all-MiniLM-L12-v2", device="cuda", api_key="")
# configs = CompleteInput(
#     provider_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cuda", api_key="")
# configs = CompleteInput(
#     provider_model="embed-english-v3.0", api_key="CbMuLJILdo1UTkqNfcwDLlw9BtS1n5VKR8CLkTOb")
# configs = CompleteInput(
#     provider_model="text-embedding-ada-002", api_key="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")
# configs = CompleteInput(
#     provider_model="models/embedding-gecko-001", api_key="AIzaSyDRNmS5Px7LvSXDA5rLbrfTrLRQFCyBW74")
# configs = CompleteInput(cfg=6.5,
#                         provider_model="dynavisionXLAllInOneStylized_release0534bakedvae_129001.safetensors", api_key="d734a50e-0fc4-4de0-8b9b-e2a6acafc302")
# configs = CompleteInput(cfg=1.5,
#                         provider_model="segmind-vega-rt-v1", api_key="SG_5841213d9381b9be")
# configs = CompleteInput(cfg=6.5,
#                         provider_model="stabilityai/stable-diffusion-xl-base-1.0", api_key="75dcd92ad4147404c2d7716824ae935a9524cdb15ad42f01038b5c92f0baae92")
configs = CompleteInput(cfg=6.5,
                        provider_model="Falconsai/text_summarization", api_key="75dcd92ad4147404c2d7716824ae935a9524cdb15ad42f01038b5c92f0baae92")

text = """
Lionel Andrés Messi[note 1] (Spanish pronunciation: [ljoˈnel anˈdɾes ˈmesi] (listen); born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards,[note 2] a record six European Golden Shoes, and in 2020 was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 35 trophies, including 10 La Liga titles, seven Copa del Rey titles and four UEFA Champions Leagues. With his country, he won the 2021 Copa América and the 2022 FIFA World Cup. A prolific goalscorer and creative playmaker, Messi holds the records for most goals in La Liga (474), most hat-tricks in La Liga (36) and the UEFA Champions League (8), and most assists in La Liga (192) and the Copa América (17). He has also the most international goals by a South American male (98). Messi has scored over 795 senior career goals for club and country, and has the most goals by a player for a single club (672).
Born and raised in central Argentina, Messi relocated to Spain at the age of 13 to join Barcelona, for whom he made his competitive debut aged 17 in October 2004. He established himself as an integral player for the club within the next three years, and in his first uninterrupted season in 2008–09 he helped Barcelona achieve the first treble in Spanish football; that year, aged 22, Messi won his first Ballon d'Or. Three successful seasons followed, with Messi winning four consecutive Ballons d'Or, making him the first player to win the award four times. During the 2011–12 season, he set the La Liga and European records for most goals scored in a single season, while establishing himself as Barcelona's all-time top scorer. The following two seasons, Messi finished second for the Ballon d'Or behind Cristiano Ronaldo (his perceived career rival), before regaining his best form during the 2014–15 campaign, becoming the all-time top scorer in La Liga and leading Barcelona to a historic second treble, after which he was awarded a fifth Ballon d'Or in 2015. Messi assumed captaincy of Barcelona in 2018, and in 2019 he won a record sixth Ballon d'Or. Out of contract, he signed for Paris Saint-Germain in August 2021.
An Argentine international, Messi holds the national record for appearances and is also the country's all-time leading goalscorer. At youth level, he won the 2005 FIFA World Youth Championship, finishing the tournament with both the Golden Ball and Golden Shoe, and an Olympic gold medal at the 2008 Summer Olympics. His style of play as a diminutive, left-footed dribbler drew comparisons with his compatriot Diego Maradona, who described Messi as his successor. After his senior debut in August 2005, Messi became the youngest Argentine to play and score in a FIFA World Cup in 2006, and reached the final of the 2007 Copa América, where he was named young player of the tournament. As the squad's captain from August 2011, he led Argentina to three consecutive finals: the 2014 FIFA World Cup, for which he won the Golden Ball, and the 2015 and 2016 Copa América, winning the Golden Ball in the 2015 edition. After announcing his international retirement in 2016, he reversed his decision and led his country to qualification for the 2018 FIFA World Cup, a third-place finish at the 2019 Copa América, and victory in the 2021 Copa América, while winning the Golden Ball and Golden Boot for the latter. This achievement would see him receive a record seventh Ballon d'Or in 2021. In 2022, he captained his country to win the 2022 FIFA World Cup, for which he won the Golden Ball for a record second time, and broke the record for most appearances in World Cup tournaments with 26 matches played.
Messi has endorsed sportswear company Adidas since 2006. According to France Football, he was the world's highest-paid footballer for five years out of six between 2009 and 2014, and was ranked the world's highest-paid athlete by Forbes in 2019 and 2022. Messi was among Time's 100 most influential people in the world in 2011 and 2012. In February 2020, he was awarded the Laureus World Sportsman of the Year, thus becoming the first footballer and the first team sport athlete to win the award. Later that year, Messi became the second footballer and second team-sport athlete to surpass $1 billion in career earnings.
"""

docs = ["The capital of France is Paris",
        "PyTorch is a machine learning framework based on the Torch library.",
        "The average cat lifespan is between 13-17 years"]

# # embed = VoyageProvider(configs, callback_manager, manipulation_manager)
# huggingface = HuggingFaceProvider(configs, callback_manager, manipulation_manager)
ctranslate = CTranslateProvider(
    configs, callback_manager, manipulation_manager)
# cohere = CohereProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = OpenAIProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = GoogleGenAIProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = GradientProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = NovitaProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = SegmindProvider(
#     configs, callback_manager, manipulation_manager)
# cohere = TogetherProvider(
#     configs, callback_manager, manipulation_manager)
start = time.time()
# res = cohere.image_generation(size="1024x1024", steps=25, metadata={"response_format": "url"},
#                               prompt="Medieval Castle, standing tall on a hill, surrounded by a moat, with banners flying and a drawbridge leading to it, evoking feelings of chivalry and bygone eras, designed in Low Poly style, with angular structures, flat color regions, and clear geometric definitions without intricate carvings.")
# res = cohere.embedding(docs)
# res = huggingface.image_search([
#     # Dog image
#     "https://unsplash.com/photos/QtxgNsmJQSs/download?ixid=MnwxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNjM1ODQ0MjY3&w=640",

#     # Cat image
#     "https://unsplash.com/photos/9UUoGaaHtNE/download?ixid=MnwxMjA3fDB8MXxzZWFyY2h8Mnx8Y2F0fHwwfHx8fDE2MzU4NDI1ODQ&w=640",

#     # Beach image
#     "https://unsplash.com/photos/Siuwr3uCir0/download?ixid=MnwxMjA3fDB8MXxzZWFyY2h8NHx8YmVhY2h8fDB8fHx8MTYzNTg0MjYzMg&w=640"
# ], "A black dog in the white snow")
# res = huggingface.translate(
#     ["سلام", "آیا VAR کمکی به کاهش اشتباهات داوری در دربی کرد؟"], "en", "fa")
res = ctranslate.translate(
    [
        "The articles discuss the use of organometallic compounds in cancer treatment, emphasizing their diverse structures and modes of action. They cover topics such as the synthesis and characterization of metal complexes, their biological activities, and their potential as anticancer agents. The potential of organometallic compounds for biological applications is highlighted, with a focus on their versatility and potential for further development. Specific compounds like RAPTA-C and RAED-C have demonstrated anti-metastatic and anti-angiogenic activity, with RAPTA-C binding to histone-protein sites and RAED-C showing selectivity toward DNA. Other bioactive ligands, such as flavonols and quinolones, have been used to design anticancer agents. Additionally, metal-carbene bonds in compounds like gold and ruthenium have shown anticancer activity by inhibiting enzymes and inducing apoptosis. Cyclometalated complexes with C-N bidentate ligands have also demonstrated cytotoxicity through activating target genes. The articles acknowledge the support of various organizations and foundations for research in this area, and overall, they highlight the challenges and potential of using organometallic compounds in cancer treatment.",
        "The paper discusses several research studies on the reaction mechanism of Rhodium-catalyzed hydroformylation of 1,3-butadiene using chelating bisphosphites. The studies utilize in situ IR and NMR experiments, kinetic measurements, and deuterioformylation experiments to elucidate the reaction mechanism. They provide insights into important intermediates, transition states, regioselectivity, and rate-determining steps of the reaction. Additionally, the stability of crotyl complexes and the reversibility of olefin insertion steps are explored. The findings contribute to a deeper understanding of the reaction mechanism and offer a basis for further research and ligand design. The investigations also involve the reaction of crotyl complexes with CO and H2 in the presence of a rhodium catalyst, observing the formation of different species and their reactivity under various conditions. Insights into the kinetics and regioselectivity of the reaction are provided, along with an examination of the reversibility of the olefin insertion step in the catalytic cycle. Furthermore, the research delves into the reaction mechanism of Rh-catalyzed hydroformylation of 1,3-butadiene to adipic aldehyde, revealing selectivity, rate-determining steps, and the stability of intermediates. The results suggest that the reaction rate is second-order in syngas pressure and independent of butadiene concentration. Overall, these studies significantly contribute to the understanding of Rh-catalyzed hydroformylation and provide valuable insights for future research and ligand development.",
     ], 
    "eng_Latn",
    "pes_Arab"
)


# batched_input = [
#     'We now have 4-month-old mice that are non-diabetic that used to be diabetic," he added.',
#     "Dr. Ehud Ur, professor of medicine at Dalhousie University in Halifax, Nova Scotia and chair of the clinical and scientific division of the Canadian Diabetes Association cautioned that the research is still in its early days."
#     "Like some other experts, he is skeptical about whether diabetes can be cured, noting that these findings have no relevance to people who already have Type 1 diabetes."
#     "On Monday, Sara Danius, permanent secretary of the Nobel Committee for Literature at the Swedish Academy, publicly announced during a radio program on Sveriges Radio in Sweden the committee, unable to reach Bob Dylan directly about winning the 2016 Nobel Prize in Literature, had abandoned its efforts to reach him.",
#     'Danius said, "Right now we are doing nothing. I have called and sent emails to his closest collaborator and received very friendly replies. For now, that is certainly enough."',
#     "Previously, Ring's CEO, Jamie Siminoff, remarked the company started when his doorbell wasn't audible from his shop in his garage.",
# ]
# res = ctranslate.translate(batched_input,"eng_Latn", "pes_Arab")

# res = huggingface.summarize_to_sentence(batched_input)


print(time.time() - start)
print(res)

with open("output.txt", "w", encoding="utf-8") as f:
    for string in res:
        f.write(string + "\n\n")
