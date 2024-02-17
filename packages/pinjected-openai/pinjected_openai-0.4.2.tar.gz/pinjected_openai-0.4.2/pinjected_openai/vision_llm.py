"""
TODO impl
"""
import asyncio
import base64
import io
import json
import os
import re
from pathlib import Path

from PIL.Image import Image
from loguru import logger
from pinjected import injected, Injected, instances, instance
from openai import AsyncOpenAI, RateLimitError


def to_content(img: Image):
    # convert Image into jpeg bytes
    jpg_bytes = io.BytesIO()
    img.convert('RGB').save(jpg_bytes, format='jpeg', quality=95)
    b64_image = base64.b64encode(jpg_bytes.getvalue()).decode('utf-8')
    mb_of_b64 = len(b64_image) / 1024 / 1024
    logger.info(f"image size: {mb_of_b64:.2f} MB in base64.")
    return {
        "type": 'image_url',
        "image_url": f"data:image/jpeg;base64,{b64_image}"
    }


@injected
async def a_repeat_for_rate_limit(logger, /, task):
    while True:
        try:
            return await task()
        except RateLimitError as e:
            logger.error(f"rate limit error: {e}")
            pat = "Please retry after (\d+) seconds."
            match = re.search(pat, e.message)
            if match:
                seconds = int(match.group(1))
                logger.info(f"sleeping for {seconds} seconds")
                await asyncio.sleep(seconds)
            else:
                logger.warning(f"failed to parse rate limit error message: {e.message}")
                await asyncio.sleep(10)


@injected
async def a_vision_llm__gpt4(
        async_openai_client: AsyncOpenAI,
        a_repeat_for_rate_limit,
        /,
        text: str,
        images: list[Image]) -> str:
    assert isinstance(async_openai_client, AsyncOpenAI)

    for img in images:
        assert isinstance(img, Image), f"image is not Image, but {type(img)}"

    async def task():
        chat_completion = await async_openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": 'text',
                            "text": text
                        },
                        *[to_content(img) for img in images]
                    ]
                }
            ],
            model="gpt-4-vision-preview",
            max_tokens=2048
        )
        return chat_completion

    chat_completion = await a_repeat_for_rate_limit(task)
    res = chat_completion.choices[0].message.content
    assert isinstance(res, str)
    logger.info(f"vision_llm__gpt4 result:\n{res}")
    return res


@injected
async def a_llm__gpt4_turbo(
        async_openai_client: AsyncOpenAI,
        a_repeat_for_rate_limit,
        /,
        text: str,
        max_completion_tokens=4096
) -> str:
    assert isinstance(async_openai_client, AsyncOpenAI)

    async def task():
        # import tiktoken
        # enc = tiktoken.get_encoding("cl100k_base")
        # n_token = len(enc.encode(text))
        chat_completion = await async_openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": 'text',
                            "text": text
                        },
                    ]
                }
            ],
            model="gpt-4-1106-preview",
            max_tokens=max_completion_tokens
        )
        return chat_completion

    chat_completion = await a_repeat_for_rate_limit(task)
    res = chat_completion.choices[0].message.content
    assert isinstance(res, str)
    logger.info(f"result:\n{res}")
    return res

@injected
async def a_json_llm__openai(
        logger,
        async_openai_client: AsyncOpenAI,
        a_repeat_for_rate_limit,
        /,
        text: str,
        max_completion_tokens=4096,
        model="gpt-4-0125-preview"
) -> str:
    assert isinstance(async_openai_client, AsyncOpenAI)

    async def task():
        # import tiktoken
        # enc = tiktoken.get_encoding("cl100k_base")
        # n_token = len(enc.encode(text))
        chat_completion = await async_openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": 'text',
                            "text": text
                        },
                    ]
                }
            ],
            model=model,
            max_tokens=max_completion_tokens,
            response_format={"type": "json_object"}
        )
        return chat_completion

    chat_completion = await a_repeat_for_rate_limit(task)
    res = chat_completion.choices[0].message.content
    assert isinstance(res, str)
    logger.info(f"\n{res}")
    return json.loads(res)



@injected
async def a_json_llm__gpt4_turbo(
        a_json_llm__openai,
        /,
        text: str,
        max_completion_tokens=4096
) -> str:
    return await a_json_llm__openai(
        text=text,
        max_completion_tokens=max_completion_tokens,
        model="gpt-4-turbo-preview"
    )



@instance
def async_openai_client(openai_api_key) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=openai_api_key,
    )


@instance
def openai_api_key() -> str:
    if (api_key := os.environ.get('OPENAI_API_KEY', None)) is None:
        api_key = Path(os.path.expanduser("~/.openai_api_key.txt")).read_text().strip()
    return api_key


test_vision_llm__gpt4 = a_vision_llm__gpt4(
    text="What are inside this image?",
    images=Injected.list(
    ),
)
"""
('The image appears to be an advertisement or an informational graphic about '
 'infant and newborn nutrition. It features a baby with light-colored hair who '
 'is lying down and holding onto a baby bottle, seemingly feeding themselves. '
 'The baby is looking directly towards the camera. The image uses a soft pink '
 'color palette, which is common for baby-related products or information. '
 'There are texts that read "Infant & Newborn Nutrition" and "Absolutely New," '
 'along with the word "PINGUIN" at the top, which could be a brand name or '
 "logo. The layout and design of this image suggest it's likely used for "
 'marketing purposes or as part of educational material regarding baby '
 'nutrition.')
"""

test_llm__gpt4_turbo = a_llm__gpt4_turbo(
    "Hello world"
)

test_json_llm__gpt4_turbo = a_json_llm__gpt4_turbo(
    "Hello world, respond to me in json"
)

__meta_design__ = instances()
