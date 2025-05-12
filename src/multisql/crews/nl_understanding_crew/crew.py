from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class NLUnderstandingCrew():
    """Natural Language Understanding Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def intent_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['intent_analyzer'],
            verbose=True
        )

    @agent
    def schema_explorer(self) -> Agent:
        return Agent(
            config=self.agents_config['schema_explorer'],
            verbose=True
        )

    @task
    def analyze_intent_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_intent'],
        )

    @task
    def identify_schema_elements_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_schema_elements'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NL Understanding crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
