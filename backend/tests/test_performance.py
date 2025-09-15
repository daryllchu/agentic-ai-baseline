import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPerformance:
    
    def test_api_response_time(self):
        """Test API response times are under acceptable limits"""
        endpoints = [
            "/health",
            "/api/data-sources/",
            "/api/employees/?limit=10",
            "/api/etl/jobs?limit=10"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            response_time = time.time() - start_time
            
            assert response_time < 2.0, f"{endpoint} took {response_time:.2f}s (>2s limit)"
            assert response.status_code in [200, 401], f"{endpoint} returned {response.status_code}"
    
    def test_concurrent_requests(self):
        """Test system handles concurrent requests"""
        def make_request():
            return client.get("/health")
        
        # Test 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
    
    def test_large_dataset_handling(self):
        """Test handling of large employee datasets"""
        # This would test pagination and memory usage
        response = client.get("/api/employees/?limit=1000")
        
        # Should handle large limits gracefully
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data.get("employees", [])) <= 1000
    
    def test_memory_usage(self):
        """Test memory usage doesn't exceed limits"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests
        for _ in range(50):
            client.get("/health")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (<100MB for 50 requests)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"