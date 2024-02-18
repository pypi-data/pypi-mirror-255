import { ServerConnection } from '@jupyterlab/services';
import { KernelSpecAPI } from '@jupyterlab/services';

interface IConfiguration {
  ATLAS_BASE_URL: string;
  SN_FILE_LIBRARY_URL: string;
  AWB_BASE_URL: string;
}

const getServerBaseUrl = (settings: ServerConnection.ISettings): string => {
  let baseUrl = settings.baseUrl;
  // Add the trailing slash if it is missing.
  if (!baseUrl.endsWith('/')) {
    baseUrl += '/';
  }
  return baseUrl;
};

export const ATLAS_BASE_URL = await (async (): Promise<string> => {
  const currentUrl = window.location.href;

  const parameters = new URL(currentUrl).searchParams;
  const baseUrl: string | undefined = parameters.get('atlas_base_url')!;
  if (baseUrl === null) {
    console.log(
      'ATLAS_BASE_URL not found in URL parameters, making server request...'
    );
    const init: RequestInit = {
      method: 'GET'
    };
    const settings = ServerConnection.makeSettings();
    const requestUrl =
      getServerBaseUrl(settings) +
      'skills_network_authoring_jupyterlab_extension/config';
    const response = await ServerConnection.makeRequest(
      requestUrl,
      init,
      settings
    );
    const configuration: IConfiguration =
      (await response.json()) as IConfiguration;
    return configuration.ATLAS_BASE_URL;
  } else {
    return decodeURIComponent(baseUrl);
  }
})();

export const AWB_BASE_URL = await (async (): Promise<string> => {
  const currentUrl = window.location.href;
  const parameters = new URL(currentUrl).searchParams;
  const baseUrl: string | undefined = parameters.get('awb_base_url')!;
  if (baseUrl === null) {
    const init: RequestInit = {
      method: 'GET'
    };
    const settings = ServerConnection.makeSettings();
    const requestUrl =
      getServerBaseUrl(settings) +
      'skills_network_authoring_jupyterlab_extension/config';
    const response = await ServerConnection.makeRequest(
      requestUrl,
      init,
      settings
    );
    const configuration: IConfiguration =
      (await response.json()) as IConfiguration;
    return configuration.AWB_BASE_URL;
  } else {
    return decodeURIComponent(baseUrl);
  }
})();

export const SN_FILE_LIBRARY_URL = await (async (): Promise<string> => {
  const currentUrl = window.location.href;

  const parameters = new URL(currentUrl).searchParams;
  const snFileLibraryURL: string | undefined = parameters.get(
    'sn_file_library_url'
  )!;
  if (snFileLibraryURL === null) {
    const init: RequestInit = {
      method: 'GET'
    };
    const settings = ServerConnection.makeSettings();
    const requestUrl =
      getServerBaseUrl(settings) +
      'skills_network_authoring_jupyterlab_extension/config';
    const response = await ServerConnection.makeRequest(
      requestUrl,
      init,
      settings
    );
    const configuration: IConfiguration =
      (await response.json()) as IConfiguration;
    return configuration.SN_FILE_LIBRARY_URL;
  } else {
    return decodeURIComponent(snFileLibraryURL);
  }
})();

/**
 * Extracts the session token. Will first try to get a token via the URL, if none was found then try to get the token via cookie.
 *
 * @returns token
 */
export const MODE = async (): Promise<string> => {
  const currentURL = window.location.href;
  const params = new URL(currentURL).searchParams;
  const mode: string | null = params.get('mode');

  return mode === 'learn' ? mode : 'author';
};

/**
 * Extracts the session token. Will first try to get a token via the URL, if none was found then try to get the token via cookie.
 *
 * @returns token
 */
export const extractAtlasTokenFromQuery = async (): Promise<string> => {
  const currentURL = window.location.href;
  const params = new URL(currentURL).searchParams;
  const token_from_query = params.get('atlas_token');

  return token_from_query !== null ? token_from_query : 'NO_TOKEN';
};

export const extractAwbTokenFromQuery = async (): Promise<string> => {
  const currentURL = window.location.href;
  const params = new URL(currentURL).searchParams;
  const token_from_query = params.get('awb_token');

  return token_from_query !== null ? token_from_query : 'NO_TOKEN';
};

export const SET_DEFAULT_LAB_NAME_AND_KERNEL = async (): Promise<string> => {
  const currentURL = window.location.href;
  const params = new URL(currentURL).searchParams;
  let env_type = params.get('env_type');

  if (env_type !== 'jupyterlab' && env_type !== 'jupyterlite') {
    env_type = 'local';
  }

  console.log('Env type: ', env_type);

  if (env_type === 'jupyterlab' || env_type === 'local') {
    // In production, jupyterlab doesn't have python3 as a kernel option so use python
    Globals.PY_KERNEL_NAME = await GET_PYKERNEL();
    Globals.DEFAULT_LAB_NAME = 'lab.ipynb';
  } else if (env_type === 'jupyterlite') {
    Globals.PY_KERNEL_NAME = 'python';
    Globals.DEFAULT_LAB_NAME = 'lab.jupyterlite.ipynb';
  }
  return env_type;
};

/**
 * Gets the python kernel. If more than one python kernel is found, prioritize python3. If only one python kernel is found, select that kernel
 *
 * @returns pykernel
 */
export const GET_PYKERNEL = async (): Promise<string> => {
  // Get the available kernels
  const kspecs = await (await KernelSpecAPI.getSpecs()).kernelspecs;

  function checkPython(spec: string) {
    return spec.includes('python');
  }

  const keys = Object.keys(kspecs);
  // filter for only the spec names with python in it, sorted
  const filtered_keys = keys.filter(checkPython).sort();
  // return the priority python
  const pykernel = filtered_keys[filtered_keys.length - 1];

  return pykernel;
};

// Global variables
export class Globals {
  public static TOKENS: Map<string, string> = new Map<string, string>();
  public static PY_KERNEL_NAME: string;
  public static DEFAULT_LAB_NAME: string;
  public static SHOW_PUBLISH_BUTTON_FOR: string | undefined = undefined;
  public static readonly PREV_PUB_HASH: string = 'prev_pub_hash' as const;
  public static readonly BACKUP_EXT: string = '.backup' as const;
}
