import logging
import typing as t
import warnings

try:
    from sarus_llm.torch_interface.sample import TextSampler
    from sarus_llm.torch_interface.typing import ModelProvider
except (ModuleNotFoundError, ValueError, RuntimeError):
    warnings.warn('Sarus LLM not available')

import pyarrow as pa

from sarus_data_spec.constants import PUBLIC
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.ops.processor.standard.standard_op import (  # noqa: E501
    StandardDatasetImplementation,
    StandardDatasetStaticChecker,
)
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.schema import schema
from sarus_data_spec.type import Struct, Text
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

logger = logging.getLogger()


class GenerateFromModelStaticChecker(StandardDatasetStaticChecker):
    async def schema(self) -> st.Schema:
        _, kwargs = self.dataset.parents()
        pretrained_model = kwargs["model"]
        assert isinstance(pretrained_model, Scalar)
        prompts = kwargs["prompts"]
        assert isinstance(prompts, Dataset)
        is_public = pretrained_model.is_public() and prompts.is_public()
        return schema(
            dataset=self.dataset,
            schema_type=Struct(
                {"text": Text()}, properties={PUBLIC: str(is_public)}
            ),
        )


class GenerateFromModel(StandardDatasetImplementation):
    async def to_arrow(
        self, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        _, kwargs = self.dataset.parents()
        pretrained_model = kwargs["model"]
        prompts = kwargs["prompts"]
        transform = self.dataset.transform()

        assert pretrained_model.prototype() == sp.Scalar, "pretrained model should be a Scalar"  # type: ignore # noqa: E501
        pretrained_ds = t.cast(st.Scalar, pretrained_model)
        model_provider = t.cast(
            ModelProvider, await pretrained_ds.async_value()
        )

        assert prompts.prototype() == sp.Dataset, "prompts should be a Dataset"
        prompts_ds = t.cast(st.Dataset, prompts)

        specs = transform.protobuf().spec.generate_from_model
        sampler = TextSampler(
            model_provider=model_provider,
            quantize=True,
            temperature=specs.temperature,
            max_new_tokens=specs.max_new_tokens,
        )

        async def async_iterator() -> t.AsyncIterator[pa.RecordBatch]:
            async for batch in await prompts_ds.async_to_arrow(batch_size):
                text_samples = pa.array(
                    sampler.generate(prompts=batch.to_pydict()['prompt'])
                )
                yield pa.RecordBatch.from_struct_array(
                    pa.StructArray.from_arrays(
                        arrays=[text_samples], names=['text']
                    )
                )

        return async_iterator()
