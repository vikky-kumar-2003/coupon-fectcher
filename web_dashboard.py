from flask import Flask, render_template, Response, send_file, jsonify
import queue
import threading
import time
import os
import json
from datetime import datetime

app = Flask(__name__)

# Global state
log_queue = queue.Queue()
stats = {
    'batch_number': 0,
    'total_accounts': 0,
    'total_coupons': 0,
    'current_batch_accounts': 0,
    'current_batch_coupons': 0,
    'running': True
}
coupons_file = 'extracted_coupons.txt'

def log_message(message):
    """Add a log message to the queue for streaming to web clients"""
    log_queue.put({
        'timestamp': datetime.now().isoformat(),
        'message': message
    })

def update_stats(batch=None, total_accounts=None, total_coupons=None, 
                 current_batch_accounts=None, current_batch_coupons=None):
    """Update dashboard statistics"""
    if batch is not None:
        stats['batch_number'] = batch
    if total_accounts is not None:
        stats['total_accounts'] = total_accounts
    if total_coupons is not None:
        stats['total_coupons'] = total_coupons
    if current_batch_accounts is not None:
        stats['current_batch_accounts'] = current_batch_accounts
    if current_batch_coupons is not None:
        stats['current_batch_coupons'] = current_batch_coupons

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/logs')
def stream_logs():
    """Server-Sent Events endpoint for live log streaming"""
    def generate():
        while stats['running']:
            try:
                # Wait for new log message with timeout
                log = log_queue.get(timeout=1)
                yield f"data: {json.dumps(log)}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stats')
def get_stats():
    """Get current statistics"""
    return jsonify(stats)

@app.route('/coupons')
def get_coupons():
    """Get list of extracted coupons"""
    coupons = []
    if os.path.exists(coupons_file):
        try:
            with open(coupons_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Parse format: phone | code | value=X | min_order=Y
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            coupon = {
                                'phone': parts[0],
                                'code': parts[1],
                                'value': parts[2].replace('value=', ''),
                                'min_order': parts[3].replace('min_order=', '')
                            }
                            coupons.append(coupon)
        except Exception as e:
            log_message(f"Error reading coupons: {e}")
    
    return jsonify(coupons)

@app.route('/download')
def download_coupons():
    """Download the coupons file"""
    if os.path.exists(coupons_file):
        return send_file(coupons_file, as_attachment=True, download_name='extracted_coupons.txt')
    else:
        return "No coupons file found", 404

def run_server(host='127.0.0.1', port=5000):
    """Run Flask server in a separate thread"""
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

def start_dashboard(host=None, port=None):
    """Start the web dashboard in a background thread"""
    # Use Railway's PORT if available, otherwise default to 5000
    if port is None:
        port = int(os.environ.get('PORT', 5000))
    
    # Use 0.0.0.0 for Railway (public access), 127.0.0.1 for local
    if host is None:
        host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') else '127.0.0.1'
    
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    
    # Return appropriate URL based on environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Railway provides RAILWAY_PUBLIC_DOMAIN or we construct from service
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-app.up.railway.app')
        return f"https://{railway_domain}"
    else:
        return f"http://{host}:{port}"

def stop_dashboard():
    """Stop the web dashboard"""
    stats['running'] = False
