import json
import os
from datetime import datetime

class PerformanceTracker:
    """Track and record query processing performance"""
    
    def __init__(self, log_file="performance_logs.jsonl"):
        self.log_file = log_file
        
    def log_performance(self, state, execution_success=None, execution_time=None):
        """Log query processing performance"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "nl_query": state.nl_query,
            "complexity_score": state.complexity_score,
            "tables_involved": state.tables_involved,
            "joins_needed": state.joins_needed,
            "schema_matching_used": state.needs_schema_matching,
            "execution_path": state.execution_path,
            "execution_time": execution_time or state.execution_time,
            "generated_sql": state.generated_sql
        }
        
        if execution_success is not None:
            log_entry["execution_success"] = execution_success
            
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def analyze_performance_trends(self):
        """Analyze performance trends, optimize decision model"""
        if not os.path.exists(self.log_file):
            return None
            
        # Read logs
        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                logs.append(json.loads(line))
                
        # Analyze schema matching effect
        schema_matching_impact = {}
        complexity_thresholds = {}
        
        # Group by complexity
        for log in logs:
            if "execution_success" not in log:
                continue
                
            complexity_bin = round(log["complexity_score"])
            schema_used = log["schema_matching_used"]
            success = log["execution_success"]
            
            if complexity_bin not in schema_matching_impact:
                schema_matching_impact[complexity_bin] = {
                    "with_schema": {"count": 0, "success": 0},
                    "without_schema": {"count": 0, "success": 0}
                }
                
            category = "with_schema" if schema_used else "without_schema"
            schema_matching_impact[complexity_bin][category]["count"] += 1
            if success:
                schema_matching_impact[complexity_bin][category]["success"] += 1
        
        # Calculate success rates, determine best complexity threshold
        for complexity, data in schema_matching_impact.items():
            with_schema = data["with_schema"]
            without_schema = data["without_schema"]
            
            with_schema_rate = with_schema["success"] / with_schema["count"] if with_schema["count"] > 0 else 0
            without_schema_rate = without_schema["success"] / without_schema["count"] if without_schema["count"] > 0 else 0
            
            # If schema matching success rate is higher, update threshold
            if with_schema_rate > without_schema_rate:
                complexity_thresholds[complexity] = True
            else:
                complexity_thresholds[complexity] = False
        
        # Return analysis results
        return {
            "schema_matching_impact": schema_matching_impact,
            "recommended_thresholds": complexity_thresholds,
            "overall_success_rate": sum(log["execution_success"] for log in logs if "execution_success" in log) / len([log for log in logs if "execution_success" in log]) if logs else 0
        }
