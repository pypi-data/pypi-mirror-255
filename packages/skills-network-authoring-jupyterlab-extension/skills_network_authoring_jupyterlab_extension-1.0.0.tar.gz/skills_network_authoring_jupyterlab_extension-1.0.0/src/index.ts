import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import menu from './menu';
import toolbar from './toolbar';

console.log('Initializing JupyterFrontEnd plugins for the extension.');

const main: JupyterFrontEndPlugin<any>[] = [menu, toolbar];

console.log(
  'JupyterFrontEnd plugins defined:',
  main.map(p => p.id)
);

export default main;
