import streamlit as st
from transformers import pipeline
from Bio import Entrez

# Set your email for NCBI Entrez API
Entrez.email = "your_email@example.com"  # Replace with your valid email

# Initialize the Hugging Face model for prompt evaluation (e.g., FLAN-T5)
flan_pipeline = pipeline("text2text-generation", model="google/flan-t5-small", device=0)  # Use GPU if available


def search_pubmed(query):
    """
    Search PubMed using the query and retrieve paper IDs.
    """
    handle = Entrez.esearch(db="pubmed", term=query, retmode="xml", retmax=100000)  # Increase retmax for large results
    record = Entrez.read(handle)
    total_papers = int(record["Count"])
    paper_ids = record.get("IdList", [])
    return paper_ids, total_papers


def fetch_paper_details(paper_ids):
    """
    Fetch details of papers from PubMed using the paper IDs.
    """
    handle_details = Entrez.efetch(db="pubmed", id=",".join(paper_ids), retmode="xml", rettype="abstract")
    papers = Entrez.read(handle_details)
    return papers


def apply_inclusion_exclusion(paper, query, mandatory_keywords):
    """
    Apply inclusion and exclusion criteria based on mandatory keywords and relevance evaluation.
    """
    title = paper["MedlineCitation"]["Article"]["ArticleTitle"]
    abstract_data = paper["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [])
    abstract = " ".join(abstract_data) if isinstance(abstract_data, list) else abstract_data

    # Combine title and abstract and check for mandatory keywords
    full_text = (title + " " + abstract).lower()
    if not all(keyword in full_text for keyword in mandatory_keywords):
        return False

    # Format the prompt for FLAN-T5 to evaluate relevance
    prompt = f"You are a PubMed research expert. The user's query is: '{query}'.\n\nTitle: {title}\nAbstract: {abstract}\n\nDoes this paper directly address all aspects of the query '{query}'? Respond with 'Relevant' if yes, or 'Not Relevant' if no."
    response = flan_pipeline(prompt, max_length=50, num_return_sequences=1)
    decision = response[0]["generated_text"].strip()
    return "Relevant" in decision


def filter_relevant_papers(papers, query, mandatory_keywords):
    """
    Filter papers based on inclusion and exclusion criteria.
    """
    relevant_papers = []
    for paper in papers.get("PubmedArticle", []):
        pubmed_id = paper["MedlineCitation"]["PMID"]
        if apply_inclusion_exclusion(paper, query, mandatory_keywords):
            title = paper["MedlineCitation"]["Article"]["ArticleTitle"]
            paper_link = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"
            relevant_papers.append({"title": title, "link": paper_link})
    return relevant_papers


# Streamlit Application
def main():
    st.title("PubMed Research Paper Finder")
    st.write(
        "This application allows you to search PubMed for research papers, apply inclusion/exclusion criteria, "
        "and display relevant results."
    )

    # Step 1: Get user input for the PubMed search query
    query = st.text_input("Enter your PubMed search query (e.g., 'AI and mental health')", "")
    mandatory_keywords = st.text_input(
        "Enter mandatory keywords (comma-separated) to filter papers (e.g., 'AI, mental health')", ""
    )

    if st.button("Search PubMed"):
        if not query.strip():
            st.warning("Please enter a search query.")
            return

        # Convert mandatory keywords to a list
        mandatory_keywords_list = [kw.strip().lower() for kw in mandatory_keywords.split(",") if kw.strip()]

        # Step 2: Search PubMed
        with st.spinner("Searching PubMed..."):
            paper_ids, total_papers = search_pubmed(query)

        if not paper_ids:
            st.error(f"No papers found for the query '{query}'.")
            return

        st.success(f"Total papers retrieved: {total_papers}")

        # Step 3: Fetch paper details
        with st.spinner("Fetching paper details..."):
            papers = fetch_paper_details(paper_ids)

        # Step 4: Filter relevant papers
        with st.spinner("Filtering relevant papers..."):
            relevant_papers = filter_relevant_papers(papers, query, mandatory_keywords_list)

        st.success(f"Total relevant papers found: {len(relevant_papers)}")

        # Step 5: Display results
        if relevant_papers:
            for idx, paper in enumerate(relevant_papers):
                st.subheader(f"Paper #{idx + 1}")
                st.write(f"**Title:** {paper['title']}")
                st.write(f"[Read on PubMed]({paper['link']})")
                st.write("---")
        else:
            st.warning("No relevant papers found. Try adjusting your search query or keywords.")


if __name__ == "__main__":
    main()
