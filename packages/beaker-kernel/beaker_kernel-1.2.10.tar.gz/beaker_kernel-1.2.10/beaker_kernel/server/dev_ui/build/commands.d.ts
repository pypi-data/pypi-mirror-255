/**
 * Set up keyboard shortcuts & commands for notebook
 */
import { ISessionContextDialogs } from '@jupyterlab/apputils';
import { CompletionHandler } from '@jupyterlab/completer';
import { NotebookPanel } from '@jupyterlab/notebook';
import { CommandRegistry } from '@lumino/commands';
import { CommandPalette } from '@lumino/widgets';
/**
 * The map of command ids used by the notebook.
 */
export declare const COMMAND_IDS: {
    invoke: string;
    select: string;
    invokeNotebook: string;
    selectNotebook: string;
    startSearch: string;
    findNext: string;
    findPrevious: string;
    save: string;
    interrupt: string;
    restart: string;
    switchKernel: string;
    runAndAdvance: string;
    run: string;
    deleteCell: string;
    selectAbove: string;
    selectBelow: string;
    extendAbove: string;
    extendTop: string;
    extendBelow: string;
    extendBottom: string;
    editMode: string;
    merge: string;
    split: string;
    commandMode: string;
    undo: string;
    redo: string;
    insert: string;
    cut: string;
    copy: string;
    paste: string;
    restartAndRun: string;
};
export declare const setupCommands: (commands: CommandRegistry, palette: CommandPalette, nbWidget: NotebookPanel, handler: CompletionHandler, sessionContextDialogs: ISessionContextDialogs) => void;
/**
 * Set up keyboard shortcuts & commands for notebook
 */
