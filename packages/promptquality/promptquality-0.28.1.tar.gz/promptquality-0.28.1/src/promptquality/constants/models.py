from enum import Enum


class Models(str, Enum):
    # OpenAI models.
    chat_gpt = "ChatGPT (4K context)"
    chat_gpt_16k = "ChatGPT (16K context)"
    gpt_35_turbo = "ChatGPT (4K context)"
    gpt_35_turbo_16k = "ChatGPT (16K context)"
    gpt_4 = "gpt-4 (8K context)"
    gpt_4_turbo = "GPT-4 Turbo"
    gpt_4_128k = "gpt-4 (128K context)"
    babbage_2 = "babbage-002"
    davinci_2 = "davinci-002"

    # Azure models.
    azure_chat_gpt = "ChatGPT (4K context) (Azure)"
    azure_chat_gpt_16k = "ChatGPT (16K context) (Azure)"
    azure_gpt_35_turbo = "ChatGPT (4K context) (Azure)"
    azure_gpt_35_turbo_16k = "ChatGPT (16K context) (Azure)"
    azure_gpt_4 = "gpt-4 (8K context) (Azure)"

    # Vertex AI models.
    text_bison = "text-bison"
    text_bison_001 = "text-bison@001"
    gemini_pro = "gemini-pro"

    # Writer models.
    palmyra_base = "Palmyra Base"
    palmyra_large = "Palmyra Large"
    palmyra_instruct = "Palmyra Instruct"
    palmyra_instruct_30 = "Palmyra Instruct 30"
    palmyra_beta = "Palmyra Beta"
    silk_road = "Silk Road"
    palmyra_e = "Palmyra E"
    palmyra_x = "Palmyra X"
    palmyra_x_32k = "Palmyra X 32K"
    palmyra_med = "Palmyra Med"
    examworks_v1 = "Exam Works"
