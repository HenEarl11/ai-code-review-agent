import * as vscode from 'vscode';

export class CodeLensProvider implements vscode.CodeLensProvider {
  provideCodeLenses(document: vscode.TextDocument): vscode.CodeLens[] {
    const firstLine = document.lineAt(0);
    return [
      new vscode.CodeLens(firstLine.range, {
        title: 'AI Review: Sync to Jira',
        command: 'aiCodeReview.syncJira',
      }),
    ];
  }
}
