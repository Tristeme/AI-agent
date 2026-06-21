# LangChain Tool abstraction allows the agent to call this function as a tool
from langchain.agents import Tool

# Shared logger for observability and audit trail
from services.logger import logger


def create_ticket_draft(issue: str) -> str:
    """
    Create a draft work order / ticket without executing any real action.

    This supports human-in-the-loop control:
    - AI can assist with drafting operational actions
    - but does not automatically submit or execute them
    """
    logger.info(f"Ticket draft tool called. Issue: {issue}")

    return f"""
DRAFT TICKET

Issue:
{issue}

Status:
NOT EXECUTED

Note:
This is only a draft. No work order has been created or submitted.
"""


# Register ticket drafting as a LangChain tool
ticket_tool = Tool(
    name="Ticket Draft",
    func=create_ticket_draft,
    description=(
        "Use this tool when the user asks to create, raise, submit, "
        "or open a work order or ticket. This tool only creates a draft "
        "and does not execute any action."
    )
)