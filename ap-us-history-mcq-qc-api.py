from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict

app = FastAPI(title="AP US MCQ QC")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Constants
ABSOLUTES="""all, always, never, solely, sole, immediate, immediately, irrelevant, complete, completely, every, none, no significant impact, always, identical, unchanging, exclusively,  purely, uniform, universal"""
PATTERN_PHRASES="""no significant impact, no significant impact, minimal impact, impact was limited, effects were limited, universal, perfectly equal,largely irrelevant, passive victims"""

GOODQS = """
Question 1: Which of the following did the Mongol armies fail to conquer, and why?


Central Asia, because of the effective diplomacy of Timur and his successors

Explanation:
This answer is incorrect because the Mongols did conquer Central Asia. The effective diplomacy of Timur (Tamerlane) came much later, after the initial Mongol conquests under Genghis Khan and his successors had already established control over the region.


Kievan Russia, because the Mongols were unable to endure the harsh Russian winters

Explanation:
This answer is incorrect because the Mongols did successfully conquer Kievan Russia. Despite the harsh winters, the Mongols were able to adapt to the climate and use their superior military tactics to overcome the Russian principalities.


The ‘Abbasid Caliphate, because the defenders flooded the Mesopotamian plains and made them impassable for the Mongol cavalry

Explanation:
This answer is incorrect because the Mongols did conquer the ‘Abbasid Caliphate. In 1258, they captured Baghdad, marking the end of the Caliphate. The defenders did not flood the plains to stop the Mongols; instead, the Mongols used their military prowess to defeat the ‘Abbasid forces.


The Southern Song Empire, because of its superior resources from earlier industrial and commercial revolutions

Explanation:
This answer is incorrect because the Mongols did conquer the Southern Song Empire. Despite the Southern Song's resources and advancements, the Mongols eventually overcame them in 1279, leading to the establishment of the Yuan Dynasty in China.
Question 2: The breakup of the Mongol Empire into separate khanates during the mid-thirteenth century was most connected to which of the following developments?


Rebellions in China overthrew Mongol rule there and led to the reestablishment of Han Chinese rule under the Ming dynasty.

Explanation:
While it is true that rebellions in China eventually led to the fall of the Yuan dynasty and the rise of the Ming dynasty, this event occurred in the 14th century and was not the primary cause of the breakup of the Mongol Empire into separate khanates during the mid-13th century.


The spread of the bubonic plague following the expansion of trade along the Silk Roads weakened the Mongol Empire demographically and militarily.

Explanation:
While the bubonic plague did spread along trade routes and had a significant impact on various parts of the world, it was not the primary reason for the breakup of the Mongol Empire into separate khanates. The fragmentation of the empire occurred before the major outbreaks of the plague in the 14th century.


Mongol traditions emphasized tribal and personal loyalties and made it difficult to establish long-lasting centralized dynastic rule, which led to civil war.

(Correct)
Explanation:
The Mongol Empire, while initially unified under Genghis Khan, was fundamentally built on a system of tribal and personal loyalties. After the death of Genghis Khan, his successors struggled to maintain centralized control, leading to internal conflicts and the eventual division of the empire into separate khanates. This fragmentation was rooted in the inherent difficulties of unifying diverse tribes and maintaining centralized authority over a vast territory.


The attempts of Mongol rulers to force their subjects to convert to Islam led to widespread rebellions in Central and East Asia.

Explanation:
Mongol rulers were generally known for their religious tolerance and did not force their subjects to convert to Islam. This option is historically inaccurate as it does not align with the Mongol Empire's policies or the reasons for its fragmentation.

Question 3:

A historian researching the effects of the Crusades on the diffusion of technology would probably find which of the following sources most useful?


European crusaders’ accounts of Islamic religious practices

Explanation:
While European crusaders' accounts of Islamic religious practices might provide some context on cultural interactions, they are not directly related to the diffusion of technology. These accounts would mainly focus on religious and cultural observations rather than technological exchanges.


Birth records from villages along the routes used by the Crusaders

Explanation:
Birth records from villages along the routes used by the Crusaders would not provide much insight into the diffusion of technology. These records are more likely to offer demographic information rather than details about technological exchanges or advancements.


Monks’ translations of Arabic mathematics texts brought from conquered territories

(Correct)
Explanation:
Monks' translations of Arabic mathematics texts brought from conquered territories would be highly relevant to understanding the diffusion of technology. These texts represent a direct transfer of knowledge and technological advancements from the Islamic world to Europe, facilitated by the Crusades. The translations would show how European scholars adopted and adapted Arabic mathematical and scientific knowledge.


Muslim accounts of European royal marriages

Explanation:
Muslim accounts of European royal marriages would primarily deal with political alliances and social structures rather than technological diffusion. These records are unlikely to provide detailed information about the transfer of technology between cultures during the Crusades.

Question 9:


Historians who argue that there was substantial global integration by the end of the thirteenth century would most likely cite which of the following as evidence to support their claims?


The widening and deepening of exchange networks linking Afro-Eurasia after the Mongol conquests

(Correct)
Explanation:
The Mongol conquests in the 13th century played a crucial role in creating substantial global integration by connecting vast regions of Afro-Eurasia. The Pax Mongolica, or Mongol Peace, facilitated trade, cultural exchange, and the movement of people and goods across the Silk Roads, linking Europe, the Middle East, Central Asia, and East Asia. This period saw increased interactions and exchanges that contributed to a more interconnected world.


The political unification of large territories under imperial rule in the Mediterranean and East Asia

Explanation:
While the political unification of large territories under imperial rule, such as the Byzantine Empire in the Mediterranean and various dynasties in East Asia, did facilitate regional integration, it did not by itself create substantial global integration by the end of the thirteenth century. These empires were significant, but their influence was largely regional rather than global.


The spread of global capitalism from Europe to Africa and Southeast Asia

Explanation:
The spread of global capitalism from Europe to Africa and Southeast Asia occurred much later, primarily in the 16th century and beyond, as part of the Age of Exploration and the rise of European colonial empires. This development is not relevant to the thirteenth century and thus does not support the argument for substantial global integration by that time.


The creation of a new Atlantic trade system based on plantation economies in the Caribbean and the Americas

Explanation:
The creation of the Atlantic trade system based on plantation economies in the Caribbean and the Americas began in the late 15th century and expanded in the 16th and 17th centuries. This development is not relevant to the thirteenth century and therefore does not support the argument for substantial global integration by that time.
"""

