from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/docs", tags=["Documentation"])

@router.get("/usage", response_class=HTMLResponse)
def api_usage_guide():
    """API Usage Guide and Examples"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Data Exchange Hub - API Usage Guide</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #fff; padding: 4px 8px; border-radius: 3px; font-weight: bold; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            .put { background: #fca130; }
            .delete { background: #f93e3e; }
            code { background: #f1f1f1; padding: 2px 4px; border-radius: 3px; }
            pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>HR Data Exchange Hub - API Usage Guide</h1>
        
        <h2>Authentication</h2>
        <p>All API endpoints require authentication via JWT tokens sent as HTTP-only cookies.</p>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/auth/login</code>
            <p>Login to get authentication token</p>
            <pre>
{
  "email": "user@example.com",
  "password": "password123"
}
            </pre>
        </div>

        <h2>Employee Data API</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/</code>
            <p>List employees with pagination and filtering</p>
            <h4>Query Parameters:</h4>
            <ul>
                <li><code>skip</code> - Number of records to skip (default: 0)</li>
                <li><code>limit</code> - Maximum records to return (default: 100, max: 1000)</li>
                <li><code>search</code> - Search across name, email, employee_id, job_title</li>
                <li><code>department</code> - Filter by department</li>
                <li><code>status</code> - Filter by employee status</li>
                <li><code>sort_by</code> - Sort field (first_name, last_name, email, department, hire_date, created_at)</li>
                <li><code>sort_order</code> - Sort direction (asc, desc)</li>
                <li><code>hire_date_from</code> - Filter by hire date from (YYYY-MM-DD)</li>
                <li><code>hire_date_to</code> - Filter by hire date to (YYYY-MM-DD)</li>
            </ul>
            <h4>Example:</h4>
            <pre>GET /api/employees/?search=john&department=engineering&sort_by=hire_date&sort_order=desc</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/{id}</code>
            <p>Get individual employee by ID</p>
            <h4>Example:</h4>
            <pre>GET /api/employees/123</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/search/advanced</code>
            <p>Advanced search with relevance scoring</p>
            <h4>Query Parameters:</h4>
            <ul>
                <li><code>q</code> - Search query (required, min 2 characters)</li>
                <li><code>fields</code> - Comma-separated fields to search in</li>
                <li><code>skip</code> - Pagination offset</li>
                <li><code>limit</code> - Results limit (max: 500)</li>
            </ul>
            <h4>Example:</h4>
            <pre>GET /api/employees/search/advanced?q=john&fields=first_name,last_name,email</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/export/csv</code>
            <p>Export employees to CSV format</p>
            <h4>Query Parameters:</h4>
            <ul>
                <li><code>department</code> - Filter by department</li>
                <li><code>status</code> - Filter by status</li>
                <li><code>fields</code> - Comma-separated fields to export</li>
            </ul>
            <h4>Example:</h4>
            <pre>GET /api/employees/export/csv?department=engineering&fields=employee_id,first_name,last_name,email</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/export/json</code>
            <p>Export employees to JSON format</p>
            <h4>Query Parameters:</h4>
            <ul>
                <li><code>department</code> - Filter by department</li>
                <li><code>status</code> - Filter by status</li>
                <li><code>fields</code> - Comma-separated fields to export</li>
            </ul>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/employees/stats/summary</code>
            <p>Get employee statistics and department breakdown</p>
        </div>

        <h2>Rate Limits</h2>
        <ul>
            <li>Employee listing: 100 requests/minute</li>
            <li>Advanced search: 50 requests/minute</li>
            <li>Data export: 10 requests/minute</li>
        </ul>

        <h2>Response Format</h2>
        <p>All API responses follow a consistent format:</p>
        <pre>
{
  "employees": [...],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 1500,
    "has_more": true
  }
}
        </pre>

        <h2>Error Handling</h2>
        <p>API errors return standard HTTP status codes with descriptive messages:</p>
        <ul>
            <li><code>400</code> - Bad Request (invalid parameters)</li>
            <li><code>401</code> - Unauthorized (authentication required)</li>
            <li><code>404</code> - Not Found (resource doesn't exist)</li>
            <li><code>429</code> - Too Many Requests (rate limit exceeded)</li>
            <li><code>500</code> - Internal Server Error</li>
        </ul>

        <h2>Field Mapping API</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/mappings/{source_id}</code>
            <p>Get field mappings for a data source</p>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/mappings/{source_id}/bulk</code>
            <p>Create multiple field mappings</p>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/mappings/preview/{source_id}</code>
            <p>Preview data transformation with quality metrics</p>
        </div>

        <h2>ETL Processing API</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/etl/upload</code>
            <p>Upload XML file for processing</p>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/etl/jobs</code>
            <p>List ETL jobs with status</p>
        </div>

        <p><strong>For interactive API documentation, visit:</strong> <a href="/docs">/docs</a></p>
    </body>
    </html>
    """
    
    return html_content

@router.get("/examples")
def api_examples():
    """API Usage Examples"""
    
    return {
        "examples": {
            "list_employees": {
                "url": "/api/employees/?skip=0&limit=50&search=john&department=engineering",
                "description": "List employees with search and filtering"
            },
            "advanced_search": {
                "url": "/api/employees/search/advanced?q=manager&fields=job_title,department",
                "description": "Search for employees with 'manager' in job title or department"
            },
            "export_csv": {
                "url": "/api/employees/export/csv?status=Active&fields=employee_id,first_name,last_name,email,department",
                "description": "Export active employees to CSV with selected fields"
            },
            "employee_stats": {
                "url": "/api/employees/stats/summary",
                "description": "Get employee statistics and department breakdown"
            },
            "date_filtering": {
                "url": "/api/employees/?hire_date_from=2023-01-01&hire_date_to=2023-12-31&sort_by=hire_date&sort_order=desc",
                "description": "Find employees hired in 2023, sorted by hire date"
            }
        },
        "curl_examples": {
            "login": "curl -X POST 'http://localhost:8000/api/auth/login' -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\",\"password\":\"password123\"}' -c cookies.txt",
            "list_employees": "curl -X GET 'http://localhost:8000/api/employees/?limit=10' -b cookies.txt",
            "search": "curl -X GET 'http://localhost:8000/api/employees/search/advanced?q=engineer' -b cookies.txt",
            "export": "curl -X GET 'http://localhost:8000/api/employees/export/csv?department=engineering' -b cookies.txt -o employees.csv"
        }
    }