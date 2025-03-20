import re
from py2neo import Graph, Node, Relationship
import spacy
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Load SpaCy model for better text analysis
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None
    logger.warning("SpaCy model not found. Using basic risk analysis.")

# Risk terms with weighted scores
RISK_TERMS = {
    "high": {
        "penalty": 10, "breach": 10, "termination": 8, "indemnity": 9,
        "liability": 8, "lawsuit": 10, "dispute": 7, "litigation": 9,
        "damages": 8, "waive": 7
    },
    "medium": {
        "confidentiality": 5, "late payment": 5, "disclosure": 4,
        "approval": 3, "extension": 3, "amendment": 4, "compliance": 5,
        "third party": 4, "representation": 3
    },
    "low": {
        "notice": 2, "delivery": 1, "payment terms": 2, "schedule": 1
    }
}

def calculate_risk_score(clauses):
    score = 0
    identified_risks = []

    for clause in clauses:
        if not clause or len(clause) < 5:
            continue

        clause_lower = clause.lower()
        clause_score = 0
        clause_risks = []

        for category, terms in RISK_TERMS.items():
            for term, weight in terms.items():
                if term in clause_lower:
                    clause_score += weight
                    clause_risks.append({"term": term, "category": category, "weight": weight})

        if clause_score > 0:
            score += clause_score
            identified_risks.append({"text": clause[:100] + "..." if len(clause) > 100 else clause,
                                     "risks": clause_risks, "score": clause_score})

    return score, identified_risks

def store_risk_in_neo4j(graph, document_id, risk_score, document_content, risk_details):
    try:
        doc_node = Node("Document", id=document_id, risk_score=risk_score)
        tx = graph.begin()
        tx.create(doc_node)

        for risk in risk_details:
            risk_node = Node("Risk", text=risk["text"], score=risk["score"])
            tx.create(risk_node)
            tx.create(Relationship(doc_node, "HAS_RISK", risk_node))

        tx.commit()
        logger.info(f"Stored risk score {risk_score} in Neo4j for {document_id}")
    except Exception as e:
        logger.error(f"Failed to store in Neo4j: {e}")
