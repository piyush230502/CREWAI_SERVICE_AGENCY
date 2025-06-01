from typing import List, Literal, Dict, Optional, Type
from pydantic import Field, BaseModel
from crewai.tools import BaseTool
import litellm
litellm.set_verbose = True




# Define Pydantic models for structured tool outputs
class ProjectAnalysisOutput(BaseModel):
    name: str = Field(description="Name of the project")
    analyzed_project_type: str = Field(description="Type of project") # Renamed from 'type'
    complexity: str = Field(description="Assessed complexity of the project")
    timeline: str = Field(description="Estimated timeline for the project")
    budget_feasibility: str = Field(description="Assessment of budget feasibility")
    requirements: List[str] = Field(description="Key requirements identified")
    class Config:
        arbitrary_types_allowed = True  # This fixes the issue

class TechnicalSpecificationOutput(BaseModel):
    project_name: str = Field(description="Name of the project")
    architecture: str = Field(description="Proposed architecture type")
    technologies: List[str] = Field(description="List of main technologies and frameworks")
    scalability: str = Field(description="Scalability needs")


class AnalyzeProjectRequirements(BaseTool):
    name: str = "AnalyzeProjectRequirementsTool"
    description: str = "Analyzes project requirements and feasibility, outputting a structured analysis."

    class ArgsSchema(BaseModel):
        project_name: str = Field(..., description="Name of the project")
        project_description: str = Field(..., description="Project description and goals")
        project_type: Literal["Web Application", "Mobile App", "API Development",
                         "Data Analytics", "AI/ML Solution", "Other"] = Field(...,
                         description="Type of project")
        budget_range: Literal["$10k-$25k", "$25k-$50k", "$50k-$100k", "$100k+"] = Field(...,
                         description="Budget range for the project")

    args_schema: Type[BaseModel] = ArgsSchema

    def _run(self, project_name: str, project_description: str, project_type: str, budget_range: str) -> ProjectAnalysisOutput:
        """Analyzes project and returns structured analysis."""
        # Simplified analysis logic, focusing on returning the structure
        # In a real scenario, an LLM might generate these values or more complex logic would exist.

        analysis = {
            "name": project_name,
            "analyzed_project_type": project_type,
            "complexity": "high", # Example value
            "timeline": "6 months", # Example value
            "budget_feasibility": "within range", # Example value
            "requirements": ["Scalable architecture", "Security", "API integration"] # Example values
        }
        return ProjectAnalysisOutput(**analysis)

class CreateTechnicalSpecification(BaseTool):
    name: str = "CreateTechnicalSpecificationTool"
    description: str = "Creates technical specifications based on project analysis, outputting a structured specification."

    class ArgsSchema(BaseModel):
        project_analysis_json: str = Field(..., description="JSON string of the project analysis output from AnalyzeProjectRequirementsTool")
        architecture_type: Literal["monolithic", "microservices", "serverless", "hybrid"] = Field(
            ...,
            description="Proposed architecture type based on the analysis"
        )
        core_technologies: str = Field(
            ...,
            description="Comma-separated list of main technologies and frameworks based on the analysis"
        )
        scalability_requirements: Literal["high", "medium", "low"] = Field(
            ...,
            description="Scalability needs based on the analysis"
        )

    args_schema: Type[BaseModel] = ArgsSchema

    def _run(self, project_analysis_json: str, architecture_type: str, core_technologies: str, scalability_requirements: str) -> TechnicalSpecificationOutput:
        """Creates technical specification based on analysis dictionary."""
        try:
            project_analysis_data = ProjectAnalysisOutput.model_validate_json(project_analysis_json)
        except Exception as e:
            raise ValueError(f"Invalid project_analysis_json: {e}. It must be a valid JSON of ProjectAnalysisOutput.")

        spec = {
            "project_name": project_analysis_data.name,
            "architecture": architecture_type,
            "technologies": core_technologies.split(","), # Assuming LLM provides comma-separated
            "scalability": scalability_requirements
        }
        return TechnicalSpecificationOutput(**spec)