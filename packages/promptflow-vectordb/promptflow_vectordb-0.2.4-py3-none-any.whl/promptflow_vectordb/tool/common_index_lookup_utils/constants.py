class IndexTypes(str):
    AzureCognitiveSearch = 'Azure AI Search'
    FAISS = 'FAISS'
    Pinecone = 'Pinecone'
    MLIndexAsset = 'Registered Index'
    MLIndexPath = 'MLIndex file from path'


class EmbeddingTypes(str):
    NoEmbedding = 'None'
    AzureOpenAI = 'Azure OpenAI'
    OpenAI = 'OpenAI'
    HuggingFace = 'Hugging Face'


class QueryTypes(str):
    Simple = 'Keyword'
    Semantic = 'Semantic'
    Vector = 'Vector'
    VectorSimpleHybrid = 'Hybrid (vector + keyword)'
    VectorSemanticHybrid = 'Hybrid + semantic'
