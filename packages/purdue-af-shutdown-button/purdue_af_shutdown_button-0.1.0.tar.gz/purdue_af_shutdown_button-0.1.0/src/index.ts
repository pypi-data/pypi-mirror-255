import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  IRouter
} from '@jupyterlab/application';

import { Widget } from '@lumino/widgets';

import { URLExt } from '@jupyterlab/coreutils';

import { Dialog, showDialog } from '@jupyterlab/apputils';

import { ServerConnection } from '@jupyterlab/services';

import '@jupyterlab/application/style/buttons.css';

import '../style/index.css';


const plugin: JupyterFrontEndPlugin<void> = {
  id: 'purdue-af-shutdown-button:plugin',
  description: 'Adds a button that shuts down Jupyter server',
  autoStart: true,
  requires: [IRouter],
  activate: async (
    app: JupyterFrontEnd,
    router: IRouter
  ) => {
    console.log('JupyterLab extension purdue-af-shutdown-button is activated!');
    const { commands } = app;
    const namespace = 'jupyterlab-topbar';
    const command = namespace + ':shutdown';
  
    commands.addCommand(command, {
      label: 'Shut Down',
      caption: 'Shut down user session',
      className: 'jp-RunningSessions-shutdownAll',
      execute: (args: any) => {
        return showDialog({
          title: 'Shut down Analysis Facility session',
          body: 'Warning: unsaved data will be lost!',
          buttons: [
            Dialog.cancelButton(),
            Dialog.warnButton({ label: 'Shut Down' })
          ]
        }).then(async (result: any) => {
          if (result.button.accept) {
            const setting = ServerConnection.makeSettings();
            const apiURL = URLExt.join(setting.baseUrl, 'api/shutdown');

            return ServerConnection.makeRequest(
              apiURL,
              { method: 'POST' },
              setting
            )
              .then((result: any) => {
                if (result.ok) {
                  // Close this window if the shutdown request has been successful
                  const body = document.createElement('div');
                  const p1 = document.createElement('p');
                  p1.textContent =
                    'You have shut down the Analysis Facility session.';

                  const baseUrl = new URL(setting.baseUrl);
                  const link = document.createElement('a');
                  link.href =
                    baseUrl.protocol + '//' + baseUrl.hostname + '/home';
                  link.textContent =
                    'Click here or refresh the page to restart the session.';
                  link.style.color = 'var(--jp-content-link-color)';

                  body.appendChild(p1);
                  body.appendChild(link);
                  void showDialog({
                    title: 'Session closed.',
                    body: new Widget({ node: body }),
                    buttons: []
                  });
                } else {
                  throw new ServerConnection.ResponseError(result);
                }
              })
              .catch((data: any) => {
                throw new ServerConnection.NetworkError(data);
              });
          }
        });
      },
    });
  }
};

export default plugin;

