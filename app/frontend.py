html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Rate Limiter Demo</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }
        * { box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }
        .card { background: var(--surface); padding: 30px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 450px; }
        h1 { margin-top: 0; font-weight: 800; font-size: 1.5rem; text-align: center; }
        input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font-size: 1rem; }
        button { background: var(--primary); font-weight: 600; border: none; cursor: pointer; transition: background 0.2s, transform 0.1s; }
        button:hover { background: var(--primary-hover); }
        button:active { transform: scale(0.98); }
        .danger { background: var(--danger); }
        .danger:hover { background: #dc2626; }
        .hidden { display: none; }
        #logs { background: var(--bg); padding: 15px; border-radius: 8px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.85rem; color: #a7f3d0; margin-top: 15px; border: 1px solid var(--border); }
        .log-error { color: #fca5a5; }
        .stat-box { display: flex; justify-content: space-between; background: var(--bg); padding: 15px; border-radius: 8px; border: 1px solid var(--border); margin: 15px 0; }
        .stat { text-align: center; }
        .stat-val { font-size: 1.5rem; font-weight: 800; color: var(--primary); }
    </style>
</head>
<body>
    <div class="card" id="auth-panel">
        <h1>Rate Limiter API</h1>
        <p style="text-align: center; color: var(--text-muted); font-size: 0.9rem;">Login to test the API demo.</p>
        <input type="email" id="email" placeholder="demo@test.com" value="demo@test.com">
        <input type="password" id="password" placeholder="password123" value="password123">
        <button onclick="login()">Login & Get Token</button>
    </div>

    <div class="card hidden" id="app-panel">
        <h1>API Dashboard</h1>
        
        <div class="stat-box">
            <div class="stat">
                <div class="stat-val" id="val-limit">5</div>
                <div style="color: var(--text-muted); font-size: 0.8rem;">Limit / 60s</div>
            </div>
            <div class="stat">
                <div class="stat-val" id="val-remaining">?</div>
                <div style="color: var(--text-muted); font-size: 0.8rem;">Remaining</div>
            </div>
        </div>

        <button onclick="sendTransaction()">Send Transaction</button>
        <button onclick="sendIdempotent()" style="background: #10b981;">Send Idempotent (Same Key)</button>
        
        <div id="logs"></div>
    </div>

    <script>
        let token = "";
        let idempKey = "key-" + Math.random().toString(36).substring(7);

        function log(msg, isError=false) {
            const logs = document.getElementById('logs');
            logs.innerHTML = `<div class="${isError ? 'log-error' : ''}">> ${msg}</div>` + logs.innerHTML;
        }

        async function login() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            try {
                const res = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({email, password})
                });
                const data = await res.json();
                if(data.access_token) {
                    token = data.access_token;
                    document.getElementById('auth-panel').classList.add('hidden');
                    document.getElementById('app-panel').classList.remove('hidden');
                    log("Logged in! Token acquired.");
                    updateStatus();
                } else {
                    alert(data.detail);
                }
            } catch(e) { alert("Error connecting to API"); }
        }

        async function updateStatus() {
            const res = await fetch('/ratelimit/status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                if (data.remaining !== undefined) {
                    document.getElementById('val-remaining').innerText = data.remaining;
                }
            }
        }

        async function makeRequest(headers) {
            try {
                const res = await fetch('/transactions', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}`, ...headers }
                });
                const data = await res.json();
                
                if (res.status === 429) {
                    log(`HTTP 429: ${data.detail}`, true);
                    document.getElementById('val-remaining').innerText = 0;
                } else if (res.ok) {
                    log(`HTTP 200: ${data.message}`);
                    document.getElementById('val-remaining').innerText = data.rate_limit.remaining;
                } else {
                    log(`HTTP ${res.status}: ${JSON.stringify(data)}`, true);
                }
            } catch(e) {
                log(`Network Error: ${e.message}`, true);
            }
        }

        function sendTransaction() {
            makeRequest({ 'Idempotency-Key': "txn-" + Math.random().toString(36).substring(7) });
        }

        function sendIdempotent() {
            makeRequest({ 'Idempotency-Key': idempKey });
        }
    </script>
</body>
</html>
"""
