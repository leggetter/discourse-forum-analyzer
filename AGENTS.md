# AGENTS.md: A Guide for AI Agents

This document provides a high-level overview of the Discourse Forum Analyzer project, designed to give AI agents the essential context needed to understand and work with this codebase. It is not exhaustive but serves as a starting point, linking to more detailed documentation where appropriate.

## 1. Project Purpose

The **Discourse Forum Analyzer** is a Python tool for collecting and analyzing discussions from public Discourse forums using LLM-powered analysis. Its primary goal is to automate the extraction of insights from community discussions.

-   **For a full overview, see:** [`README.md`](./README.md)
-   **For project planning and history, see:** [`.plan/`](./.plan/)

## 2. Core Components and Key Files

This project is structured as a Python CLI application. Here are the most important directories and files for an agent to be aware of:

-   **`src/forum_analyzer/`**: The main source code for the application.
    -   **`cli.py`**: The entry point for all CLI commands. This is the best place to understand the tool's capabilities.
    -   **`collector/`**: Contains the logic for fetching data from the Discourse API.
        -   `api_client.py`: The rate-limited, asynchronous HTTP client.
        -   `orchestrator.py`: Manages the overall collection process.
    -   **`analyzer/`**: Contains the logic for LLM-based analysis.
        -   `llm_analyzer.py`: Integrates with the Claude API to perform analysis.
    -   **`config/`**: Configuration management.
        -   `settings.py`: Handles project-based configuration loading.
        -   `config_template.yaml`: Template used by `init` command.
-   **`README.md`**: The main project documentation, including setup instructions and a full command reference.
-   **`.plan/`**: Contains detailed planning documents, including the original project plan, progress reports, and architecture diagrams.

## 2.1 Project-Based Structure

The tool now uses a **project-based architecture**. Each analysis project is a directory containing:

```
my-forum-project/
├── config.yaml          # Configuration file
├── forum.db            # SQLite database
├── checkpoints/        # Recovery checkpoints
├── exports/            # Analysis reports
└── logs/               # Application logs
```

Projects are initialized with `forum-analyzer init` and all paths are relative to the project directory.

## 3. Key Concepts and Workflow

The tool operates on a few key concepts:

-   **Project Initialization**: Creating a new project directory with `forum-analyzer init`.
-   **Collection**: Scraping topics and posts from a Discourse category.
-   **Theme Discovery**: Using an LLM to find high-level themes in the collected data.
-   **Analysis**: Using an LLM to analyze individual topics for specific problems, categories, and severity.

The recommended workflow is:

1. **Initialize**: `forum-analyzer init` - Creates project structure and configuration
2. **Collect**: `forum-analyzer collect` - Gathers forum data (creates database automatically)
3. **Discover**: `forum-analyzer themes discover` - Identifies themes in the data
4. **Analyze**: `forum-analyzer llm-analyze` - Performs LLM-based analysis
5. **Query**: `forum-analyzer ask "question"` - Natural language queries

All commands support the `--dir` flag to specify a project directory.

## 4. How to Make Changes

1.  **Understand the Goal**: Before making changes, review the `README.md` and the relevant files in `src/forum_analyzer/` to understand the existing implementation.
2.  **Modify the Code**: Make changes to the relevant Python files in the `src/` directory.
3.  **Follow Existing Patterns**: The project uses `SQLAlchemy` for database interaction, `Click` for the CLI, and `Pydantic` for configuration. Adhere to these patterns.
4.  **Test Your Changes**: (Note: The test suite is currently minimal). Run existing tests and add new ones if possible.

## 5. System Architecture

The system is a multi-layered Python application. For a visual representation of the architecture and data flow, please refer to the diagrams in [`architecture-diagram.md`](./.plan/architecture-diagram.md).

This concise guide should provide any agent with the necessary starting points to effectively work on this project.