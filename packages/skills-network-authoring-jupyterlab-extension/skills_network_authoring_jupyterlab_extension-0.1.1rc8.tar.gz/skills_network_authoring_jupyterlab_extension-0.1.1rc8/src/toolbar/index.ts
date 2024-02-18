import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { Dialog, showDialog, ToolbarButton } from '@jupyterlab/apputils';
import { getFileContents, openLab, openIndependentLab } from '../tools';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import {
  axiosHandler,
  postLabModel,
  awbAxiosHandler,
  postIndependentLabModel
} from '../handler';
import { showFailureImportLabDialog } from '../dialog';
import { Globals } from '../config';
import {
  extractAtlasTokenFromQuery,
  extractAwbTokenFromQuery,
  SET_DEFAULT_LAB_NAME_AND_KERNEL,
  MODE
} from '../config';
import jwt_decode from 'jwt-decode';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  NotebookPanel,
  INotebookModel,
  INotebookTracker
} from '@jupyterlab/notebook';

import { SkillsNetworkFileLibrary } from '../sn-file-library';

/**
 * The plugin registration information.
 */
const toolbar: JupyterFrontEndPlugin<void> = {
  id: 'skills_network_authoring_jupyterlab_extension:toolbar',
  description: 'Toolbar plugin for Skills Network Authoring Extension',
  autoStart: true,
  requires: [INotebookTracker, IDocumentManager],
  activate
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
/**
 * Clean up workspace by closing all opened widgets
 */
async function cleanUpEnvironment(
  notebookTracker: INotebookTracker
): Promise<void> {
  console.log(
    '[cleanUpEnvironment] Cleaning up environment by closing all opened notebook widgets.'
  );
  notebookTracker.forEach(notebookPanel => {
    notebookPanel.dispose();
  });
}

export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  /**
   * Create a new extension for the notebook panel widget.
   *
   * @param panel Notebook panel
   * @param context Notebook context
   * @returns Disposable on the added button
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    console.log(
      `[ButtonExtension] createNew invoked for notebook: ${context.path}`
    );
    if (Globals.SHOW_PUBLISH_BUTTON_FOR !== context.path) {
      console.log(
        '[ButtonExtension] No publish button due to context path mismatch.'
      );
      // This is not a Skills Network Lab notebook so return a no-op disposable
      return new DisposableDelegate(() => {});
    } else {
      // This is a Skills Network Lab notebook so add the publish button
      const start = async () => {
        console.log('[ButtonExtension] Publish button clicked.');

        // POST to Atlas the file contents/lab model
        const fullPath: string = context.path;
        const filename: string = fullPath.split('/').pop() || '';
        const token = Globals.TOKENS.get(filename);
        if (token === undefined) {
          console.log(
            `[ButtonExtension] No token found for filename: ${filename}`
          );
          await showDialog({
            title: 'Publishing Restricted',
            body: `Only the lab '${
              Globals.TOKENS.keys().next().value
            }' can be published during this editing session.`,
            buttons: [Dialog.okButton({ label: 'Dismiss' })]
          });
          return;
        }
        console.log(
          `[ButtonExtension] Token found for filename: ${filename}, proceeding with lab model post.`
        );
        const token_info = jwt_decode(token) as { [key: string]: any };

        if ('version_id' in token_info) {
          await postIndependentLabModel(
            awbAxiosHandler(token),
            panel,
            context,
            token
          );
        } else {
          await postLabModel(axiosHandler(token), panel, context);
        }
      };

      const download = async () => {
        console.log('[ButtonExtension] Download button clicked.');
        const file = await getFileContents(panel, context);
        const blob = new Blob([file], { type: 'application/x-ipynb+json' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.setAttribute('download', context.path);
        link.setAttribute('href', url);

        document.body.appendChild(link);
        link.click();

        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      };

      const downloadButton = new ToolbarButton({
        className: 'download-lab-button',
        label: 'Download Notebook',
        onClick: download,
        tooltip: 'Download the current notebook ipynb file to your local system'
      });

      const publishButton = new ToolbarButton({
        className: 'publish-lab-button',
        label: 'Publish on SN',
        onClick: start,
        tooltip: 'Publish Lab'
      });

      const snFileLibraryButton = new ToolbarButton({
        className: 'sn-file-library-button',
        label: 'SN File Library',
        onClick: () => {
          console.log('[ButtonExtension] SN File Library button clicked.');
          new SkillsNetworkFileLibrary(panel.id).launch();
        },
        tooltip: 'Skills Network File Library'
      });

      console.log('[ButtonExtension] Adding buttons to notebook toolbar.');
      panel.toolbar.insertItem(8, 'download', downloadButton);
      panel.toolbar.insertItem(9, 'sn-file-library', snFileLibraryButton);
      panel.toolbar.insertItem(10, 'publish', publishButton);
      return new DisposableDelegate(() => {
        console.log(
          '[ButtonExtension] Disposing buttons from notebook toolbar.'
        );
        downloadButton.dispose();
        publishButton.dispose();
        snFileLibraryButton.dispose();
      });
    }
  }
}

/**
 * Activate the extension.
 *
 * @param app Main application object
 */
async function activate(
  app: JupyterFrontEnd,
  notebookTracker: INotebookTracker,
  docManager: IDocumentManager
) {
  console.log('Activating skillsnetwork-authoring-extension button plugin!');
  if ((await MODE()) === 'learn') {
    console.log('[activate] Mode is "learn", not activating plugin.');
    return;
  }

  console.log('[activate] Initializing globals and attempting to open lab...');
  const token = await extractAtlasTokenFromQuery();
  const awb_token = await extractAwbTokenFromQuery();
  const env_type = await SET_DEFAULT_LAB_NAME_AND_KERNEL();
  console.log('Using default kernel: ', Globals.PY_KERNEL_NAME);
  console.log('[activate] Environment type set, adding widget extension.');

  console.log(
    'skills_network_authoring_jupyterlab_extension:toolbar extension activated'
  );

  // Only show toolbar buttons for the lab that's launched via token
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension());

  // Try to load up a notebook when author is using the browser tool (not in local)
  await app.serviceManager.ready;
  app.restored.then(async () => {
    console.log('[activate] App restored, cleaning up environment.');
    await cleanUpEnvironment(notebookTracker);
    if (token !== 'NO_TOKEN' && env_type !== 'local') {
      try {
        console.log('[activate] Opening lab with Atlas token.');
        await openLab(token, docManager, app.serviceManager.contents);
      } catch (e) {
        console.error('[activate] Error opening lab with Atlas token:', e);
        Dialog.flush(); // remove spinner
        showFailureImportLabDialog();
      }
    } else if (awb_token !== 'NO_TOKEN' && env_type !== 'local') {
      try {
        console.log('[activate] Opening lab with AWB token.');
        await openIndependentLab(
          awb_token,
          docManager,
          app.serviceManager.contents
        );
      } catch (e) {
        console.error('[activate] Error opening lab with AWB token:', e);
        Dialog.flush(); // remove spinner
        showFailureImportLabDialog();
      }
    }
  });
  console.log('[activate] Plugin activated successfully.');
}

/**
 * Export the plugin as default.
 */
export default toolbar;
