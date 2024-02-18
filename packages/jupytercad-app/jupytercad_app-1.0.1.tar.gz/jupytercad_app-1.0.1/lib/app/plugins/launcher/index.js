import { ILabShell } from '@jupyterlab/application';
const launcherPlugin = {
    id: '@jupyterlab/-custom-launcher-extension',
    description: 'Customize the default launcher.',
    requires: [ILabShell],
    autoStart: true,
    activate: (app, labShell) => {
        labShell.layoutModified.connect(() => {
            const els = document.getElementsByClassName('jp-Launcher-sectionTitle');
            const length = els.length;
            for (let idx = 0; idx < length; idx++) {
                const element = els.item(idx);
                if (element) {
                    element.innerHTML = 'Create New Project';
                }
            }
        });
    }
};
export default launcherPlugin;
