import * as vscode from 'vscode';
import { CodeLensProvider } from './codeLensProvider';
import { ConfigManager } from './configManager';
import { DiagnosticsProvider } from './diagnosticsProvider';
import { syncIssuesToJira } from './jiraIntegration';

export function activate(context: vscode.ExtensionContext): void {
  const config = new ConfigManager();
  const diagnosticsCollection = vscode.languages.createDiagnosticCollection('ai-code-review');
  const diagnosticsProvider = new DiagnosticsProvider(diagnosticsCollection);
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBarItem.text = 'AI Review: Ready';
  statusBarItem.show();

  const runAnalysis = async (document?: vscode.TextDocument): Promise<number> => {
    const target = document ?? vscode.window.activeTextEditor?.document;
    if (!target) {
      return 0;
    }

    const issues = diagnosticsProvider.publish(target);
    statusBarItem.text = `AI Review: ${issues.length} issue(s) [${config.getProfile()}]`;
    return issues.length;
  };

  context.subscriptions.push(
    diagnosticsCollection,
    statusBarItem,
    vscode.languages.registerCodeLensProvider({ scheme: 'file' }, new CodeLensProvider()),
    vscode.workspace.onDidSaveTextDocument(async (doc) => {
      await runAnalysis(doc);
    }),
    vscode.commands.registerCommand('aiCodeReview.runAnalysis', async () => {
      const count = await runAnalysis();
      vscode.window.showInformationMessage(`Analysis complete: ${count} issue(s) found via ${config.getBackendUrl()}.`);
    }),
    vscode.commands.registerCommand('aiCodeReview.syncJira', async () => {
      const count = await runAnalysis();
      await syncIssuesToJira(count);
    }),
    vscode.commands.registerCommand('aiCodeReview.openResults', async () => {
      const count = await runAnalysis();
      const panel = vscode.window.createWebviewPanel('aiCodeReview.results', 'AI Code Review Results', vscode.ViewColumn.Beside, {});
      panel.webview.html = `<html><body><h2>AI Code Review</h2><p>Detected <strong>${count}</strong> issue(s).</p></body></html>`;
    })
  );
}

export function deactivate(): void {
  // no-op
}