BADQS = """
HISTORY BAD Qs {
          "question": "In what way did Neo-Confucianism emerge as a response to Buddhism during the Song Dynasty? \nA It completely rejected all Buddhist teachings and practices.\nB It integrated some Buddhist concepts while reinforcing Confucian values, creating a syncretic philosophy. \nC It promoted atheism as a new belief system among scholars. \nD It led to widespread persecution of Buddhist monks and temples throughout China.",
          "pass": false,
          "reason": "Absolute statements using words like all, every, never, completely, entirely, complete, are not plausible distractors."
        }
{
          "question": "Which of the following factors contributed most significantly to the agricultural productivity of Song China?\nA The adoption of crop rotation methods from Europe \n B The introduction of Champa rice from Vietnam (correct) \nC The use of chemical fertilizers developed in India \nD The implementation of large-scale irrigation systems from Mesopotamia",
          "pass": false,
          "reason": "The distractor option C too obviously false because it is a technology from a time period more than 600 years apart from the song dynasty"
        }
 {
          "question": "The role of women in Song Dynasty society was characterized by:        \nA) Complete equality with men in all aspects of public and private life. \nB) Increased economic opportunities alongside persistent social restrictions. \nC) Exclusion from all forms of education and literary pursuits. \nD) Mandatory participation in the civil service examination system.",
          "pass": false,
          "reason": "Distractors contain absolute statements such as all, complete, completely, never"
        }
        {
          "question": "The impact of Neo-Confucianism on Song Dynasty society can be best described as:\nA) A return to pure, unadulterated early Confucian thought without any new interpretations. \nB) A complete rejection of Confucian principles in favor of Buddhist and Daoist philosophies.\nC) A reinterpretation of Confucian ideas that reinforced social hierarchy and moral cultivation. \nD) An emphasis on individual spiritual enlightenment at the expense of social responsibilities.",
          "pass": false,
          "reason": "Distractors are obvious due to words such as all, complete, completely, never"
        }
  {
          "question": "In what way did the Song Dynasty's approach to commerce differ from previous dynasties, and what was a significant economic consequence of this approach?\n\nA By imposing strict trade restrictions, it minimized foreign influence and reduced economic growth.\nB By promoting maritime trade and technological innovations, it led to the commercialization of the economy.(correct) \nC By focusing solely on land-based trade routes like the Silk Road, it neglected naval advancements.\nD By adopting a barter system over currency, it simplified transactions but limited economic complexity.\n",
          "pass": false,
          "reason": "Neither the correct response nor any of the distractors respond to both parts of the question. The question asks for the difference from previous dynasties as well as the economic consequence. meaning there is no correct repsonse available"
        }

{
          "question": "What primarily facilitated diverse economic exchanges between different Indigenous groups before European colonization?        \nA CORRECT: Established trade networks based on regional resource specializations\nB A universally accepted system of coinage used across tribes \nCContracts enforced through a centralized legal authority \nD Digital communication platforms facilitating long.distance barter deals\n",
          "pass": false,
          "reason": "Distractor not a believable lie because it is wildly out of time period suggesting digital networks between 1200 & 1400"
        }
        {
          "question": "How did environmental factors most likely affect political structures in native societies before European arrival?\nA Varied climates led to different subsistence strategies that influenced social hierarchy and governance. \nB Frequent volcanic eruptions prompted a unified pan.Native American political coalition.\nC Widespread desertification drove the creation of continent.wide democratic assemblies. \nD Seasonal monsoons standardized government forms across all native societies on the continent.\n",
          "pass": false,
          "reason": "Distractors not plausible because students would not believe these lies. They are too silly."
        }
 {
          "question": "How did the differing views on land use between Europeans and Native Americans reflect their broader worldviews during the early interactions in North America?\n\nA Both Europeans and Native Americans believed land should be respected and not exploited for economic gain.\nB Both Europeans and Native Americans believed land was meant to be owned individually and used for personal gain.\nC The Europeans viewed land as a commodity for ownership, while Native Americans saw it as a shared resource. \nD Both Europeans and Native Americans believed land should be owned privately and used for farming.\n",
          "pass": false,
          "reason": "Neither the correct response nor any of the distractors connect the concepts in the question. The question asks for an explanation of how views on land use reflect broader world views. All response options address only views on land use meaning there is no correct repsonse available"
        }
"""

