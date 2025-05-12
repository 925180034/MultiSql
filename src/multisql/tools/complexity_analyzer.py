class ComplexityAnalyzer:
    """Query complexity analysis tool"""
    
    def calculate_complexity(self, tables_count, joins_needed, intent):
        """
        Calculate the complexity score of a query
        
        Parameters:
            tables_count: Number of tables involved
            joins_needed: Number of JOIN operations needed
            intent: Parsed query intent
            
        Returns:
            Complexity score (0-10)
        """
        # Base score
        base_score = 0
        
        # Table factor
        table_factor = min(tables_count * 1.5, 5)
        
        # JOIN complexity factor
        join_factor = min(joins_needed * 2, 5)
        
        # Query operation complexity factor
        operation_factor = 0
        
        # Check various complex operations
        if intent.get("aggregation"):
            operation_factor += 1
        if intent.get("grouping"):
            operation_factor += 1
        if intent.get("nesting"):
            operation_factor += 2.5
        if intent.get("sorting"):
            operation_factor += 0.5
        if intent.get("distinct"):
            operation_factor += 0.5
            
        # Calculate total score
        total_score = base_score + table_factor + join_factor + min(operation_factor, 5)
        
        # Ensure score is in 0-10 range
        return min(max(total_score, 0), 10)
