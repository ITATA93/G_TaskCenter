Create tests for the specified code:

1. Analyze the target file or function: {{input}}
2. Detect the testing framework from project:
   - Python: pytest (look for pytest.ini, conftest.py)
   - JavaScript/TypeScript: jest (look for jest.config.js)
   - Other: ask user
3. Generate comprehensive tests:
   - Happy path tests
   - Edge cases
   - Error cases
   - Boundary conditions
4. Use mocks for external dependencies (DB, APIs, filesystem)
5. NEVER use real sensitive data - generate mock data
6. Follow naming convention: test_{function_name}_{scenario}
7. Include descriptive docstrings/comments
8. Place in appropriate tests/ subdirectory

Output the complete test file content ready to save.
Include any new dependencies needed in requirements.txt or package.json.
