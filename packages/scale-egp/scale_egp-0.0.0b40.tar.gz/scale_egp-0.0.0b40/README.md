<img src="https://static.remotasks.com/uploads/602b25a6e0984c00343d3b26/scale-1.png"/>

# Scale EGP Python Client

**The official Python client for Scale's [Enterprise Generative AI Platform](https://scale.com/generative-ai-platform)**.

Generative AI applications are proliferating in the modern enterprise. However, building these applications can be challenging and expensive, especially when they need to conform to enterprise security and scalability standards. Scale EGP APIs provide the full-stack capabilities enterprises need to rapidly develop and deploy Generative AI applications for custom use cases. These capabilities include loading custom data sources, indexing data into vector stores, running inference, executing agents, and robust evaluation features.

### Install from PyPI:
```shell
pip install scale-egp
```

## End to End RAG + Evaluation Script

### Quickstart

```python
import hashlib
import json
import os
import pickle
import time
from datetime import datetime
from typing import List, Union

import questionary as q

from scale_egp.sdk.client import EGPClient
from scale_egp.sdk.enums import (
    CrossEncoderModelName,
    EmbeddingModelName,
    ExtraInfoSchema,
    TestCaseSchemaType,
    EvaluationType,
)
from scale_egp.sdk.types.chunks import CrossEncoderRankParams, CrossEncoderRankStrategy,

RougeRankStrategy
RougeRankParams
from scale_egp.sdk.types.evaluation_test_case_results import GenerationTestCaseResultData
from scale_egp.sdk.types.evaluation_dataset_test_cases import ExtraInfo
from scale_egp.sdk.types.evaluation_configs import CategoricalChoice, CategoricalQuestion,

StudioEvaluationConfig
from scale_egp.sdk.types.knowledge_base_uploads import S3DataSourceConfig,

CharacterChunkingStrategyConfig
from scale_egp.utils.model_utils import BaseModel


# Helper functions
def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def dump_model(model: Union[BaseModel, List[BaseModel]]):
    if isinstance(model, list):
        return json.dumps([m.dict() for m in model], indent=2, sort_keys=True, default=str)
    return json.dumps(model.dict(), indent=2, sort_keys=True, default=str)


# Not part of our SDK. This is scratch code example of what a user might write as an application.
class MyGenerativeAIApplication:

    def __init__(self, knowledge_base_id: str = None):
        self.knowledge_base_id = knowledge_base_id
        self.name = "Simple Retrieval AI"
        self.description = "AI Chatbot to help analyze 8k documents"
        self.llm_model = "gpt-3.5-turbo"

    def generate(self, input_prompt: str):
        re_ranked_chunks = self.generate_chunks(input_prompt)

        chunk_string = ""
        for index, re_ranked_top_3_chunk in enumerate(re_ranked_chunks):
            chunk_string += f"CHUNK {index + 1}\n"
            chunk_string += "=" * 30 + "\n"
            chunk_string += re_ranked_top_3_chunk.text + "\n"
            chunk_string += "\n"

        rag_prompt = f"{input_prompt}\n\nAdditional information:\n{chunk_string}"
        completion = client.completions().create(model=self.llm_model, prompt=rag_prompt)
        output = completion.completion.text

        extra_info = ExtraInfo(
            info=chunk_string,
            schema_type=ExtraInfoSchema.STRING,
        )
        return output, extra_info

    def generate_chunks(
        self, query: str, initial_recall: int = 10, rouge_recall: int = 5, top_k: int = 3
    ):
        chunks = client.knowledge_bases().query(
            knowledge_base=knowledge_base,
            query=query,
            top_k=initial_recall,
            include_embeddings=False
        )

        sub_re_ranked_chunks = client.chunks().rank(
            query=query,
            relevant_chunks=chunks,
            rank_strategy=RougeRankStrategy(
                params=RougeRankParams(
                    method="rouge2",
                    score="recall",
                )
            ),
            top_k=rouge_recall,
        )

        re_ranked_chunks = client.chunks().rank(
            query=query,
            relevant_chunks=sub_re_ranked_chunks,
            rank_strategy=CrossEncoderRankStrategy(
                params=CrossEncoderRankParams(
                    cross_encoder_model=
                    CrossEncoderModelName.CROSS_ENCODER_MS_MARCO_MINILM_L12_V2.value,
                )
            ),
            top_k=top_k,
        )
        return re_ranked_chunks

    def tags(self):
        return {
            "llm_model": self.llm_model,
            "knowledge_base_id": self.knowledge_base_id,
        }

    @property
    def version(self):
        """
        Returns a hash of the application state that is stable across processes.
        """
        return hashlib.sha256(pickle.dumps(self.tags)).hexdigest()


if __name__ == "__main__":
    api_key = q.text(f"Please enter your EGP API key:", default=os.environ.get("EGP_API_KEY")).ask()
    client = EGPClient(api_key=api_key)

    # Contains public 8ks from amazon, microsoft, apple, morgan stanley
    KNOWLEDGE_BASE_ID = None

    knowledge_base_name = "small_8k_demo"
    embedding_model_name = EmbeddingModelName.OPENAI_TEXT_EMBEDDING_ADA_002
    if KNOWLEDGE_BASE_ID:
        knowledge_base_id = KNOWLEDGE_BASE_ID
    else:
        knowledge_base_id = q.text(
            f"ID of existing knowledge base (Leave blank to create a new one with name "
            f"'{knowledge_base_name}' and embedding model '{embedding_model_name}'):"
        ).ask()

    if knowledge_base_id:
        knowledge_base = client.knowledge_bases().get(id=knowledge_base_id)
    else:
        knowledge_base = client.knowledge_bases().create(
            name=knowledge_base_name,
            embedding_model_name=embedding_model_name,
        )
    print(f"Knowledge base:\n{dump_model(knowledge_base)}")

    print("=" * 50)

    UPLOAD_ID = None
    if UPLOAD_ID:
        upload_id = UPLOAD_ID
    else:
        upload_id = q.text(f"ID of existing upload (Leave blank to create a new one):").ask()

    if upload_id:
        upload = client.knowledge_bases().uploads().get(id=upload_id, knowledge_base=knowledge_base)
    else:
        print("Please enter the following information to create a new upload:")
        s3_bucket = q.text(f"S3 bucket:").ask()
        s3_prefix = q.text(f"S3 prefix:").ask()
        aws_region = q.text(f"AWS region:").ask()
        aws_account_id = q.text(f"AWS account ID:").ask()
        upload = client.knowledge_bases().uploads().create_remote_upload(
            knowledge_base=knowledge_base,
            data_source_config=S3DataSourceConfig(
                s3_bucket=s3_bucket,
                s3_prefix=s3_prefix,
                aws_region=aws_region,
                aws_account_id=aws_account_id,
            ),
            data_source_auth_config=None,
            chunking_strategy_config=CharacterChunkingStrategyConfig(
                separator="\n\n",
                chunk_size=1000,
                chunk_overlap=200,
            ),
        )
    print(f"Knowledge Base Upload:\n{dump_model(upload)}")

    complete = False
    poll_count = 1
    while not complete:
        upload = client.knowledge_bases().uploads().get(
            id=upload.upload_id, knowledge_base=knowledge_base
        )
        complete = upload.status == "Completed"
        print(f"Poll count: {poll_count}")
        print(f"Status: {upload.status}")
        print(f"Status Reason: {upload.status_reason}")
        print(f"Artifact Statuses: {upload.artifacts_status}\n")
        poll_count += 1
        time.sleep(3)

    print("=" * 50)

    print("Artifacts in knowledge base:")
    artifacts = client.knowledge_bases().artifacts().list(knowledge_base=knowledge_base)
    if not artifacts:
        print("No artifacts in knowledge base.")

    for artifact in artifacts:
        print(f"({artifact.artifact_id}) {artifact.artifact_uri}")

    print("=" * 50)

    selected_artifact = artifacts[-1]
    print(f"Chunks in artifact: {selected_artifact.artifact_uri}")
    artifact = client.knowledge_bases().artifacts().get(
        id=artifacts[-1].artifact_id, knowledge_base=knowledge_base
    )
    for index, chunk in enumerate(artifact.chunks):
        print(f"Chunk {index}")
        print("=" * 30)
        print(chunk.text)

    print("=" * 50)

    query = "What new events did Morgan Stanley report in their latest 8k?"
    print(f"Querying knowledge base: {query}")
    chunks = client.knowledge_bases().query(
        knowledge_base=knowledge_base,
        query=query,
        top_k=3,
        include_embeddings=False
    )
    if not chunks:
        print("No chunks returned.")

    for index, chunk in enumerate(chunks):
        print(f"Chunk rank: {index}")
        print("=" * 30)
        print(chunk.text)

    print("=" * 50)

    print("Comparing raw retrieval with cross-encoder/rouge re-ranked retrieval...")
    chunks = client.knowledge_bases().query(
        knowledge_base=knowledge_base,
        query=query,
        top_k=3,
        include_embeddings=False
    )

    print("Original Top 3 Chunks")
    for index, original_top_3_chunk in enumerate(chunks[:3]):
        print(f"CHUNK {index + 1}")
        print("=" * 30)
        print(original_top_3_chunk.text)
        print()

    # Try a larger recall with reranking
    print("Re-ranking chunks with cross-encoder/rouge...")
    gen_ai_app = MyGenerativeAIApplication(knowledge_base_id=knowledge_base.knowledge_base_id)
    re_ranked_chunks = gen_ai_app.generate_chunks(
        query=query, initial_recall=500, rouge_recall=100, top_k=3
    )

    print("\n\n\nRe-ranked Top 3 Chunks")
    for index, re_ranked_top_3_chunk in enumerate(re_ranked_chunks):
        print(f"CHUNK {index + 1}")
        print("=" * 30)
        print(re_ranked_top_3_chunk.text)
        print()

    print("=" * 50)

    EVALUATION_DATASET_ID = None
    evaluation_dataset_name = f"8k Question Dataset {timestamp()}"
    if EVALUATION_DATASET_ID:
        evaluation_dataset_id = EVALUATION_DATASET_ID
    else:
        evaluation_dataset_id = q.text(
            f"ID of existing dataset (Leave blank to create a new one with name "
            f"'{evaluation_dataset_name}'):"
        ).ask()
    if evaluation_dataset_id:
        evaluation_dataset = client.evaluation_datasets().get(id=evaluation_dataset_id)
    else:
        evaluation_dataset = client.evaluation_datasets().create_from_file(
            name=evaluation_dataset_name,
            schema_type=TestCaseSchemaType.GENERATION,
            filepath="data/8k_test_suite.jsonl",
        )
    print(f"Evaluation dataset:\n{dump_model(evaluation_dataset)}")

    # Examine the test cases within the dataset¶
    print("Test cases in evaluation dataset:")
    for test_case in client.evaluation_datasets().test_cases().iter(
        evaluation_dataset=evaluation_dataset
    ):
        print(dump_model(test_case))

    print("=" * 50)

    APPLICATION_SPEC_ID = None
    application_spec_name = f"Simple Retrieval AI {timestamp()}"
    if APPLICATION_SPEC_ID:
        application_spec_id = APPLICATION_SPEC_ID
    else:
        application_spec_id = q.text(
            f"ID of existing application spec (Leave blank to create a new one with name "
            f"'{application_spec_name}'):"
        ).ask()
    if application_spec_id:
        application_spec = client.application_specs().get(id=application_spec_id)
    else:
        application_spec = client.application_specs().create(
            name=application_spec_name,
            description=gen_ai_app.description
        )
    print(f"Application Spec:\n{dump_model(application_spec)}")

    print("=" * 50)

    STUDIO_PROJECT_ID = None
    studio_project_name = f"{timestamp()}"
    if STUDIO_PROJECT_ID:
        studio_project_id = STUDIO_PROJECT_ID
    else:
        studio_project_id = q.text(
            f"ID of existing studio project (Leave blank to create a new one with name "
            f"'{studio_project_name}'):"
        ).ask()
    if studio_project_id:
        studio_project = client.studio_projects().get(id=studio_project_id)
    else:
        studio_project = client.studio_projects().create(
            name=studio_project_name,
            description=f"Annotation project for the {application_spec.name} project",
            studio_api_key=os.environ.get("STUDIO_API_KEY"),
        )
        studio_project_id = studio_project.id
    print(f"Studio project:\n{dump_model(studio_project)}")

    print("=" * 50)

    print("Create and submit an evaluation...")

    evaluation = client.evaluations().create(
        application_spec=application_spec,
        name=f"{application_spec.name} Regression Test - {timestamp()}",
        description=f"Evaluation of the {application_spec.name} project.",
        tags=gen_ai_app.tags(),
        evaluation_config=StudioEvaluationConfig(
            evaluation_type=EvaluationType.STUDIO,
            studio_project_id=studio_project.id,
            questions=[
                # For categorical questions, the value is used as a score for the answer.
                # Higher values are better. This score will be used to track if the AI is improving.
                # The value can be set to None if
                CategoricalQuestion(
                    question_id="based_on_content",
                    title="Was the answer based on the content provided?",
                    choices=[
                        CategoricalChoice(label="No", value=0),
                        CategoricalChoice(label="Yes", value=1),
                    ],
                ),
                CategoricalQuestion(
                    question_id="accurate",
                    title="Was the answer accurate?",
                    choices=[
                        CategoricalChoice(label="No", value=0),
                        CategoricalChoice(label="Yes", value=1),
                    ],
                ),
                CategoricalQuestion(
                    question_id="complete",
                    title="Was the answer complete?",
                    choices=[
                        CategoricalChoice(label="No", value=0),
                        CategoricalChoice(label="Yes", value=1),
                    ],
                ),
                CategoricalQuestion(
                    question_id="recent",
                    title="Was the information recent?",
                    choices=[
                        CategoricalChoice(label="Not Applicable", value="not_applicable"),
                        CategoricalChoice(label="No", value=0),
                        CategoricalChoice(label="Yes", value=1),
                    ],
                ),
                CategoricalQuestion(
                    question_id="core_issue",
                    title="What was the core issue?",
                    choices=[
                        CategoricalChoice(label="No Issue", value="no_issue"),
                        CategoricalChoice(label="User Behavior Issue", value="user_behavior_issue"),
                        CategoricalChoice(
                            label="Unable to Provide Response",
                            value="unable_to_provide_response"
                        ),
                        CategoricalChoice(label="Incomplete Answer", value="incomplete_answer"),
                    ],
                ),
            ]
        ),
    )
    print(f"Evaluation:\n{dump_model(evaluation)}\n")

    print(f"Generating data to evaluate per test case...")
    test_case_results = []
    for test_case in client.evaluation_datasets().test_cases().iter(
        evaluation_dataset=evaluation_dataset
    ):
        output, extra_info = gen_ai_app.generate(input_prompt=test_case.test_case_data.input)
        test_case_result = client.evaluations().test_case_results().create(
            evaluation=evaluation,
            evaluation_dataset=evaluation_dataset,
            test_case=test_case,
            test_case_evaluation_data=GenerationTestCaseResultData(
                generation_output=output,
                generation_extra_info=extra_info,
            ),
        )
        test_case_results.append(test_case_result)
        print(dump_model(test_case_result))

    print(
        f"\nCreated {len(test_case_results)} test case results for review."
        f"Please visit https://dashboard.scale.com/studio/annotate to annotate these tasks."
    )

    print("=" * 50)

    print("Retrieving test case results...")

    fetch_again = True
    while fetch_again:
        print(f"Application State at time of Evaluation:\n{evaluation.tags}\n")

        for test_case_result in test_case_results:
            updated_test_case_result = client.evaluations().test_case_results().get(
                id=test_case_result.id, evaluation=evaluation
            )
            test_case = client.evaluation_datasets().test_cases().get(
                id=test_case_result.test_case_id, evaluation_dataset=evaluation_dataset
            )

            annotation_status = "COMPLETE" if updated_test_case_result.result else "PENDING"
            print(f"Test Case Input: {test_case.test_case_data.input}")
            print(
                f"Test Case Result ({updated_test_case_result.id}): "
                f"{json.dumps(updated_test_case_result.result, indent=2)}"
            )
            print(f"Annotation Status: {annotation_status}")
            print()

        print("To label pending tasks, visit: https://dashboard.scale.com/studio/annotate")
        fetch_again = q.confirm("Fetch again?").ask()
```
