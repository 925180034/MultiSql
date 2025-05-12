from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class SQLGeneratorCrew():
    """SQL Generator Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def sql_composer(self) -> Agent:
        return Agent(
            config=self.agents_config['sql_composer'],
            verbose=True
        )

    @agent
    def sql_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config['sql_optimizer'],
            verbose=True
        )

    @task
    def compose_sql_task(self) -> Task:
        return Task(
            config=self.tasks_config['compose_sql'],
        )

    @task
    def optimize_sql_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_sql'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SQL Generator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
