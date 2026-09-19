from pydantic import BaseModel, Field


class AssistantResponse(BaseModel):
    answer: str = Field(
        description="A concise and accurate answer to the user's question."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )


class RAGResponse(BaseModel):
    answer: str = Field(
        description="Answer grounded only in the retrieved context."
    )

    source_ids: list[str] = Field(
        description="IDs of the retrieved sources used to support the answer."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in whether the retrieved context supports the answer."
    )
    
class ModelResponse(BaseModel):
    provider: str = Field(
        description="Provider used to generate the response."
    )

    model: str = Field(
        description="Model used to generate the response."
    )

    answer: str = Field(
        description="Generated answer."
    )