from openai import OpenAI

from logger_config import setup_logging

logger = setup_logging()


class OpenAIHandler:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key,
                             base_url='https://api.proxyapi.ru/openai/v1')

    async def get_response(self, model: str, messages: list) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.8,
                top_p=0.5
            )
            if response.choices:
                return (response.choices[0].message.content.strip(),
                        response.usage.total_tokens)
            else:
                return 'Не удалось получить ответ от OpenAI', 0
        except Exception as e:
            logger.error(f'Ошибка: {e}')
            return ('Произошла ошибка при запросе к OpenAI.'
                    'Пожалуйста, попробуйте позже.', 0)
