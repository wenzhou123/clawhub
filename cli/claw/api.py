"""API client for ClawHub."""

import json
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from claw.config import config_manager


class APIError(Exception):
    """API error exception."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ClawHubAPI:
    """ClawHub API client."""
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or config_manager.get_api_url()
        self.token = token or config_manager.get_token()
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_headers(self, content_type: bool = True) -> Dict[str, str]:
        """Get request headers."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if content_type:
            headers["Content-Type"] = "application/json"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        try:
            data = response.json() if response.text else {}
        except json.JSONDecodeError:
            data = {"message": response.text}
        
        if not response.ok:
            message = data.get("message", data.get("error", f"HTTP {response.status_code}"))
            raise APIError(message, response.status_code, data)
        
        return data
    
    def _url(self, path: str) -> str:
        """Build full URL."""
        return urljoin(f"{self.base_url}/", path.lstrip("/"))
    
    # Authentication
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get token."""
        response = self.session.post(
            self._url("/api/v1/auth/login"),
            json={"username": username, "password": password},
        )
        return self._handle_response(response)
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info."""
        response = self.session.get(
            self._url("/api/v1/auth/me"),
            headers=self._get_headers(),
        )
        return self._handle_response(response)
    
    # Lobsters
    
    def search_lobsters(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search lobsters."""
        response = self.session.get(
            self._url("/api/v1/lobsters/search"),
            headers=self._get_headers(),
            params={"q": keyword, "limit": limit},
        )
        return self._handle_response(response)
    
    def list_my_lobsters(self) -> List[Dict[str, Any]]:
        """List user's lobsters."""
        response = self.session.get(
            self._url("/api/v1/lobsters/mine"),
            headers=self._get_headers(),
        )
        return self._handle_response(response)
    
    def get_lobster(self, namespace: str, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get lobster details."""
        path = f"/api/v1/lobsters/{namespace}/{name}"
        if version:
            path = f"{path}/versions/{version}"
        
        response = self.session.get(
            self._url(path),
            headers=self._get_headers(),
        )
        return self._handle_response(response)
    
    def download_lobster(self, namespace: str, name: str, version: str, output_path: str) -> str:
        """Download lobster package."""
        path = f"/api/v1/lobsters/{namespace}/{name}/versions/{version}/download"
        
        response = self.session.get(
            self._url(path),
            headers=self._get_headers(content_type=False),
            stream=True,
        )
        
        if not response.ok:
            self._handle_response(response)  # Will raise APIError
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return output_path
    
    def upload_lobster(self, namespace: str, name: str, version: str, file_path: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Upload lobster package."""
        path = f"/api/v1/lobsters/{namespace}/{name}/versions"
        
        with open(file_path, "rb") as f:
            files = {"file": (f"{name}-{version}.clawpack", f, "application/gzip")}
            data = {"version": version}
            if description:
                data["description"] = description
            
            # Don't include Content-Type header, requests will set it with boundary
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = self.session.post(
                self._url(path),
                headers=headers,
                data=data,
                files=files,
            )
        
        return self._handle_response(response)
    
    def check_namespace_available(self, namespace: str) -> bool:
        """Check if namespace is available."""
        try:
            response = self.session.get(
                self._url(f"/api/v1/namespaces/{namespace}/check"),
                headers=self._get_headers(),
            )
            result = self._handle_response(response)
            return result.get("available", False)
        except APIError:
            return False


# Global API client instance
def get_api() -> ClawHubAPI:
    """Get API client instance."""
    return ClawHubAPI()
