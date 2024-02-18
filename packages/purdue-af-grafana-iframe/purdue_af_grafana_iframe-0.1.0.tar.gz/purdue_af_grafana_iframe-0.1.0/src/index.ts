import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { ICommandPalette, IThemeManager } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { LabIcon } from '@jupyterlab/ui-components';

const PALETTE_CATEGORY = 'Extensions';
const LAUNCHER_CATEGORY = 'Other';

namespace CommandIDs {
  export const open_iframe = 'jlab:open-iframe-from-launcher';
}

import iconSvgString from '../style/icons/grafana.svg';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'purdue-af-grafana-iframe:plugin',
  description: 'Adds a custom iframe item that opens an iframe when clicked.',
  autoStart: true,
  optional: [ISettingRegistry, ILauncher, ICommandPalette, IThemeManager],
  activate: async (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    launcher: ILauncher | null,
    palette: ICommandPalette | null,
    themeManager: IThemeManager | null
  ) => {
    const { commands } = app;
    const command = CommandIDs.open_iframe;
    console.log('JupyterLab extension purdue-af-grafana-iframe is activated!');

    let url = '';
    let launcherItemLabel = 'Open iframe';
    let launcherItemCaption = 'Open iframe in a new tab';
    let launcherItemRank = 1;

    if (settingRegistry) {
      try {
        const settings = await settingRegistry.load(plugin.id);
        if ('url' in settings.composite) {
          url = settings.composite['url'] as string;
        }
        if ('label' in settings.composite) {
          launcherItemLabel = settings.composite['label'] as string;
        }
        if ('caption' in settings.composite) {
          launcherItemCaption = settings.composite['caption'] as string;
        }
        if ('rank' in settings.composite) {
          launcherItemRank = parseInt(settings.composite['rank'] as string, 10) || launcherItemRank;
        }
        console.log('purdue-af-grafana-iframe settings loaded:', settings.composite);
      } catch (reason) {
        console.error('Failed to load settings for purdue-af-grafana-iframe.', reason);
      }
    }

    themeManager?.themeChanged.connect((sender, args) => {
      const isLight =
      themeManager && themeManager.theme
        ? themeManager.isLight(themeManager.theme)
        : true;

      url = updateUrlTheme(url, isLight);

      const iframes = document.querySelectorAll('iframe');
      iframes.forEach(iframe => {
        let iframeSrc = iframe.getAttribute('src') || '';
        if (iframeSrc.includes("grafana")) {
          iframeSrc = updateUrlTheme(iframeSrc, isLight);
          iframe.setAttribute('src', iframeSrc);
          iframe.src = iframe.src;
        }
      });
    });

    const icon = new LabIcon({
      name: 'launcher:grafana-icon',
      svgstr: iconSvgString
    });

    commands.addCommand(command, {
      label: launcherItemLabel,
      caption: launcherItemCaption,
      icon: icon,
      execute: async args => {
        await commands.execute('iframe:open', { path:url });
      }
    });

    if (launcher) {
      launcher.add({
        command,
        category: LAUNCHER_CATEGORY,
        rank: launcherItemRank
      });
    }

    if (palette) {
      palette.addItem({
        command,
        args: { isPalette: true },
        category: PALETTE_CATEGORY
      });
    }

  }
};

function updateUrlTheme(url: string, isLight: boolean) {
  if (url.includes("&theme=")) {
    url = url.replace(/&theme=(light|dark)/, "");
  }
  if (isLight) {
    url += "&theme=light";
  } else {
    url += "&theme=dark";
  }
  return url;
}

export default plugin;
