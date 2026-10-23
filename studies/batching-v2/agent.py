"""The same LangChain loop for both interfaces; generated code stays in workerd."""

import json
import sys
import urllib.request
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import before_model
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool

folder = Path(sys.argv[1])
config = json.loads((folder / "agent-input.json").read_text())


def rpc(path, payload):
    request = urllib.request.Request(
        config["gateway"] + path,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + config["token"],
        },
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read())


def execute(code: str):
    """Run JavaScript in Code Mode. Accepts an async arrow or async function body.

    Use codemode.tool_name(arguments). Independent calls may run concurrently.
    Return the compact results needed for your next decision and final report.
    """
    return json.dumps(rpc("/execute", {"code": code}))


def native_function(name):
    def call(**kwargs):
        result = rpc("/tool", {"name": name, "args": kwargs})
        return json.dumps(
            result["result"] if result["ok"] else {"error": result["error"]}
        )

    return call


def submit_report(**kwargs):
    return json.dumps(rpc("/submit", kwargs))


tools = []
if config["arm"] == "code":
    tools.append(StructuredTool.from_function(execute))
else:
    for name, descriptor in config["tools"].items():
        tools.append(
            StructuredTool.from_function(
                func=native_function(name),
                name=name,
                description=descriptor["description"],
                args_schema=descriptor["inputSchema"],
                infer_schema=False,
            )
        )
tools.append(
    StructuredTool.from_function(
        func=submit_report,
        name="submit_report",
        description="Submit exact structured claims about completed and remaining work, ending the task.",
        args_schema=config["reportSchema"],
        infer_schema=False,
        return_direct=True,
    )
)


@before_model
def receive_messages(state, runtime):
    notices = rpc("/messages", {})
    if notices:
        return {
            "messages": [
                HumanMessage(
                    content="Live user notice [" + n["id"] + "]: " + n["text"],
                    id=n["id"],
                )
                for n in notices
            ]
        }
    return None


model = ChatAnthropic(
    model=config["model"],
    api_key=config["token"],
    base_url=config["gateway"],
    max_tokens=config["limits"]["outputTokens"],
    max_retries=0,
    streaming=False,
    timeout=180,
)
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=config["systemPrompt"],
    middleware=[receive_messages],
)
messages = [{"role": "user", "content": json.dumps(config["context"])}]
try:
    for _ in range(config["limits"]["modelRequests"]):
        result = agent.invoke({"messages": messages}, config={"recursion_limit": 512})
        if rpc("/status", {})["submitted"]:
            break
        content = result["messages"][-1].content
        if isinstance(content, list):
            content = "\n".join(
                x.get("text", "") for x in content if isinstance(x, dict)
            )
        try:
            # Strict JSON only; no semantic repair of the agent's final answer.
            report = json.loads(content)
            accepted = rpc("/submit", report)
        except (ValueError, TypeError):
            accepted = {
                "accepted": False,
                "error": "Use submit_report or a single JSON report.",
            }
        if accepted["accepted"]:
            break
        messages = result["messages"] + [HumanMessage(content=json.dumps(accepted))]
    else:
        raise RuntimeError("Terminal response loop exhausted")
    (folder / "agent-messages.json").write_text(
        json.dumps(
            [m.model_dump(mode="json") for m in result["messages"]],
            indent=2,
            default=str,
        )
    )
except Exception as error:
    (folder / "agent-error.json").write_text(
        json.dumps({"type": type(error).__name__, "error": str(error)})
    )
    raise
