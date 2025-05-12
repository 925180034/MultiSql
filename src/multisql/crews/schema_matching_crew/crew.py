from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class SchemaMatchingCrew():
    """Schema Matching Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def relationship_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['relationship_analyst'],
            verbose=True
        )

    @agent
    def semantic_matcher(self) -> Agent:
        return Agent(
            config=self.agents_config['semantic_matcher'],
            verbose=True
        )

    @task
    def analyze_relationships_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_relationships'],
        )

    @task
    def perform_semantic_matching_task(self) -> Task:
        return Task(
            config=self.tasks_config['perform_semantic_matching'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Schema Matching crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
