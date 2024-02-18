import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { Contents } from '@jupyterlab/services';
import { show_spinner, showFailureImportLabDialog } from '../dialog';
import { MODE } from '../config';
import { openIndependentLab, openLab } from '../tools';
import jwt_decode from 'jwt-decode';

const menu: JupyterFrontEndPlugin<void> = {
  id: 'skills_network_authoring_jupyterlab_extension:menu',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker, IDocumentManager],
  activate: async (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    notebookTracker: INotebookTracker,
    docManager: IDocumentManager
  ) => {
    console.log(
      'skills_network_authoring_jupyterlab_extension:menu extension activated'
    );
    if ((await MODE()) === 'learn') {
      console.log(
        'The current mode is "learn". The menu will not be activated.'
      );
      return;
    }
    const { commands } = app;

    const commandID = 'mainMenu:editLabFromToken';
    commands.addCommand(commandID, {
      label: 'Edit a Lab',
      execute: (args: any) => {
        console.log('Executing editLabFromToken command...');
        showTokenDialog(
          notebookTracker,
          docManager,
          app.serviceManager.contents
        );
      }
    });

    const category = 'skillsNetwork';
    palette.addItem({
      command: commandID,
      category,
      args: { origin: 'from the palette' }
    });
  }
};

export default menu;

function showTokenDialog(
  notebookTracker: INotebookTracker,
  docManager: IDocumentManager,
  contentsManager: Contents.IManager
): void {
  console.log('Showing token dialog for editing a lab...');

  // Generate Dialog body
  const bodyDialog = document.createElement('div');
  const nameLabel = document.createElement('label');
  nameLabel.textContent = 'Enter your authorization token';
  const tokenInput = document.createElement('input');
  tokenInput.className = 'jp-mod-styled';
  bodyDialog.appendChild(nameLabel);
  bodyDialog.appendChild(tokenInput);

  showDialog({
    title: 'Edit a Lab',
    body: new Widget({ node: bodyDialog }),
    buttons: [Dialog.cancelButton(), Dialog.okButton()]
  })
    .then(async result => {
      if (result.button.accept) {
        console.log('Token dialog accepted, loading lab...');
        show_spinner('Loading up your lab...');

        const token = tokenInput.value;
        console.log(`Token received: ${token.substring(0, 15)}...`);

        const token_info = jwt_decode(token) as { [key: string]: any };
        if ('version_id' in token_info) {
          console.log('Token contains version_id, opening independent lab...');
          await openIndependentLab(token, docManager, contentsManager);
        } else {
          console.log('Token does not contain version_id, opening lab...');
          await openLab(token, docManager, contentsManager);
        }
      } else {
        console.log('Token dialog canceled by the user.');
      }
    })
    .catch(e => {
      Dialog.flush(); //remove spinner
      showFailureImportLabDialog();
      console.error('Error occurred while importing lab:', e);
    });
}
