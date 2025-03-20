from utils.pdf_handler import extract_text_from_pdf
from utils.export_handler import export_to_pdf, export_to_text
from utils.risk_scoring import calculate_risk_score, store_risk_in_neo4j
from models.mistral import mistral_summarize
from models.deepseek import deepseek_extract
from utils.load_config import load_config
from py2neo import Graph
import os
import logging
import argparse

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_document(pdf_path, config, output_formats=None):
    """Process a single legal document with comprehensive analysis."""
    try:
        file_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = config['export']['output_dir']
        
        logger.info(f"Extracting text from {pdf_path}")
        extraction_method = config['pdf']['extraction_engine']
        text = extract_text_from_pdf(pdf_path, method=extraction_method)
        
        if not text:
            logger.error(f"Failed to extract text from {pdf_path}")
            return False
            
        clauses = [p for p in text.split('\n\n') if p.strip()]
        
        logger.info("Generating summary with Mistral")
        summary = mistral_summarize(text)
        
        logger.info("Extracting insights with DeepSeek")
        insights = deepseek_extract(text)
        
        full_analysis = f"# Summary\n\n{summary}\n\n# Key Insights\n\n{insights}"
        
        # Unpacking the risk score and risk details correctly
        risk_score, risk_details = calculate_risk_score(clauses)  
        risk_level = "Low" if risk_score < 20 else "Medium" if risk_score < 50 else "High"
        logger.info(f"Risk assessment: {risk_score} points ({risk_level} risk)")
        
        if not output_formats:
            output_formats = config['pdf']['export_formats']
            
        if 'pdf' in output_formats:
            export_to_pdf(full_analysis, risk_score, file_name, output_dir)
        if 'txt' in output_formats:
            export_to_text(full_analysis, risk_score, file_name, output_dir)
        
        try:
            neo4j_uri = config['neo4j']['uri']
            neo4j_user = config['neo4j']['user']
            neo4j_password = config['neo4j']['password']
            
            graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
            # Passing risk details to store in Neo4j
            store_risk_in_neo4j(graph, file_name, risk_score, full_analysis, risk_details)
            logger.info(f"Data stored in Neo4j for {file_name}")
        except Exception as e:
            logger.error(f"Neo4j storage failed: {e}")
        
        logger.info(f"✅ Analysis completed successfully for {file_name}!")
        return True
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Legal Document Analysis')
    parser.add_argument('--file', '-f', help='Path to PDF file')
    parser.add_argument('--dir', '-d', help='Directory containing PDF files')
    parser.add_argument('--formats', choices=['pdf', 'txt', 'json'], nargs='+', help='Export formats')
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
    
    os.makedirs(config['export']['output_dir'], exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if args.file:
        process_document(args.file, config, args.formats)
    elif args.dir:
        successful = 0
        failed = 0
        for filename in os.listdir(args.dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(args.dir, filename)
                result = process_document(pdf_path, config, args.formats)
                if result:
                    successful += 1
                else:
                    failed += 1
        logger.info(f"Batch processing complete: {successful} successful, {failed} failed")
    else:
        pdf_path = "./data/sample1.pdf"
        if os.path.exists(pdf_path):
            process_document(pdf_path, config)
        else:
            logger.error(f"Default test file {pdf_path} not found")
            logger.info("Use --file or --dir arguments to specify inputs")

if __name__ == '__main__':
    main()
