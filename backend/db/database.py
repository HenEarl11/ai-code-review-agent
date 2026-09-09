from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AnalysisResult(db.Model):
    """Store analysis results"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, unique=True)
    language = db.Column(db.String(20), nullable=False)
    analysis_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_path': self.file_path,
            'language': self.language,
            'analysis_data': self.analysis_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class JiraIssue(db.Model):
    """Track synced Jira issues"""
    __tablename__ = 'jira_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    jira_key = db.Column(db.String(20), nullable=False, unique=True)
    file_path = db.Column(db.String(500), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    line_number = db.Column(db.Integer, nullable=True)
    analysis_result_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'jira_key': self.jira_key,
            'file_path': self.file_path,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'line_number': self.line_number,
            'created_at': self.created_at.isoformat(),
            'synced_at': self.synced_at.isoformat()
        }