JSON_RESPONSE_SCHEMA = """{
        "score": 0 or 1,
        "rationale": "Your 2-line explanation here",
        "feedback": "Your 2-line feedback here"
      }"""

JSON_RESPONSE_SCHEMA_2 = """{
        "score": 0 or 1,
        "rationale": "Your 2-line explanation here",
        "ek_aligned": "the ek code that is aligned to the text"
        "lo_aligned": "the lo code that is aligned to the text"
        "skill_aligned": "the skill code that is aligned to the text"
    }"""

JSON_RESPONSE_SCHEMA_3 = """{
        "score": 0 or 1,
        "rationale": "Your 2-line explanation here",
        "difficulty": "0, 1, 2, or 3",
        "questiontype": "Question type determined"
        }"""

# bloom_easy: Bloom's (Remembering, Understanding), DOK (1-2)
BLOOM_EASY = """
Define: Provide the exact meaning of a word, term, or concept.
Identify: Recognize and name specific components or characteristics.
List: Enumerate items or ideas in a concise format.
State: Express information clearly and concisely.
Describe: Provide a detailed account of something's characteristics or features.
Explain: Clarify a concept or process by providing reasons or examples.
Summarize: Present the main points of information in a concise form.
Interpret: Explain the meaning or significance of something.
Illustrate: Provide examples or visual representations to clarify a point.
Classify: Organize items into categories based on shared characteristics.
Compare: Examine similarities between two or more things.
Contrast: Examine differences between two or more things.
Categorize: Group items or concepts based on shared characteristics.
Estimate: Make an approximate calculation or judgment.
Predict: Anticipate future outcomes based on current information.
Infer: Draw a conclusion based on evidence and reasoning.
"""

