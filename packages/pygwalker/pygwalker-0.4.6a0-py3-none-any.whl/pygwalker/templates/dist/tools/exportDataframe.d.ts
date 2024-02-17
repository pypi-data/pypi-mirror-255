import React from 'react';
import type { IAppProps } from '../interfaces';
import type { ToolbarButtonItem } from "@kanaries/graphic-walker/dist/components/toolbar/toolbar-button";
import type { VizSpecStore } from '@kanaries/graphic-walker/dist/store/visualSpecStore';
export declare function getExportDataframeTool(props: IAppProps, storeRef: React.MutableRefObject<VizSpecStore | null>): ToolbarButtonItem;
