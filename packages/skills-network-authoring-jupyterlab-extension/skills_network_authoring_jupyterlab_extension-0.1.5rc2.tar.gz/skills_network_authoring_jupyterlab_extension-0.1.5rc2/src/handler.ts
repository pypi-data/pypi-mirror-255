/* eslint-disable no-async-promise-executor */
import { AxiosError, AxiosInstance } from 'axios';
import FormData from 'form-data';
import { INotebookModel, NotebookPanel } from '@jupyterlab/notebook';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
  showStandaloneSpinner,
  showConfirmationStatus,
  showSuccessPublishDialog,
  showFailurePublishDialog
} from './dialog';
import { Dialog } from '@jupyterlab/apputils';
import { ATLAS_BASE_URL, AWB_BASE_URL } from './config';
import { getFileContents, updateLabCommitID } from './tools';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

export const axiosHandler = (lab_token: string): AxiosInstance => {
  console.log(`base URL: ${ATLAS_BASE_URL}`);
  const atlasClient = axios.create({
    baseURL: ATLAS_BASE_URL,
    headers: {
      Authorization: `Bearer ${lab_token}`,
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      Accept: 'application/json'
    }
  });
  return atlasClient;
};

export const awbAxiosHandler = (lab_token: string): AxiosInstance => {
  console.log(`base URL: ${AWB_BASE_URL}`);
  const awbClient = axios.create({
    baseURL: AWB_BASE_URL,
    headers: {
      Authorization: `Bearer ${lab_token}`,
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      Accept: 'application/json'
    }
  });
  return awbClient;
};

/**
 * GET the lab model / JSON that represents a .ipynb file/notebook from AWB
 *
 * @param awbAxiosHandler Axios client that contains a JWT Bearer token
 * @param lab_token JWT Bearer token
 * @returns Promise<void>
 */
export const getIndependentLabModel = async (
  awbAxiosHandler: AxiosInstance,
  lab_token: string
) => {
  try {
    const token_info = jwt_decode(lab_token) as { [key: string]: any };
    const version_id = token_info.version_id;
    const lab_id = token_info.lab_id;

    console.log(
      `Fetching lab model for lab_id: ${lab_id}, version_id: ${version_id}`
    );
    const labFilename = `${token_info.lab_name}.ipynb`;
    const instructions = await awbAxiosHandler
      .get(`api/v1/labs/${lab_id}/lab_versions/${version_id}/download`)
      .then(result => {
        console.log('Lab model fetched successfully');
        return result.data;
      });

    Dialog.flush();
    return { labFilename, body: instructions };
  } catch (error) {
    throw 'Failed to fetch notebook';
  }
};

/**
 * POST the lab model / JSON from the .ipynb file/notebook to AWB
 *
 * @param awbAxiosHandler Axios client that contains a JWT Bearer token
 * @param panel Notebook panel
 * @param context Notebook context
 * @param lab_token lab token
 * @returns Promise<void>
 */
export const postIndependentLabModel = async (
  awbAxiosHandler: AxiosInstance,
  panel: NotebookPanel,
  context: DocumentRegistry.IContext<INotebookModel>,
  lab_token: string
): Promise<void> => {
  const confirmation_status = await showConfirmationStatus(
    'Publishing your lab onto Skills Network...'
  )
    .then((resolve: any) => true)
    .catch((err: any) => false);
  if (!confirmation_status) {
    return;
  }
  showStandaloneSpinner('Publishing your changes...');

  const token_info = jwt_decode(lab_token) as { [key: string]: any };
  const version_id = token_info.version_id;
  const lab_id = token_info.lab_id;
  // Create hash and update the metadata.
  // Hash is used to signal changes to the notebook between pulling and pushing lab content

  await updateLabCommitID(panel, context);

  // Get the current file contents
  const labModel: string = await getFileContents(panel, context);

  const formData = new FormData();
  formData.append('publish', 'true');
  formData.append('draft[changelog]', 'updated notebook');
  formData.append('file', labModel);

  console.log(
    `Posting lab model to AWB for lab_id: ${lab_id}, version_id: ${version_id}`
  );
  return new Promise<void>(async (resolve, reject) => {
    await awbAxiosHandler
      .post(`api/v1/labs/${lab_id}/lab_versions/${version_id}/drafts`, formData)
      .then(res => {
        console.log('SUCCESSFULLY PUSHED', res);
        Dialog.flush(); //remove spinner
        showSuccessPublishDialog();
        resolve();
      })
      .catch((error: AxiosError) => {
        Dialog.flush(); // remove spinner
        showFailurePublishDialog();
        reject(new Error('Failed to post lab model'));
      });
  });
};

/**
 * GET the lab model / JSON that represents a .ipynb file/notebook from ATLAS
 *
 * @param axiosHandler Axios client that contains a JWT Bearer token
 * @returns Promise<void>
 */
export const getLabModel = (axiosHandler: AxiosInstance) => {
  return axiosHandler
    .get('v1/labs')
    .then(result => {
      Dialog.flush(); //remove spinner
      return result.data;
    })
    .catch(error => {
      throw 'Failed to fetch notebook';
    });
};

/**
 * POST the lab model / JSON from the .ipynb file/notebook to ATLAS
 *
 * @param axiosHandler Axios client that contains a JWT Bearer token
 * @param panel Notebook panel
 * @param context Notebook context
 * @returns Promise<void>
 */
export const postLabModel = async (
  axiosHandler: AxiosInstance,
  panel: NotebookPanel,
  context: DocumentRegistry.IContext<INotebookModel>
): Promise<void> => {
  const confirmation_status = await showConfirmationStatus(
    'Publishing your lab onto Skills Network...'
  )
    .then((resolve: any) => true)
    .catch((err: any) => false);
  if (!confirmation_status) {
    return;
  }
  showStandaloneSpinner('Publishing your changes...');

  console.log('Updating lab commit ID');
  await updateLabCommitID(panel, context);

  const labModel: string = await getFileContents(panel, context);

  console.log('Posting lab model to ATLAS');
  return new Promise<void>(async (resolve, reject) => {
    await axiosHandler
      .post('v1/labs', {
        body: labModel
      })
      .then(res => {
        Dialog.flush(); //remove spinner
        showSuccessPublishDialog();
        resolve();
      })
      .catch((error: AxiosError) => {
        Dialog.flush(); // remove spinner
        showFailurePublishDialog();
        reject(new Error('Failed to post lab model to ATLAS'));
      });
  });
};
