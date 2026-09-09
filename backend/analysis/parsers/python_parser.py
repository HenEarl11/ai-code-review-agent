import ast
from typing import Dict, Any

class PythonParser:
    """Parse Python code and extract AST information"""
    
    def parse(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code and return structured data
        
        Args:
            code (str): Python source code
        
        Returns:
            dict: Parsed data including AST, imports, functions, classes, etc.
        """
        try:
            tree = ast.parse(code)
            
            return {
                'ast': tree,
                'imports': self._extract_imports(tree),
                'functions': self._extract_functions(tree),
                'classes': self._extract_classes(tree),
                'variables': self._extract_variables(tree),
                'lines_of_code': len(code.split('\n')),
                'code': code
            }
        
        except SyntaxError as e:
            return {
                'error': f'Syntax error at line {e.lineno}: {e.msg}',
                'line': e.lineno
            }
    
    def _extract_imports(self, tree: ast.AST) -> list:
        """Extract all imports from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'name': alias.name,
                        'asname': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        'type': 'from',
                        'module': node.module,
                        'name': alias.name,
                        'asname': alias.asname,
                        'line': node.lineno
                    })
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> list:
        """Extract all functions from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if node.returns else None,
                    'decorators': [ast.unparse(d) for d in node.decorator_list]
                })
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> list:
        """Extract all classes from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': [ast.unparse(b) for b in node.bases],
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
        return classes
    
    def _extract_variables(self, tree: ast.AST) -> list:
        """Extract module-level variables from AST"""
        variables = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            'name': target.id,
                            'line': node.lineno
                        })
        return variables
