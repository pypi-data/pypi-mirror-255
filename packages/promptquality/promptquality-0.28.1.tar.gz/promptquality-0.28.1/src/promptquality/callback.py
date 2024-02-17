from collections import defaultdict
from json import dumps
from time import time_ns
from typing import Any, DefaultDict, Dict, List, Optional, Sequence, Union
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.embeddings import __all__ as LangchainEmbeddingNames
from langchain.prompts.chat import ChatPromptValue
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.schema.document import Document
from langchain.schema.messages import BaseMessage
from langchain.schema.messages import _message_to_dict as message_to_dict
from langchain.schema.output import LLMResult
from langchain.vectorstores import __all__ as LangchainVectorStoreNames
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

from promptquality.chain_run import chain_run
from promptquality.constants.run import TagType
from promptquality.constants.scorers import Scorers
from promptquality.set_config import set_config
from promptquality.types.chains.node_type import NodeType
from promptquality.types.chains.row import NodeRow
from promptquality.types.config import Config
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.registered_scorers import RegisteredScorer
from promptquality.types.run import RunTag
from promptquality.utils.logger import logger

Stringable = (str, int, float)
EmbeddingRunTagKey = "Embedding Model"
VectorStoreRunTagKey = "Vector Store"


class GalileoPromptCallback(BaseCallbackHandler):
    def __init__(
        self,
        project_name: Optional[str] = None,
        run_name: Optional[str] = None,
        scorers: Optional[List[Union[Scorers, CustomScorer, RegisteredScorer, str]]] = None,
        run_tags: Optional[List[RunTag]] = None,
        config: Optional[Config] = None,
        **kwargs: Any,
    ) -> None:
        """
        LangChain callbackbander for logging prompts to Galileo.

        Parameters
        ----------
        project_name : str
            Name of the project to log to
        """
        # Galileo parameters.
        self.project_name = project_name
        self.run_name = run_name
        self.scorers = scorers
        self.run_tags = run_tags
        self.config = config or set_config()

        # Row information.
        # Mapping of root of the chain to all children.
        self.root_child_mapping: DefaultDict = defaultdict(list)
        self.root_nodes: List[UUID] = list()
        # Mapping of parent to children.
        self.parent_child_mapping: DefaultDict = defaultdict(list)
        # Mapping of child to parent.
        self.child_parent_mapping: Dict[UUID, Optional[UUID]] = dict()

        self.chain_inputs: Dict[UUID, Dict[str, Any]] = dict()
        self.serializations: Dict[UUID, Dict[str, Any]] = dict()

        self.rows: Dict[UUID, NodeRow] = dict()

    def set_relationships(self, run_id: UUID, node_type: NodeType, parent_run_id: Optional[UUID] = None) -> None:
        self.child_parent_mapping[run_id] = parent_run_id
        if parent_run_id:
            self.parent_child_mapping[parent_run_id].append(run_id)
            self.rows[parent_run_id].has_children = True
        root_id = self.get_root_id(run_id)
        self.root_child_mapping[root_id].append(run_id)
        self.rows[run_id] = NodeRow(
            node_id=run_id,
            node_type=node_type,
            # -1 because the step is incremented after the callback is run.
            step=len(self.root_child_mapping[root_id]) - 1,
            chain_id=parent_run_id,
            chain_root_id=root_id,
        )
        if root_id == run_id:
            self.root_nodes.append(run_id)

    def get_root_id(self, run_id: UUID) -> UUID:
        parent_id = self.child_parent_mapping[run_id]
        if parent_id:
            return self.get_root_id(parent_id)
        else:
            return run_id

    def mark_step_start(
        self,
        run_id: UUID,
        serialized: Dict[str, Any],
        prompt: Optional[str] = None,
        node_input: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        root_id = self.get_root_id(run_id)
        self.rows[run_id].serialized = serialized
        self.rows[run_id].prompt = prompt
        self.rows[run_id].node_input = node_input
        self.rows[run_id].params = kwargs.get("invocation_params", dict())
        self.rows[run_id].inputs = self.chain_inputs.get(root_id, dict())
        # Parse and set the name of the node.
        node_class_reference = serialized.get("id")
        if node_class_reference:
            self.rows[run_id].node_name = node_class_reference[-1]
        # Set the prompt for all of the parent nodes if it isn't set.
        parent_id = self.child_parent_mapping[run_id]
        while parent_id:
            if self.rows[parent_id].prompt is None:
                self.rows[parent_id].prompt = prompt
            parent_id = self.child_parent_mapping.get(parent_id)

    def mark_step_end(
        self, run_id: UUID, response: Optional[str] = None, node_output: Optional[str] = None, **kwargs: Dict[str, Any]
    ) -> None:
        self.rows[run_id].latency = time_ns() - self.rows[run_id].creation_timestamp
        if response:
            self.rows[run_id].response = response
            # Update the output of the parent nodes.
            parent_id = self.child_parent_mapping.get(run_id)
            while parent_id:
                self.rows[parent_id].response = response
                parent_id = self.child_parent_mapping.get(parent_id)
        # Agents set node_output before the chain_end step, so check if value already set
        if not self.rows[run_id].node_output:
            self.rows[run_id].node_output = node_output

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever starts running."""
        self.set_relationships(run_id, node_type=NodeType.retriever, parent_run_id=parent_run_id)
        self.mark_step_start(run_id, serialized, node_input=query, **kwargs)
        # Try to add relevant tags to self.run_tags
        existing_tag_keys = [tag.key for tag in self.run_tags] if self.run_tags else []
        if tags:
            run_tags = self.run_tags or []
            for tag in tags:
                if tag in LangchainEmbeddingNames and EmbeddingRunTagKey not in existing_tag_keys:
                    run_tags.append(RunTag(key=EmbeddingRunTagKey, value=tag, tag_type=TagType.RAG))
                if tag in LangchainVectorStoreNames and VectorStoreRunTagKey not in existing_tag_keys:
                    run_tags.append(RunTag(key=VectorStoreRunTagKey, value=tag, tag_type=TagType.RAG))
            self.run_tags = run_tags

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever ends running."""
        node_output = dumps(
            [{"page_content": document.page_content, "metadata": document.metadata} for document in documents]
        )
        self.mark_step_end(run_id, node_output=node_output, **kwargs)

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever errors."""
        del self.rows[run_id]

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool starts running."""
        self.set_relationships(run_id, node_type=NodeType.tool, parent_run_id=parent_run_id)
        self.mark_step_start(run_id, serialized, node_input=input_str, **kwargs)

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool ends running."""
        self.mark_step_end(run_id, node_output=output, **kwargs)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool errors."""
        del self.rows[run_id]

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Run on agent finish.

        The order of operations for agents is on_chain_start, on_agent_action x times, on_agent_finish, on_chain_finish.
        We are creating the agent node with on_chain_start, then populating all of it's agent specific data in
        on_agent_finish. We are skipping on_agent_action, because there is no relevant info there as of yet and it could
        also be called 0 times.
        """
        self.rows[run_id].node_type = NodeType.agent
        self.rows[run_id].node_input = self.chain_inputs[run_id].get("input")
        self.rows[run_id].node_output = finish.return_values.get("output") or finish.log

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when LLM starts running."""
        self.set_relationships(run_id, node_type=NodeType.llm, parent_run_id=parent_run_id)
        prompt = prompts[0]
        self.mark_step_start(run_id, serialized, prompt=prompt, node_input=prompt, **kwargs)

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Chat Model starts running."""
        self.set_relationships(run_id, node_type=NodeType.chat, parent_run_id=parent_run_id)

        chat_messages = ChatPromptValue(messages=messages[0])
        prompt = chat_messages.to_string()
        self.mark_step_start(run_id, serialized, prompt=prompt, node_input=prompt, **kwargs)

    def on_llm_end(
        self, response: LLMResult, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when LLM ends running."""

        # Flatten the response and pull out the generation.
        generation = response.flatten()[0].generations[0][0]
        self.mark_step_end(run_id, response=generation.text, node_output=generation.text, **kwargs)

        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            self.rows[run_id].query_input_tokens = usage.get("prompt_tokens", 0)
            self.rows[run_id].query_output_tokens = usage.get("completion_tokens", 0)
            self.rows[run_id].query_total_tokens = usage.get("total_tokens", 0)

        if generation.generation_info:
            self.rows[run_id].finish_reason = generation.generation_info.get("finish_reason", "")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when LLM errors."""
        del self.rows[run_id]

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Union[Dict[str, Any], Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Run when chain starts running.

        The inputs here are expected to only be a dictionary per the `langchain` docs
        but from experience, we do see strings and `BaseMessage`s in there, so we
        support those as well.
        """
        self.set_relationships(run_id, node_type=NodeType.chain, parent_run_id=parent_run_id)
        if isinstance(inputs, Stringable):
            node_input = {"input": inputs}
        elif isinstance(inputs, BaseMessage):
            node_input = message_to_dict(inputs)
        elif isinstance(inputs, dict):
            # We only support string inputs since those are the likely slots.
            node_input = inputs = {
                key: value for key, value in inputs.items() if value and isinstance(value, Stringable)
            }
        elif isinstance(inputs, list) and all(isinstance(v, Document) for v in inputs):
            node_input = {str(index): value.page_content for index, value in enumerate(inputs)}
        else:
            logger.warning(
                f"Unsupported input type {type(inputs)} for {run_id=}, {parent_run_id=}, {inputs=}. Skipping..."
            )
            node_input = dict()
        self.chain_inputs[run_id] = node_input
        self.mark_step_start(run_id, serialized, node_input=dumps(node_input), **kwargs)

    def on_chain_end(
        self, outputs: Union[str, Dict[str, Any]], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when chain ends running."""
        self.rows[run_id].finish_reason = "chain_end"
        response: Optional[str] = None
        if isinstance(outputs, str):
            response = outputs
            node_output = {"output": outputs}
        elif isinstance(outputs, dict):
            # casting to a str because it should work somewhat cleanly with most output parser types
            # https://python.langchain.com/docs/modules/model_io/output_parsers/types
            # The 'output' key is present on agent chains
            response = str(outputs.get("text", "")) or str(outputs.get("output", ""))
            node_output = outputs
        elif isinstance(outputs, (AgentFinish, AgentAction)):
            response = outputs.json()
            node_output = outputs.dict()
        else:
            logger.warning(f"Unsupported output type {type(outputs)} for {run_id=}, {parent_run_id=}. Skipping...")
            node_output = dict()
        self.mark_step_end(
            run_id,
            response=response,
            node_output=dumps(
                node_output,
                default=GalileoPromptCallback.json_serializer,
            ),
            **kwargs,
        )

    def on_chain_error(
        self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when chain errors."""

    @staticmethod
    def json_serializer(obj: Any) -> Union[str, Dict[Any, Any]]:
        """
        For serializing objects that cannot be serialized by default with json.dumps.

        Checks for certain methods to convert object to dict.
        """
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, BaseModelV1):
            return obj.dict()
        logger.warning(f"Unable to serialize {type(obj)}, for visualization in Galileo console")
        return str(type(obj))

    def finish(self) -> None:
        rows_to_log: List[NodeRow] = list()
        # Exclude chains that don't have children.
        for root_id in self.root_nodes:
            for node_id in self.root_child_mapping[root_id]:
                row = self.rows.get(node_id)
                if row is None:
                    logger.debug(f"Skipping row {node_id} because its row doesn't exist.")
                # If the node is a non-chain node, or is a parent node with any children, include it.
                elif row.node_type != NodeType.chain or node_id in self.parent_child_mapping.keys():
                    rows_to_log.append(row)
                else:
                    logger.debug(f"Skipping row {node_id} because it is an empty chain.")
        chain_run(
            rows_to_log, self.project_name, self.run_name, self.scorers, run_tags=self.run_tags, config=self.config
        )
