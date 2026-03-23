"""Handler for /labs command."""

from services.lms_client import LMSClient


def handle_labs() -> str:
    """Handle the /labs command.
    
    Returns:
        List of available labs from the real LMS API.
    """
    client = LMSClient()
    result = client.get_items()
    
    if not result["success"]:
        return f"Error fetching labs: {result['error']}"
    
    items = result["items"]
    if not items:
        return "No labs available."
    
    # Format labs from the API response
    # Expected format: [{"id": "lab-01", "name": "...", "type": "lab", ...}, ...]
    labs = []
    for item in items:
        if item.get("type") == "lab" or "lab" in item.get("id", "").lower():
            lab_id = item.get("id", "Unknown")
            lab_name = item.get("name", item.get("title", lab_id))
            labs.append(f"• {lab_id}: {lab_name}")
    
    if not labs:
        # Fallback: show all items if no explicit lab type
        for item in items:
            lab_id = item.get("id", "Unknown")
            lab_name = item.get("name", item.get("title", lab_id))
            labs.append(f"• {lab_id}: {lab_name}")
    
    return "Available Labs:\n\n" + "\n".join(labs) + "\n\nUse /scores <lab> to view scores for a specific lab."
