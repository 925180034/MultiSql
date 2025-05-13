#!/usr/bin/env python
import sys
import warnings
import argparse
from datetime import datetime

from multisql.crew import Multisql
from multisql.flow import NL2SQLFlow
from multisql.models.state import NL2SQLState, DatabaseSchema
from multisql.tools.schema_manager import SchemaManager
from multisql.tools.performance_tracker import PerformanceTracker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file supports both the original crew and the NL2SQL flow

def run():
    """
    Run the crew or NL2SQL flow.
    """
    # Check if the --nl2sql flag is present
    if len(sys.argv) > 1 and "--nl2sql" in sys.argv:
        sys.argv.remove("--nl2sql")  # Remove the flag
        run_nl2sql()
    else:
        run_original_crew()

def run_original_crew(topic="AI LLMs"):
    """Run the original multisql crew."""
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year)
    }
    
    try:
        Multisql().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_nl2sql():
    """Run the NL2SQL flow."""
    parser = argparse.ArgumentParser(description="Natural Language to SQL Conversion System")
    parser.add_argument("--query", type=str, help="Natural language query")
    parser.add_argument("--db-id", type=str, help="Database ID")
    parser.add_argument("--db-dir", type=str, default="./spider/database", help="Database directory")
    parser.add_argument("--schema-cache", type=str, default="./schema_cache.json", help="Schema cache file")
    
    args = parser.parse_args()
    
    # If no query provided, use default
    if not args.query:
        query = "List all employees who earn more than 50000"
        db_id = "company_db"
        print(f"Using default query: '{query}'")
    else:
        query = args.query
        db_id = args.db_id or "default_db"
    
    try:
        # Schema manager
        schema_manager = SchemaManager(db_path=args.db_dir, schema_cache_path=args.schema_cache)
        
        # Get database schema - simplified for demo
        # In production, you would use schema_manager.get_database_schema(db_id)
        db_schema = {
            "db_id": db_id,
            "tables": [
                {
                    "name": "employees",
                    "columns": [
                        {"name": "id", "type": "int", "table": "employees"},
                        {"name": "name", "type": "text", "table": "employees"},
                        {"name": "salary", "type": "int", "table": "employees"}
                    ]
                }
            ]
        }
        
        # Initialize state
        state = NL2SQLState(
            nl_query=query,
            db_schema=DatabaseSchema(**db_schema)
        )
        
        # Create and run flow
        flow = NL2SQLFlow(state=state)
        result = flow.kickoff()
        
        # Display results
        print("\n= Processing Results =")
        print(f"Natural Language Query: {query}")
        print(f"Generated SQL: {result['sql']}")
        print(f"Complexity Score: {result['complexity_score']:.2f}")
        print(f"Schema Matching Used: {'Yes' if result['schema_matching_used'] else 'No'}")
        print(f"Execution Path: {', '.join(result['execution_path'])}")
        
        # Record performance
        tracker = PerformanceTracker()
        tracker.log_performance(state)
    except Exception as e:
        raise Exception(f"An error occurred while running the NL2SQL flow: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Multisql().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Multisql().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Multisql().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
    
def main():
    # Create the main parser
    main_parser = argparse.ArgumentParser(description="MultiSQL - NL to SQL translation system")
    subparsers = main_parser.add_subparsers(dest="command", help="Sub-commands")
    
    # Original crew parser
    crew_parser = subparsers.add_parser("crew", help="Run the original multisql crew")
    crew_parser.add_argument("--topic", default="AI LLMs", help="Research topic")
    
    # NL2SQL parser
    nl2sql_parser = subparsers.add_parser("nl2sql", help="Run the NL to SQL translation flow")
    nl2sql_parser.add_argument("--query", type=str, help="Natural language query")
    nl2sql_parser.add_argument("--db-id", type=str, help="Database ID")
    nl2sql_parser.add_argument("--db-dir", type=str, default="./spider/database", help="Database directory")
    nl2sql_parser.add_argument("--schema-cache", type=str, default="./schema_cache.json", help="Schema cache file")
    
    # Train parser
    train_parser = subparsers.add_parser("train", help="Train the crew")
    train_parser.add_argument("iterations", type=int, help="Number of iterations")
    train_parser.add_argument("filename", help="Output filename")
    
    # Parse arguments
    args = main_parser.parse_args()
    
    # Execute appropriate command
    if args.command == "crew":
        run_original_crew(args.topic)
    elif args.command == "nl2sql":
        run_nl2sql(args)
    elif args.command == "train":
        train_crew(args.iterations, args.filename)
    else:
        main_parser.print_help()

if __name__ == "__main__":
    run()