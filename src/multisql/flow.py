from typing import Dict, Any
import time
from crewai.flow.flow import Flow, listen, router, start

from multisql.models.state import NL2SQLState
from multisql.crews.nl_understanding_crew.crew import NLUnderstandingCrew
from multisql.crews.schema_matching_crew.crew import SchemaMatchingCrew
from multisql.crews.sql_generator_crew.crew import SQLGeneratorCrew
from multisql.tools.complexity_analyzer import ComplexityAnalyzer

class NL2SQLFlow(Flow[NL2SQLState]):
    """
    Main flow controlling the entire NL to SQL conversion process
    """
    
    @start()
    def understand_query(self):
        """Starting phase: understand the natural language query"""
        start_time = time.time()
        self.state.execution_path.append("understand_query")
        
        # Use NL Understanding Crew to parse query intent
        nl_understanding_crew = NLUnderstandingCrew()
        result = nl_understanding_crew.crew().kickoff(
            inputs={
                "nl_query": self.state.nl_query,
                "db_schema": self.state.db_schema
            }
        )
        
        # Update state
        self.state.parsed_intent = result.intent
        self.state.tables_involved = result.tables
        
        end_time = time.time()
        self.state.execution_time["understand_query"] = end_time - start_time
        
        return "query_understood"
    
    @listen(event="query_understood")
    def evaluate_complexity(self, _):
        """Evaluate query complexity"""
        start_time = time.time()
        self.state.execution_path.append("evaluate_complexity")
        
        # Use complexity analyzer tool
        analyzer = ComplexityAnalyzer()
        self.state.complexity_score = analyzer.calculate_complexity(
            tables_count=len(self.state.tables_involved),
            joins_needed=self._calculate_joins_needed(),
            intent=self.state.parsed_intent
        )
        
        # Calculate required JOIN operations
        self.state.joins_needed = self._calculate_joins_needed()
        
        end_time = time.time()
        self.state.execution_time["evaluate_complexity"] = end_time - start_time
        
        return "complexity_evaluated"
    
    def _calculate_joins_needed(self):
        """Calculate number of JOIN operations needed"""
        if len(self.state.tables_involved) <= 1:
            return 0
            
        # Based on table relationship graph, calculate minimum JOINs needed
        # Simplified version: tables count - 1 (minimum spanning tree)
        return len(self.state.tables_involved) - 1
    
    @listen(event="complexity_evaluated")
    def make_routing_decision(self, _):
        """Make routing decision based on complexity and table relationships"""
        start_time = time.time()
        self.state.execution_path.append("make_routing_decision")
        
        # Decision logic: enable schema matching when complexity is above threshold and multiple joins required
        complex_query = self.state.complexity_score > 6.5  # threshold can be adjusted
        multi_table = self.state.joins_needed >= 2
        complex_intent = self.state.parsed_intent.get("aggregation") or self.state.parsed_intent.get("nesting")
        
        if (complex_query and multi_table) or complex_intent:
            self.state.needs_schema_matching = True
            route = "route_to_enhanced"
        else:
            self.state.needs_schema_matching = False
            route = "route_to_standard"
            
        end_time = time.time()
        self.state.execution_time["make_routing_decision"] = end_time - start_time
        
        return route
    
    @router(router_function=lambda self, state, route: route)
    def route_processing(self, route):
        """Route to appropriate processing flow"""
        self.state.execution_path.append(f"routed_to_{route}")
        return route
    
    @listen(event="route_to_standard")
    def standard_processing(self, _):
        """Standard processing flow (without schema matching)"""
        start_time = time.time()
        self.state.execution_path.append("standard_processing")
        
        # Directly use SQL generator
        generator_crew = SQLGeneratorCrew()
        result = generator_crew.crew().kickoff(
            inputs={
                "nl_query": self.state.nl_query,
                "intent": self.state.parsed_intent,
                "db_schema": self.state.db_schema,
                "tables_involved": self.state.tables_involved
            }
        )
        
        self.state.generated_sql = result.sql
        
        end_time = time.time()
        self.state.execution_time["standard_processing"] = end_time - start_time
        
        return "processing_complete"
    
    @listen(event="route_to_enhanced")
    def enhanced_processing(self, _):
        """Enhanced processing flow (using schema matching)"""
        start_time = time.time()
        self.state.execution_path.append("enhanced_processing")
        
        # Step 1: Use Schema Matching Crew
        matcher_start = time.time()
        matcher_crew = SchemaMatchingCrew()
        match_result = matcher_crew.crew().kickoff(
            inputs={
                "nl_query": self.state.nl_query,
                "intent": self.state.parsed_intent,
                "db_schema": self.state.db_schema,
                "tables_involved": self.state.tables_involved
            }
        )
        
        self.state.schema_matching_result = match_result.matches
        matcher_end = time.time()
        self.state.execution_time["schema_matching"] = matcher_end - matcher_start
        
        # Step 2: Use SQL Generator with schema matching results
        generator_start = time.time()
        generator_crew = SQLGeneratorCrew()
        gen_result = generator_crew.crew().kickoff(
            inputs={
                "nl_query": self.state.nl_query,
                "intent": self.state.parsed_intent,
                "db_schema": self.state.db_schema,
                "tables_involved": self.state.tables_involved,
                "schema_matching": self.state.schema_matching_result
            }
        )
        
        self.state.generated_sql = gen_result.sql
        generator_end = time.time()
        self.state.execution_time["sql_generation_enhanced"] = generator_end - generator_start
        
        end_time = time.time()
        self.state.execution_time["enhanced_processing"] = end_time - start_time
        
        return "processing_complete"
    
    @listen(event="processing_complete")
    def validate_sql(self, _):
        """Validate the generated SQL"""
        start_time = time.time()
        self.state.execution_path.append("validate_sql")
        
        # SQL validation logic can be implemented here
        # Can check for syntax errors, validate the generated SQL conforms to database dialect, etc.
        
        end_time = time.time()
        self.state.execution_time["validate_sql"] = end_time - start_time
        
        return self._prepare_final_output()
    
    def _prepare_final_output(self):
        """Prepare final output"""
        total_time = sum(self.state.execution_time.values())
        
        result = {
            "nl_query": self.state.nl_query,
            "sql": self.state.generated_sql,
            "complexity_score": self.state.complexity_score,
            "schema_matching_used": self.state.needs_schema_matching,
            "execution_path": self.state.execution_path,
            "execution_time": {
                "total": total_time,
                **self.state.execution_time
            }
        }
        
        return result
