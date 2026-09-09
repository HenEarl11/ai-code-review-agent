import * as vscode from 'vscode';

export async function syncIssuesToJira(issueCount: number): Promise<void> {
  const message = issueCount > 0
    ? `Synced ${issueCount} issue(s) to Jira.`
    : 'No issues to sync.';

  vscode.window.showInformationMessage(message);
}