# bloom_moderate: Bloom's (Applying, Analyzing), DOK (3) Task verbs:
BLOOM_MODERATE = """
Analyze: Examine in detail to identify causes, key factors, or constituent parts.
Calculate: Determine a value using mathematical processes.
Demonstrate: Show how something works or how a process is completed.
Determine: Establish or conclude after consideration or investigation.
Develop: Create or expand on an idea, situation, or product.
Differentiate: Identify the differences between two or more things.
Examine: Inspect or scrutinize something in detail.
Formulate: Create or devise a plan, strategy, or system.
Investigate: Conduct a systematic inquiry to establish facts or principles.
Justify: Provide reasons or evidence to support a claim or decision.
Organize: Arrange information or items in a structured manner.
Relate: Show or establish a connection between things.
Solve: Find a solution to a problem or challenge.
Support: Provide evidence or arguments to back up a claim or position.
Use: Apply knowledge or skills for a specific purpose.
"""

# bloom_difficult: Bloom's (Evaluating, Creating), DOK (4) Task verbs:
BLOOM_DIFFICULT = """
Appraise: Assess the value or quality of something.
Apply: Use knowledge or skills in a new situation.
Argue: Present reasons for or against a point or idea.
Assess: Evaluate or estimate the nature, quality, or significance of something.
Compose: Create by putting elements together.
Conclude: Reach a logical end or judgment by reasoning.
Construct: Build or create something by systematically arranging parts.
Create: Bring something into existence that didn't exist before.
Critique: Offer a detailed analysis and assessment of something.
Design: Plan or create something for a specific purpose.
Evaluate: Make a judgment about the value or quality of something.
Generate: Produce or create something new.
Hypothesize: Propose an explanation for a phenomenon based on limited evidence.
Invent: Create a new product, process, or idea.
Judge: Form an opinion or conclusion about something.
Plan: Devise a method for doing or achieving something.
Produce: Make or manufacture something from components or raw materials.
Propose: Put forward an idea or plan for consideration.
Recommend: Suggest something as worthy of being adopted or done.
Revise: Reconsider and alter something in light of further evidence.
Synthesize: Combine different elements to form a coherent whole.
Validate: Demonstrate or support the truth or value of something.
"""

SKILL_DESCRIPTION = """[
    {'code': '1', 'skill': 'Developments and Processes', 'description': 'Identify and explain historical developments and processes.'},
    {'code': '2', 'skill': 'Sourcing and Situation', 'description': 'Analyze sourcing and situation of primary and secondary sources.'},
    {'code': '3', 'skill': 'Claims and Evidence in Sources', 'description': 'Analyze arguments in primary and secondary sources.'},
    {'code': '4', 'skill': 'Contextualization', 'description': 'Analyze the contexts of historical events, developments, or processes.'},
    {'code': '5', 'skill': 'Making Connections', 'description': 'Analyze patterns and connections between and among historical developments and processes using historical reasoning.'},
    {'code': '6', 'skill': 'Argumentation', 'description': 'Develop and support a historical argument.'}
]"""


# API Configuration
API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = ""
HEADERS = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# Request Models
class QuestionData(BaseModel):
    article: str
    topic_questions: str
    difficulty_level: int
    question: str
    responses: str
    correct: str
    distractors: str
    explanations: str
    ek_description: str
    lo_description: str

def call_claude_api(prompt: str) -> Optional[str]:
    payload = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 8192,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()['content'][0]['text']
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return None

def parallel_api_calls(prompts: List[str]) -> List[str]:
    responses = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(call_claude_api, prompt): i 
                          for i, prompt in enumerate(prompts)}

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                print(f'Prompt {index} generated an exception: {exc}')
                responses[index] = f"Error: {exc}"

    return responses

