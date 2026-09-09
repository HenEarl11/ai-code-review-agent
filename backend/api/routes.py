from flask import Blueprint, request, jsonify
from analysis.engine import AnalysisEngine
from jira.client import JiraClient
from db.database import db, AnalysisResult, JiraIssue
import hashlib
import logging

api_bp = Blueprint('api', __name__)

analysis_engine = AnalysisEngine()
jira_client = JiraClient()
logger = logging.getLogger(__name__)

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Code Review Agent Backend'
    }), 200

@api_bp.route('/analyze', methods=['POST'])
def analyze_code():
    """
    Analyze code for issues
    
    Request body:
    {
        "file_path": "path/to/file.py",
        "code": "code content",
        "language": "python"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data or 'file_path' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        code = data['code']
        file_path = data['file_path']
        language = data.get('language', 'python')
        
        # Calculate file hash for caching
        file_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Check cache
        cached = AnalysisResult.query.filter_by(file_hash=file_hash).first()
        if cached:
            return jsonify(cached.to_dict()), 200
        
        # Run analysis
        results = analysis_engine.analyze(code, file_path, language)
        
        # Store in database
        analysis_result = AnalysisResult(
            file_path=file_path,
            file_hash=file_hash,
            language=language,
            analysis_data=results
        )
        db.session.add(analysis_result)
        db.session.commit()
        
        return jsonify(analysis_result.to_dict()), 200
    
    except Exception:
        logger.exception("Failed to analyze code")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/issues', methods=['GET'])
def get_issues():
    """Get all synced Jira issues"""
    try:
        issues = JiraIssue.query.all()
        return jsonify([issue.to_dict() for issue in issues]), 200
    except Exception:
        logger.exception("Failed to fetch issues")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/jira-sync', methods=['POST'])
def sync_to_jira():
    """
    Sync analysis results to Jira
    
    Request body:
    {
        "analysis_result_id": 1,
        "create_new": true
    }
    """
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_result_id')
        
        if not analysis_id:
            return jsonify({'error': 'Missing analysis_result_id'}), 400
        
        # Get analysis result
        analysis = AnalysisResult.query.get(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis result not found'}), 404
        
        # Sync each issue to Jira
        issues = analysis.analysis_data.get('issues', [])
        synced_issues = []
        
        for issue in issues:
            jira_key = jira_client.create_issue(
                summary=issue['message'],
                description=f"File: {analysis.file_path}\nLine: {issue.get('line', 'N/A')}\n\n{issue.get('suggestion', '')}",
                issue_type=issue['type'],
                severity=issue['severity']
            )
            
            if jira_key:
                jira_issue = JiraIssue(
                    jira_key=jira_key,
                    file_path=analysis.file_path,
                    issue_type=issue['type'],
                    severity=issue['severity'],
                    line_number=issue.get('line'),
                    analysis_result_id=analysis_id
                )
                db.session.add(jira_issue)
                synced_issues.append(jira_key)
        
        db.session.commit()
        
        return jsonify({
            'status': 'synced',
            'synced_issues': synced_issues,
            'count': len(synced_issues)
        }), 200
    
    except Exception:
        logger.exception("Failed to sync issues to Jira")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/status', methods=['GET'])
def system_status():
    """Get system status"""
    try:
        from analysis.llm.inference import LLMService
        llm_service = LLMService()
        ollama_status = llm_service.check_health()
        jira_status = jira_client.check_connection()
        
        return jsonify({
            'ollama': ollama_status,
            'jira': jira_status,
            'database': 'connected'
        }), 200
    except Exception:
        logger.exception("Failed to fetch system status")
        return jsonify({'error': 'Internal server error'}), 500
