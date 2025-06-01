import os
from crewai import Agent, Task, Crew, Process
from typing import List, Literal, Type
import json
from backend.tools.tools import *
from backend.llms.llm import get_llms
import litellm
litellm.set_verbose = True





def run_project_analysis(data):
    project_name = data.get('project_name')
    project_description = data.get('project_description')
    project_type = data.get('project_type')
    timeline = data.get('timeline')
    budget_range = data.get('budget_range')
    priority = data.get('priority')
    tech_requirements = data.get('tech_requirements', '')
    special_considerations = data.get('special_considerations', '')
    groq_api_key = data.get('groq_api_key')
    model_name = 'gemma2-9b-it'  # Use a Groq-supported model name

    # Dynamically get LLMs with the correct API key
    llms = get_llms(groq_api_key=groq_api_key, model_name=model_name)
    ceo_llm = llms['ceo_llm']
    cto_llm = llms['cto_llm']
    pm_llm = llms['pm_llm']
    dev_llm = llms['dev_llm']
    client_llm = llms['client_llm']

    analyze_tool = AnalyzeProjectRequirements()
    spec_tool = CreateTechnicalSpecification()

    ceo = Agent(
        role="Project Director (CEO)",
        goal=f"""Analyze the provided project details (name: {project_name}, description: {project_description}, type: {project_type}, budget: {budget_range}) using the AnalyzeProjectRequirementsTool.\nYour final output must be the structured project analysis data as per the ProjectAnalysisOutput model.\nProvide a brief summary of your strategic assessment based on this analysis.""",
        backstory="You are a seasoned CEO with extensive experience in evaluating project feasibility and strategic alignment. You are meticulous and data-driven.",
        tools=[analyze_tool],
        llm=ceo_llm,
        verbose=True,
        allow_delegation=False
    )

    cto = Agent(
        role="Technical Architect (CTO)",
        goal="""Based on the project analysis provided by the CEO, create a detailed technical specification using the CreateTechnicalSpecificationTool.\nYou will receive the project analysis as a JSON string. Use this to determine the architecture_type, core_technologies, and scalability_requirements.\nYour final output must be the structured technical specification data as per the TechnicalSpecificationOutput model.\nProvide a brief summary of your technical recommendations.""",
        backstory="You are a highly experienced Technical Architect with a deep understanding of various system architectures, technologies, and scalability patterns. You translate project needs into robust technical plans.",
        tools=[spec_tool],
        llm=cto_llm,
        verbose=True,
        allow_delegation=False
    )

    product_manager = Agent(
        role="Product Manager",
        goal="""Based on the project information, CEO's analysis, and CTO's technical specification, develop a high-level product roadmap.\nDefine potential core product features and outline a phased approach if applicable.\nFocus on product-market fit and initial go-to-market considerations.""",
        backstory="You are an experienced Product Manager skilled in defining product vision, strategy, and roadmaps, ensuring alignment with business goals and market needs.",
        llm=pm_llm,
        verbose=True
    )

    developer = Agent(
        role="Lead Developer",
        goal="""Based on the project information, CEO's analysis, CTO's technical specification, and Product Manager's roadmap, provide an initial technical implementation plan.\nOutline key development phases, suggest a core tech stack (complementing CTO's choices), identify potential technical challenges, and give a rough effort estimation breakdown.\nConsider cloud service costs if applicable.""",
        backstory="You are a Senior Full-Stack Developer with broad experience in implementing complex software projects. You are pragmatic and skilled in estimation and risk assessment.",
        llm=dev_llm,
        verbose=True
    )

    client_manager = Agent(
        role="Client Success Manager",
        goal="""Based on all available project information (initial details, CEO analysis, CTO spec, PM roadmap, Dev plan), outline a client engagement and success strategy.\nFocus on communication, expectation management, feedback loops, and key milestones for client review.\nSuggest a preliminary go-to-market and customer acquisition outline from a client success perspective.""",
        backstory="You are an experienced Client Success Manager dedicated to ensuring client satisfaction and successful project delivery through proactive communication and strategic guidance.",
        llm=client_llm,
        verbose=True
    )

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

    ceo_task = Task(
        description=f"""Analyze the following project and produce a structured analysis:\nProject Name: {project_name}\nProject Description: {project_description}\nProject Type: {project_type}\nBudget Range: {budget_range}\nYour output should be the structured ProjectAnalysisOutput and a brief strategic summary.""",
        expected_output="A ProjectAnalysisOutput object containing the detailed analysis, and a brief textual summary of strategic insights.",
        agent=ceo,
        output_pydantic=ProjectAnalysisOutput
    )

    cto_task = Task(
        description=f"""Given the project analysis from the CEO (available as '{{@ceo_task}}'), create a technical specification.\nYou must convert the CEO's analysis (which will be a ProjectAnalysisOutput object from the context) into a JSON string to pass to the 'project_analysis_json' parameter of your CreateTechnicalSpecificationTool.\nChoose appropriate architecture, core technologies, and scalability requirements based on the analysis.\nYour output should be the structured TechnicalSpecificationOutput and a brief technical summary.""",
        expected_output="A TechnicalSpecificationOutput object containing the detailed technical specification, and a brief textual summary of technical recommendations.",
        agent=cto,
        context=[ceo_task],
        output_pydantic=TechnicalSpecificationOutput
    )

    pm_task = Task(
        description=f"""Based on project information: {str(project_info)},\nCEO's analysis (context: '{{@ceo_task}}'), and\nCTO's technical specification (context: '{{@cto_task}}'),\ndevelop a high-level product roadmap and define potential core features.""",
        expected_output="A textual high-level product roadmap, list of potential core features, and initial go-to-market considerations.",
        agent=product_manager,
        context=[ceo_task, cto_task]
    )

    dev_task = Task(
        description=f"""Based on project information: {str(project_info)},\nCEO's analysis (context: '{{@ceo_task}}'),\nCTO's technical specification (context: '{{@cto_task}}'), and\nPM's roadmap (context: '{{@pm_task}}'),\nprovide an initial technical implementation plan, tech stack suggestions, identify challenges, and estimate effort. Include potential cloud costs.""",
        expected_output="A textual technical implementation plan, tech stack ideas, challenge list, effort estimates, and cloud cost considerations.",
        agent=developer,
        context=[ceo_task, cto_task, pm_task]
    )

    client_task = Task(
        description=f"""Based on all project information: {str(project_info)},\nCEO's analysis (context: '{{@ceo_task}}'),\nCTO's specification (context: '{{@cto_task}}'),\nPM's roadmap (context: '{{@pm_task}}'), and\nDeveloper's plan (context: '{{@dev_task}}'),\noutline a client engagement and success strategy, including communication, expectation management, and go-to-market ideas.""",
        expected_output="A textual client engagement strategy, communication plan, and preliminary go-to-market outline.",
        agent=client_manager,
        context=[ceo_task, cto_task, pm_task, dev_task]
    )

    project_crew = Crew(
        agents=[ceo, cto, product_manager, developer, client_manager],
        tasks=[ceo_task, cto_task, pm_task, dev_task, client_task],
        process=Process.sequential,
        verbose=True
    )

    crew_result = project_crew.kickoff()

    def get_output(task):
        if task.output:
            return {
                'raw_output': getattr(task.output, 'raw_output', str(task.output)),
                'exported_output': getattr(task.output, 'exported_output', None)
            }
        return {'raw_output': None, 'exported_output': None}

    return {
        'ceo': get_output(ceo_task),
        'cto': get_output(cto_task),
        'pm': get_output(pm_task),
        'dev': get_output(dev_task),
        'client': get_output(client_task),
        'crew_result': str(crew_result)
    }