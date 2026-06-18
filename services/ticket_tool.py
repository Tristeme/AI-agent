from langchain.agents import Tool
from services.logger import logger


def create_ticket_draft(issue: str) -> str:
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


ticket_tool = Tool(
    name="Ticket Draft",
    func=create_ticket_draft,
    description="Use this tool when the user asks to create, raise, submit, or open a work order or ticket. This tool only creates a draft and does not execute any action."
)