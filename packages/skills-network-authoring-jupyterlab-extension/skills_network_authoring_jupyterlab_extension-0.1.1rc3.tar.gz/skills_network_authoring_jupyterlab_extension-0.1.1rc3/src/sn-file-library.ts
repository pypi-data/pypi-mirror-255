import { Widget } from '@lumino/widgets';
import { Dialog } from '@jupyterlab/apputils';
import { Globals, SN_FILE_LIBRARY_URL } from './config';
import jwt_decode from 'jwt-decode';

export class SkillsNetworkFileLibraryWidget extends Widget {
  constructor(nbPanelId: string) {
    console.log(
      `Creating SkillsNetworkFileLibraryWidget with nbPanelId: ${nbPanelId}`
    );
    const frame = document.createElement('iframe');
    const token = Globals.TOKENS.get(nbPanelId);
    console.log(`Retrieved token for nbPanelId ${nbPanelId}: ${token}`);
    const token_info = token
      ? (jwt_decode(token) as { [key: string]: any })
      : {};
    console.log('Decoded token info:', token_info);
    if ('project_id' in token_info) {
      frame.src = `${SN_FILE_LIBRARY_URL}?atlas_token=${token}`;
      console.log(`Setting iframe src to ${frame.src}`);
    }
    frame.setAttribute('frameborder', '0');
    frame.setAttribute('allow', 'clipboard-read; clipboard-write');
    frame.classList.add('sn-file-library-frame');
    super({ node: frame });
    console.log('SkillsNetworkFileLibraryWidget created.');
  }
}

export class SkillsNetworkFileLibrary {
  #nbPanelId: string;

  constructor(nbPanelId: string) {
    console.log(
      `Initializing SkillsNetworkFileLibrary with nbPanelId: ${nbPanelId}`
    );
    this.#nbPanelId = nbPanelId;
  }

  launch() {
    console.log(
      `Launching SkillsNetworkFileLibrary dialog for nbPanelId: ${this.#nbPanelId}`
    );
    const imgLibDialog = new Dialog({
      title: 'Skills Network File Library',
      body: new SkillsNetworkFileLibraryWidget(this.#nbPanelId),
      hasClose: true,
      buttons: []
    });
    console.log('SkillsNetworkFileLibrary dialog created.');

    const dialogContent = imgLibDialog.node.querySelector('.jp-Dialog-content');
    if (dialogContent) {
      dialogContent.classList.add('sn-file-library-dialog');
      console.log("Added 'sn-file-library-dialog' class to dialog content.");
    }
    imgLibDialog
      .launch()
      .then(() => {
        console.log('SkillsNetworkFileLibrary dialog launched.');
      })
      .catch(err => {
        console.error('Error launching SkillsNetworkFileLibrary dialog:', err);
      });
  }
}
