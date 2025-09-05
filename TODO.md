# TODO & Notes

* [X] WIP

  * [X] "Source" is always showing something, guess it keeps the last ... fix it
  * [ ] Long-term memory ? Multi-session? SQLite? (Q)
    * [ ] UI chat history saved, restored next session and update agent's messages
  * [ ] LangGraph Studio?
  * [ ] Folder structure (p1)
  * [ ] Load 1K pdfs -> Vector DB, Chroma? (Q)
  * [ ] Deploy App to cloud/server (Q)
  * [ ] Documentation
  * [X] Token usage by user



* [X] Rebuild CPA using LangGraph Studio
* [X] Build the graph from scratch
* [X] UI link to LangGraph workflow
* [ ] Step by step

  * [ ] Define what to build
    * [ ] Vector Database
      * [X] Install new vector db
      * [X] Load documents
      * [X] Search documents
      * [ ] Test cases
    * [ ] Database
      * [ ] Load data
      * [ ] Search
      * [ ] Return table
    * [ ] Code (out of scope)
      * [ ] Get input data
      * [ ] Generate plot
      * [ ] Return plot
  * [ ] TDD

## 🚀 High Priority

- [X] LangGraph

  - [X] Graphs
  - [X] Agents
  - [X] Tools
    - [X] Tool matching
- [ ] Memory

  - [X] Short-term
  - [ ] Long-term
- [X] Chat history
- [X] SQL Database (SQLite)
- [ ] Analytical Database (Duckdb)
- [X] Query database (SQL)
- [ ] API endpoints for external integrations
- [X] API key validation
- [X] API limit rate
- [ ] Logging

  - [X] Logfiles (Python logging)
  - [X] LangSmith
  - [ ] Centralized logging/visualization (nice to have)
  - [X] Remove Loki
- [ ] App functionality

  - [ ] Add campaign uplift
- [ ] LangGraph

  - [ ] Server architecture (out of scope)

## 🔧 Medium Priority

- [X] Local LLM
- [ ] Implement MCP (Client and Servier)
- [ ] LangGraph Studio

## 📝 Low Priority

- [X] Charts
- [ ] Images
  - [ ] Explanation
  - [ ] Composition
- [ ] User authentication
- [ ] Session management
- [ ] Unit tests
- [ ] Integration tests
- [X] Structural retriever (Pydantic?)

## 💡 Ideas & Research

- [ ] Look into caching strategies for faster responses
- [ ] Consider using FastAPI for API endpoints
- [ ] Research vector database alternatives (Pinecone, Weaviate)
- [ ] Explort different splitting/chuncking options

## 📋 Notes

### Architecture Decisions

- Using HuggingFace embeddings for local processing
- ChromaDB for vector storage (good for development)
- Loguru for consistent logging across components

### Performance Considerations

- Document chunking size: 1000 characters
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Retrieval: Top 4 most similar documents

### Known Issues

- Fix: VectorDB getting Campaing Executive
  - Summary and passing to LLM, score < 0.5 (for some reason not getting documents)
  - We may need to tune chunks
- Large PDF files may take time to process
- Need to handle concurrent file uploads better

## Project 2: Feedback

* [X] Pyproject.toml lacks some metadata about project, now it's just boilerplate
* [ ] Hardcoded credentials here and there - use .env file all troughout
* [ ] Project structure could be cleaner, especially in the root
* [ ] All endpoints and similar constants should be parametrized same way as passwords - .env file/env variables work best
* [X] Both requirements.txt and pyproject.toml for dependencies?
* [ ] Testing would be good at some point
* [ ] What would you do with chroma_db in prod?
* [ ] Deployment strategy - ec2 not very good option, more segmented approach would be better

# Project 3:

## Task Requirements

The exact task requirements are as follows:

1. **Agent Purpose** :

* [X] Define a clear purpose for your agent
* [X] Explain why this agent is useful
* [X] Identify the target users

2. **Core Functionality** :

* [X] Implement the main features that make your agent useful
* [X] Ensure the agent can perform its primary tasks effectively
* [X] Include necessary user interactions

3. **User Interface** :

