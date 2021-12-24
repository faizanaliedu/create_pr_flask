import * as vscode from 'vscode';
import { JiraTaskPanel } from './JiraTaskPanel';

export function activate(context: vscode.ExtensionContext) {
	console.log('Congratulations, your extension "jiragiteasy" is now active!');
	let disposable = vscode.commands.registerCommand('jiragiteasy.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from JiraGitEasy!');
		JiraTaskPanel.createOrShow(context.extensionUri);
	});
	

	context.subscriptions.push(disposable);
	context.subscriptions.push(vscode.commands.registerCommand('jiragiteasy.askQuestion', () => {
		vscode.window.showInformationMessage('How are you today?');
	}));
}

export function deactivate() {}
