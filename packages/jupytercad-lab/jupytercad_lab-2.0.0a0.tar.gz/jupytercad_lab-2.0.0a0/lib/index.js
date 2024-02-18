import { ControlPanelModel, jcLightIcon, LeftPanelWidget, RightPanelWidget, addCommands, CommandIDs } from '@jupytercad/base';
import { IAnnotationToken, IJCadFormSchemaRegistryToken, IJupyterCadDocTracker } from '@jupytercad/schema';
import { ILayoutRestorer } from '@jupyterlab/application';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';
import { notebookRenderePlugin } from './notebookrenderer';
const NAME_SPACE = 'jupytercad';
const plugin = {
    id: 'jupytercad:lab:main-menu',
    autoStart: true,
    requires: [IJupyterCadDocTracker, IJCadFormSchemaRegistryToken],
    optional: [IMainMenu, ITranslator],
    activate: (app, tracker, formSchemaRegistry, mainMenu, translator) => {
        console.log('jupytercad:lab:main-menu is activated!');
        translator = translator !== null && translator !== void 0 ? translator : nullTranslator;
        const isEnabled = () => {
            return (tracker.currentWidget !== null &&
                tracker.currentWidget === app.shell.currentWidget);
        };
        addCommands(app, tracker, translator, formSchemaRegistry);
        if (mainMenu) {
            populateMenus(mainMenu, isEnabled);
        }
    }
};
const controlPanel = {
    id: 'jupytercad:lab:controlpanel',
    autoStart: true,
    requires: [
        ILayoutRestorer,
        IJupyterCadDocTracker,
        IAnnotationToken,
        IJCadFormSchemaRegistryToken
    ],
    activate: (app, restorer, tracker, annotationModel, formSchemaRegistry) => {
        const controlModel = new ControlPanelModel({ tracker });
        const leftControlPanel = new LeftPanelWidget({
            model: controlModel,
            annotationModel,
            tracker
        });
        leftControlPanel.id = 'jupytercad::leftControlPanel';
        leftControlPanel.title.caption = 'JupyterCad Control Panel';
        leftControlPanel.title.icon = jcLightIcon;
        const rightControlPanel = new RightPanelWidget({
            model: controlModel,
            formSchemaRegistry
        });
        rightControlPanel.id = 'jupytercad::rightControlPanel';
        rightControlPanel.title.caption = 'JupyterCad Control Panel';
        rightControlPanel.title.icon = jcLightIcon;
        if (restorer) {
            restorer.add(leftControlPanel, NAME_SPACE);
            restorer.add(rightControlPanel, NAME_SPACE);
        }
        app.shell.add(leftControlPanel, 'left', { rank: 2000 });
        app.shell.add(rightControlPanel, 'right', { rank: 2000 });
    }
};
/**
 * Populates the application menus for the notebook.
 */
function populateMenus(mainMenu, isEnabled) {
    // Add undo/redo hooks to the edit menu.
    mainMenu.editMenu.undoers.redo.add({
        id: CommandIDs.redo,
        isEnabled
    });
    mainMenu.editMenu.undoers.undo.add({
        id: CommandIDs.undo,
        isEnabled
    });
}
export default [plugin, controlPanel, notebookRenderePlugin];