* [X] Build a user-friendly interface for all functionalities
* [X] Make the interface intuitive and easy to use

4. **Technical Implementation** :

* [X] Use appropriate tools and libraries
* [X] Implement proper error handling
* [X] Ensure the agent can handle real-world usage

5. **Documentation** :

* [ ] Provide clear documentation on how to use your agent
* [ ] Include examples of common use cases
* [ ] Explain any technical decisions made

## Optional Tasks

After the main functionality is implemented and your code works correctly, and you feel that you want to upgrade your project, choose various improvements from this list. The list is sorted by difficulty levels.

**Caution: Some of the tasks in medium or hard categories may contain tasks with concepts or libraries that may be introduced in later sections or even require outside knowledge/time to research outside of the course.**

**Easy:**

1. [ ] Ask ChatGPT to critique your solution from the usability, security, and prompt-engineering sides.
2. [ ] Give the agent a personality—tweak responses to make them more formal, friendly, or concise based on user needs.
3. [ ] Provide the user with the ability to choose from a list of LLMs (Gemini, OpenAI, etc.) for this project.
4. [ ] Add all of the OpenAI settings (temperature, top-p frequency) for the user to tune as sliders/fields.
5. [ ] Add a feature to allow users to preview the dataset before and after cleaning.
6. [ ] Add an interactive help feature or chatbot guide.

**Medium:**

1. [ ] Calculate and display token usage and costs.
2. [ ] Add retry logic for agents.
3. [ ] Implement long-term or short-term memory in LangChain/LangGraph.
4. [ ] Implement one more function tool that would call an external API.
5. [ ] Add user authentication and personalization.
6. [ ] Implement a caching mechanism to store and retrieve frequently used responses.
7. [ ] Implement a feedback loop where users can rate the responses, and use this feedback to improve the agent's performance.
8. [ ] Implement 2 extra function tools (5 in total).
9. [ ] Have a UI for the user to either enable or disable these function tools.
1. [ ] Develop a plugin system that allows users to add or remove functionalities from the chatbot dynamically.
1. [ ] Implement multi-model support (OpenAI, Anthropic, etc.).

**Hard:**

1. [ ] Agentic RAG: Think of a way to add RAG functionality to the LangChain/LangGraph application and implement it.
2. [ ] Add one off these LLM observability tools: Arize Pheonix, LangSmith, Lunary, or others.
3. [ ] Make your solution scalable, meaning that you can clean large CSV files: 500MB or even in the GB range.
4. [ ] Fine-tune the model for your specific domain.
5. [ ] Create an agent that can learn from user feedback on the cleaned dataset. This agent should be able to adjust its cleaning strategies based on the feedback to improve future performance.
6. [ ] Implement an agent that can integrate with external data sources to enrich the dataset. This could involve fetching additional data from APIs or databases.
7. [ ] Implement an agent that can collaborate with other agents in a distributed system. This agent should be able to work with agents running on different machines or in different environments, coordinating their efforts to clean the dataset efficiently.
8. [ ] Deploy your app to the cloud with proper scaling.

## Evaluation Criteria

**Problem Definition**

* [ ] The learner has a well defined problem that they are aiming to solve with this project.
* [ ] The learner can articulate how the app they’re building addresses the problem they identified.

**Understanding Core Concepts:**

* [ ] The learner understands the basic principles of how agents work.
* [ ] The learner can mention differences between different agent types.
* [ ] The learner can explain function calling implementation clearly.
* [ ] The learner demonstrates good code organization practices.
* [ ] The learner can identify potential error scenarios and edge cases.

**Technical Implementation:**

* [ ] The learner knows how to use a front-end library using their knowledge and/or external resources.
* [ ] The learner has created a relevant knowledge base for their domain if applicable.
* [ ] The learner has implemented appropriate security considerations.

**Reflection and Improvement:**

* [ ] The learner understands the potential problems with the application.
* [ ] The learner can offer suggestions on improving the code and the project.
* [ ] The learner understands when to use prompt engineering, RAG, or agents.

**Bonus Points:**

* [ ] For maximum points, the learner should implement at least 2 medium and 1 hard optional tasks.

---

*Last updated: [Current Date]*
