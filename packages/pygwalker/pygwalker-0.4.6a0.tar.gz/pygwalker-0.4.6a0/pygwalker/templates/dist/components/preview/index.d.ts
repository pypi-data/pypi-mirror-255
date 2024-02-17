import React from "react";
import type { IDarkMode } from '@kanaries/graphic-walker/dist/interfaces';
interface IPreviewProps {
    themeKey: string;
    dark: IDarkMode;
    charts: {
        visSpec: any;
        data: string;
    }[];
}
declare const Preview: React.FC<IPreviewProps>;
interface IChartPreviewProps {
    themeKey: string;
    dark: string;
    visSpec: any;
    data: string;
    title: string;
    desc: string;
}
declare const ChartPreview: React.FC<IChartPreviewProps>;
export { Preview, ChartPreview, };
export type { IPreviewProps, IChartPreviewProps };
