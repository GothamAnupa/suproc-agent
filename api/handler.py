import json
from app.agent import run_agent


def handler(request):
    """Handle HTTP requests"""
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode() if isinstance(request.body, bytes) else request.body)
            query = data.get("query", "").strip()
            
            if not query:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing 'query' field"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            response = run_agent(query)
            return {
                "statusCode": 200,
                "body": json.dumps(response.model_dump(), indent=2),
                "headers": {"Content-Type": "application/json"}
            }
        
        elif request.method == "GET":
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "ok"}),
                "headers": {"Content-Type": "application/json"}
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }


