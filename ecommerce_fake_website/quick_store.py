import httpx
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="CY-02 Target Store Simulator")

CY02_INGEST_URL = "http://127.0.0.1:9000/api/v1/logs"

@app.middleware("http")
async def send_logs_to_cy02(request: Request, call_next):
    response = await call_next(request)
    
    payload = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "client_id": request.headers.get("X-Client-ID", f"client_{request.client.host}"),
        "ip": request.client.host,
        "endpoint": request.url.path,
        "status": response.status_code,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "username": "demo_user"
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(CY02_INGEST_URL, json=payload, timeout=0.5)
        except Exception:
            pass

    return response

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Target App Simulator</title>
        <style>
            body { font-family: Arial; background: #0d1117; color: #fff; padding: 40px; text-align: center; }
            .card { background: #161b22; border: 1px solid #30363d; padding: 20px; margin: 15px auto; width: 340px; border-radius: 8px; }
            button { background: #238636; color: white; border: none; padding: 10px 16px; border-radius: 5px; cursor: pointer; margin: 4px; font-weight: bold; }
            button.danger { background: #da3633; }
            button.warn { background: #d29922; color: black; }
        </style>
    </head>
    <body>
        <h1>🛒 Live Target Application</h1>
        <p>Click buttons below to fire live attack vectors directly into <b>CY-02 Sentinel</b>.</p>
        
        <div class="card">
            <h3>✅ Normal Human Traffic</h3>
            <button onclick="fetch('/api/products')">Browse Catalog</button>
            <button onclick="fetch('/api/checkout', {method:'POST'})">Checkout Order</button>
        </div>

        <div class="card">
            <h3>🚨 Attack Vector Simulator</h3>
            <button class="danger" onclick="triggerAttack('credential_stuffing')">1. Credential Stuffing (Critical)</button> <br>
            <button class="danger" onclick="triggerAttack('low_and_slow')">2. Low & Slow Attack</button> <br>
            <button class="warn" onclick="triggerAttack('scraper')">3. Product Scraper</button> <br>
            <button class="warn" onclick="triggerAttack('enumeration')">4. User ID Enumeration</button>
        </div>

        <script>
            function triggerAttack(type) {
                if(type === 'credential_stuffing') {
                    for(let i=0; i<20; i++) {
                        fetch('/api/login', {
                            method: 'POST',
                            headers: {
                                'User-Agent': 'Python-requests/Bot-v1.0 (Credential Stuffer)', 
                                'X-Client-ID': 'attacker_stuffer_critical'
                            }
                        });
                    }
                    alert('Fired Heavy Credential Stuffing Attack (20 Failed Requests) to CY-02!');
                } else if(type === 'scraper') {
                    for(let i=1; i<=25; i++) {
                        fetch('/api/products?page=' + i, {
                            headers: {
                                'User-Agent': 'HeadlessChrome/ScraperBot-v2', 
                                'X-Client-ID': 'catalog_scraper_critical'
                            }
                        });
                    }
                    alert('Fired Web Scraper Attack to CY-02!');
                } else if(type === 'enumeration') {
                    for(let i=1001; i<=1020; i++) {
                        fetch('/api/users/' + i, {
                            headers: {
                                'User-Agent': 'Python-requests/EnumBot',
                                'X-Client-ID': 'enumerator_bot_critical'
                            }
                        });
                    }
                    alert('Fired Resource Enumeration Attack to CY-02!');
                } else if(type === 'low_and_slow') {
                    for(let i=1; i<=8; i++) {
                        fetch('/api/login', {
                            method: 'POST',
                            headers: {
                                'User-Agent': 'StealthBot/1.0',
                                'X-Client-ID': 'stealth_bot_' + i
                            }
                        });
                    }
                    alert('Fired Multi-IP Low & Slow Attack to CY-02!');
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/products")
def products(): 
    return {"data": ["Laptop", "Phone"]}

# 🚨 RETURN HTTP 404 FOR ENUMERATION ATTEMPTS
@app.get("/api/users/{user_id}")
def get_user(user_id: int): 
    return JSONResponse(status_code=404, content={"status": "user_not_found"})

# 🚨 RETURN HTTP 401 FOR FAILED LOGIN ATTEMPTS
@app.post("/api/login")
def login(): 
    return JSONResponse(status_code=401, content={"status": "invalid_credentials"})

@app.post("/api/checkout")
def checkout(): 
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)