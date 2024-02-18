# mypy: disable-error-code="override"
from typing import NoReturn, Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.common.client import KluClientBase
from klu.common.errors import (
    InvalidUpdateParamsError,
    NotSupportedError,
    UnknownKluAPIError,
    UnknownKluError,
)
from klu.finetune.constants import (
    FINETUNE_ENDPOINT,
    PROCESS_FINETUNE_ENDPOINT,
    READ_FINETUNE_STATUS_ENDPOINT,
)
from klu.finetune.errors import FinetuneNotFoundError
from klu.finetune.models import Finetune, FinetuneStatusResponse
from klu.utils.dict_helpers import dict_no_empty


class FinetuneClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, FINETUNE_ENDPOINT, Finetune)

    async def create(self) -> NoReturn:
        raise NotSupportedError()

    async def get(self, guid: str) -> Finetune:
        """
        Retrieves fine_tune information based on the unique Finetune guid, created during the Finetune creation.

        Args:
            guid (str): GUID of a fine_tune to fetch. The one that was used during the fine_tune creation

        Returns:
            Finetune object
        """
        return await super().get(guid)

    async def update(
        self,
        guid: str,
        name: Optional[str] = None,
        openai_finetune_name: Optional[str] = None,
    ) -> Finetune:
        """
        Update fine_tune data. At least one of the params has to be provided

        Args:
            guid (str): GUID of a fine_tune to update.
            name: Optional[str]. New fine_tune name
            openai_fine_tune_name: Optional[str]. New fine_tune openai_name

        Returns:
            Updated fine_tune instance
        """

        if not name and not openai_finetune_name:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty(
                    {
                        "name": name,
                        "openai_finetune_name": openai_finetune_name,
                    }
                ),
            }
        )

    async def delete(self, guid: str) -> Finetune:
        """
        Delete fine_tune based on the id.

        Args:
            guid (str): Unique Guid of a finetune to delete.

        Returns:
            Deleted finetune object
        """
        return await super().delete(guid)

    async def process(
        self,
        finetune_guid: str,
        base_model: str,
    ) -> Finetune:
        """
        Process the finetune.

        Args:
            finetune_guid (str): The GUID of the finetune to process.
            base_model (str): Can be one of [gpt-3.5-1106, gpt-4-0613, gpt-3.5-0613, babbage-002, davinci-002] or a fine-tuned model created by your organization.

        Returns:
            The Finetune object
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            try:
                response = await client.post(
                    PROCESS_FINETUNE_ENDPOINT,
                    {
                        "baseModel": base_model,
                        "finetuneGuid": finetune_guid,
                    },
                )
                return Finetune._from_engine_format(response)
            except ClientResponseError as e:
                if e.status == 404:
                    raise FinetuneNotFoundError(finetune_guid)

                raise UnknownKluAPIError(e.status, e.message)
            except Exception as e:
                raise UnknownKluError(e)

    async def read_status(
        self,
        finetune_guid: str,
    ) -> FinetuneStatusResponse:
        """
        Read fine_tune status.

        Args:
            finetune_guid (str): The GUID of the fine_tune to process.

        Returns:
            The status of a Finetune and OpenAI Finetune name
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            try:
                response = await client.get(
                    READ_FINETUNE_STATUS_ENDPOINT.format(id=finetune_guid)
                )
                return FinetuneStatusResponse._create_instance(**response)
            except ClientResponseError as e:
                if e.status == 404:
                    raise FinetuneNotFoundError(finetune_guid)

                raise UnknownKluAPIError(e.status, e.message)
            except Exception as e:
                raise UnknownKluError(e)
