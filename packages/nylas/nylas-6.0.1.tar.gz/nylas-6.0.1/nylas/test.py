from nylas import Client

nylas = Client(
    api_key="nyk_v0_up6S8vyyNVrltKH3lUg904VN7UiRtKY4AVWoBG6oxSk8aaF9VoGR3BoiWTcnWfIy",
    api_uri="https://api-staging.us.nylas.com",
)

code_exchange_response = nylas.auth.exchange_code_for_token(
    request={
        "code": "kTYuArDhittwi9iGMBqk8mm7sEKFjZ8ONA3aKGaDCkRuPcHqc-K3Z36EiN3M3cogt9ixcvVM-pTTWpFyqQgcfuQjNSp0mUsP",
        "client_id": "5a6524f3-c7a0-40d2-82a6-f28b18392d87",
        "client_secret": "VsABbTlYZMd5C0U0b8mKaCw4zIouKEQj4",
        "redirect_uri": "http://localhost:3000",
    }
)

token_info = nylas.auth.id_token_info(
    id_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdF9oYXNoIjoiRUFnLVl0blVqZURlM1JERmFnTHFZQSIsImF1ZCI6Imh0dHBzOi8vYXBpLXN0YWdpbmcudXMubnlsYXMuY29tL3YzIiwiZW1haWwiOiJtb3N0YWZhLnJAbnlsYXMuY29tIiwiZXhwIjoxNzA3NDAzNDI1LCJmYW1pbHlfbmFtZSI6IlJhc2hlZCIsImdpdmVuX25hbWUiOiJNb3N0YWZhIiwiaWF0IjoxNzA3Mzk5ODI1LCJpc3MiOiJodHRwczovL255bGFzLmNvbSIsImxvY2FsZSI6ImVuIiwibmFtZSI6Ik1vc3RhZmEgUmFzaGVkIiwicHJvdmlkZXIiOiJnb29nbGUiLCJzdWIiOiJmYjQyYWNjNS05YzZmLTQ3OTctOWFmNC01ZjZhNGFjMTM0ODAifQ.dVLNvBLLAi18EHOL1qdHjw45KsF2HnFHJcpL5-kvOEI"
)

print(token_info)
