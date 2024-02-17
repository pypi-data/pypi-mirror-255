import loguru
from pinjected import instances, providers

__meta_design__ = instances(
    default_design_path="pinjected_openai.default_design"
)
default_design=instances(

) + providers(
    logger = lambda: loguru.logger
)

