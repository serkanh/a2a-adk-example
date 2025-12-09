## FEATURE

I want to setup an additional agent that is based on [aws strands](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/) framework. This will have tools to interact with AWS services. It will include `shell` and `python_repl`. It needs to run as headless agent and exposed via A2A protocol. 
This agent will use different dockerfile since it will be using aws strands framework. It needs to be added as another service in the docker-compose.yml file and also added to coordinator agent as a sub-agent.

## EXAMPLES



## DOCUMENTATION

Strands A2A implementation example: docs/strands-a2a.md
Strands multi-agent example: docs/strands-multi-agent-example.md
quickstart: docs/quickstart.md
anthropic: docs/anthropic.md
gemini: docs/gemini.md

## OTHER CONSIDERATIONS
