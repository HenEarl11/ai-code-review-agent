import * as vscode from 'vscode';

export type AnalysisProfile = 'strict' | 'balanced' | 'fast';

export class ConfigManager {
  getBackendUrl(): string {
    return vscode.workspace.getConfiguration('aiCodeReview').get<string>('backendUrl', 'http://localhost:8080');
  }

  getProfile(): AnalysisProfile {
    return vscode.workspace.getConfiguration('aiCodeReview').get<AnalysisProfile>('configuration', 'balanced');
  }
}
