

def parse_login_details(login_details,name):
    """Parse login details string into a dictionary."""
    parts = login_details.split(':')
    return {
        'name':name,
        'email': parts[0],
        'password': parts[1],
        'recovery_mail': parts[2]
    }

def parse_proxy_details(proxy_details):
    """Parse proxy details string into a dictionary."""
    if not proxy_details or proxy_details.lower() == 'none':
        return None
    
    parts = proxy_details.split(':')
    return {
        'ip': parts[0],
        'port': parts[1],
        'username': parts[2],
        'password': parts[3]
    }
