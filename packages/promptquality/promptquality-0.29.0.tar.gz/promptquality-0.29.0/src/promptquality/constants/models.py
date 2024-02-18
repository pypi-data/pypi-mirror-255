from enum import Enum


class Models(str, Enum):
    # OpenAI models.
    chat_gpt = "ChatGPT (4K context)"
    chat_gpt_16k = "ChatGPT (16K context)"
    gpt_35_turbo = "ChatGPT (4K context)"
    gpt_35_turbo_16k = "ChatGPT (16K context)"
    gpt_35_turbo_16k_0125 = "ChatGPT (16K context, 0125)"
    gpt_4 = "gpt-4 (8K context)"
    gpt_4_turbo = "GPT-4 Turbo"
    gpt_4_turbo_0125 = "GPT-4 Turbo (0125)"
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

    # AWS Bedrock models.
    aws_titan_tg1_large = "AWS - Titan TG1 Large (Bedrock)"
    aws_titan_text_lite_v1 = "AWS - Titan Lite v1 (Bedrock)"
    aws_titan_text_express_v1 = "AWS - Titan Express v1 (Bedrock)"
    cohere_command_text_v14 = "Cohere - Command v14 (Bedrock)"
    cohere_command_light_text_v14 = "Cohere - Command Light v14 (Bedrock)"
    ai21_j2_mid_v1 = "AI21 - Jurassic-2 Mid v1 (Bedrock)"
    ai21_j2_ultra_v1 = "AI21 - Jurassic-2 Ultra v1 (Bedrock)"
    anthropic_claude_instant_v1 = "Anthropic - Claude Instant v1 (Bedrock)"
    anthropic_claude_v1 = "Anthropic - Claude v1 (Bedrock)"
    anthropic_claude_v2 = "Anthropic - Claude v2 (Bedrock)"
    meta_llama2_13b_chat_v1 = "Meta - Llama 2 Chat 13B v1 (Bedrock)"

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
