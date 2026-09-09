import * as vscode from 'vscode';

export type ReviewIssue = {
  line: number;
  message: string;
  severity: vscode.DiagnosticSeverity;
};

export class DiagnosticsProvider {
  constructor(private readonly collection: vscode.DiagnosticCollection) {}

  analyzeDocument(document: vscode.TextDocument): ReviewIssue[] {
    const content = document.getText();
    const issues: ReviewIssue[] = [];

    if (content.includes('dangerouslySetInnerHTML')) {
      issues.push({ line: this.findLine(content, 'dangerouslySetInnerHTML'), message: 'Potential XSS risk detected.', severity: vscode.DiagnosticSeverity.Error });
    }

    if (content.includes('console.log')) {
      issues.push({ line: this.findLine(content, 'console.log'), message: 'Console logging found in production code.', severity: vscode.DiagnosticSeverity.Warning });
    }

    if (content.includes('except:')) {
      issues.push({ line: this.findLine(content, 'except:'), message: 'Bare except clause detected.', severity: vscode.DiagnosticSeverity.Warning });
    }

    return issues;
  }

  publish(document: vscode.TextDocument): ReviewIssue[] {
    const issues = this.analyzeDocument(document);
    const diagnostics = issues.map((issue) => {
      const position = new vscode.Position(Math.max(0, issue.line), 0);
      return new vscode.Diagnostic(new vscode.Range(position, position), issue.message, issue.severity);
    });

    this.collection.set(document.uri, diagnostics);
    return issues;
  }

  private findLine(content: string, token: string): number {
    const index = content.indexOf(token);
    if (index === -1) {
      return 0;
    }

    return content.slice(0, index).split('\n').length - 1;
  }
}
