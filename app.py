from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Literal, Type
import json
import litellm
litellm.set_verbose = True

# Import your tool classes from the original file (assuming they are in the same directory)
from backend.agents.agents import run_project_analysis

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Helper to run the CrewAI pipeline

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    try:
        result = run_project_analysis(data)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)
