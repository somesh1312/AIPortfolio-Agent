from backend.rag_utils import load_vectorstore

vs = load_vectorstore()
retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 8})

query = "certifications"
docs = retriever.invoke(query)

print("🔎 Retrieved Docs:")
for d in docs:
    print("Source:", d.metadata.get("source"))
    print(d.page_content[:200], "\n")