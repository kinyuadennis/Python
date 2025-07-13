import requests
from bs4 import BeautifulSoup
import tldextract

# List of domains to test
domains = [
    "secure-paypal-login.com",
    "accounts.google.com",
    "login-apple-support.ru",
    "mybanksecurity-alert.net"
]

# Suspicious keywords often used in phishing
phishing_keywords = ['login', 'secure', 'verify', 'update', 'account', 'password']

def check_domain(domain):
    try:
        print(f"\n🔍 Checking: {domain}")
        # Check keyword in domain
        domain_parts = tldextract.extract(domain)
        full_domain = f"{domain_parts.subdomain}.{domain_parts.domain}.{domain_parts.suffix}"
        keyword_flag = any(keyword in domain for keyword in phishing_keywords)

        # Make HTTP request
        response = requests.get(f"http://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for login forms
        has_form = bool(soup.find('form'))
        has_password_input = bool(soup.find('input', {'type': 'password'}))

        # Final flag
        is_suspicious = keyword_flag or has_password_input

        result = {
            "domain": domain,
            "keyword_flag": keyword_flag,
            "has_form": has_form,
            "has_password_input": has_password_input,
            "is_suspicious": is_suspicious
        }

        print(result)
        return result

    except Exception as e:
        print(f"❌ Failed to scan {domain}: {e}")
        return None

# Run scanner
for d in domains:
    check_domain(d)

