"""
Simple HTML API Documentation (No External CDN)
Alternative to Swagger UI for when CDN is slow/blocked
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/simple-docs", response_class=HTMLResponse)
async def simple_docs():
    """
    Simple HTML documentation that doesn't require external CDN.
    Lists all available endpoints with descriptions.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bizy AI API - Simple Docs</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }

            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .version {
                opacity: 0.9;
                font-size: 1em;
            }

            .endpoint {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .endpoint-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }

            .method {
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 5px;
                margin-right: 15px;
                font-size: 0.9em;
                text-transform: uppercase;
            }

            .method.get {
                background: #61affe;
                color: white;
            }

            .method.post {
                background: #49cc90;
                color: white;
            }

            .method.patch {
                background: #fca130;
                color: white;
            }

            .method.delete {
                background: #f93e3e;
                color: white;
            }

            .path {
                font-family: 'Courier New', monospace;
                font-size: 1.1em;
                color: #333;
            }

            .description {
                color: #666;
                margin-bottom: 15px;
            }

            .try-it {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }

            .try-it h4 {
                margin-bottom: 10px;
                color: #667eea;
            }

            code {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                display: block;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                margin: 10px 0;
            }

            .response {
                background: #f0f4f8;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }

            .status-code {
                display: inline-block;
                background: #49cc90;
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 0.9em;
                margin-right: 10px;
            }

            footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: #666;
            }

            a {
                color: #667eea;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>🚀 Bizy AI API</h1>
            <div class="version">Version 0.1.0</div>
            <p style="margin-top: 10px;">AI-Powered Business Planning & Execution Agent</p>
        </header>

        <div class="endpoint">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="path">/health</span>
            </div>
            <p class="description">Health check endpoint for monitoring. Returns server status and version information.</p>

            <div class="try-it">
                <h4>Try it:</h4>
                <code>curl http://localhost:8000/health</code>

                <div class="response">
                    <span class="status-code">200 OK</span>
                    <strong>Response:</strong>
                </div>
                <code>{
  "status": "healthy",
  "service": "bizy-ai-api",
  "version": "0.1.0"
}</code>
            </div>
        </div>

        <div class="endpoint">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="path">/</span>
            </div>
            <p class="description">Root endpoint with API information and links to documentation.</p>

            <div class="try-it">
                <h4>Try it:</h4>
                <code>curl http://localhost:8000/</code>

                <div class="response">
                    <span class="status-code">200 OK</span>
                    <strong>Response:</strong>
                </div>
                <code>{
  "message": "Bizy AI API",
  "version": "0.1.0",
  "docs": "/api/docs",
  "health": "/health"
}</code>
            </div>
        </div>

        <div class="endpoint" style="background: #fff9e6;">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="path">/api/openapi.json</span>
            </div>
            <p class="description">OpenAPI specification in JSON format. Machine-readable API schema.</p>

            <div class="try-it">
                <h4>Try it:</h4>
                <code>curl http://localhost:8000/api/openapi.json</code>
            </div>
        </div>

        <footer>
            <p><strong>Alternative Documentation:</strong></p>
            <p>
                <a href="/api/docs">Swagger UI</a> (Interactive) |
                <a href="/api/simple-docs">Simple Docs</a> (This page)
            </p>
            <p style="margin-top: 20px; color: #999;">
                Built with FastAPI • Phase 3 Backend Foundation
            </p>
        </footer>
    </body>
    </html>
    """
    return html_content


@router.get("/endpoints", response_class=HTMLResponse)
async def list_endpoints():
    """Quick endpoint listing"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Endpoints</title>
        <style>
            body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
            h1 { color: #4ec9b0; }
            .endpoint { margin: 10px 0; padding: 10px; background: #2d2d2d; border-radius: 5px; }
            .method { color: #569cd6; font-weight: bold; }
            .path { color: #ce9178; }
            a { color: #4fc1ff; }
        </style>
    </head>
    <body>
        <h1>Available Endpoints</h1>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/health</span> - Health check
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/</span> - API info
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/docs</span> - Swagger UI
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/simple-docs</span> - Simple docs (no CDN)
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/endpoints</span> - This page
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/openapi.json</span> - OpenAPI schema
        </div>
        <p style="margin-top: 20px;">
            <a href="/">← Back to API root</a>
        </p>
    </body>
    </html>
    """
    return html