def generate_prompts(data: QuestionData) -> List[str]:
    blooms_difficulty = (BLOOM_EASY if data.difficulty_level == 1 
                        else BLOOM_MODERATE if data.difficulty_level == 2 
                        else BLOOM_DIFFICULT)
    
    prompts = {
        "prompt1": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the clarity of this question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate: #### {data.question} + {data.responses} ####
    Article: #### {data.article} ####
    Scoring:
    Assign a score of 1 if ALL of the following conditions are met:
    +There is a singular clear interpretation of the question.
    +Sufficient context is provided for a well-prepared student to answer correctly.
    -If the questions indicates the presence of information that will be given, a table, or reference text, it is given
    +Ensure the question could be answered based on the article or using critical thinking to apply knowledge learned in this or previous chapters

    Assign a score of 0 if ANY of the above conditions are not met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt2": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the format of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate: #### {data.question} + {data.responses} ####
    Scoring:
    Assign a score of 1 if ALL of the following conditions are met:
    +Confirm the question has 4 or 5 answer options in #### {data.responses} #### to select from.
    +Verify any formulas in #### {data.question} #### and #### {data.responses} #### are formatted and presented correctly in markdown + LaTeX
    +Verify all necessary components (e.g., passage, stem) are present as mentioned in the question.

    Assign a score of 0 if ANY of the above conditions are not met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt3": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the content of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate: #### {data.question} ####
    Essential Knowledge Code:  #### {data.ek_description} ####
    Learning Objective Code:  #### {data.lo_description} ####
    AP Skills:  #### {SKILL_DESCRIPTION} ####
    Article:  #### {data.article} ####

    Scoring:
    Assign a score of 1 if all of the following conditions are met:
    +The question can be answered by reading the accompanying article.
    -Even if a question contains new information it is answerable with the article if students can apply knowledge from the  #### {data.article} ####  to the new situation to come to a conclusion
    +The content is culturally sensitive (e.g. correct terminology is used to represent groups, does not discuss benefits of free, unpaid, slave labor as a positive construct)
    +The content is not similar in meaning to any other  #### {data.topic_questions} ####

    Assign a score of 0 if ANY of the above conditions are not met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt4": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the curriculum alignment of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate:  #### {data.question} + {data.responses} ####
    Essential Knowledge Code:  #### {data.ek_description} ####
    Learning Objective Code:  #### {data.lo_description} ####
    AP Skills:  #### {SKILL_DESCRIPTION} ####
    Article:  #### {data.article} ####

    Scoring:
    Assign a score of 1 if any one of the following conditions are met:
    +The question is aligned to a specific AP skill  #### {SKILL_DESCRIPTION} ####
    +The question is aligned to a specific AP Learning objective or  #### {data.lo_description} ####
    +The question is aligned to a specific AP Essential Knowledge Code  #### {data.ek_description} ####

    Assign a score of 0 if NONE of the above conditions are met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA_2}""",
        "prompt5": f"""As a renowned Psychometrician, assign a difficulty to the question. Apply your deep understanding of cognitive development, Bloom's Taxonomy, and Depth of Knowledge (DOK) levels in your analysis.

    Question to evaluate:  #### {data.question}+{data.responses}+{data.explanations} ####
    AP Skills: #### {data.article} ####

    Bloom Easy  #### {BLOOM_EASY} ####
    Bloom Moderate  #### {BLOOM_MODERATE} ####
    Bloom Difficult  #### {BLOOM_DIFFICULT} ####

    +The question type is “reading comprehension” and has  difficulty of 0 if all of the information required to respond is stated explicitly in the text.
    +The question type is “recall” and the difficulty is 1 if the task in the question is related to BLOOM_EASY
    +The question type is “analyze” and the difficulty is 2 if the task in the question is related to BLOOM_MODERATE
    +The question type is “evaluate” and the difficulty is 3 if the task in question is related to BLOOM_DIFFICULT
    +The task type is “apply” and the difficulty is 3 if the question presents new information or a new situation and the student must apply information from the ARTICLE to a new situation.

    +Now determine whether the difficulty is appropriate for AP learning materials. If the difficulty is 0, assign a score of 0. If the difficulty is greater than 0, assign a score of 1.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA_3}""",
        "prompt6": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the correct response to a multiple choice question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate and the correct response:  #### {data.question}+{data.correct} ####
    TaskVerb Definition:  #### {blooms_difficulty} ####


    Scoring:
    Assign a score of 1 if all of the following conditions are met:
    +The correct response is factually correct
    +The correct response is not more than one sentence in length
    +The correct response responds to all parts of the question. If the question asks for a combination, the response includes a combination
    +The correct response correctly uses the task verb. If the question is regarding an argument, the response includes an argument. If the question asks for a comparison between two things, a comparison is made.

    Assign a score of 0 if any of the above conditions are not  met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt7": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the distractors of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate and the responses:  #### {data.question}+{data.responses} ####
    TaskVerb Definition:  #### {blooms_difficulty} ####
    Multishot for reference:  #### {GOODQS} {BADQS} ####

    A distractor is a little lie that a teacher might tell to trick a high school student who came to class, but did not read the book or study before the exam.
    Distractors should be related to the topic, and general vocabulary, of the subject, but not too difficult that a first time learner would struggle if they read the chapter well.

    Scoring:
    Assign a score of 1 if all of the following conditions are met:
    +Each distractor is not more than 2 words longer or shorter than the correct response.
    +Each distractor correctly uses the task verbs in blooms to respond to all parts of the question. If the question is regarding an argument, the response includes an argument. If the question asks for a combination, the response includes a combination
    +Responds to all parts of the question. If the question asks for a comparison, a comparison is made.
    +A Distractor could not be confused for a correct answer if a student studied well

    Assign a score of 0 if any of the above conditions are not  met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt8": f"""As a preeminent AP educator and assessment expert with over three decades of cross-disciplinary experience, your task is to evaluate the quality of the distractor options. Apply your extensive knowledge of AP standards and effective pedagogical practices in your analysis.

    Question to evaluate:  #### {data.question} ####
    Distractor options:  #### {data.distractors} ####
    Absolutes for reference:  #### {ABSOLUTES} ####
    Patterns for reference:  #### {PATTERN_PHRASES} ####

    Scoring:
    Assign a score of 1 if all of the following conditions are met:

      + Not more than one response option contain a word in the list  #### {ABSOLUTES} ####
      + Distractors do not contain words from  #### {PATTERN_PHRASES} ####
      Assign a score of 0 if ANY of the above conditions are not met.

    7. Rationale and Feedback:
      Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    8. Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt9": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the coherence of the response set of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate and the correct response:  #### {data.question}+{data.responses} ####
    TaskVerb Definition  #### {blooms_difficulty} ####
    Multishot for reference:  #### {GOODQS} {BADQS} ####

    Scoring:
    Assign a score of 1 if all of the following conditions are met:
    +All responses has the same number of commas
    +Each Response correctly uses the task verbs ####  {blooms_difficulty} ####  to  respond to all parts of the question. (e.g. If the question asks for a comparison, a comparison is made.)
    +Each response is unique in interpretation from all other response options
    +There is only one response that is arguably correct for a student who has studied well
    +All responses are written in the same tense and style


    Assign a score of 0 if any of the above conditions are not  met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}""",
        "prompt10": f"""As a world-renowned expert in educational assessment with 30 years of experience designing AP exams across various subjects, your task is to evaluate the explanations for a response set of a question. Apply your unparalleled expertise and critical thinking skills to this evaluation.

    Question to evaluate and the correct response:  #### {data.question}+{data.responses} ####
    Explanations to evaluate: #### {data.explanations}
    TaskVerb Definition:  #### {blooms_difficulty} ####
    Multishot for reference:  #### {GOODQS} {BADQS} ####

    Scoring:
    Assign a score of 1 if all of the following conditions are met:
    +There exists an explanation for all correct and incorrect responses
    + Each explanation is factually correct
    +Each explanation is between 2 and 4 sentences
    +Each explanation addresses why the answer is correct or incorrect


    Assign a score of 0 if any of the above conditions are not  met.

    Provide a concise 2-line explanation for your scoring decision and 2 lines of actionable feedback.

    Response Format:
      Return ONLY a JSON object with this structure:
      {JSON_RESPONSE_SCHEMA}"""
    }
    
    return list(prompts.values())

@app.post("/analyze-question")
async def analyze_question(data: QuestionData) -> Dict[str, dict]:
    try:
        # Generate all prompts
        prompts = generate_prompts(data)
        
        # Make parallel API calls
        responses = parallel_api_calls(prompts)
        
        # Format response
        result = {}
        for i, response in enumerate(responses, 1):
            try:
                # Parse JSON response if valid
                if response and isinstance(response, str):
                    result[f"prompt{i}"] = eval(response)
                else:
                    result[f"prompt{i}"] = {"error": "Invalid response"}
            except Exception as e:
                result[f"prompt{i}"] = {"error": f"Failed to parse response: {str(e)}"}
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
