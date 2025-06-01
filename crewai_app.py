from typing import List, Literal, Dict, Optional, Type
import os # Added for environment variables
import uuid
import litellm
litellm.set_verbose = True

# CrewAI Imports
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_groq import ChatGroq # Changed from langchain_openai to langchain_groq

from pydantic import Field, BaseModel
import streamlit as st

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

def init_session_state() -> None:
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None

def main() -> None:
    st.set_page_config(page_title="AI Services Agency", layout="wide")
    init_session_state()

    st.title("🚀 AI Services Agency (Groq Edition)")

    # API Configuration
    with st.sidebar:
        st.header("🔑 API Configuration")
        groq_api_key = st.text_input( # Changed variable name and label
            "Groq API Key",
            type="password",
            help="Enter your Groq API key to continue"
        )

        if groq_api_key:
            st.session_state.api_key = groq_api_key # Store Groq key
            st.success("API Key accepted!")
        else:
            st.warning("⚠️ Please enter your Groq API Key to proceed")
            st.markdown("Get your API key from [Groq Console](https://console.groq.com/keys)")
            return

    # Project Input Form
    with st.form("project_form"):
        st.subheader("Project Details")

        project_name = st.text_input("Project Name")
        project_description = st.text_area(
            "Project Description",
            help="Describe the project, its goals, and any specific requirements"
        )

        col1, col2 = st.columns(2)
        with col1:
            project_type = st.selectbox(
                "Project Type",
                ["Web Application", "Mobile App", "API Development",
                 "Data Analytics", "AI/ML Solution", "Other"]
            )
            timeline = st.selectbox(
                "Expected Timeline",
                ["1-2 months", "3-4 months", "5-6 months", "6+ months"]
            )

        with col2:
            budget_range = st.selectbox(
                "Budget Range",
                ["$10k-$25k", "$25k-$50k", "$50k-$100k", "$100k+"]
            )
            priority = st.selectbox(
                "Project Priority",
                ["High", "Medium", "Low"]
            )

        tech_requirements = st.text_area(
            "Technical Requirements (optional)",
            help="Any specific technical requirements or preferences"
        )

        special_considerations = st.text_area(
            "Special Considerations (optional)",
            help="Any additional information or special requirements"
        )

        submitted = st.form_submit_button("Analyze Project")

        if submitted and project_name and project_description:
            try:
                # Set Groq API key as environment variable for CrewAI/Langchain
                os.environ["GROQ_API_KEY"] = st.session_state.api_key

                # Define a default Groq model
                default_groq_model = "groq/gemma2-9b-it" # Or "llama3-70b-8192", "gemma-7b-it" etc.

                # Define LLM configurations for agents
                ceo_llm = ChatGroq(temperature=0.7, groq_api_key=st.session_state.api_key, model_name=default_groq_model)
                cto_llm = ChatGroq(temperature=0.5, groq_api_key=st.session_state.api_key, model_name=default_groq_model)
                pm_llm = ChatGroq(temperature=0.4, groq_api_key=st.session_state.api_key, model_name=default_groq_model)
                dev_llm = ChatGroq(temperature=0.3, groq_api_key=st.session_state.api_key, model_name=default_groq_model)
                client_llm = ChatGroq(temperature=0.6, groq_api_key=st.session_state.api_key, model_name=default_groq_model)

                # Instantiate tools
                analyze_tool = AnalyzeProjectRequirements()
                spec_tool = CreateTechnicalSpecification()

                # Create agents
                ceo = Agent(
                    role="Project Director (CEO)",
                    goal=f"""Analyze the provided project details (name: {project_name}, description: {project_description}, type: {project_type}, budget: {budget_range}) using the AnalyzeProjectRequirementsTool.
                    Your final output must be the structured project analysis data as per the ProjectAnalysisOutput model.
                    Provide a brief summary of your strategic assessment based on this analysis.""",
                    backstory="You are a seasoned CEO with extensive experience in evaluating project feasibility and strategic alignment. You are meticulous and data-driven.",
                    tools=[analyze_tool],
                    llm=ceo_llm,
                    verbose=True,
                    allow_delegation=False
                )

                cto = Agent(
                    role="Technical Architect (CTO)",
                    goal="""Based on the project analysis provided by the CEO, create a detailed technical specification using the CreateTechnicalSpecificationTool.
                    You will receive the project analysis as a JSON string. Use this to determine the architecture_type, core_technologies, and scalability_requirements.
                    Your final output must be the structured technical specification data as per the TechnicalSpecificationOutput model.
                    Provide a brief summary of your technical recommendations.""",
                    backstory="You are a highly experienced Technical Architect with a deep understanding of various system architectures, technologies, and scalability patterns. You translate project needs into robust technical plans.",
                    tools=[spec_tool],
                    llm=cto_llm,
                    verbose=True,
                    allow_delegation=False
                )

                product_manager = Agent(
                    role="Product Manager",
                    goal="""Based on the project information, CEO's analysis, and CTO's technical specification, develop a high-level product roadmap.
                    Define potential core product features and outline a phased approach if applicable.
                    Focus on product-market fit and initial go-to-market considerations.""",
                    backstory="You are an experienced Product Manager skilled in defining product vision, strategy, and roadmaps, ensuring alignment with business goals and market needs.",
                    llm=pm_llm,
                    verbose=True
                )

                developer = Agent(
                    role="Lead Developer",
                    goal="""Based on the project information, CEO's analysis, CTO's technical specification, and Product Manager's roadmap, provide an initial technical implementation plan.
                    Outline key development phases, suggest a core tech stack (complementing CTO's choices), identify potential technical challenges, and give a rough effort estimation breakdown.
                    Consider cloud service costs if applicable.""",
                    backstory="You are a Senior Full-Stack Developer with broad experience in implementing complex software projects. You are pragmatic and skilled in estimation and risk assessment.",
                    llm=dev_llm,
                    verbose=True
                )

                client_manager = Agent(
                    role="Client Success Manager",
                    goal="""Based on all available project information (initial details, CEO analysis, CTO spec, PM roadmap, Dev plan), outline a client engagement and success strategy.
                    Focus on communication, expectation management, feedback loops, and key milestones for client review.
                    Suggest a preliminary go-to-market and customer acquisition outline from a client success perspective.""",
                    backstory="You are an experienced Client Success Manager dedicated to ensuring client satisfaction and successful project delivery through proactive communication and strategic guidance.",
                    llm=client_llm,
                    verbose=True
                )

                # Prepare project info
                project_info = {
                    "name": project_name,
                    "description": project_description,
                    "type": project_type,
                    "timeline": timeline,
                    "budget": budget_range,
                    "priority": priority,
                    "technical_requirements": tech_requirements,
                    "special_considerations": special_considerations
                }

                st.session_state.messages.append({"role": "user", "content": f"New Project Submitted: {project_name}\nDetails: {str(project_info)}"})

                # Define Tasks
                ceo_task = Task(
                    description=f"""Analyze the following project and produce a structured analysis:
                    Project Name: {project_name}
                    Project Description: {project_description}
                    Project Type: {project_type}
                    Budget Range: {budget_range}
                    Your output should be the structured ProjectAnalysisOutput and a brief strategic summary.""",
                    expected_output="A ProjectAnalysisOutput object containing the detailed analysis, and a brief textual summary of strategic insights.",
                    agent=ceo,
                    output_pydantic=ProjectAnalysisOutput # CrewAI will expect the tool to return this Pydantic model
                )

                cto_task = Task(
                    description=f"""Given the project analysis from the CEO (available as '{{{{@ceo_task}}}}'), create a technical specification.
                    You must convert the CEO's analysis (which will be a ProjectAnalysisOutput object from the context) into a JSON string to pass to the 'project_analysis_json' parameter of your CreateTechnicalSpecificationTool.
                    Choose appropriate architecture, core technologies, and scalability requirements based on the analysis.
                    Your output should be the structured TechnicalSpecificationOutput and a brief technical summary.""",
                    expected_output="A TechnicalSpecificationOutput object containing the detailed technical specification, and a brief textual summary of technical recommendations.",
                    agent=cto,
                    context=[ceo_task], # Depends on ceo_task
                    output_pydantic=TechnicalSpecificationOutput # CrewAI will expect the tool to return this Pydantic model
                )

                pm_task = Task(
                    description=f"""Based on project information: {str(project_info)},
                    CEO's analysis (context: '{{{{@ceo_task}}}}'), and
                    CTO's technical specification (context: '{{{{@cto_task}}}}'),
                    develop a high-level product roadmap and define potential core features.""",
                    expected_output="A textual high-level product roadmap, list of potential core features, and initial go-to-market considerations.",
                    agent=product_manager,
                    context=[ceo_task, cto_task]
                )

                dev_task = Task(
                    description=f"""Based on project information: {str(project_info)},
                    CEO's analysis (context: '{{{{@ceo_task}}}}'),
                    CTO's technical specification (context: '{{{{@cto_task}}}}'), and
                    PM's roadmap (context: '{{{{@pm_task}}}}'),
                    provide an initial technical implementation plan, tech stack suggestions, identify challenges, and estimate effort. Include potential cloud costs.""",
                    expected_output="A textual technical implementation plan, tech stack ideas, challenge list, effort estimates, and cloud cost considerations.",
                    agent=developer,
                    context=[ceo_task, cto_task, pm_task]
                )

                client_task = Task(
                    description=f"""Based on all project information: {str(project_info)},
                    CEO's analysis (context: '{{{{@ceo_task}}}}'),
                    CTO's specification (context: '{{{{@cto_task}}}}'),
                    PM's roadmap (context: '{{{{@pm_task}}}}'), and
                    Developer's plan (context: '{{{{@dev_task}}}}'),
                    outline a client engagement and success strategy, including communication, expectation management, and go-to-market ideas.""",
                    expected_output="A textual client engagement strategy, communication plan, and preliminary go-to-market outline.",
                    agent=client_manager,
                    context=[ceo_task, cto_task, pm_task, dev_task]
                )

                # Create and run the crew
                project_crew = Crew(
                    agents=[ceo, cto, product_manager, developer, client_manager],
                    tasks=[ceo_task, cto_task, pm_task, dev_task, client_task],
                    process=Process.sequential, # Tasks will run in the order defined
                    verbose=True # 0 for no logs, 1 for agent logs, 2 for detailed logs
                )

                with st.spinner("AI Services Agency (using Groq) is analyzing your project..."):
                    try:
                        crew_result = project_crew.kickoff()

                        # Extract results from tasks
                        # For tasks with output_pydantic, .output.exported_output is the Pydantic model instance
                        # .output.raw_output contains the agent's final textual output for that task.

                        ceo_analysis_data = None
                        ceo_summary = "CEO task did not produce expected output."
                        if ceo_task.output:
                            ceo_analysis_data = ceo_task.output.exported_output if hasattr(ceo_task.output, 'exported_output') else None
                            ceo_summary = ceo_task.output.raw_output if hasattr(ceo_task.output, 'raw_output') else str(ceo_task.output)


                        cto_spec_data = None
                        cto_summary = "CTO task did not produce expected output."
                        if cto_task.output:
                            cto_spec_data = cto_task.output.exported_output if hasattr(cto_task.output, 'exported_output') else None
                            cto_summary = cto_task.output.raw_output if hasattr(cto_task.output, 'raw_output') else str(cto_task.output)

                        pm_response = pm_task.output.raw_output if pm_task.output and hasattr(pm_task.output, 'raw_output') else str(pm_task.output)
                        developer_response = dev_task.output.raw_output if dev_task.output and hasattr(dev_task.output, 'raw_output') else str(dev_task.output)
                        client_response = client_task.output.raw_output if client_task.output and hasattr(client_task.output, 'raw_output') else str(client_task.output)

                        # Create tabs for different analyses
                        tabs = st.tabs([
                            "CEO's Project Analysis",
                            "CTO's Technical Specification",
                            "Product Manager's Plan",
                            "Developer's Implementation",
                            "Client Success Strategy"
                        ])

                        with tabs[0]:
                            st.markdown("## CEO's Strategic Analysis")
                            st.markdown("### Summary:")
                            st.markdown(ceo_summary)
                            if ceo_analysis_data and isinstance(ceo_analysis_data, BaseModel):
                                st.markdown("### Structured Analysis Data:")
                                st.json(ceo_analysis_data.model_dump_json(indent=2))
                                st.session_state.messages.append({"role": "assistant", "content": f"**CEO Analysis:**\n{ceo_summary}\n**Data:**\n{ceo_analysis_data.model_dump_json(indent=2)}"})
                            else:
                                st.markdown("### Structured Analysis Data: Not available or not in expected format.")
                                st.session_state.messages.append({"role": "assistant", "content": f"**CEO Analysis:**\n{ceo_summary}\n**Data:**\n{str(ceo_analysis_data)}"})


                        with tabs[1]:
                            st.markdown("## CTO's Technical Specification")
                            st.markdown("### Summary:")
                            st.markdown(cto_summary)
                            if cto_spec_data and isinstance(cto_spec_data, BaseModel):
                                st.markdown("### Structured Specification Data:")
                                st.json(cto_spec_data.model_dump_json(indent=2))
                                st.session_state.messages.append({"role": "assistant", "content": f"**CTO Specification:**\n{cto_summary}\n**Data:**\n{cto_spec_data.model_dump_json(indent=2)}"})
                            else:
                                st.markdown("### Structured Specification Data: Not available or not in expected format.")
                                st.session_state.messages.append({"role": "assistant", "content": f"**CTO Specification:**\n{cto_summary}\n**Data:**\n{str(cto_spec_data)}"})


                        with tabs[2]:
                            st.markdown("## Product Manager's Plan")
                            st.markdown(pm_response)
                            st.session_state.messages.append({"role": "assistant", "content": f"**Product Manager Plan:**\n{pm_response}"})

                        with tabs[3]:
                            st.markdown("## Lead Developer's Development Plan")
                            st.markdown(developer_response)
                            st.session_state.messages.append({"role": "assistant", "content": f"**Developer Plan:**\n{developer_response}"})

                        with tabs[4]:
                            st.markdown("## Client Success Strategy")
                            st.markdown(client_response)
                            st.session_state.messages.append({"role": "assistant", "content": f"**Client Success Strategy:**\n{client_response}"})

                        st.markdown("---")
                        st.markdown("## Full Crew Execution Log:")
                        st.text_area("Crew Kickoff Result (Output of last task or overall summary)", value=str(crew_result), height=200)
                        st.session_state.messages.append({"role": "system", "content": f"**Crew Final Output:**\n{str(crew_result)}"})


                    except Exception as e:
                        st.error(f"Error during CrewAI analysis: {str(e)}")
                        st.error("Please check your inputs, API key, and tool/agent configurations and try again.")
                        import traceback
                        st.text_area("Traceback", traceback.format_exc(), height=300)


            except Exception as e:
                st.error(f"Error during setup or form processing: {str(e)}")
                st.error("Please check your API key and try again.")
                import traceback
                st.text_area("Traceback", traceback.format_exc(), height=300)


    # Add history management in sidebar
    with st.sidebar:
        st.subheader("Options")
        if st.checkbox("Show Analysis History"):
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if st.button("Clear History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()
