import { JupyterCadModel, IJupyterCadTracker, IJCadWorkerRegistry, IJCadExternalCommandRegistry } from '@jupytercad/schema';
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { CommandRegistry } from '@lumino/commands';
import { JupyterCadWidget } from '@jupytercad/base';
interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    tracker: IJupyterCadTracker;
    commands: CommandRegistry;
    workerRegistry: IJCadWorkerRegistry;
    externalCommandRegistry: IJCadExternalCommandRegistry;
    backendCheck?: () => boolean;
}
export declare class JupyterCadWidgetFactory extends ABCWidgetFactory<JupyterCadWidget, JupyterCadModel> {
    constructor(options: IOptions);
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    protected createNewWidget(context: DocumentRegistry.IContext<JupyterCadModel>): JupyterCadWidget;
    private _commands;
    private _workerRegistry;
    private _externalCommandRegistry;
    private _backendCheck?;
}
export {};
